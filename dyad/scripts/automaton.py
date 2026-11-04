#!/usr/bin/env python3
"""`dyad automaton scan|run` — the d-work automaton (d-work #556; backlog #542 absorbed). Kernel: Python 3.12+, git.

The d-work's clerical edges, run by a party that decides nothing: the countersign model's executor, #553's
automaton. Everything between a recorded disposition and the next inferred act is defined, so it is run here, from
ledger lines only and never from a conversation:
  (a) **merge** — every PR an operative `Y done` names, pinned to the head it names, in the order it names them, as
      one cut: the record-bound `merge_all` (scripts/merge.py: the entry, the live heads, clean merges, one push through
      the gate, so the gate judges the cut's final tree once; d-work #562). A cut lands whole or not at all. A push that
      loses a race to `main` is re-merged at once, without backoff: after a ledger-only drift the gate's code-keyed memo
      skips the suite, so the retry costs the guards only (#562 (c));
  (b) **close** — a row whose every named head is on `main` goes `done`, its accreted rows close under its mandate and
      its board entry is dropped (`dyad steps close-landed --land`, scripts/steps.py);
  (c) **notice** — a row whose last disposition is a `Y plan` and whose board entry names owners: the entry is set
      waiting on its first owner, the plan its next act, its question removed (#572 K1), and each owner's inbox gets
      one `notice`, "row #N planned; read plans/N.md", with "; yours: <part>" when the plan's `parts:` line names the
      owner's part (K2, the relay that restated the plan). A `Y done` whose cut does not land in the run sets the
      entry waiting on that merge (K3). The seat still infers from the plan.
  (d) **corroborate** — after a cut lands, `check --corroborate <before> <after>` runs on the landed tree in the same
      job: what hosted CI on `main` checks, which a push made with the workflow's token never starts (d-work #564 E1).
      The suite runs only when the landed code differs from an evidenced PR head. A failure is posted to home and the
      run exits 1, so the run's conclusion shows it.
A refusal decides nothing: it is posted once to the home's inbox as a `notice` (the board's `_cos` holder, or
`AUTOMATON_HOME`), and the home takes it from there by inference. Every message names the row and never quotes an entry
(the inbox carries information, never authority, #536).

**Stateless.** Every run re-reads `origin/main` (the rows, the board, the inbox) and every act is idempotent: a merged
head, a closed row and a notice already posted are skipped. Any run may be retried, and a run that dies mid-way loses
nothing. Memory across runs (a retry) lives in the run itself or in the store, never here.

  dyad automaton scan      read-only: the acts a run would take now, one line each
  dyad automaton run       take them; one line per act and per refusal; exit 1 when a landed cut failed
                           corroboration, else 0 unless the automaton itself failed
  dyad automaton sweep [--row <id>]
                           read-only, twice a day (d-work #564): every guard over every store and the full suite on
                           origin/main, Y dones whose heads never landed, stale board entries, released tags
                           against their entries, the mirror against main, and code pushes to main with no
                           completed corroboration, the backlog's hygiene (scripts/hygiene.py, #565: findings
                           and `candidate:` similarity lines) and the work in flight (W1-W10', #569, one notice
                           per kind). One `finding:` line each; a finding not yet told is posted, in
                           one notice, to the home's inbox on `--row`. Exit 1 when a finding fails

It runs from `main`'s own code: server-side in `.github/workflows/dyad-automaton.yml` on every push to `main`, gated by
the repository variable `DYAD_AUTOMATON` (`on`, the operator's switch), and by hand by any unit for recovery. Its
commits carry the identity of whoever runs it; its inbox messages come from the seat `automaton` (`DYAD_SESSION`).
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("automaton.py: Python 3.12+ required")
import os, re, subprocess
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

HERE = Path(__file__).resolve().parent
land = dyadlib.load_module(HERE / "land.py", "land")
merge_mod = dyadlib.load_module(HERE / "merge.py", "merge")
steps = dyadlib.load_module(HERE / "steps.py", "steps")
hygiene_mod = dyadlib.load_module(HERE / "hygiene.py", "hygiene")   # the sweep's backlog hygiene (d-work #565)
Refused = land.Refused
SEAT = "automaton"                           # the inbox sender; path-shaped, so a box name too
RACE_TRIES = 5                               # a push that lost a race to main, re-merged at once (#562 (c))
PLANNED = "row #{rid} planned; read plans/{rid}.md"
USAGE = "usage: dyad automaton scan|run|sweep [--row <id>]"

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("seat-is-path-shaped", lambda: bool(re.fullmatch(r"[A-Za-z0-9._-]+", SEAT))),
    ("retries-bounded", lambda: 1 < RACE_TRIES <= 10),
]
TREE_INVARIANTS = [   # loads a guard, so never at import (crafts/syseng/rules/invariants.md)
    ("notice-is-information", lambda: not dyadlib.load_guard("agent", "inbox").DISPOSITION.search(PLANNED.format(rid=1))),
]


def rows_guard():
    return dyadlib.load_guard("agent", "rows")


def inbox():
    return dyadlib.load_guard("agent", "inbox")


def board():
    return dyadlib.load_guard("agent", "board")


# ---- reading main
def show(repo: Path, base: str, rel: str) -> str | None:
    r = land.git(repo, "show", f"{base}:{rel}", check=False)
    return r.stdout if r.returncode == 0 else None


def ls(repo: Path, base: str, rel: str) -> list[str]:
    r = land.git(repo, "ls-tree", "--name-only", f"{base}:{rel}", check=False)
    return r.stdout.split() if r.returncode == 0 else []


def inst(repo: Path) -> str:
    rel = dyadlib.instance_rel(repo)
    if rel is None:
        raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree")
    return rel


def home(repo: Path, base: str) -> str | None:
    """The home's seat: `AUTOMATON_HOME`, else the holder of the board's `_cos` entry on main."""
    if os.environ.get("AUTOMATON_HOME"):
        return os.environ["AUTOMATON_HOME"]
    text = show(repo, base, f"{inst(repo)}/d-work/board/{board().COS}.md")
    return board().parse(text)[0].get("holder") if text else None


def box_messages(repo: Path, base: str, seat: str) -> list[dict[str, str]]:
    d = f"{inst(repo)}/d-work/inbox/{seat}"
    return [board().parse(show(repo, base, f"{d}/{n}") or "")[0] for n in ls(repo, base, d) if n.endswith(".md")]


def posted(repo: Path, base: str, seat: str, row: int, body: str) -> bool:
    return any(m.get("from") == SEAT and m.get("row") == str(row) and m.get("body") == body for m in box_messages(repo, base, seat))


# ---- the acts a run would take
def plan(repo: Path) -> tuple[str, list[tuple]]:
    """(base, acts) on a freshly fetched origin/main: ("merge", rid, [(pr, sha), …]) — one cut per row, in the row's
    own order — then ("close", rid), then ("board", rid, pairs) and ("notice", rid, owner, body). Pure reading."""
    base = land.fetch(repo)
    rows = dyadlib.read_rows(repo, at=base)
    rg, acts = rows_guard(), []
    for r in rows:
        if r.state in dyadlib.TERMINAL_STATES or not rg.operative_done(r.disposed):
            continue
        named = [(pr, h) for _, pr, h, _ in rg.named_heads([r])]
        if not named:
            continue
        owed = [(pr, h) for pr, h in named if not steps.ancestor(repo, h, base)]
        cut = [(int(pr), h) for pr, h in owed if pr]
        if cut:
            acts.append(("merge", r.id, cut))
        if not owed:
            acts.append(("close", r.id))
    for r in rows:
        last = [e for e in rg.entries(r.disposed) if not rg.is_ready(e)][-1:] or [""]
        if r.state != "planned" or not rg.PLAN_Y.match(last[0]):
            continue
        text = show(repo, base, f"{inst(repo)}/d-work/board/{r.id}.md")
        if not text:
            continue
        entry = board().parse(text)[0]
        owners = board().owners(entry)
        if owners and (pairs := planned_flip(r.id, entry, owners)):
            acts.append(("board", r.id, pairs))                       # #572 K1: before the notices it announces
        parts = plan_parts(show(repo, base, f"{inst(repo)}/d-work/plans/{r.id}.md") or "")
        for owner in owners:
            body = notice_body(r.id, part_for(parts, owner))
            if not posted(repo, base, owner, r.id, body):
                acts.append(("notice", r.id, owner, body))
    return base, acts


# ---- the clerical board writes a recorded line decides (d-work #572 K1-K3)
PARTS = re.compile(r"(?im)^\s*parts:\s*(.+)$")

def plan_parts(text: str) -> dict[str, str]:
    """{unit: part} from a plan's optional `parts:` line, `<unit>: <part>; <unit>: <part>` (#572 K2); {} without one."""
    m = PARTS.search(text)
    out = {}
    for item in (m.group(1).split(";") if m else []):
        unit, sep, part = item.partition(":")
        if sep and unit.strip() and part.strip():
            out[unit.strip()] = part.strip()
    return out

