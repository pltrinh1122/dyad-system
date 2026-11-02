"""The seat-hop simulator's world (d-work #546; the fixture the scenarios of `test_seat_hops.py` script against).

What it builds, all in scratch directories:
- a bare `origin` seeded with a d-work row store;
- one clone per session; a session is a seat on a host. The host is set by env — `CLAUDE_CODE_REMOTE` (`true` for
  cloud, `false` for a terminal) and `DYAD_SIM_OS` (a label: `linux`, `mac`) — and the holder by
  `CLAUDE_CODE_SESSION_ID`, so `board.py` reads them as it reads a real harness's;
- a mailbox that models `send_message` between sessions. A terminal holder cannot read it (no inbound messages), but
  it can send;
- seats: cloud seats receive a dispatch, run its act once and report to the cos address they know. A terminal desk
  receives nothing, so it reads the board and reports by writing it;
- the Operator, as the log of lines the Operator sees;
- external runs, as a status table.

The cos protocol modelled is P1 as built by #535 (`dyad board set` and `dyad board resume`, write-ahead), and nothing
else: no inbox (#536), no lease (#537). Every board write is a real `dyad board set`, landed through `land.py` onto the
bare origin. The merge is the real `dyad merge`.

Not simulated, stated: the real harness's permission classifier, a real Remote Control attach, and a real
`send_message` transport — the mailbox stands in for it.
"""
import collections, contextlib, dataclasses, datetime, io, os, shutil, subprocess, sys, unittest.mock
from pathlib import Path

PKG = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib, livetest

INST = "agent-corpus"
ROW = "id: {id}\ntitle: row {id}\nopened: 2026-11-02\nstate: {state}\ndisposed: {disposed}\nrefs: \n"
RESUMED = "cos resumed in {seat}"
bd = dyadlib.load_guard("agent", "board")


def git(d: Path, *a: str, check: bool = True) -> str:
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=dyadlib.git_env())
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(a)} in {d}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


@dataclasses.dataclass
class Host:
    name: str
    kind: str                  # "cloud" | "terminal"
    os: str = "linux"
    skew_minutes: int = 0      # how far this host's clock runs ahead

    @property
    def terminal(self) -> bool:
        return self.kind == "terminal"


class Mailbox:
    """`send_message`: a message goes to a harness id; a terminal holder cannot read its box (Rule-16's hosts; #536)."""
    def __init__(self):
        self.boxes: dict[str, list[tuple]] = collections.defaultdict(list)

    def send(self, to: str, msg: tuple) -> None:
        self.boxes[to].append(msg)

    def read(self, session: "Session") -> list[tuple]:
        if session.host.terminal:
            return []
        got, self.boxes[session.harness] = self.boxes[session.harness], []
        return got

    def unread(self) -> list[tuple]:
        return [(to, m) for to, ms in self.boxes.items() for m in ms]


