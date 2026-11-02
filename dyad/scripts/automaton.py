#!/usr/bin/env python3
"""`dyad automaton scan|run` — the d-work automaton (d-work #556; backlog #542 absorbed). Kernel: Python 3.12+, git.

The d-work's clerical edges, run by a party that decides nothing: the countersign model's executor, #553's
automaton. Everything between a recorded disposition and the next inferred act is defined, so it is run here, from
ledger lines only and never from a conversation:
  (a) **merge** — every PR an operative `Y done` names, pinned to the head it names, in the order it names them, by the
      record-bound `dyad merge` (scripts/merge.py: the entry, the live head, a clean merge, one push through the gate).
      A push that loses a race to `main` is retried with backoff; any other refusal stops that row's later PRs;
  (b) **close** — a row whose every named head is on `main` goes `done`, its accreted rows close under its mandate and
      its board entry is dropped (`dyad steps close-landed --land`, scripts/steps.py);
  (c) **notice** — a row whose last disposition is a `Y plan` and whose board entry names owners: each owner's inbox
      gets one `notice`, "row #N planned; read plans/N.md". The seat still infers from the plan; this replaces only the
      message saying "go".
A refusal decides nothing: it is posted once to the home's inbox as a `notice` (the board's `_cos` holder, or
`AUTOMATON_HOME`), and the home takes it from there by inference. Every message names the row and never quotes an entry
(the inbox carries information, never authority, #536).

**Stateless.** Every run re-reads `origin/main` (the rows, the board, the inbox) and every act is idempotent: a merged
head, a closed row and a notice already posted are skipped. Any run may be retried, and a run that dies mid-way loses
nothing. Memory across runs (a retry, a backoff) lives in the run itself or in the store, never here.

  dyad automaton scan      read-only: the acts a run would take now, one line each
  dyad automaton run       take them; one line per act and per refusal; exit 0 unless the automaton itself failed

It runs from `main`'s own code: server-side in `.github/workflows/dyad-automaton.yml` on every push to `main`, gated by
the repository variable `DYAD_AUTOMATON` (`on`, the operator's switch), and by hand by any unit for recovery. Its
commits carry the identity of whoever runs it; its inbox messages come from the seat `automaton` (`DYAD_SESSION`).
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("automaton.py: Python 3.12+ required")
import os, re, time
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

HERE = Path(__file__).resolve().parent
land = dyadlib.load_module(HERE / "land.py", "land")
merge_mod = dyadlib.load_module(HERE / "merge.py", "merge")
steps = dyadlib.load_module(HERE / "steps.py", "steps")
Refused = land.Refused
SEAT = "automaton"                           # the inbox sender; path-shaped, so a box name too
RACE_TRIES = 5                               # a push that lost a race to main, retried with backoff (#552's merge saw two lose)
BACKOFF = 2.0                                # seconds, doubled per try; AUTOMATON_BACKOFF overrides (tests set 0)
PLANNED = "row #{rid} planned; read plans/{rid}.md"
USAGE = "usage: dyad automaton scan|run"

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("seat-is-path-shaped", lambda: bool(re.fullmatch(r"[A-Za-z0-9._-]+", SEAT))),
    ("retries-bounded", lambda: 1 < RACE_TRIES <= 10 and BACKOFF >= 0),
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
    """(base, acts) on a freshly fetched origin/main: ("merge", rid, pr, sha) in each row's own order, then
    ("close", rid), then ("notice", rid, owner). Pure reading."""
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
        acts += [("merge", r.id, int(pr), h) for pr, h in owed if pr]
        if not owed:
            acts.append(("close", r.id))
    for r in rows:
        last = [e for e in rg.entries(r.disposed) if not rg.is_ready(e)][-1:] or [""]
        if r.state != "planned" or not rg.PLAN_Y.match(last[0]):
            continue
        text = show(repo, base, f"{inst(repo)}/d-work/board/{r.id}.md")
        if not text:
            continue
        for owner in board().owners(board().parse(text)[0]):
            if not posted(repo, base, owner, r.id, PLANNED.format(rid=r.id)):
                acts.append(("notice", r.id, owner))
    return base, acts


def describe(act: tuple) -> str:
    kind = act[0]
    if kind == "merge":
        return f"merge PR #{act[2]} at {act[3]} (row #{act[1]})"
    if kind == "close":
        return f"close row #{act[1]} (every named head is on main)"
    return f"notice {act[2]}: {PLANNED.format(rid=act[1])}"


# ---- taking them
def backoff() -> float:
    v = os.environ.get("AUTOMATON_BACKOFF")
    try:
        return float(v) if v is not None else BACKOFF
    except ValueError:
        return BACKOFF


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


def do_merge(repo: Path, rid: int, pr: int, sha: str) -> tuple[bool, str]:
    wait = backoff()
    for n in range(RACE_TRIES):
        try:
            return True, merge_mod.merge(repo, pr, sha)
        except Refused as e:
            msg = str(e)
            if "already on origin/main" in msg:
                return True, f"PR #{pr} at {sha[:12]} has landed (row #{rid}); nothing to do"
            if "main moved under the push" in msg and n + 1 < RACE_TRIES:
                time.sleep(wait); wait *= 2
                continue
            return False, escalate(repo, rid, f"merge of PR #{pr}", msg)
    return False, escalate(repo, rid, f"merge of PR #{pr}", "main kept moving")


def do_close(repo: Path, rid: int) -> str:
    try:
        return "\n".join(l for l in steps.close_landed(repo, rid, True) if l)
    except Refused as e:
        if str(e).startswith("already closed"):
            return str(e)
        return escalate(repo, rid, "close", str(e))


def run(repo: Path) -> list[str]:
    out, stopped = [], set()
    _, acts = plan(repo)
    for act in acts:
        if act[0] == "merge":
            if act[1] in stopped:
                out.append(f"skipped: {describe(act)} — an earlier PR of row #{act[1]} was refused")
                continue
            ok, line = do_merge(repo, act[1], act[2], act[3])
            out.append(line)
            if not ok:
                stopped.add(act[1])
        elif act[0] == "close":
            out.append(do_close(repo, act[1]))
        else:
            try:
                out.append(post(repo, act[2], act[1], PLANNED.format(rid=act[1])))
            except (Refused, inbox().Refused) as e:
                out.append(f"notice to {act[2]} refused: {e}")
    # merges just landed may make a row due: one more pass closes it in the same run
    _, again = plan(repo)
    out += [do_close(repo, a[1]) for a in again if a[0] == "close" and a[1] not in stopped]
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
        if a == ["run"]:
            print("\n".join(run(Path(repo))))
            return 0
        print(USAGE, file=sys.stderr)
        return 2
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], dyadlib.repo_root()))