def part_for(parts: dict[str, str], seat: str) -> str | None:
    """The part a plan's `parts:` line names for `seat`: by its full seat name, or by its function (the name before
    its `-<hp>`)."""
    return parts.get(seat) or parts.get(re.sub(r"-[0-9a-f]{8}$", "", seat))

def notice_body(rid: int, part: str | None) -> str:
    """The plan notice, quoting the unit's own part when the plan names one (#572 K2: the relay that restated the
    plan); masked as `post` masks it, so the told text and the compared text are the same."""
    body = PLANNED.format(rid=rid) + (f"; yours: {part}" if part else "")
    return inbox().DISPOSITION.sub("[an entry, read in the ledger]", body)

def planned_flip(rid: int, entry: dict[str, str], owners: list[str]) -> dict[str, str] | None:
    """#572 K1: the board pairs a recorded `Y plan` decides — waiting on the first owner, the plan as the next act, no
    question — or None when the entry already waits on a unit (the flip is done, or home has moved it on)."""
    if entry.get("waiting-on", "").startswith(("unit ", board().UNIT_ALIAS)):
        return None
    return {"waiting-on": f"unit {owners[0]}", "next": f"execute plans/{rid}.md", "question": "",
            "holder": entry.get("holder", "")}

def pending_flip(entry: dict[str, str], cut: list[tuple[int, str]]) -> dict[str, str] | None:
    """#572 K3: the board pairs a recorded `Y done` whose cut did not land in this run decides — waiting on the merge,
    no question — or None when the entry already waits on it."""
    want = "external merge " + ", ".join(f"PR #{pr}" for pr, _ in cut)
    if entry.get("waiting-on") == want:
        return None
    return {"waiting-on": want, "question": "", "holder": entry.get("holder", "")}