class Session:
    """A seat on a host: one clone of the origin, its env, and `dyad board` run in-process under that env."""
    def __init__(self, world: "World", seat: str, host: Host, harness: str):
        self.world, self.seat, self.host, self.harness = world, seat, host, harness
        self.dir = world.top / f"clone-{harness}"
        git(world.top, "clone", "-q", str(world.origin), str(self.dir))
        for k, v in (("user.email", "t@example.com"), ("user.name", "t"), ("core.hooksPath", str(world.hooks))):
            git(self.dir, "config", k, v)
        self.warnings: list[str] = []

    @property
    def env(self) -> dict[str, str]:
        return {"DYAD_INSTANCE": INST, "DYAD_SESSION": self.seat, "CLAUDE_CODE_SESSION_ID": self.harness,
                "CLAUDE_CODE_REMOTE": "false" if self.host.terminal else "true", "DYAD_SIM_OS": self.host.os}

    @contextlib.contextmanager
    def acting(self):
        """This session's env, and its host's clock for `since`."""
        skew = datetime.timedelta(minutes=self.host.skew_minutes)
        clock = lambda: (datetime.datetime.now(datetime.timezone.utc) + skew).strftime("%Y-%m-%dT%H:%MZ")
        with unittest.mock.patch.dict(os.environ, self.env), unittest.mock.patch.object(bd, "now_iso", clock):
            yield

    def board(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with self.acting(), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = bd.cli(list(argv), self.dir)
        self.warnings += [l for l in err.getvalue().splitlines() if l.startswith("warn: ")]
        return rc, out.getvalue(), err.getvalue()

    def set(self, row, **pairs) -> int:
        """`dyad board set <row> key=value…`; keys written with `_` for `-`. Raises on a refusal other than
        `already landed`, so a scenario never mistakes a failed write for one that landed."""
        argv = ["set", str(row)] + [f"{k.replace('_', '-')}={v}" for k, v in pairs.items()]
        rc, out, err = self.board(*argv)
        if rc and "already landed" not in err:
            raise WriteRefused(err.strip())
        return rc

    def sync(self) -> bool:
        """`git pull --ff-only` of main; False when the hosting is unreachable (the local clone is all there is)."""
        return subprocess.run(["git", "pull", "-q", "--ff-only", "origin", "main"], cwd=self.dir, capture_output=True,
                              env=dyadlib.git_env()).returncode == 0

    def entries(self) -> dict[str, dict[str, str]]:
        with self.acting():
            return dict(bd.load(self.dir))

    def resume_text(self) -> str:
        return self.board("resume")[1]


class WriteRefused(Exception):
    pass


class Seat:
    """A seat the cos dispatches to. A cloud seat receives messages; a terminal desk receives none, so it reads the
    board. Each act it runs is counted in `world.acts`; its report goes to the cos address it last knew."""
    def __init__(self, world: "World", session: Session, cos: str):
        self.world, self.session, self.cos = world, session, cos
        self.pending: list[str] = []
        self.done: set[str] = set()

    @property
    def name(self) -> str:
        return self.session.seat

    def step(self) -> None:
        """Read what reached it, run each act once per message, report each."""
        if self.session.host.terminal:
            self.session.sync()
            for row, f in self.session.entries().items():
                nxt = f.get("next", "")
                if row != bd.COS and f.get("owner", "").split()[:1] == [self.name] and nxt.startswith("do "):
                    task = nxt[3:]
                    self.world.acts[task] += 1
                    self.session.set(row, next=f"reported {task}")
            return
        for msg in self.world.mailbox.read(self.session):
            if msg[0] == "announce":
                self.cos = msg[1]
            elif msg[0] in ("dispatch", "relay"):
                self.world.acts[msg[1]] += 1
                self.pending.append(msg[1])
        for task in self.pending:
            self.world.mailbox.send(self.cos, ("report", task))
        self.pending = []


class Cos:
    """The cos mode in one session: the P1 protocol, write-ahead, on the board."""
    def __init__(self, world: "World", session: Session, operator: "Operator"):
        self.world, self.s, self.operator = world, session, operator

    # ---- acts before a hop; `crash` stops the turn at "before-wa" or "after-wa"
    def dispatch(self, row: int, seat: Seat, task: str, crash: str | None = None, kind: str = "dispatch") -> None:
        if crash == "before-wa":
            return
        verb = "do" if seat.session.host.terminal else "send"
        self.s.set(row, owner=f"{seat.name} {seat.session.harness}", waiting_on=f"seat {seat.name}", next=f"{verb} {task}")
        if crash == "after-wa":
            return
        self.send_pending(row)

    def send_pending(self, row) -> None:
        f = self.s.entries().get(str(row), {})
        nxt = f.get("next", "")
        if nxt.startswith("send "):
            task, owner = nxt[5:], f["owner"].split()
            self.world.mailbox.send(owner[1], ("relay" if task.startswith("relay ") else "dispatch", task))
            self.s.set(row, next=f"await {task}")

    def ask(self, row: int, question: str, crash: str | None = None) -> None:
        if crash == "before-wa":
            return
        self.s.set(row, waiting_on="operator", question=question)
        if crash == "after-wa":
            return
        self.operator.show(question)

    def gate(self, row: int, run: str, crash: str | None = None) -> None:
        if crash == "before-wa":
            return
        self.s.set(row, waiting_on=f"external run {run}", next=f"record release after run {run}")

    def promise(self, row: int, text: str, crash: str | None = None) -> None:
        if crash == "before-wa":
            return
        self.s.set(row, promised=text)
        if crash == "after-wa":
            return
        self.operator.show(f"promised: {text}")

    # ---- the hop
    def resume(self, retry_until_reachable: bool = True) -> str:
        """`dyad board resume` and act on it: say the one resume line, take the holder (write-ahead), re-present every
        question owed verbatim, send what is written but unsent, run what a gate allows, announce to every seat."""
        self.s.sync()
        text = self.s.resume_text()
        self.operator.show(RESUMED.format(seat=self.s.seat))
        while True:
            try:
                self.s.set(bd.COS, holder=self.s.seat)
                break
            except WriteRefused:
                if not retry_until_reachable or not self.world.outage_over():
                    raise
        for row, f in self.s.entries().items():
            if row == bd.COS:
                continue
            if f.get("waiting-on") == "operator" and f.get("question"):
                self.operator.show(f["question"])
            self.send_pending(row)
            self.run_gate(row, f)
            self.run_merge(row, f)
        seats = [l for l in text.splitlines() if l.startswith("announce to")]
        for name in (seats[0].split(": ", 1)[1].split(";")[0].split(", ") if seats else []):
            seat = self.world.seats.get(name)
            if seat:
                self.world.mailbox.send(seat.session.harness, ("announce", self.s.harness))
        return text

    def run_gate(self, row, f) -> None:
        w = f.get("waiting-on", "")
        if w.startswith("external run "):
            run = w.split()[-1]
            if self.world.runs.get(run) == "completed":
                self.world.acts[f"release {run}"] += 1
                self.s.set(row, waiting_on="", next=f"released {run}")

    def run_merge(self, row, f) -> None:
        nxt = f.get("next", "")
        if nxt.startswith("merge "):
            pr, sha = nxt.split()[1], nxt.split()[3]
            self.world.merge(self.s, int(pr), sha)
            self.s.set(row, next=f"merged {pr}", waiting_on="")

    # ---- after the hop
    def read_reports(self) -> None:
        for msg in self.world.mailbox.read(self.s):
            if msg[0] == "report":
                self.world.completed.add(msg[1])
        self.s.sync()
        for row, f in self.s.entries().items():
            if f.get("next", "").startswith("reported "):
                self.world.completed.add(f["next"][9:])
            self.run_gate(row, f)


class Operator:
    def __init__(self, name: str = "operator"):
        self.name, self.lines = name, []

    def show(self, line: str) -> None:
        self.lines.append(line)


@dataclasses.dataclass
class Item:
    """One thing in flight at the hop: `kind` is one of the (c) values, `key` the act, question or text."""
    kind: str
    key: str
    row: int


class World:
    def __init__(self, scratch: livetest.ScratchInstalls, rows: dict[int, str] | None = None, pr: bool = False):
        self.top = scratch.mkdtemp(prefix="dyad-sim-")
        seed, self.origin, self.hooks = self.top / "seed", self.top / "origin.git", self.top / "hooks"
        seed.mkdir(); git(seed, "init", "-q", "-b", "main")
        rows_dir = seed / INST / "d-work" / "rows"; rows_dir.mkdir(parents=True)
        (seed / "dyad").mkdir(); (seed / "dyad" / "a.txt").write_text("a\n")
        self.rows = dict(rows or {5: "planned", 6: "done"})
        for rid, state in self.rows.items():
            (rows_dir / f"{rid}.md").write_text(ROW.format(id=rid, state=state, disposed="2026-11-02 Y plan"))
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "seed")
        git(self.top, "clone", "-q", "--bare", str(seed), str(self.origin))
        self.racer, self.race, self.race_log = self.top / "racer", self.top / "race", self.top / "raced"
        git(self.top, "clone", "-q", str(self.origin), str(self.racer))
        self.hooks.mkdir()
        (self.hooks / "pre-push").write_text(      # a push loses a race once when `arm_race` armed one: main moves first
            "#!/bin/sh\ncat >/dev/null\n"
            f"if [ -f '{self.race}' ]; then rm -f '{self.race}'; echo raced >> '{self.race_log}'; "
            f"env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git -C '{self.racer}' push -q origin HEAD:main; fi\n"
            "exit 0\n")
        (self.hooks / "pre-push").chmod(0o755)
        self.mailbox, self.acts, self.completed = Mailbox(), collections.Counter(), set()
        self.seats: dict[str, Seat] = {}
        self.runs: dict[str, str] = {}
        self.sessions: list[Session] = []
        self._outage: Path | None = None
        self.outages_seen = 0
        self.pr_sha = self.open_pr(7) if pr else None

    # ---- hosts, sessions, seats
    def session(self, seat: str, host: Host, harness: str) -> Session:
        s = Session(self, seat, host, harness); self.sessions.append(s)
        return s

    def cos(self, seat: str, host: Host, harness: str, operator: Operator) -> Cos:
        return Cos(self, self.session(seat, host, harness), operator)

    def seat(self, name: str, host: Host, harness: str, cos: Cos) -> Seat:
        s = Seat(self, self.session(name, host, harness), cos.s.harness); self.seats[name] = s
        return s

    def settle(self, cos: Cos, rounds: int = 3) -> None:
        """Seats act and report, the holder reads; a few rounds, as turns would."""
        for _ in range(rounds):
            for seat in self.seats.values():
                seat.step()
            cos.read_reports()

    # ---- the merge and the hosting
    def open_pr(self, pr: int) -> str:
        """A PR branch pushed as `refs/pull/<pr>/head`, and row 9 carrying its operative `Y done`."""
        work = self.top / "author"
        git(self.top, "clone", "-q", str(self.origin), str(work))
        git(work, "checkout", "-q", "-b", "pr")
        (work / "dyad" / "b.txt").write_text("b\n"); git(work, "add", "-A"); git(work, *livetest.IDENTITY, "commit", "-qm", "pr")
        sha = git(work, "rev-parse", "HEAD")
        git(work, "push", "-q", "origin", f"{sha}:refs/pull/{pr}/head")
        git(work, "checkout", "-q", "main")
        (work / INST / "d-work" / "rows" / "9.md").write_text(
            ROW.format(id=9, state="planned", disposed=f"2026-11-02 Y plan; 2026-11-02 Y done (merges PR #{pr} at {sha})"))
        git(work, "add", "-A"); git(work, *livetest.IDENTITY, "commit", "-qm", "ledger: #9"); git(work, "push", "-q", "origin", "HEAD:main")
        self.rows[9] = "planned"
        return sha

    def merge(self, session: Session, pr: int, sha: str) -> str:
        """The real `dyad merge`, from this session's clone; `refused: …` when it refuses."""
        mod = dyadlib.load_module(PKG / "scripts" / "merge.py", "merge")
        out, err = io.StringIO(), io.StringIO()
        with session.acting(), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            mod.main([str(pr), "--head", sha], session.dir)
        return (out.getvalue() + err.getvalue()).strip()

    def landings(self, sha: str) -> int:
        """How many first-parent merges on origin's main bring `sha` in: a merge executed twice would be two."""
        lines = git(self.origin, "rev-list", "--first-parent", "--merges", "--parents", "main").splitlines()
        return sum(1 for l in lines if l.split()[2:3] == [sha])

    def arm_race(self) -> None:
        """The next push through a session's hook finds `main` moved by another seat's commit (a lost push)."""
        git(self.racer, "pull", "-q", "--ff-only", "origin", "main")
        n = len(list((self.racer / "dyad").glob("race-*.txt")))
        (self.racer / "dyad" / f"race-{n}.txt").write_text(f"{n}\n")
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", f"racing {n}")
        self.race.write_text("1")

    @property
    def raced(self) -> int:
        return len(self.race_log.read_text().splitlines()) if self.race_log.exists() else 0

    def outage(self) -> None:
        """The hosting unreachable: the bare origin moved aside."""
        self._outage = self.origin.with_name("origin-away.git"); self.origin.rename(self._outage)

    def reconnect(self) -> None:
        if self._outage:
            self._outage.rename(self.origin); self._outage = None

    def outage_over(self) -> bool:
        """A retry loop's tick: the hosting comes back on the first retry (the scenario says when it went away)."""
        if self._outage:
            self.outages_seen += 1; self.reconnect(); return True
        return False


