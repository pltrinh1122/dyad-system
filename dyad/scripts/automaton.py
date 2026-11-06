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
      entry waiting on that merge (K3). The seat still infers from the plan. An entry that carries a `phase` (#587) gets
      none of the three: its `board advance answered-Y` wrote the flip and the relay, and its landing waits on the merge;
      one still at plan-ready, plan-asked, done-ready or done-asked whose answer home recorded with plain `dwork state` is
      caught up instead — the same builder, `recorded`, writing the board and its relays and no ledger line ("catch up
      #N answered-Y"); a `Y done` recorded at any other phase is reported by `run` and left to home (the guard warns).
  (d) **corroborate** — after a cut lands, `check --corroborate <before> <after>` runs on the landed tree in the same
      job: what hosted CI on `main` checks, which a push made with the workflow's token never starts (d-work #564 E1).
      The suite runs only when the landed code differs from an evidenced PR head. A failure is posted to home and the
      run exits 1, so the run's conclusion shows it.
A refusal decides nothing: it is posted once to the home's inbox as a `notice` (the holder of the `_cos[-<operator>]`
file of the row's cabinet, #594, or `AUTOMATON_HOME`), and the home takes it from there by inference. Every message names the row and never quotes an entry
(the inbox carries information, never authority, #536).

**Stateless.** Every run re-reads `origin/main` (the rows, the board, the inbox) and every act is idempotent: a merged
head, a closed row and a notice already posted are skipped. Any run may be retried, and a run that dies mid-way loses
nothing. Memory across runs (a retry) lives in the run itself or in the store, never here.

  dyad automaton scan      read-only: the acts a run would take now, one line each
  dyad automaton run [--evidence-from <file>]
                           take them; one line per act and per refusal, then `landed: <n> merge(s)` (#617: with
                           GITHUB_OUTPUT set, the outputs `landed` and `landed-at` too, so the job dispatches the
                           full sweep once per landed cut); exit 1 when a landed cut failed
                           corroboration, else 0 unless the automaton itself failed. With --evidence-from (#587 X10)
                           the evidence acts fire the file's verdicts instead of computing them: each line is
                           untrusted, checked strictly (shape, a verdict of the machine's table, the row in
                           verifying, its heads the board's recorded and the live ones) and dropped with a reason
                           when any check fails
  dyad automaton evidence --out <file>
                           read-only, sandbox-only (never in a job holding a write token): the combined evidence of
                           every evidence act, one JSON line each, {rid, event, evidence or note, heads}, to <file>;
                           fires, posts and commits nothing
  dyad automaton sweep [--stores] [--row <id>]
                           read-only, after each landed merge (d-work #564, #617): every guard over every store and
                           the full suite on origin/main, released tags against their entries and the mirror
                           against main, and the audit's coded checks (#619, `scripts/audits.py`: `reading:` lines,
                           never posted, and warnings). One `finding:` line each, in two groups, `standing` (told
                           already) and `new`; a new finding is posted, in one notice, to the home's inbox on
                           `--row`. Exit 1 when a finding fails. With no `--row` it is the audit's report: the stall
                           block, `checks-sha256=` and `report-sha256=`, the text stored under the git common dir. The stall findings (heads
                           not landed, corroboration, stale board, work in flight, backlog hygiene) are the home's
                           read since #617: `dyad board resume` prints them (`stall_lines`). With --stores, after
                           each ledger push: the whole-store guards only (`check --guards`, no suite, no drift, no
                           events), told the same way. A health
                           run that appended an event (a changed reading, #438) has it landed on main as an
                           events-only commit citing no d-work, on `--row` only (#593); one `events:` line says
                           what happened, and a landing that fails never changes a finding or the exit

It runs from `main`'s own code: server-side in `.github/workflows/dyad-automaton.yml` on every push to `main`, gated by
the repository variable `DYAD_AUTOMATON` (`on`, the operator's switch), and by hand by any unit for recovery. Its
commits carry the identity of whoever runs it; its inbox messages come from the seat `automaton` (`DYAD_SESSION`).
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("automaton.py: Python 3.12+ required")
import contextlib, io, json, os, re, subprocess
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

HERE = Path(__file__).resolve().parent
land = dyadlib.load_module(HERE / "land.py", "land")
merge_mod = dyadlib.load_module(HERE / "merge.py", "merge")
steps = dyadlib.load_module(HERE / "steps.py", "steps")
hygiene_mod = dyadlib.load_module(HERE / "hygiene.py", "hygiene")   # the sweep's backlog hygiene (d-work #565)
runbook_mod = dyadlib.load_module(HERE / "runbook.py", "runbook")   # the event store's primitives (Rule-19)
Refused = land.Refused
SEAT = "automaton"                           # the inbox sender; path-shaped, so a box name too
RACE_TRIES = 5                               # a push that lost a race to main, re-merged at once (#562 (c))
PLANNED = "row #{rid} planned; read plans/{rid}.md"
USAGE = "usage: dyad automaton scan | run [--evidence-from <file>] | evidence --out <file> | sweep [--stores] [--row <id>]"
CLI_FLAGS = dyadlib.cli_forms("automaton")   # #592 R-a: {verb: its dyadlib.CLI form}, the one home of the flags this parser reads (dyad/tests/test_cli.py)
ROW_FLAG, = CLI_FLAGS["sweep"].value_flags
STORES_FLAG, = CLI_FLAGS["sweep"].bare                # #617: the whole-store guards only, after each ledger push

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("seat-is-path-shaped", lambda: bool(re.fullmatch(r"[A-Za-z0-9._-]+", SEAT))),
    ("retries-bounded", lambda: 1 < RACE_TRIES <= 10),
    ("evidence-events-are-the-automatons-from-verifying",          # #587 X10: an evidence line fires only these
     lambda: all("automaton" in dyadlib.orch_actors(dyadlib.ORCH_EVENTS[("verifying", e)][1]) for e in EVIDENCE_EVENTS)),
    ("ci-read-within-the-ceiling", lambda: 0 < CI_TIMEOUT_S < STALL_CEILING_S and 0 < CI_PAGE <= 100),   # #617 P5
    ("evidence-file-bounded", lambda: 0 < EVIDENCE_FILE_LINES and 0 < EVIDENCE_HEADS <= 100 and EVIDENCE_FILE_BYTES <= 1 << 24),
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


def home(repo: Path, base: str, cabinet: str) -> str | None:
    """The home's seat: `AUTOMATON_HOME`, else the holder of `cabinet`'s `_cos[-<operator>]` file on main (#594), else —
    when that file is absent or holds no holder — `program`'s, so a finding or a refusal always reaches some leader.
    `cabinet` has no default: a row-scoped call names its row's cabinet (`row_cabinet`), so a missed site fails loudly."""
    if os.environ.get("AUTOMATON_HOME"):
        return os.environ["AUTOMATON_HOME"]
    for c in dict.fromkeys([cabinet, board().SOLO]):
        text = show(repo, base, f"{inst(repo)}/d-work/board/{board().cos_name(c)}.md")
        if text and (h := board().parse(text)[0].get("holder")):
            return h
    return None


def row_cabinet(repo: Path, base: str, rid: int) -> str:
    """The cabinet row `rid`'s board entry on main is filed under; `program` when it has no entry (#594)."""
    text = show(repo, base, f"{inst(repo)}/d-work/board/{rid}.md")
    return board().entry_cabinet(board().parse(text)[0] if text else {})


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
    w = watch(repo, base, rows)                                        # #587 X6 moved heads, then X5 combined evidence
    void = {a[1] for a in w if a[0] in ("head-moved", "withdrawn")}
    acts += [a for a in catch_ups(repo, base, rows) if a[1] not in void]   # #587: the board follows a Y recorded by
    acts += w                                                          # hand — never a Y on a moved head (Rule-2: void)
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
    byid = {r.id: r for r in rows}
    for r in rows:   # #574 G5: a Done naming no merge is `done` at once and no close runs; its retires are archived here
        op = (rg.operative_done(r.disposed) or "") if r.state == "done" else ""
        if not op or rg.DONE_MERGES.search(f"2000-01-01 {op}"):
            continue                                   # a merge-naming Done's retires are its close's, once (close_landed)
        named = steps.retired_rows(op)
        due = [x for x in named if x in byid and byid[x].state in ("backlog", "done")]
        if due:
            acts.append(("archive", r.id, due))
        for x in named:                                # told once, never resolved (G5): a row no longer backlog or done
            if x not in byid or byid[x].state not in ("backlog", "done", "archived"):
                why = stray_body(r.id, x, byid[x].state if x in byid else "no row")
                to = home(repo, base, row_cabinet(repo, base, r.id))   # the row's cabinet's home (#594)
                if to and not posted(repo, base, to, r.id, why):
                    acts.append(("tell", r.id, why))
    for r in rows:
        last = [e for e in rg.entries(r.disposed) if not rg.is_ready(e)][-1:] or [""]
        if r.state != "planned" or not rg.PLAN_Y.match(last[0]):
            continue
        text = show(repo, base, f"{inst(repo)}/d-work/board/{r.id}.md")
        if not text:
            continue
        entry = board().parse(text)[0]
        if entry.get("phase"):
            continue                                                   # #587: `answered-Y` wrote the flip and the relay
        owners = board().owners(entry)
        if (refusal := board().retired_waiting(entry.get("waiting-on", ""))):   # #604: told to home, never rewritten
            why = retired_body(r.id, refusal)
            to = home(repo, base, row_cabinet(repo, base, r.id))   # the row's cabinet's home (#594)
            if to and not posted(repo, base, to, r.id, why):
                acts.append(("tell", r.id, why))
        if owners and not board_after_plan_y(repo, base, r.id) and (pairs := planned_flip(r.id, entry, owners)):
            acts.append(("board", r.id, pairs))                       # #572 K1: before the notices it announces
        parts = plan_parts(show(repo, base, f"{inst(repo)}/d-work/plans/{r.id}.md") or "")
        for owner in owners:
            body = notice_body(r.id, part_for(parts, owner))
            if not posted(repo, base, owner, r.id, body):
                acts.append(("notice", r.id, owner, body))
    return base, acts


def catch_ups(repo: Path, base: str, rows) -> list[tuple]:
    """#587: ("advance", rid, "answered-Y", phase) for each phased entry whose answer the ledger already holds — home
    recorded it with plain `dwork state`, asked through `board advance asked` or in chat without it: at `plan-ready` or
    `plan-asked` with the row planned and its last disposition a `Y plan`, or at `done-ready` or `done-asked` with an
    operative `Y done` naming every PR the phase lists (the others only under a batch entry naming the row,
    `board.recorded_done_heads`). A Y done that does not cover the phase, or one recorded at another phase, proposes
    nothing; the guard's warning stands and `run` says so."""
    rg, b, out = rows_guard(), board(), []
    by_id = {r.id: r for r in rows}
    d = f"{inst(repo)}/d-work/board"
    for name in ls(repo, base, d):
        if not name.endswith(".md") or not name[:-3].isdigit():
            continue
        rid = int(name[:-3])
        r = by_id.get(rid)
        f = b.parse(show(repo, base, f"{d}/{name}") or "")[0]
        if r is None or r.state in dyadlib.TERMINAL_STATES or not f.get("phase"):
            continue
        try:
            phase, sub = b.phase_of(f["phase"])
        except ValueError:
            continue
        last = [e for e in rg.entries(r.disposed) if not rg.is_ready(e)][-1:] or [""]
        if phase in b.CATCH_UP_PLAN and r.state == "planned" and rg.PLAN_Y.match(last[0]) \
                and not board_after_plan_y(repo, base, rid):   # S11: a question asked after that Y is not answered by it
            out.append(("advance", rid, "answered-Y", phase))
        elif phase in b.CATCH_UP_DONE and rg.operative_done(r.disposed) and b.recorded_done_heads(rid, r, sub) is not None:
            out.append(("advance", rid, "answered-Y", phase))
    return out


def catch_up(repo: Path, rid: int, phase: str) -> str:
    """One catch-up (#587): `board advance`'s own builder with `recorded=True`, from the automaton's seat — the board
    flip and its relays only, no ledger line (the ledger already holds the answer), no trace, no actor check."""
    with_env = {"DYAD_SESSION": SEAT}
    old = {k: os.environ.get(k) for k in with_env}
    os.environ.update(with_env)
    try:
        i, run = inst(repo), dyadlib.runner_module()
        build = board().advance_builder([rid], "answered-Y", {}, phase, None, i, repo, run.DWORK_VALUE_FLAGS,
                                        run.dwork_args, run.words, SEAT, recorded=True)
        land.land(repo, i, None, build, "board advance")
        return f"board #{rid}: caught up answered-Y from {phase} (recorded on the ledger)"
    except (Refused, board().Refused) as e:
        return f"board #{rid} not caught up: {e}"
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ---- #587 X5, X6: the automaton's own events, fired through `board advance`'s builder
def live(repo: Path, pr: int) -> str | None:
    """A PR's live head, or None when the hosting does not answer in time: The World unreadable proposes nothing, and
    one hanging `ls-remote` never costs the run its merges and closes."""
    try:
        return steps.live_head(repo, pr)
    except subprocess.TimeoutExpired:
        return None


def watch(repo: Path, base: str, rows) -> list[tuple]:
    """#587 X6 and X5, from the phased board entries on `base`: ("head-moved", rid, phase, [(pr, live head), …]) for an
    entry in `dyadlib.ORCH_WATCHED` whose recorded PR heads are not the live ones (`git ls-remote refs/pull/<n>/head`;
    a recorded head may be abbreviated); for a moved entry in done-asked, ("withdrawn", sib, note) for every other row
    its stored question names that sits in done-asked under the identical question and did not move itself (Rule-2: a
    batch Y is void once any head it names moves); else ("evidence", rid, [(pr, live head), …]) for an entry in
    `verifying` whose every listed PR is up at its recorded head and whose row carries no operative `Y done` (one
    recorded by hand outside done-asked is reported by `run` and left to home). A PR with no live head, or whose head
    the hosting does not give in time, proposes nothing for its row (the hosting is The World). Read-only."""
    b, out, seen = board(), [], {}
    by_id = {r.id: r for r in rows}
    d = f"{inst(repo)}/d-work/board"
    for name in ls(repo, base, d):
        if not name.endswith(".md") or not name[:-3].isdigit():
            continue
        rid = int(name[:-3])
        r = by_id.get(rid)
        f = b.parse(show(repo, base, f"{d}/{name}") or "")[0]
        if r is None or r.state in dyadlib.TERMINAL_STATES or not f.get("phase"):
            continue
        try:
            phase, sub = b.phase_of(f["phase"])
        except ValueError:
            continue
        seen[rid] = (f, phase)
        prs = b.pr_list(sub)
        if phase not in dyadlib.ORCH_WATCHED or not prs:
            continue
        heads = [(n, h, live(repo, n)) for n, h in prs]
        if any(l is None for _, _, l in heads):
            continue
        moved = [(n, l) for n, h, l in heads if not l.startswith(h)]
        if moved:
            out.append(("head-moved", rid, phase, moved))
        elif phase == "verifying" and not rows_guard().operative_done(r.disposed):   # a Y done recorded by hand
            out.append(("evidence", rid, [(n, l) for n, _, l in heads]))            # binds its own heads: home's
    moved_ids = {a[1] for a in out if a[0] == "head-moved"}
    told = set()
    for a in [a for a in out if a[0] == "head-moved" and a[2] == "done-asked"]:
        q = seen[a[1]][0].get("question", "")
        pr, head = a[3][0]
        for sib in b.ids_of(q):
            if sib == a[1] or sib in moved_ids or sib in told or sib not in seen:
                continue
            f, phase = seen[sib]
            if phase == "done-asked" and f.get("question", "") == q:
                told.add(sib)
                out.append(("withdrawn", sib, f"PR #{pr} of #{a[1]} moved to {head[:12]}"))
    return out


OID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
COMBINED_IDENT = {"GIT_AUTHOR_NAME": "dyad automaton", "GIT_AUTHOR_EMAIL": "automaton@dyad.invalid",
                  "GIT_COMMITTER_NAME": "dyad automaton", "GIT_COMMITTER_EMAIL": "automaton@dyad.invalid"}

def combined_head(repo: Path, base: str, cut: list[tuple[int, str]]) -> tuple[str | None, str]:
    """(the combined merge commit, "") of `cut` onto `base`, in the cut's order, as `merge_all` would merge it but
    with `git merge-tree` and `commit-tree` only: no worktree, no push, nothing on any ref. The commit is the same for
    the same base and heads (identity and dates fixed to `base`'s), so its evidence can be re-run and compared. (None,
    the conflict) when a PR does not merge cleanly onto the merges before it."""
    when = land.out(repo, "log", "-1", "--format=%cI", base)
    env = {**land.env(), **COMBINED_IDENT, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    cur = base
    for pr, head in cut:
        steps.fetch_head(repo, pr)
        if land.git(repo, "cat-file", "-e", f"{head}^{{commit}}", check=False).returncode:
            raise Refused(f"PR #{pr} head {head[:12]} is not in the object store after the fetch (moved since it was read?)")
        if steps.ancestor(repo, head, cur):
            continue
        r = land.git(repo, "merge-tree", "--write-tree", "--name-only", cur, head, check=False)
        first = (r.stdout.split() or [""])[0]
        if r.returncode and not (r.returncode == 1 and OID.fullmatch(first)):   # exit 1 with a tree is a conflict;
            raise Refused(f"git merge-tree {cur[:12]} {head[:12]} exited {r.returncode}: "   # anything else is no verdict
                          f"{(r.stderr or r.stdout).strip() or 'no output'}")
        if r.returncode:
            onto = "the merges before it" if cur != base else f"origin/main {base[:12]}"
            paths = r.stdout.split("\n\n")[0].split()[1:6]           # the conflicted paths, before git's messages
            return None, (f"PR #{pr} at {head[:12]} does not merge cleanly onto {onto}: "
                          f"{', '.join(paths) or 'conflict'}")
        tree = r.stdout.split()[0]
        c = subprocess.run(["git", "commit-tree", tree, "-p", cur, "-p", head, "-m",
                            f"automaton: combined merge of PR #{pr} at {head} (#587 X5)"],
                           cwd=repo, capture_output=True, text=True, env=env)
        if c.returncode:
            raise Refused(f"git commit-tree: {c.stderr.strip()}")
        cur = c.stdout.strip()
    return cur, ""


def evidence_at(repo: Path, sha: str) -> tuple[int, list[str]]:
    """(exit code, lines) of `check --evidence --at <sha>`: the merged tree's own runner, in a detached worktree the
    runner removes afterwards (Rule-14 property 3's block; never the caller's checkout)."""
    r = subprocess.run([sys.executable, str(HERE / "package.py"), "check", "--evidence", "--at", sha], cwd=repo,
                       capture_output=True, text=True, env={**dyadlib.git_env(), **EVIDENCE_ENV})
    return r.returncode, (r.stdout + r.stderr).splitlines()


# The evidence child runs code no one has reviewed yet (the PR heads' own runner and tests). An empty value resets the
# credential header a CI checkout persists; hooks are left alone, since the suite's own scratch repos rely on theirs.
# Not a fence against malice — the child can read the config itself — which is why `evidence_allowed` keeps it out of
# a job holding a write token.
EVIDENCE_ENV = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader", "GIT_CONFIG_VALUE_0": ""}

def evidence_allowed() -> bool:
    """Whether X5 may run the PR heads' code here: never inside GitHub Actions (whose automaton job holds a write
    token) unless the job says it is a sandbox without one (`AUTOMATON_EVIDENCE_SANDBOX=on`)."""
    return os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("AUTOMATON_EVIDENCE_SANDBOX") == "on"


def evidence_event(repo: Path, base: str, cut: list[tuple[int, str]]) -> tuple[str | None, dict[str, str], str]:
    """#587 X5: (event, its fields, a line for the run's output) of the combined evidence of `cut` onto `base`:
    `evidence-verified` with evidence=<sha256> when the merge is clean and `check --evidence` passes;
    `evidence-failed` with note=<the conflict, or the first FAIL line> when it is not. (None, {}, why) when the run
    says nothing about the PRs — the evidence could not be taken here (a `[evidence]` line: a shallow clone, a missing
    tag), or no evidence-sha256= line was printed — which is escalated to home, never fired."""
    sha, conflict = combined_head(repo, base, cut)
    if sha is None:
        return "evidence-failed", {"note": note_of(f"combined merge: {conflict}")}, conflict
    rc, lines = evidence_at(repo, sha)
    fails = [l for l in lines if l.startswith("FAIL")]
    ev = [l.removeprefix("evidence-sha256=") for l in lines if l.startswith("evidence-sha256=")]
    if any(l.startswith("FAIL [evidence]") for l in fails) or not ev:
        return None, {}, ((fails or lines or ["no output"])[0] + f" (exit {rc})")   # no base-dependent sha: told once
    if rc == 0 and not fails:
        return "evidence-verified", {"evidence": ev[-1]}, f"combined head {sha[:12]}, evidence {ev[-1][:12]}"
    first_fail = (fails or [f"check --evidence exited {rc}"])[0]
    return "evidence-failed", {"note": note_of(f"combined evidence at {sha[:12]}: {first_fail}")}, first_fail


def note_of(text: str) -> str:
    """A board `note` the automaton writes: one line, at most 300 characters, an entry-shaped fragment masked as `post`
    masks it (the board carries information, never authority, #587 X2)."""
    return inbox().DISPOSITION.sub("[an entry, read in the ledger]", " ".join(text.split()))[:300]


def fire(repo: Path, rid: int, event: str, expect: str, pairs: dict[str, str]) -> str:
    """One automaton event (#587 X5, X6) through `board advance`'s own builder from the automaton's seat: the table,
    `--expect`, the board, the relays, one ledger-only commit. A refusal is the run's line, never an escalation (the
    next run re-reads main and re-decides)."""
    with_env = {"DYAD_SESSION": SEAT}
    old = {k: os.environ.get(k) for k in with_env}
    os.environ.update(with_env)
    try:
        i, run_ = inst(repo), dyadlib.runner_module()
        ran: list = []
        build = board().advance_builder([rid], event, pairs, expect, None, i, repo, run_.DWORK_VALUE_FLAGS,
                                        run_.dwork_args, run_.words, SEAT, ran=ran, automaton=True)
        land.land(repo, i, None, build, "board advance")
        ring = land.ring_list(ran)
        return (f"board #{rid}: {event} from {expect}" + (f" ({', '.join(f'{k}={v}' for k, v in sorted(pairs.items()))})" if pairs else "")
                + (f"; ring owed: {', '.join(ring)} (home rings, #587 X8)" if ring else ""))
    except (Refused, board().Refused) as e:
        return f"board #{rid} {event} not fired: {e}"
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def evidence_what(cut: list[tuple[int, str]]) -> str:
    return "the combined evidence of " + ", ".join(f"PR #{pr} at {h[:12]}" for pr, h in cut)


def evidence_verdict(repo: Path, base: str, rid: int, cut: list[tuple[int, str]]) -> tuple[dict | None, str]:
    """#587 X5, the read half of `do_evidence`: (record, a line for the output) of the combined evidence of `cut` onto
    `base`, firing and posting nothing. The record is `{rid, event, evidence | note, heads}`: event `evidence-verified`
    or `evidence-failed`, or None when the evidence says nothing about the PRs (note: why, for home). (None, line) when
    that refusal is already told to home for these heads: it is neither re-run nor re-told until a head moves."""
    what = evidence_what(cut)
    to, prefix = home(repo, base, row_cabinet(repo, base, rid)), f"automaton: {what} refused for row #{rid}:"
    if to and any(m.get("from") == SEAT and m.get("row") == str(rid) and m.get("body", "").startswith(prefix)
                  for m in box_messages(repo, base, to)):
        return None, f"refused, already told {to}: {prefix} (not re-run)"
    heads = [[pr, h] for pr, h in cut]
    try:
        event, pairs, line = evidence_event(repo, base, cut)
    except (Refused, subprocess.TimeoutExpired) as e:
        return {"rid": rid, "event": None, "note": home_note(str(e)), "heads": heads}, str(e)
    if event is None:
        return {"rid": rid, "event": None, "note": home_note(line), "heads": heads}, line
    return {"rid": rid, "event": event, **pairs, "heads": heads}, line


def home_note(text: str) -> str:
    """A no-verdict line's `note`: what `escalate` keeps of it (its first non-blank line, at most 300 characters), so a
    long refusal — `git merge-tree`'s stderr — stays within `EVIDENCE_NOTE_CHARS` and still reaches home."""
    return (text.strip().splitlines() or ["no reason given"])[0].strip()[:300] or "no reason given"


def evidence_act(repo: Path, rec: dict | None, line: str, what: str) -> str:
    """The write half: a verdict fired from `verifying`, a no-verdict told to home once, a told one only reported."""
    if rec is None:
        return line
    if rec["event"] is None:
        return escalate(repo, rec["rid"], what, rec["note"])
    pairs = {k: rec[k] for k in ("evidence", "note") if k in rec}
    return fire(repo, rec["rid"], rec["event"], "verifying", pairs) + f" [{line}]"


def do_evidence(repo: Path, rid: int, cut: list[tuple[int, str]]) -> str:
    """#587 X5: the combined merge and its evidence, fired as `evidence-verified` or `evidence-failed`; whatever says
    nothing about the PRs is told to home once (`escalate`), keyed on the row and the cut's heads — never on main's
    sha, which every run moves — and checked before the evidence is paid for, so a told refusal is neither re-run nor
    re-told until a head moves. The verdict is advisory: a Done-Y's evidence stays the main Agent's own
    `check --evidence` (Rule-2, Binding)."""
    what = evidence_what(cut)
    if not evidence_allowed():
        return escalate(repo, rid, f"{what} in this job", "not taken in a job holding a write token (unreviewed PR "
                        "code); home runs check --evidence --at the combined head")
    rec, line = evidence_verdict(repo, land.fetch(repo), rid, cut)
    return evidence_act(repo, rec, line, what)


# ---- #587 X10: the evidence split across two jobs — a sandbox that computes, a write job that fires
EVIDENCE_EVENTS = ("evidence-verified", "evidence-failed")   # the verdicts an evidence line may carry, or null
EVIDENCE_SHA = re.compile(r"[0-9a-f]{64}")
EVIDENCE_FILE_BYTES = 1 << 20      # an evidence file is another job's artifact: bounded before it is parsed
EVIDENCE_FILE_LINES = 500
EVIDENCE_HEADS = 20                # PRs one line may name
EVIDENCE_NOTE_CHARS = 2000         # a note's raw length; what is written is `note_of`'s, at most 300


def evidence_out(repo: Path, out: Path) -> list[str]:
    """`automaton evidence --out <file>` (#587 X10): one JSON line per evidence act the run would take — every
    `verifying` entry whose PRs are up at their recorded heads, and every entry whose head moved (its cut the live
    heads, which `run` re-verifies once `head-moved` has fired) — computed as `do_evidence` computes it, then written
    to `out`. Fires nothing, posts nothing, commits nothing; refused where `evidence_allowed` refuses (a job holding a
    write token), since it runs the PR heads' own code. Its lines are the output."""
    if not evidence_allowed():
        raise Refused("evidence --out runs the PR heads' code: never in a job holding a write token "
                      "(set AUTOMATON_EVIDENCE_SANDBOX=on in a sandbox without one)")
    base = land.fetch(repo)
    rows = dyadlib.read_rows(repo, at=base)
    by_id, rg, b = {r.id: r for r in rows}, rows_guard(), board()
    cuts: list[tuple[int, list[tuple[int, str]]]] = []
    for a in watch(repo, base, rows):
        if a[0] == "evidence":
            cuts.append((a[1], a[2]))
        elif a[0] == "head-moved" and not rg.operative_done(by_id[a[1]].disposed):
            text = show(repo, base, f"{inst(repo)}/d-work/board/{a[1]}.md") or ""
            now = dict(a[3])        # only the moved PRs: every other one's live head is read, never its recorded
            cut = [(n, now.get(n) or live(repo, n))       # one, which may be abbreviated (`run` compares full heads)
                   for n, _ in b.pr_list(b.phase_of(b.parse(text)[0]["phase"])[1])]
            if all(h for _, h in cut):
                cuts.append((a[1], cut))
    records, lines = [], []
    for rid, cut in cuts:
        rec, line = evidence_verdict(repo, base, rid, cut)
        lines.append(f"evidence #{rid}: " + (f"{rec['event'] or 'no verdict, for home'} [{line}]" if rec else line))
        if rec:
            records.append(rec)
    try:
        out.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records))
    except OSError as e:
        raise Refused(f"evidence --out {out}: {e}")
    return lines + [f"wrote {len(records)} evidence line(s) to {out}"]


def evidence_line_problem(obj) -> str | None:
    """Why a parsed evidence line is not admissible, or None. Strict: the file is untrusted (another job's artifact,
    written after the PR heads' code ran), so every key, type and shape is checked and nothing it holds is echoed."""
    if not isinstance(obj, dict):
        return "not a JSON object"
    event = obj.get("event")
    if event is not None and (event not in EVIDENCE_EVENTS or ("verifying", event) not in dyadlib.ORCH_EVENTS):
        return "not an evidence event of the machine's table"
    want = {"rid", "event", "heads", "evidence" if event == "evidence-verified" else "note"}
    if set(obj) != want:
        return "its keys are not exactly " + ", ".join(sorted(want))
    if type(obj["rid"]) is not int or obj["rid"] <= 0:
        return "rid is not a positive integer"
    heads = obj["heads"]
    if not isinstance(heads, list) or not 0 < len(heads) <= EVIDENCE_HEADS:
        return f"heads is not a list of 1 to {EVIDENCE_HEADS} [pr, head] pairs"
    for h in heads:
        if not (isinstance(h, list) and len(h) == 2 and type(h[0]) is int and h[0] > 0 and isinstance(h[1], str)
                and OID.fullmatch(h[1])):
            return "a head is not [<pr>, <full sha>]"
    if len({h[0] for h in heads}) != len(heads):
        return "a PR is named twice"
    if "evidence" in want and not (isinstance(obj["evidence"], str) and EVIDENCE_SHA.fullmatch(obj["evidence"])):
        return "evidence is not a sha256"
    if "note" in want and not (isinstance(obj["note"], str) and obj["note"].strip()
                               and len(obj["note"]) <= EVIDENCE_NOTE_CHARS):
        return f"note is not a non-empty string of at most {EVIDENCE_NOTE_CHARS} characters"
    return None


def read_evidence(path: Path) -> tuple[dict[int, tuple[int, dict]], list[str]]:
    """({rid: (line number, record)}, the lines dropped) of an evidence file. An unreadable, oversized or overlong
    file yields nothing; a line that is not JSON or fails `evidence_line_problem` is dropped; a row named by more
    than one line has every one of them dropped (which one is meant is not the run's to guess)."""
    try:
        if path.exists() and not path.is_file():      # a FIFO, a device, a directory: never opened
            return {}, [f"evidence file {path}: not a regular file; nothing fired from it"]
        with path.open("rb") as fh:
            data = fh.read(EVIDENCE_FILE_BYTES + 1)     # never more than the bound is read
        if len(data) > EVIDENCE_FILE_BYTES:
            return {}, [f"evidence file {path}: larger than {EVIDENCE_FILE_BYTES} bytes; nothing fired from it"]
        text = data.decode("utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {}, [f"evidence file {path}: unreadable ({type(e).__name__}); nothing fired from it"]
    lines = text.splitlines()
    if len(lines) > EVIDENCE_FILE_LINES:
        return {}, [f"evidence file {path}: more than {EVIDENCE_FILE_LINES} lines; nothing fired from it"]
    got: dict[int, list[tuple[int, dict]]] = {}
    dropped = []
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except (ValueError, RecursionError):         # a deeply nested line recurses past the stack: not JSON here
            dropped.append(f"evidence line {n} dropped: not JSON"); continue
        if why := evidence_line_problem(obj):
            dropped.append(f"evidence line {n} dropped: {why}"); continue
        got.setdefault(obj["rid"], []).append((n, obj))
    out = {}
    for rid, items in got.items():
        if len(items) > 1:
            dropped += [f"evidence line {n} dropped: row #{rid} is named by {len(items)} lines" for n, _ in items]
        else:
            out[rid] = items[0]
    return out, dropped


def heads_problem(repo: Path, base: str, rid: int, heads: list[tuple[int, str]]) -> str | None:
    """Why an evidence line for row `rid` at `heads` may not fire on `base` now, or None: the entry is in `verifying`,
    its row neither terminal nor carrying an operative `Y done`, its recorded PRs the line's in order, each recorded head
    a prefix of the line's (a recorded head may be abbreviated), and each PR's live head the line's exactly."""
    b = board()
    text = show(repo, base, f"{inst(repo)}/d-work/board/{rid}.md")
    if not text:
        return f"row #{rid} has no board entry"
    try:
        phase, sub = b.phase_of(b.parse(text)[0].get("phase", ""))
    except ValueError:
        return f"row #{rid}'s board entry has no phase"
    if phase != "verifying":
        return f"row #{rid} is in {phase}, not verifying"
    r = next((r for r in dyadlib.read_rows(repo, at=base) if r.id == rid), None)
    if r is None or r.state in dyadlib.TERMINAL_STATES or rows_guard().operative_done(r.disposed):
        return f"row #{rid} is not open to evidence (no row, terminal, or a Y done recorded)"
    recorded = b.pr_list(sub)
    if [n for n, _ in recorded] != [n for n, _ in heads]:
        return f"row #{rid}'s board lists other PRs"
    if any(not h.startswith(rh) for (_, rh), (_, h) in zip(recorded, heads)):
        return f"row #{rid}'s board records other heads"
    for n, h in heads:
        if live(repo, n) != h:
            return f"PR #{n} is no longer at {h[:12]} (moved, or its head unreadable)"
    return None


def serve_evidence(repo: Path, rid: int, cut: list[tuple[int, str]], pending: dict[int, tuple[int, dict]]) -> str:
    """`run --evidence-from`'s evidence act: the file's line for this row, fired through `fire` once its heads are
    this act's and still hold on a fresh main (`heads_problem`); a null verdict told to home once. A row the file
    has no line for is reported and left (the evidence job takes it); nothing is ever computed here."""
    what = evidence_what(cut)
    item = pending.pop(rid, None)
    if item is None:
        return f"evidence #{rid}: no line for {what} in the evidence file (not fired)"
    n, rec = item
    heads = [(p, h) for p, h in rec["heads"]]
    if heads != list(cut):
        return f"evidence line {n} dropped: row #{rid}'s heads are not the board's recorded and live heads"
    if why := heads_problem(repo, land.fetch(repo), rid, heads):
        return f"evidence line {n} dropped: {why}"
    if rec["event"] is None:
        return escalate(repo, rid, what, rec["note"])
    pairs = {"evidence": rec["evidence"]} if rec["event"] == "evidence-verified" else {"note": note_of(rec["note"])}
    return fire(repo, rid, rec["event"], "verifying", pairs) + f" [evidence file, line {n}]"

def stray_body(rid: int, x: int, state: str) -> str:
    """The notice for a row a Done retires that is no longer backlog or done (#574 G5), as `escalate` words it."""
    return inbox().DISPOSITION.sub("[an entry, read in the ledger]", f"automaton: archive of the rows its Done retires refused for "
                                   f"row #{rid}: row #{x} is {state}; a Done retires only a backlog or done row (#574 G2)")

def retired_body(rid: int, refusal: str) -> str:
    """The notice for a planned row's board entry still in the removed `seat <name>` form (#604): the board guard's own
    refusal, which names the form to write; the entry is left as it stands."""
    return f"automaton: board flip refused for row #{rid}: board/{rid}.md {refusal}; the entry is left as it stands"

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

def board_after_plan_y(repo: Path, base: str, rid: int) -> bool:
    """#587 S11: the row's board entry was written after the commit that recorded its last `Y plan` — home's own act
    (a new question asked of a planned row, a re-route), which a flip the older `Y` implies must never overwrite. Read
    from git on `base`: the newest commit touching the board file is not an ancestor of the newest touching the row."""
    i = inst(repo)
    def last(rel: str) -> str:
        return land.git(repo, "log", "-1", "--format=%H", base, "--", rel, check=False).stdout.strip()
    row, brd = last(f"{i}/d-work/rows/{rid}.md"), last(f"{i}/d-work/board/{rid}.md")
    if not row or not brd or row == brd:
        return False
    return land.git(repo, "merge-base", "--is-ancestor", brd, row, check=False).returncode != 0


def planned_flip(rid: int, entry: dict[str, str], owners: list[str]) -> dict[str, str] | None:
    """#572 K1: the board pairs a recorded `Y plan` decides — waiting on the first owner, the plan as the next act, no
    question — or None when the entry already waits on a unit (the flip is done, or home has moved it on), or still
    holds the removed `seat <name>` form (#604: that entry is told to home by the scan, never rewritten, so the unit it
    names and its open question are not lost)."""
    w = entry.get("waiting-on", "")
    if w.startswith("unit ") or board().retired_waiting(w):
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
    if kind == "advance":
        return f"catch up #{act[1]} {act[2]} (recorded on the ledger)"
    if kind == "head-moved":
        return f"head-moved #{act[1]} from {act[2]}: " + ", ".join(f"PR #{pr} now at {h}" for pr, h in act[3])
    if kind == "withdrawn":
        return f"withdrawn #{act[1]} from done-asked: the batch Done question it shares is void ({act[2]})"
    if kind == "evidence":
        return f"evidence #{act[1]}: combined merge of {', '.join(f'PR #{pr} at {h}' for pr, h in act[2])} onto main"
    if kind == "archive":
        return f"archive {', '.join(f'#{x}' for x in act[2])} (retired by row #{act[1]}'s Done)"
    if kind == "tell":
        return f"tell home: {act[2]}"
    if kind == "board":
        return f"board #{act[1]}: " + ", ".join(f"{k}={v}" if v else f"{k} removed" for k, v in sorted(act[2].items()) if k != "holder")
    return f"notice {act[2]}: {act[3]}"


# ---- the sweep (d-work #564): read-only; what the pre-push gate leaves, plus checks the gate never had
SWEEP_LANDING_HOURS = "sweep-landing-hours"   # tunable (#590): a Y done whose named heads are not on main after this long is a finding
SWEEP_STALE_DAYS = "sweep-board-stale-days"   # tunable (#590): a board entry whose `since` is older than this is a finding
SWEEP_CI_HOURS = "sweep-ci-hours"             # tunable (#590): code pushes to main in this window are checked for a completed corroboration
CI_WORKFLOWS = ("rule-11 package", "d-work automaton")   # the runs that corroborate a code push (#564 E1, E4)
HEXWORD = re.compile(r"\b[0-9a-f]{7,64}\b")

def finding_key(line: str) -> str:
    """The line a finding is told under: its shas masked, so a finding that only moved its sha is not new again, and an
    entry-shaped fragment masked as `post` masks it, so the told text and the key compare equal."""
    return inbox().DISPOSITION.sub("[an entry, read in the ledger]", HEXWORD.sub("<sha>", " ".join(line.split())))

def sweep_check(wt: Path, stores: bool = False) -> list[tuple[bool, str]]:
    """(fails, line) for every FAIL and warn line `check` prints on the swept tree (every guard, the full suite); with
    `stores` (#617), `check --guards` on that tree — every guard's whole-store check and the transaction guards over an
    empty range, the suite never run (`DYAD_NO_NESTED_TESTS`) — and then `suite:live`, the tests that read the stores
    (`sweep_live`, #618 H4)."""
    argv, env = ["check"], dyadlib.git_env()
    if stores:
        argv, env = ["check", "--guards"], {**env, "DYAD_NO_NESTED_TESTS": "1"}
    r = subprocess.run([sys.executable, str(wt / "dyad" / "scripts" / "package.py"), *argv], cwd=wt,
                       capture_output=True, text=True, env=env)
    CHECK_LINES[:] = r.stdout.splitlines()           # #619: the report's checks-sha256 reads them, in check's order
    out = [(l.startswith(("FAIL", "ERROR: ")), l) for l in (r.stdout + r.stderr).splitlines()
           if l.startswith(("FAIL", "warn", "ERROR: "))]          # #619: a test's ERROR line names it, as FAIL: does
    if r.returncode and not any(f for f, _ in out):
        out.append((True, f"FAIL [sweep] check exited {r.returncode} with no FAIL line"))
    return out + (sweep_live(wt) if stores else [])

# #618 H4: the LiveCase tests read the instance's stores, so they run after each ledger push, in `sweep --stores`;
# listed per root by the runner's own child, each id kept only when its test is a `livetest.LiveCase`
LIVE_LIST_CHILD = ("import sys, unittest\nsys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[2])\nimport livetest\n"
                   "def ids(s):\n    for t in s:\n        yield from ids(t) if isinstance(t, unittest.TestSuite) else "
                   "([t.id()] if isinstance(t, livetest.LiveCase) else [])\n"
                   "print(*ids(unittest.defaultTestLoader.discover(sys.argv[1])), sep='\\n')")

def sweep_live(wt: Path) -> list[tuple[bool, str]]:
    """(fails, line) of `suite:live` (#618 H4) on the swept tree: every `livetest.LiveCase` test of every test root,
    run class by class through the tree's own runner child (`package.suite_child`, the environment `check --tests`
    sets), the classes in parallel. One FAIL line per failing test, and one per root whose listing failed; nothing
    when every test passes or no root holds one."""
    from concurrent.futures import ThreadPoolExecutor
    pkg = dyadlib.load_module(wt / "dyad" / "scripts" / "package.py", "dyad_live_runner")
    out, work = [], []
    for root in pkg.test_suites():
        r, kept = pkg.suite_child(["-c", LIVE_LIST_CHILD, str(root), str(wt / "dyad" / "scripts")])
        rel = Path(root).relative_to(wt) if Path(root).is_relative_to(wt) else root
        if r.returncode:
            out.append((True, f"FAIL [suite:live] {rel}: the listing failed ({(r.stderr.strip().splitlines() or ['no output'])[-1][:200]})"))
            continue
        groups: dict[str, list[str]] = {}
        for i in r.stdout.split():
            groups.setdefault(i.rsplit(".", 1)[0], []).append(i)
        work += [(rel, root, ids) for ids in groups.values()]
    with ThreadPoolExecutor(max(1, min(pkg.SUITE_JOBS, len(work)))) as pool:
        done = list(pool.map(lambda w: (w[0], pkg.suite_child(["-c", pkg.SUITE_UNIT_CHILD, str(w[1]), *w[2]])), work))
    for rel, (r, kept) in done:
        if r.returncode:
            out += [(True, f"FAIL [suite:live] {rel}: {f}") for f in (pkg.suite_failures(r.stderr) or [r.stderr.strip()[-200:]])]
    return out

def sweep_ledger(repo: Path, base: str, now, prefs: Path | None = None) -> list[tuple[bool, str]]:
    """Y dones whose heads never landed, and stale board entries, read from `base`; the tunables from `prefs` (the
    worktree at `base`), else `repo`."""
    import datetime
    out, rg = [], rows_guard()
    for r in dyadlib.read_rows(repo, at=base):
        e = rg.operative_done(r.disposed) if r.state not in dyadlib.TERMINAL_STATES else None
        if not e:
            continue
        m = re.match(r"\s*(\d{4}-\d{2}-\d{2})", e)
        when = datetime.datetime.fromisoformat(m.group(1)).replace(tzinfo=datetime.timezone.utc) if m else None
        owed = [(pr, h) for _, pr, h, _ in rg.named_heads([r]) if not steps.ancestor(repo, h, base)]
        if owed and when and (now - when).total_seconds() > dyadlib.tunable(SWEEP_LANDING_HOURS, prefs or repo) * 3600:
            out.append((False, f"finding: row #{r.id}'s done answer of {m.group(1)} names heads not on main: "
                               + ", ".join(f"PR #{pr} at {h[:12]}" for pr, h in owed)))
    d = f"{inst(repo)}/d-work/board"
    for name in ls(repo, base, d):
        if not name.endswith(".md"):
            continue
        fields = board().parse(show(repo, base, f"{d}/{name}") or "")[0]
        since = board().parse_since(fields.get("since", "")) if fields.get("since") else None
        if since and (now - since).days > (days := dyadlib.tunable(SWEEP_STALE_DAYS, prefs or repo)):
            out.append((False, f"finding: board {name[:-3]} unchanged since {fields['since']} (over {days} days)"))
    return out

def sweep_drift(repo: Path, wt: Path, base: str) -> list[tuple[bool, str]]:
    """The world against the record: released tags against their entries (the `released` run-book's health), and
    the mirror branch (`MIRROR`) against main."""
    out = []
    r = subprocess.run([sys.executable, str(wt / "dyad" / "scripts" / "package.py"), "runbook", "run", "released", "health",
                        "--as", "automaton"],   # the automaton's own party, a read-only run (#593)
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

def sweep_audit(wt: Path) -> list[str]:
    """The audit's coded checks on the swept tree (#619, `scripts/audits.py`): `reading:` lines, never posted or
    counted, and `finding:` lines, each a warning; the full sweep only, after each landed merge (`CHECK_INPUTS`: the
    code tree), and one more reading of its own time, F15's measure."""
    import time
    t = time.monotonic()
    out = dyadlib.load_module(HERE / "audits.py", "audits").audit(wt)
    return out + [f"reading: audit: {time.monotonic() - t:.1f} s"]

def new_events(wt: Path) -> tuple[str | None, dict[str, str], list[str]]:
    """(store, {path: appended text}, notes) for the run-book event files the sweep's runs appended to in the swept
    worktree `wt`: `store` the event store's repo-relative path (`dyadlib.events_rel`), each path under it, its text
    the lines after its content at `wt`'s HEAD. The runner appends only a changed reading (`runbook.unchanged`,
    #438), so this is often empty. A file changed other than by appending, removed, or unreadable is never landed: one
    note says so, and nothing here raises into the sweep."""
    rel = dyadlib.events_rel(wt)
    if not rel:
        return None, {}, []
    fresh, notes = {}, []
    for p in land.written(wt):
        if not (p.startswith(f"{rel}/") and p.endswith(".jsonl")):
            continue
        if not (wt / p).is_file():
            notes.append(f"events: {p} removed or not a file; not landed")
            continue
        try:
            r = land.git(wt, "show", f"HEAD:{p}", check=False)
            before = r.stdout if r.returncode == 0 else ""
            now = (wt / p).read_text(encoding="utf-8")
        except (OSError, UnicodeError, Refused) as e:
            notes.append(f"events: {p} not read ({type(e).__name__}); not landed")
            continue
        if not now.startswith(before):
            notes.append(f"events: {p} changed other than by an append; not landed")
        elif now[len(before):].strip():
            fresh[p] = now[len(before):]
    return rel, fresh, notes


def events_builder(fresh: dict[str, str]):
    """`land.land`'s builder: append each fresh event line to its file on the freshly fetched main, unless that file's
    last event of the same command already holds the same reading (output digest and exit, `runbook.unchanged`'s
    test) — so a rebuild after a moved main, or a reading another run landed meanwhile, never records twice."""
    def build(w: Path):
        for rel, text in fresh.items():
            p = w / rel
            for line in text.splitlines(keepends=True):
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                last = runbook_mod.last_event(p, ev.get("name", "")) if p.is_file() else None
                if last and last.get("output_sha256") == ev.get("output_sha256") and last.get("exit") == ev.get("exit"):
                    continue
                p.parent.mkdir(parents=True, exist_ok=True)
                with open(p, "a", encoding="utf-8") as f:
                    f.write(line if line.endswith("\n") else line + "\n")
        paths = land.written(w)
        if not paths:
            raise Refused("already landed: main holds the same reading; nothing pushed")
        names = ", ".join(sorted(Path(r).stem for r in fresh))
        return paths, f"events: {names} (automaton sweep)", ""
    return build


def land_events(repo: Path, rel: str | None, fresh: dict[str, str], row: int | None) -> str:
    """One `events:` line: the sweep's new event lines landed on main as an events-only commit through the land
    machinery (its worktree, its lock, its push-race rebuilds), under a subject that cites no d-work (Rule-3 Ledger,
    #438). Skipped without `--row` — a sweep run without it acts on nothing. Never raises: a refused or failed landing
    (no push rights, a moved main on every try) is the line, and the sweep's findings and exit are unchanged."""
    if not fresh:
        return "events: no new reading to land"
    names = ", ".join(sorted(Path(r).stem for r in fresh))
    if not row:
        return f"events: {names} not landed (no --row: this sweep acts on nothing)"
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            land.land(repo, "", None, events_builder(fresh), "the sweep's events", prefix=f"{rel}/", kind="events-only")
    except Refused as e:
        return f"events: {names} not landed ({str(e).splitlines()[0][:300]})"
    except Exception as e:                       # a landing never fails the sweep
        return f"events: {names} not landed ({type(e).__name__}: {(str(e).splitlines() or [''])[0][:300]})"
    m = re.search(r"landed ([0-9a-f]{40}) on main", buf.getvalue())
    return f"events: {names} landed on main{f' as {m.group(1)[:12]}' if m else ''} (events-only)"

def corroborated(repo: Path, c: str, own: list[dict], listed: list[dict], firstparent: set[str], recent: list[dict]) -> bool:
    """Whether code push `c` on main is corroborated (#564, #614): a successful `CI_WORKFLOWS` run on `c` itself (`own`);
    or one on a later first-parent commit of main whose tree contains `c` (`listed`, `firstparent`), whatever executed
    that merge, since corroboration runs once per landed tree and a newer push cancels the run on the older one (Rule-14
    property 3); or, for a merge `dyad merge` executed, a successful automaton run created after it (`recent`), which
    corroborates in the run that merged. A run cancelled with no later success covering `c` corroborates nothing."""
    ok = lambda w: w.get("name") in CI_WORKFLOWS and w.get("conclusion") == "success"
    if any(ok(w) for w in own):
        return True
    for w in listed:
        h = w.get("head_sha") or ""
        if ok(w) and h != c and h in firstparent and \
                land.git(repo, "merge-base", "--is-ancestor", c, h, check=False).returncode == 0:
            return True
    if "Executed by `dyad merge`" in land.out(repo, "log", "-1", "--format=%B", c):
        t = land.out(repo, "log", "-1", "--format=%cI", c)
        return any(w.get("created_at", "") >= t for w in recent)
    return False


CI_FILES = {"rule-11 package": "dyad-package.yml", "d-work automaton": "dyad-automaton.yml",
            "d-work sweep": "dyad-sweep.yml"}   # CI_WORKFLOWS' files, and the full sweep's (#619 delivery)
CI_ANY = ("d-work automaton", "d-work sweep")   # listed at every status (delivery counts a run in progress); the rest successes only
CI_PAGE = 30   # the newest runs read per workflow: a day of package runs, and the automaton's latest (#617, the ceiling)
CI_TIMEOUT_S = 3   # the hosting's round trip the home's read waits for; slower reads as "not read" (STALL_CEILING_S)
DELIVERED = ("success", "failure")   # #619 F10: a completed run that ran; cancelled and skipped deliver nothing
DELIVERY_GRACE_S = 300   # #619: a push younger than this is not yet judged; a run on it or a later push still covers the older
WORKFLOW_IDENTITY = "41898282+github-actions[bot]@users.noreply.github.com"   # the jobs' committer (dyad-automaton.yml)

def repo_slug(repo: Path) -> str | None:
    """`owner/name` of the hosting: GITHUB_REPOSITORY in a job, else read off `origin`'s URL (#617: a session's home
    reads the public run list too); None when neither names one."""
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"]
    url = land.git(repo, "remote", "get-url", "origin", check=False).stdout.strip()
    m = re.search(r"(?:github\.com[:/]|/git/)([A-Za-z0-9._-]+/[A-Za-z0-9._-]+?)(?:\.git)?/?$", url)   # github, or a git proxy's /git/
    return m.group(1) if m else None

def delivered(c: str, order: dict[str, int], listed: list[dict], name: str) -> bool:
    """Whether a `name` run started on main at `c` or at a later first-parent commit (`order`: newest first), queued,
    in progress or completed with a result (`DELIVERED`, #619 F10)."""
    for w in listed:
        h = w.get("head_sha") or ""
        ran = w.get("status") != "completed" or w.get("conclusion") in DELIVERED
        if w.get("name") == name and ran and h in order and order[h] <= order[c]:
            return True
    return False

def sweep_ci(repo: Path, base: str, now, prefs: Path | None = None) -> list[tuple[bool, str]]:
    """Code pushes to main within `sweep-ci-hours` with no successful corroborating run (`CI_WORKFLOWS`), and sweeps not
    delivered (#619): the newest code push with no `d-work sweep` run at it or after, and the newest ledger-only or
    events-only push not made by the jobs' own identity (`WORKFLOW_IDENTITY`: the same run's stores step sweeps those)
    with no `d-work automaton` run at it or after; a push younger than `DELIVERY_GRACE_S` waits. Read from the hosting:
    the repository is public, so the run list reads with `GITHUB_TOKEN` when set and without it otherwise (#617: the
    home's read in a session). One listing per workflow (`CI_FILES`), fetched in parallel with the commits' classing, so
    `board resume` stays under its ceiling; a hosting that cannot be read is one finding saying so, never a crash."""
    import datetime, json, urllib.request
    from concurrent.futures import ThreadPoolExecutor
    token, slug = os.environ.get("GITHUB_TOKEN"), repo_slug(repo)
    try:
        since = now - datetime.timedelta(hours=dyadlib.tunable(SWEEP_CI_HOURS, prefs or repo))
    except OverflowError:   # a valid but huge preference falls back, as a malformed one does (#590)
        since = now - datetime.timedelta(hours=dyadlib.tunable_default(SWEEP_CI_HOURS))
    since = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = [l.split() for l in land.git(repo, "log", "--first-parent", "--format=%H %ct %ce", f"--since={since}", base,
                                        check=False).stdout.splitlines() if len(l.split()) == 3]
    log = [m[0] for m in meta]
    if not log:
        return []
    def is_code(c):
        return not (dyadlib.ledger_only(repo, f"{c}^1", c) or dyadlib.events_only(repo, f"{c}^1", c))
    def runs(name):
        status = "" if name in CI_ANY else "&status=success"
        req = urllib.request.Request(f"https://api.github.com/repos/{slug}/actions/workflows/{CI_FILES[name]}/runs"
                                     f"?branch=main{status}&per_page={CI_PAGE}",
                                     headers={"Accept": "application/vnd.github+json",
                                              **({"Authorization": f"Bearer {token}"} if token else {})})
        with urllib.request.urlopen(req, timeout=CI_TIMEOUT_S) as resp:
            return [{**w, "name": w.get("name") or name} for w in json.load(resp).get("workflow_runs", [])]
    with ThreadPoolExecutor(8) as pool:                  # #617: the hosting and git at once, the home's ceiling
        fetched = [pool.submit(runs, n) for n in CI_FILES] if slug else []
        kinds = dict(zip(log, pool.map(is_code, log)))
        listed, error = [], None
        for f in fetched:
            try:
                listed += f.result()
            except Exception as e:                       # the hosting is The World: unreadable is a finding
                error = e
    code = [c for c in log if kinds[c]]
    ripe = [c for c, t, _ in meta if now.timestamp() - int(t) >= DELIVERY_GRACE_S]
    full = next((c for c in ripe if kinds[c]), None)
    stores = next((c for c, _, e in meta if c in ripe and not kinds[c] and e != WORKFLOW_IDENTITY), None)
    if not (code or full or stores):
        return []
    if not slug:
        return [(False, f"finding: corroboration of {len(code)} code push(es) to main not read (no hosting named by origin or GITHUB_REPOSITORY)")]
    if error is not None:
        return [(False, f"finding: corroboration not read from the hosting ({type(error).__name__})")]
    ok = [w for w in listed if w.get("conclusion") == "success"]
    recent = [w for w in ok if w.get("name") == "d-work automaton"]
    firstparent, out, order = set(log), [], {c: i for i, c in enumerate(log)}
    for c in code:
        own = [w for w in ok if w.get("head_sha") == c]
        if not corroborated(repo, c, own, ok, firstparent, recent):
            out.append((True, f"finding: code push {c[:12]} to main has no successful corroboration ({', '.join(CI_WORKFLOWS)})"))
    if full and not delivered(full, order, listed, "d-work sweep"):
        out.append((False, f"finding: delivery: no full sweep started on main at or after the landed merge {full[:12]}"))
    if stores and not delivered(stores, order, listed, "d-work automaton"):
        out.append((False, f"finding: delivery: no stores sweep started on main at or after the push {stores[:12]}"))
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

STALL_CEILING_S = 5.0   # #617 P5: `dyad board resume` prints the stall lines within this; dyad/tests/guards/agent/test_board.py holds it

def stall_lines(repo: Path, base: str, prefs: Path | None = None, now=None, cabinet: str | None = None) -> list[str]:
    """The stall findings the home reads at each prompt (`dyad board resume`, #617), read from the ledger at `base`:
    Y dones whose heads never landed and stale board entries (`sweep_ledger`), code pushes to main with no completed
    corroboration (`sweep_ci`, which needs the hosting and otherwise says it was not read), the work in flight (W-lines, the hosting's PRs read only with
    a token) and the backlog's hygiene (I-lines and `candidate:` pairs). With `cabinet` (#594), only the in-flight lines
    whose home is that cabinet's — a cabinet with no home of its own falls back to `program`'s, as the sweep once routed
    them. Read-only: it posts nothing."""
    import datetime
    from concurrent.futures import ThreadPoolExecutor
    now = now or datetime.datetime.now(datetime.timezone.utc)
    with ThreadPoolExecutor(2) as pool:                 # the hosting's round trip beside the ledger reads (the ceiling)
        ci = pool.submit(sweep_ci, repo, base, now, prefs)
        found = sweep_ledger(repo, base, now, prefs)
        hyg, candidates = hygiene_mod.hygiene(repo, base, now.timestamp(), prefs)
        pulls = sweep_pulls() if os.environ.get("GITHUB_TOKEN") else None
        flight = hygiene_mod.inflight_cabinets(repo, base, now.timestamp(), pulls, prefs=prefs)
        found += ci.result()
    if cabinet is not None:                              # the lines whose home is this cabinet's (`home` falls back)
        mine = home(repo, base, cabinet)
        flight = [(c, h) for c, h in flight if home(repo, base, c) == mine]
    flight = [h for _, h in flight]
    return ([l for _, l in found] + [f"finding: {h}" for h in hyg + flight] + candidates)

SWEEP_STORE = "dyad-sweep"   # `<git common dir>/dyad-sweep/<report-sha256>.txt`: every no-`--row` report, never tracked (#619)
CHECK_LINES: list[str] = []   # the swept tree's own `check` stdout, in order, as `sweep_check` read it: `checks-sha256`

def check_readings(lines: list[str]) -> list[str]:
    """The suite's summary per root and the invariant pass's count, read off the tree's own `check` lines (#619): the
    self-diagnostic's L1 to L3 read them in the report, so a report whose check ran no suite, or no invariant pass,
    says so by lacking the line."""
    out = [f"reading: suite {l.split('[Rule-12] ', 1)[1]}" for l in lines if "[Rule-12] " in l and ": Ran " in l]
    ok, bad = (sum(1 for l in lines if l.startswith(p)) for p in ("ok   [invariant]", "FAIL [invariant]"))
    return out + ([f"reading: invariants {ok} ok, {bad} FAIL"] if ok or bad else [])

def sweep(repo: Path, row: int | None, stores: bool = False) -> tuple[list[str], int]:
    """(lines, rc). Read-only but for one write: the event its own health run recorded, landed events-only on `row`
    (#593, `land_events`). The full sweep's readings print first (#619: the audit's, never posted or counted), then the
    findings in two groups, `standing` (already told to the home) and `new`; the new ones are posted in one notice on
    `row`; rc 1 when any finding fails. The stall findings (heads not landed, corroboration, stale board, work in
    flight, backlog hygiene, sweeps not delivered) are not the sweep's since #617: the home reads them in `dyad board
    resume` (`stall_lines`). With `stores` (#617): the whole-store guards only — no suite, no drift, no audit, no
    events — run after each ledger push in the automaton's job, folded against what was told the same way. With no
    `row` (#619) it is the audit's report: the stall block too, `checks-sha256=` over the tree's own `check` lines and
    `report-sha256=` over the whole text, which is stored under the git common dir (`SWEEP_STORE`); nothing lands."""
    import datetime, hashlib
    now = datetime.datetime.now(datetime.timezone.utc)
    base = land.fetch(repo)
    common = Path(land.out(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    wt = common / land.WORKTREE
    CHECK_LINES.clear()
    with land.locked(common):
        land.prepare(repo, wt, base)
        found = sweep_check(wt, stores) + ([] if stores else sweep_drift(repo, wt, base))
        readings = []
        if not stores:
            try:
                audit = sweep_audit(wt)
            except Exception as e:                           # the audit never fails the sweep's other findings
                audit = [f"finding: audit not read ({type(e).__name__})"]
            readings = check_readings(CHECK_LINES) + [l for l in audit if l.startswith("reading: ")]
            found += [(False, l) for l in audit if not l.startswith("reading: ")]
        events_at, fresh, event_notes = None, {}, []
        if not stores:
            try:                                             # read before the lock goes: the next land resets wt
                events_at, fresh, event_notes = new_events(wt)
            except Exception as e:                           # the event step never fails the sweep's findings
                events_at, fresh, event_notes = None, {}, [f"events: not read ({type(e).__name__}); not landed"]
    lines = [l if l.startswith("finding: ") else f"finding: {l}" for _, l in found]
    rc = 1 if any(f for f, _ in found) else 0
    routed: dict[str | None, list[str]] = {home(repo, base, board().SOLO): lines} if lines else {}
    told = {to: " ".join(m.get("body", "") for m in box_messages(repo, base, to) if m.get("from") == SEAT) if to else ""
            for to in routed}
    new = {to: [l for l in ls if finding_key(l.removeprefix("finding: ")) not in told[to]] for to, ls in routed.items()}
    fresh_lines = {l for v in new.values() for l in v}
    standing = [l for l in lines if l not in fresh_lines]
    count = sum(len(v) for v in new.values())
    summary = (f"{'stores sweep' if stores else 'sweep'} of main {base[:12]}: {len(lines)} finding(s), "
               f"{sum(f for f, _ in found)} failing, {count} new")
    sent, untold = [], False
    for to, ls in new.items():
        if ls and row and to:
            for kind, group in notice_groups(ls):
                for part in notice_parts(group):
                    body = f"automaton {'stores sweep' if stores else 'sweep'} at {base[:12]}, {kind}: " + " | ".join(part)
                    try:
                        sent.append(post(repo, to, row, body))
                    except (Refused, inbox().Refused) as e:
                        sent.append(f"the notice to {to} was refused ({e})")
        elif ls:
            untold = True
    if sent:
        summary += "; " + "; ".join(sent)
    if untold:
        summary += "; not told (no --row or no home)"
    event_lines = [] if stores else event_notes + [land_events(repo, events_at, fresh, row)]   # after the notices; never changes rc
    out = (readings + [f"standing: {len(standing)} finding(s) already told to the home"] + standing
           + [f"new: {count} finding(s) not yet told"] + [l for l in lines if l in fresh_lines] + event_lines + [summary])
    if row:
        return out, rc
    try:
        stalls = stall_lines(repo, base, now=now)
    except Exception as e:                               # the report still prints; the home's read says the same
        stalls = [f"finding: stalls not read ({type(e).__name__})"]
    out += [f"stalls: {len(stalls)} line(s), the home's read (`dyad board resume`)"] + stalls
    out.append(f"checks-sha256={hashlib.sha256(chr(10).join(CHECK_LINES).encode()).hexdigest()}")
    out.append(f"report-sha256={(digest := hashlib.sha256(chr(10).join(out).encode()).hexdigest())}")
    try:
        (common / SWEEP_STORE).mkdir(exist_ok=True)
        (common / SWEEP_STORE / f"{digest}.txt").write_text("\n".join(out) + "\n")
        out.append(f"stored: {common / SWEEP_STORE / f'{digest}.txt'}")
    except OSError:
        out.append("stored: none")
    return out, rc

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


REASON_LINES = 5                                   # at most this many failing lines a notice carries (#592)
REASON_CHARS = 600                                 # and at most this many characters
FAILING = re.compile(r"^\s*(FAIL\b|FAIL:|refused\b|error:|fatal:|! \[remote rejected\]|! \[rejected\])")


def reason(why: str) -> str:
    """A refusal's reason for a notice (#592): its first line, and when that line only introduces what follows (a
    failed push's hook output), the failing lines after it — never an empty reason. Capped, one line."""
    lines = [l.strip() for l in why.strip().splitlines() if l.strip()]
    if not lines:
        return "no reason given"
    head, rest = lines[0], lines[1:]
    failing = [l for l in rest if FAILING.match(l)][:REASON_LINES]
    if not failing and head.endswith(":") and rest:
        failing = rest[-REASON_LINES:]
    out = " | ".join([head.rstrip(":") + (":" if failing else "")] + failing) if failing else head
    return out[:REASON_CHARS]


def escalate(repo: Path, row: int, what: str, why: str) -> str:
    """A refusal, posted once to the home's inbox; the home decides."""
    base = land.fetch(repo)
    to = home(repo, base, row_cabinet(repo, base, row))
    body = f"automaton: {what} refused for row #{row}: {reason(why)}"
    body = inbox().DISPOSITION.sub("[an entry, read in the ledger]", body)
    if not to:
        return f"refused, and no home to tell (no AUTOMATON_HOME and no holder of the row's cabinet's _cos file): {body}"
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
            MERGES_LANDED.extend(heads)                    # #617: the job starts the full sweep once per landed cut
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
        lines = [l for l in steps.close_landed(repo, rid, True) if l]
        # #574 G5: a row the Done retires that is neither backlog nor done is told to home, never resolved
        lines += [escalate(repo, rid, "archive on close", l.removeprefix(steps.NOT_ARCHIVED))
                  for l in lines if l.startswith(steps.NOT_ARCHIVED)]
        return "\n".join(lines)
    except Refused as e:
        if str(e).startswith("already closed"):
            return str(e)
        return escalate(repo, rid, "close", str(e))


CORROBORATION_FAILED: set[int] = set()   # rows whose landed cut failed corroboration in this run: the run exits 1
MERGES_LANDED: list[str] = []            # #617: the merge commits this run landed, reported for the job

def landed_report(heads: list[str]) -> str:
    """The one line `run` ends with (#617), and, when the job set `GITHUB_OUTPUT`, its outputs `landed` (`true` or
    `false`) and `landed-at` (the last merge this run landed), which the job reads to dispatch the full sweep."""
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"landed={'true' if heads else 'false'}\nlanded-at={heads[-1] if heads else ''}\n")
    return f"landed: {len(heads)} merge(s)" + (f", the last at {heads[-1][:12]}" if heads else "")

def run(repo: Path, evidence_from: Path | None = None) -> list[str]:
    """Take the acts. With `evidence_from` (#587 X10) the evidence acts are served from that file, which an
    `evidence --out` job wrote, and never computed here (`serve_evidence`)."""
    out, stopped = [], set()
    pending: dict[int, tuple[int, dict]] = {}
    if evidence_from is not None:
        pending, dropped = read_evidence(evidence_from)
        out += dropped
    evidence = (lambda rid, cut: serve_evidence(repo, rid, cut, pending)) if evidence_from is not None else \
        (lambda rid, cut: do_evidence(repo, rid, cut))
    _, acts = plan(repo)
    moved = {a[1] for a in acts if a[0] == "head-moved"}
    for act in acts:
        if act[0] == "merge":
            ok, line = do_merge(repo, act[1], act[2])
            out.append(line)
            if not ok:
                stopped.add(act[1])
        elif act[0] == "close":
            out.append(do_close(repo, act[1]))
        elif act[0] == "archive":
            try:
                out.append(steps.batch(repo, [f"state {x} archived --retired-by {act[1]}" for x in act[2]]))
            except Refused as e:
                if "already landed: every line of the batch is on origin/main" in str(e):
                    out.append(f"row #{act[1]}: the rows its Done retires are already archived")
                else:
                    out.append(escalate(repo, act[1], "archive of the rows its Done retires", str(e)))
        elif act[0] == "tell":
            fresh = land.fetch(repo)
            to = home(repo, fresh, row_cabinet(repo, fresh, act[1]))   # the row's cabinet's home (#594)
            try:
                out.append(f"refused, {post(repo, to, act[1], act[2])}: {act[2]}")
            except (Refused, inbox().Refused) as e:
                out.append(f"the notice to {to} was refused ({e}): {act[2]}")

        elif act[0] == "board":
            out.append(board_set(repo, act[1], act[2]))
        elif act[0] == "advance":
            out.append(catch_up(repo, act[1], act[3]))
        elif act[0] == "head-moved":                                  # #587 X6: one event per moved PR, the first
            for k, (pr, head) in enumerate(act[3]):                    # from the recorded phase, the rest from verifying
                out.append(fire(repo, act[1], "head-moved", act[2] if k == 0 else "verifying", {"pr": str(pr), "head": head}))
        elif act[0] == "withdrawn":                                   # #587 X6, a batch's other rows
            out.append(fire(repo, act[1], "withdrawn", "done-asked", {"note": note_of(act[2])}))
        elif act[0] == "evidence":
            out.append(evidence(act[1], act[2]))                      # #587 X5
        else:
            try:
                out.append(post(repo, act[2], act[1], act[3]))
            except (Refused, inbox().Refused) as e:
                out.append(f"notice to {act[2]} refused: {e}")
    # merges just landed may make a row due: one more pass closes it in the same run
    base, again = plan(repo)
    out += [do_close(repo, a[1]) for a in again if a[0] == "close" and a[1] not in stopped]
    # #587 X5 after X6: a row whose head moved in this run is back in verifying; its new heads are verified now, since
    # the automaton's own push starts no workflow run of its own
    out += [evidence(a[1], a[2]) for a in again if a[0] == "evidence" and a[1] in moved]
    out += [f"evidence line {n} dropped: row #{rid} has no evidence act at those heads now" for rid, (n, _) in pending.items()]
    # #572 K3: a cut still owed after this run's merges waits on its merge, not on the operator
    for a in again:
        if a[0] == "merge":
            text = show(repo, base, f"{inst(repo)}/d-work/board/{a[1]}.md")
            entry = board().parse(text)[0] if text else {}
            if text and not entry.get("phase") and (pairs := pending_flip(entry, a[2])):   # #587: landing already says it
                out.append(board_set(repo, a[1], pairs))
            elif text and (ph := board().phase_name(entry)) not in (None, "landing", "held"):
                out.append(f"board #{a[1]} phase {ph}: Y done recorded by hand, merge "            # #587: never board_set,
                           f"{', '.join(f'PR #{pr}' for pr, _ in a[2])} pending; board not flipped")   # the guard fails it
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
            stores = STORES_FLAG in rest
            rest = [x for x in rest if x != STORES_FLAG]
            if (stores and a[1:].count(STORES_FLAG) > 1) or (rest not in ([],) and not (len(rest) == 2 and rest[0] == ROW_FLAG and rest[1].isdigit())):
                print(USAGE, file=sys.stderr); return 2
            lines, rc = sweep(Path(repo), int(rest[1]) if rest else None, stores)
            print("\n".join(lines)); return rc
        if a[:1] == ["evidence"]:
            if len(a) != 3 or a[1] != "--out":
                print(USAGE, file=sys.stderr); return 2
            print("\n".join(evidence_out(Path(repo), Path(a[2]))))
            return 0
        if a == ["run"] or (len(a) == 3 and a[:2] == ["run", "--evidence-from"]):
            CORROBORATION_FAILED.clear(); MERGES_LANDED.clear()
            lines = run(Path(repo), Path(a[2]) if len(a) == 3 else None)
            report = landed_report(MERGES_LANDED)             # always the job's outputs; the line only when one landed
            print("\n".join(lines + ([report] if MERGES_LANDED else [])))
            return 1 if CORROBORATION_FAILED else 0
        print(USAGE, file=sys.stderr)
        return 2
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], dyadlib.repo_root()))