def board_set(repo: Path, rid: int, pairs: dict[str, str]) -> str:
    """One board write from the automaton's seat, landed ledger-only through `board set`'s own builder; `holder` is
    passed as it stands, so the write never takes the holder."""
    with_env = {"DYAD_SESSION": SEAT}
    old = {k: os.environ.get(k) for k in with_env}
    os.environ.update(with_env)
    try:
        i = inst(repo)
        pairs = {k: v for k, v in pairs.items() if k != "holder" or v}
        land.land(repo, i, None, board().set_builder(str(rid), pairs, False, i), "board set")
        return f"board #{rid}: " + ", ".join(f"{k}={v}" if v else f"{k} removed" for k, v in sorted(pairs.items()) if k != "holder")
    except (Refused, board().Refused) as e:
        return f"board #{rid} not written: {e}"
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def describe(act: tuple) -> str:
    kind = act[0]
    if kind == "merge":
        return f"merge {', '.join(f'PR #{pr} at {h}' for pr, h in act[2])} (row #{act[1]})"
    if kind == "close":
        return f"close row #{act[1]} (every named head is on main)"
    if kind == "board":
        return f"board #{act[1]}: " + ", ".join(f"{k}={v}" if v else f"{k} removed" for k, v in sorted(act[2].items()) if k != "holder")
    return f"notice {act[2]}: {act[3]}"


# ---- the sweep (d-work #564): read-only; what the pre-push gate leaves, plus checks the gate never had
SWEEP_LANDING_HOURS = 24       # a Y done whose named heads are not on main after this long is a finding
SWEEP_STALE_DAYS = 3           # a board entry whose `since` is older than this is a finding
SWEEP_CI_HOURS = 24            # code pushes to main in this window are checked for a completed corroboration
CI_WORKFLOWS = ("rule-11 package", "d-work automaton")   # the runs that corroborate a code push (#564 E1, E4)
HEXWORD = re.compile(r"\b[0-9a-f]{7,64}\b")