def oracle(world: World, truth: list[Item], operator: Operator, mark: int, holder: Cos, owed: list[str]) -> list[str]:
    """The plan's four clauses, as violations: an item of (c) lost, an act run twice, a state question asked of the
    Operator, more than the one resume line visible. `mark` is the Operator log's length at the hop; `owed` the
    questions the Operator truly owes at it, whose re-presentation is the resume, not noise."""
    v = []
    after = operator.lines[mark:]
    board = holder.s.entries()
    for it in truth:
        if it.kind in ("dispatch", "relay") and it.key not in world.completed:
            v.append(f"lost: {it.kind} {it.key} (its report never reached the holder)")
        elif it.kind == "question" and it.key not in after and it.key not in operator.lines[:mark]:
            v.append(f"lost: question {it.key!r}")
        elif it.kind == "gate" and not (board.get(str(it.row), {}).get("waiting-on") == f"external run {it.key}"
                                        or world.acts[f"release {it.key}"]):
            v.append(f"lost: gate run {it.key}")
        elif it.kind == "promised" and board.get(str(it.row), {}).get("promised") != it.key:
            v.append(f"lost: promise {it.key!r}")
    v += [f"executed twice: {k} ({n} times)" for k, n in sorted(world.acts.items()) if n > 1]
    v += [f"state question: {l!r}" for l in after if l.lower().startswith("state?")]
    noise = [l for l in after if l not in owed and not l.startswith("cos resumed in ")]
    resumed = [l for l in after if l.startswith("cos resumed in ")]
    if len(resumed) > 1:
        v.append(f"visible: {len(resumed)} resume lines")
    v += [f"visible: {l!r} (not owed at the hop)" for l in noise]
    return v