def finding_key(line: str) -> str:
    """The line a finding is told under: its shas masked, so a finding that only moved its sha is not new again, and an
    entry-shaped fragment masked as `post` masks it, so the told text and the key compare equal."""
    return inbox().DISPOSITION.sub("[an entry, read in the ledger]", HEXWORD.sub("<sha>", " ".join(line.split())))

def sweep_check(wt: Path) -> list[tuple[bool, str]]:
    """(fails, line) for every FAIL and warn line `check` prints on the swept tree (every guard, the full suite)."""
    r = subprocess.run([sys.executable, str(wt / "dyad" / "scripts" / "package.py"), "check"], cwd=wt,
                       capture_output=True, text=True, env=dyadlib.git_env())
    out = [(l.startswith("FAIL"), l) for l in (r.stdout + r.stderr).splitlines() if l.startswith(("FAIL", "warn"))]
    if r.returncode and not any(f for f, _ in out):
        out.append((True, f"FAIL [sweep] check exited {r.returncode} with no FAIL line"))
    return out

def sweep_ledger(repo: Path, base: str, now) -> list[tuple[bool, str]]:
    """Y dones whose heads never landed, and stale board entries, read from `base`."""
    import datetime
    out, rg = [], rows_guard()
    for r in dyadlib.read_rows(repo, at=base):
        e = rg.operative_done(r.disposed) if r.state not in dyadlib.TERMINAL_STATES else None
        if not e:
            continue
        m = re.match(r"\s*(\d{4}-\d{2}-\d{2})", e)
        when = datetime.datetime.fromisoformat(m.group(1)).replace(tzinfo=datetime.timezone.utc) if m else None
        owed = [(pr, h) for _, pr, h, _ in rg.named_heads([r]) if not steps.ancestor(repo, h, base)]
        if owed and when and (now - when).total_seconds() > SWEEP_LANDING_HOURS * 3600:
            out.append((False, f"finding: row #{r.id}'s done answer of {m.group(1)} names heads not on main: "
                               + ", ".join(f"PR #{pr} at {h[:12]}" for pr, h in owed)))
    d = f"{inst(repo)}/d-work/board"
    for name in ls(repo, base, d):
        if not name.endswith(".md"):
            continue
        fields = board().parse(show(repo, base, f"{d}/{name}") or "")[0]
        since = board().parse_since(fields.get("since", "")) if fields.get("since") else None
        if since and (now - since).days > SWEEP_STALE_DAYS:
            out.append((False, f"finding: board {name[:-3]} unchanged since {fields['since']} (over {SWEEP_STALE_DAYS} days)"))
    return out

def sweep_drift(repo: Path, wt: Path, base: str) -> list[tuple[bool, str]]:
    """The world against the record: released tags against their entries (the `released` run-book's health), and
    the mirror branch (`MIRROR`) against main."""
    out = []
    r = subprocess.run([sys.executable, str(wt / "dyad" / "scripts" / "package.py"), "runbook", "run", "released", "health"],
                       cwd=wt, capture_output=True, text=True, env=dyadlib.git_env(), timeout=600)
    gaps = [l for l in r.stdout.splitlines() if l.startswith(("no tag:", "tag not at cut:", "no Release:"))]
    out += [(True, f"finding: released: {g}") for g in gaps]
    if r.returncode and not gaps:
        out.append((False, f"finding: released health not read (exit {r.returncode}): {(r.stdout + r.stderr).strip().splitlines()[-1:] or ['']}"))
    mirror = os.environ.get("MIRROR")
    if mirror:
        at = (land.git(repo, "ls-remote", "origin", f"refs/heads/{mirror}", check=False).stdout.split() or [""])[0]
        if at != base:
            out.append((False, f"finding: mirror {mirror} at {at[:12] or 'absent'}, main at {base[:12]}"))
    return out

def sweep_ci(repo: Path, base: str, now) -> list[tuple[bool, str]]:
    """Code pushes to main within SWEEP_CI_HOURS with no successful corroborating run (`CI_WORKFLOWS`), read from the
    hosting with `GITHUB_TOKEN` and `GITHUB_REPOSITORY`; one skip finding when either is absent."""
    import datetime, json, urllib.request
    token, slug = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    since = (now - datetime.timedelta(hours=SWEEP_CI_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    log = land.git(repo, "log", "--first-parent", "--format=%H", f"--since={since}", base, check=False).stdout.split()
    code = [c for c in log if not (dyadlib.ledger_only(repo, f"{c}^1", c) or dyadlib.events_only(repo, f"{c}^1", c))]
    if not code:
        return []
    if not (token and slug):
        return [(False, f"finding: corroboration of {len(code)} code push(es) to main not read (no GITHUB_TOKEN/GITHUB_REPOSITORY)")]
    def runs(sha=None, name=None):
        q = f"head_sha={sha}" if sha else "per_page=50"
        req = urllib.request.Request(f"https://api.github.com/repos/{slug}/actions/runs?{q}",
                                     headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp).get("workflow_runs", [])
    out = []
    try:
        recent = [w for w in runs() if w.get("name") == "d-work automaton" and w.get("conclusion") == "success"]
        for c in code:
            ok = any(w.get("name") in CI_WORKFLOWS and w.get("conclusion") == "success" for w in runs(sha=c))
            if not ok and "Executed by `dyad merge`" in land.out(repo, "log", "-1", "--format=%B", c):
                t = land.out(repo, "log", "-1", "--format=%cI", c)
                ok = any(w.get("created_at", "") >= t for w in recent)    # the automaton corroborates in the run that merged
            if not ok:
                out.append((True, f"finding: code push {c[:12]} to main has no successful corroboration ({', '.join(CI_WORKFLOWS)})"))
    except Exception as e:                               # the hosting is The World: unreadable is a finding, never a crash
        out.append((False, f"finding: corroboration not read from the hosting ({type(e).__name__})"))
    return out

def sweep_pulls() -> list[dict] | None:
    """The hosting's open PRs for the in-flight kinds W4-W6 (d-work #569), as [{number, title, body, head_ref, head_sha,
    updated_at}], read with `GITHUB_TOKEN` and `GITHUB_REPOSITORY`; None when either is absent or the hosting is
    unreadable (The World: never a crash), and those kinds then print one skip line."""
    import json, urllib.request
    token, slug = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not (token and slug):
        return None
    out, page = [], 1
    try:
        while True:
            req = urllib.request.Request(f"https://api.github.com/repos/{slug}/pulls?state=open&per_page=100&page={page}",
                                         headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                got = json.load(resp)
            out += [{"number": p["number"], "title": p.get("title") or "", "body": p.get("body") or "",
                     "head_ref": p["head"]["ref"], "head_sha": p["head"]["sha"], "updated_at": p.get("updated_at") or ""}
                    for p in got]
            if len(got) < 100:
                return out
            page += 1
    except Exception:
        return None

NOTICE_CHARS = 3000   # one notice's body at most; a longer group is split, never cut, so nothing new goes untold

def notice_groups(new: list[str]) -> list[tuple[str, list[str]]]:
    """The new lines by kind, as the notices tell them (d-work #565): backlog hygiene first, then similarity candidates,
    then every other finding; each line by its key (`finding_key`), so what is told is what the next sweep compares."""
    kinds = ((("backlog hygiene", lambda l: l.startswith("finding: hygiene ")),)
             + tuple((f"work in flight {k}", lambda l, k=k: l.startswith(f"finding: inflight {k} "))   # one per kind (#569)
                     for k in hygiene_mod.INFLIGHT_KINDS)
             + (("similarity candidates", lambda l: l.startswith("candidate:")), ("findings", lambda l: True)))
    out, left = [], list(new)
    for name, test in kinds:
        group = [finding_key(l.removeprefix("finding: ")) for l in left if test(l)]
        left = [l for l in left if not test(l)]
        if group:
            out.append((name, group))
    return out

def notice_parts(group: list[str]) -> list[list[str]]:
    """`group` split into parts whose joined body stays under NOTICE_CHARS; a single longer line is its own part."""
    parts, cur, size = [], [], 0
    for line in group:
        if cur and size + len(line) + 3 > NOTICE_CHARS - 80:
            parts.append(cur); cur, size = [], 0
        cur.append(line); size += len(line) + 3
    return parts + ([cur] if cur else [])

def sweep(repo: Path, row: int | None) -> tuple[list[str], int]:
    """Read-only: (lines, rc). Every finding prints; findings no automaton notice in the home's inbox has told yet are
    posted in one notice on `row`; rc 1 when any finding fails."""
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    base = land.fetch(repo)
    common = Path(land.out(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    wt = common / land.WORKTREE
    with land.locked(common):
        land.prepare(repo, wt, base)
        found = sweep_check(wt) + sweep_drift(repo, wt, base)
    found += sweep_ledger(repo, base, now) + sweep_ci(repo, base, now)
    hyg, candidates = hygiene_mod.hygiene(repo, base, now.timestamp())   # after check, whatever check returned (#565 A8)
    found += [(False, f"finding: {h}") for h in hyg]
    found += [(False, f"finding: {h}") for h in hygiene_mod.inflight(repo, base, now.timestamp(), sweep_pulls())]   # #569
    lines = [l if l.startswith("finding: ") else f"finding: {l}" for _, l in found] + candidates
    rc = 1 if any(f for f, _ in found) else 0
    to = home(repo, base)
    told = " ".join(m.get("body", "") for m in box_messages(repo, base, to) if m.get("from") == SEAT) if to else ""
    new = [l for l in lines if finding_key(l.removeprefix("finding: ")) not in told]
    summary = f"sweep of main {base[:12]}: {len(lines)} finding(s), {sum(f for f, _ in found)} failing, {len(new)} new"
    if new and row and to:
        sent = []
        for kind, group in notice_groups(new):
            for part in notice_parts(group):
                body = f"automaton sweep at {base[:12]}, {kind}: " + " | ".join(part)
                try:
                    sent.append(post(repo, to, row, body))
                except (Refused, inbox().Refused) as e:
                    sent.append(f"the notice to {to} was refused ({e})")
        summary += "; " + "; ".join(sent)
    elif new:
        summary += "; not told (no --row or no home)"
    return lines + [summary], rc

# ---- taking them
def post(repo: Path, to: str, row: int, body: str) -> str:
    """One inbox notice from the automaton's seat, landed; information only, so an entry is never quoted."""
    body = inbox().DISPOSITION.sub("[an entry, read in the ledger]", body)
    with_env = {"DYAD_SESSION": SEAT}
    old = {k: os.environ.get(k) for k in with_env}
    os.environ.update(with_env)
    try:
        inbox().post(repo, to, row, "notice", body)
        return f"posted a notice to {to} (row #{row})"
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def escalate(repo: Path, row: int, what: str, why: str) -> str:
    """A refusal, posted once to the home's inbox; the home decides."""
    base = land.fetch(repo)
    to = home(repo, base)
    body = f"automaton: {what} refused for row #{row}: {why.splitlines()[0][:300]}"
    body = inbox().DISPOSITION.sub("[an entry, read in the ledger]", body)
    if not to:
        return f"refused, and no home to tell (no AUTOMATON_HOME and no board _cos holder): {body}"
    if posted(repo, base, to, row, body):
        return f"refused, already told {to}: {body}"
    try:
        return f"refused, {post(repo, to, row, body)}: {body}"
    except (Refused, inbox().Refused) as e:
        return f"refused, and the notice to {to} was refused too ({e}): {body}"


LANDED = re.compile(r" as ([0-9a-f]{40}):")

def corroborate(repo: Path, before: str, after: str) -> tuple[bool, list[str]]:
    """Run `check --corroborate <before> <after>` with the landed tree's own runner, in the tool-owned worktree
    detached at `after` (d-work #564 E1: the corroboration hosted CI cannot give a merge the workflow token pushed).
    (passed, its lines)."""
    common = Path(land.out(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    wt = common / land.WORKTREE
    with land.locked(common):
        land.prepare(repo, wt, after)
        r = subprocess.run([sys.executable, str(wt / "dyad" / "scripts" / "package.py"), "check", "--corroborate",
                                 before, after], cwd=wt, capture_output=True, text=True, env=dyadlib.git_env())
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()

def do_merge(repo: Path, rid: int, cut: list[tuple[int, str]]) -> tuple[bool, str]:
    what = "merge of " + ", ".join(f"PR #{pr}" for pr, _ in cut)
    for n in range(RACE_TRIES):
        try:
            lines = merge_mod.merge_all(repo, cut)
            heads = [m.group(1) for m in (LANDED.search(l) for l in lines) if m]
            if not heads:
                return True, "\n".join(lines)
            before = land.out(repo, "rev-parse", f"{heads[0]}^1")
            ok, out = corroborate(repo, before, heads[-1])
            fails = [l for l in out if l.startswith("FAIL")]
            if ok:
                return True, "\n".join(lines + [f"corroborated row #{rid}'s cut at {heads[-1][:12]} (d-work #564)"])
            CORROBORATION_FAILED.add(rid)
            return True, "\n".join(lines + [escalate(repo, rid, "corroboration of the landed cut",
                                                       (fails or out or ["no output"])[0])])
        except Refused as e:
            msg = str(e)
            if "already on origin/main" in msg:
                return True, f"row #{rid}: a PR of the cut has landed meanwhile ({msg.splitlines()[0][:200]}); re-read next run"
            if "main moved under the push" in msg and n + 1 < RACE_TRIES:
                continue                                   # at once: a ledger-only drift costs the guards only (#562 (c))
            return False, escalate(repo, rid, what, msg)
    return False, escalate(repo, rid, what, "main kept moving")


def do_close(repo: Path, rid: int) -> str:
    try:
        return "\n".join(l for l in steps.close_landed(repo, rid, True) if l)
    except Refused as e:
        if str(e).startswith("already closed"):
            return str(e)
        return escalate(repo, rid, "close", str(e))


CORROBORATION_FAILED: set[int] = set()   # rows whose landed cut failed corroboration in this run: the run exits 1

def run(repo: Path) -> list[str]:
    out, stopped = [], set()
    _, acts = plan(repo)
    for act in acts:
        if act[0] == "merge":
            ok, line = do_merge(repo, act[1], act[2])
            out.append(line)
            if not ok:
                stopped.add(act[1])
        elif act[0] == "close":
            out.append(do_close(repo, act[1]))
        elif act[0] == "board":
            out.append(board_set(repo, act[1], act[2]))
        else:
            try:
                out.append(post(repo, act[2], act[1], act[3]))
            except (Refused, inbox().Refused) as e:
                out.append(f"notice to {act[2]} refused: {e}")
    # merges just landed may make a row due: one more pass closes it in the same run
    base, again = plan(repo)
    out += [do_close(repo, a[1]) for a in again if a[0] == "close" and a[1] not in stopped]
    # #572 K3: a cut still owed after this run's merges waits on its merge, not on the operator
    for a in again:
        if a[0] == "merge":
            text = show(repo, base, f"{inst(repo)}/d-work/board/{a[1]}.md")
            if text and (pairs := pending_flip(board().parse(text)[0], a[2])):
                out.append(board_set(repo, a[1], pairs))
    return out or ["nothing to do"]


def main(argv: list[str], repo: Path) -> int:
    a = list(argv)
    if a in (["-h"], ["--help"]):
        print(__doc__); return 0
    try:
        if a == ["scan"]:
            _, acts = plan(Path(repo))
            print("\n".join(describe(x) for x in acts) or "nothing to do")
            return 0
        if a[:1] == ["sweep"]:
            rest = a[1:]
            if rest not in ([],) and not (len(rest) == 2 and rest[0] == "--row" and rest[1].isdigit()):
                print(USAGE, file=sys.stderr); return 2
            lines, rc = sweep(Path(repo), int(rest[1]) if rest else None)
            print("\n".join(lines)); return rc
        if a == ["run"]:
            CORROBORATION_FAILED.clear()
            print("\n".join(run(Path(repo))))
            return 1 if CORROBORATION_FAILED else 0
        print(USAGE, file=sys.stderr)
        return 2
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], dyadlib.repo_root()))
