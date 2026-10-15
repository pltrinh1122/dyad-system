#!/usr/bin/env python3
"""Row-file guard (entity `row`, agent corpus; Rule-3 owns the content and the fence, Rule-16 the
store; placed per Rule-11 property 1). Kernel: Python 3.12+.

Package check (`check_package`): every `<instance>/d-work/rows/<id>.md` parses (dyadlib.FIELDS), its
id equals its file name, its state is one of dyadlib.STATES, and no id is duplicated.

Transaction check (`check_transaction`, TRANSACTION; the main fence, referenced by Rule-2): a commit
pushed directly to main (non-merge, first-parent) may touch only <instance>/d-work/ and, for row
files, may only add a file or change state/disposed/refs: never delete a row file or change its id
or title (C3). A state change must be a transition in dyadlib.TRANSITIONS (Rule-16: state never
regresses; d-work #112) and a new row file must start in dyadlib.NEW_STATES. The rendered
LEDGER.md is untracked (d-work #111) and is not diffed. This full fence applies on `main` only;
on a branch `check_transaction` instead runs `check_id_collisions` (d-work #32 F2): a row id this
range adds or modifies must not already exist at the base under a *different* title — the
signature of two sessions racing the allocator — leaving the append-only rules themselves to this
same fence once the branch reaches `main`, and the plan gate to `prs.py`. That hand-off held only for
a branch replayed onto `main`: a PR merge (`--no-ff`) lands commits this fence, walking
`--first-parent`, never visits. So a ledger-only branch, which the plan gate now skips (#191), is
fenced here, each of its own commits as `main` would fence it (`check_ledger_branch`). On both, every `disposed`
entry a range *adds* must have the entry shape `<YYYY-MM-DD> <Y|N>[ <text>]` with balanced
parentheses (`check_disposed`, d-work #133): a `;` inside disposition text splits one entry into
two, and nothing judged the shape before (#67, #100). Entries already present are never re-judged. A row's
`mode` (dyadlib.OPTIONAL_FIELDS, d-work #290) is append-only in the same way: it never changes after the
commit that adds the row, in either direction, so a mandate is neither revoked nor granted by an edit; and a
row born `implicit` is born `open` carrying exactly one `disposed` entry `<date> Y plan (mandate #<id>)`,
since implicit mode takes no disposition of its own and a `backlog` row can carry no PR. Two clauses keep the Done order Rule-3's completion clause prescribes (d-work #202): one commit may not
both record a `Y done` that names a merge and set the row `done` (`done_order_problems`), since the state
follows the merge; and the commit that does set `done` must show every head those entries name as an
ancestor of itself (`landing_problems`), an unresolvable sha printing one line rather than failing. The
interval between the two is read by the package check as one warning per row (`done_recorded_not_closed`).
The append-only rule of the run-book event store
(the sysadmin craft's server-instances rule) lives in the craft's guard `crafts/sysadmin/guards/events.py`;
the CLI below runs both when that guard is installed, as the former `main_fence.py` did (#155).
  rows.py <before> <after>          the main fence over a pushed range (rows and events)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("rows.py: Python 3.12+ required")
import os, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "row", "agent", True
NAME, OWNER = "d-work row file", "Rule-3 (content), Rule-16 (store)"
FIELDS = dyadlib.FIELDS
INVARIANTS = [("fields-are-dyadlib-fields", lambda: FIELDS is dyadlib.FIELDS)]   # crafts/syseng/rules/invariants.md
# #290: `mode` is not asserted here. `crafts/sysarch/tests/test_project_entities.py` pins this guard's
# INVARIANTS names to exactly the one above and this card's fields to exactly `dyadlib.FIELDS`, so the two
# facts — `mode` is a Row field, and FIELDS and OPTIONAL_FIELDS are disjoint — are `dyadlib`'s own invariants
# (`row-fields-match-dataclass`, `row-optional-fields-disjoint`), which the runner's pass runs all the same.
ENTRY = re.compile(r"\d{4}-\d{2}-\d{2} [YN](?: |$)")   # Rule-3 Ledger: `<date> <Y|N> <plan|done|merge #n|reason>`
MANDATE = re.compile(r"\d{4}-\d{2}-\d{2} Y plan \(mandate #\d+\)$")   # the one entry an implicit-mode row is born with (Rule-3, #290)
DONE_Y = re.compile(r"\d{4}-\d{2}-\d{2} Y done\b")                    # a *given* completion disposition (Rule-3 Completion, #202)
DONE_MERGES = re.compile(r"\d{4}-\d{2}-\d{2} Y done\b[^;]*\bmerge[sd]?\b[^;]*#\d+")   # one that ratifies a merge: the state waits for it
HEAD_AT = re.compile(r"\bat ([0-9a-f]{7,40})\b")                       # the head the `Y` was given on
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

def git(*a, cwd, stderr=None): return subprocess.check_output(["git", *a], cwd=cwd, text=True, stderr=stderr)

def parent(sha, cwd):
    p = git("rev-list", "--parents", "-n", "1", sha, cwd=cwd).split()
    return p[1] if len(p) > 1 else EMPTY_TREE

def branch(cwd) -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd).strip()

# ---- package check
def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    d = dyadlib.rows_dir(root)
    if not d.is_dir():
        return []
    fails, seen, parsed = [], set(), []
    for p in sorted(d.glob("*.md"), key=lambda p: int(p.stem) if p.stem.isdigit() else -1):
        if not p.stem.isdigit():
            continue
        rel = p.relative_to(root) if p.is_relative_to(root) else p
        try:
            r = dyadlib.parse_row_file(p.read_text())
        except ValueError as e:
            fails.append(f"{rel}: {e}"); continue
        if p.stem != str(r.id):
            fails.append(f"{rel}: id {r.id} differs from the file name (the name is exactly `<id>.md`, #191)")
        if r.state not in dyadlib.STATES:
            fails.append(f"{rel}: state '{r.state}' not one of {' '.join(sorted(dyadlib.STATES))}")
        if r.id in seen:
            fails.append(f"{rel}: duplicate id {r.id}")
        seen.add(r.id); parsed.append(r)
    return fails + done_recorded_not_closed(parsed)

def summary(root: Path | None = None) -> str:
    root = root or dyadlib.repo_root()
    d = dyadlib.rows_dir(root)
    return f"{sum(1 for p in d.glob('*.md') if p.stem.isdigit()) if d.is_dir() else 0} rows"

# ---- disposed-entry shape (d-work #133)
def entries(disposed: str) -> list[str]:
    return [e.strip() for e in disposed.split(";") if e.strip()]

def added_entries(before: str, after: str) -> list[str]:
    """The entries `after` holds beyond `before`'s — a prefix append, or whatever is new if the
    prefix was rewritten (which `disposed_problems` then judges on shape)."""
    old = entries(before); new = entries(after)
    return new[len(old):] if new[:len(old)] == old else [e for e in new if e not in old]

def disposed_problems(path: str, before: str, after: str, label: str) -> list[str]:
    """Every entry `after` holds beyond `before`'s must be one well-shaped entry: a `;` inside a
    disposition's text leaves a fragment (`falsify extensibility first)`, #100) that fails here."""
    return [f"FAIL [disposed]: {label} {path} adds entry {e!r}: not `<YYYY-MM-DD> <Y|N> <text>` with balanced "
            f"parentheses — a `;` inside disposition text splits one entry in two (Rule-3 Ledger)"
            for e in added_entries(before, after) if not ENTRY.match(e) or e.count("(") != e.count(")")]

# ---- the Done state follows the merge (d-work #202)
def done_order_problems(path: str, before, after, label: str) -> list[str]:
    """Rule-3 Completion: a Done-`Y` that ratifies a merge is recorded with the state left as it is, the
    merges execute, and a second commit sets `done`. One commit that does both is the old order, and it is
    what closed every route to the pushes a refused merge needs — `done` is terminal (Rule-16) and the plan
    gate refuses every commit citing a terminal row, so the rebase, the conflict resolution or the second
    PR of a ratified set had nowhere legal to go (eleven rows between 2026-09-30 and 2026-10-15; #202).
    The cure is to split the commit, and it is always available: both halves are ledger-only, which the
    plan gate skips (#191)."""
    if after.state != "done" or before.state == "done":
        return []
    return [f"FAIL [main-fence]: {label} row file {path} is set done by the commit that records {e!r} "
            f"(Rule-3 Completion: the state follows the merge — record the entry with the state unchanged, "
            f"merge, then `dyad dwork state <id> done`)"
            for e in added_entries(before.disposed, after.disposed) if DONE_MERGES.search(e)]

def landing_problems(path: str, before, after, label: str, sha: str, cwd, base: str | None = None) -> list[str]:
    """The commit that sets `done` asserts two things. That a Done-`Y` was given at all: a row reaches
    `done` only with a `Y done` entry already on it — the coupling the 2026-10-08 chain-of-authority audit
    found missing (C2: a dispositionless `dwork state <id> done` wrote the state with nothing behind it),
    which matters more now that the dispositionless write is the prescribed closing act. And that every
    head the operative entry names (`Y done (merges PR #402 at 0fa99a7)`) is reachable: an ancestor of the
    base branch this range is pushed to, or of this commit itself where the merge and the close travel
    together. A sha unknown to this clone
    prints one line and is not checked — a hard failure on an unresolvable sha is the cross-clone wedge of
    #321's I7, where one seat's local commit refused every other seat's push for sixteen minutes. Only the
    last `Y done` entry governs: a resolution that changes a head voids the `Y` given against it (Rule-2,
    Binding), so the question is asked again and the head of a superseded entry is history, not an
    obligation (#202, attack A5)."""
    if after.state != "done" or before.state == "done":
        return []
    done = [e for e in entries(after.disposed) if DONE_Y.search(e)]
    if not done:
        return [f"FAIL [main-fence]: {label} sets row file {path} done with no `Y done` entry on the row "
                f"(Rule-3 Completion: only the Operator closes a d-work, and the state executes that `Y`)"]
    fails = []
    for e in done[-1:]:     # the operative record only: see the docstring
        for s in HEAD_AT.findall(e):
            try:
                git("cat-file", "-e", f"{s}^{{commit}}", cwd=cwd, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                print(f"skip [main-fence]: {label} row file {path} names head {s}, which this clone "
                      f"cannot resolve: not checked (#202)")
                continue
            if any(reachable(s, ref, cwd) for ref in (base, sha) if ref):
                continue
            fails.append(f"FAIL [main-fence]: {label} sets row file {path} done while head {s}, which "
                         f"{e!r} names, is on neither {base or 'the base'} nor this commit: the merge that "
                         f"`Y` ratified has not landed (Rule-3 Completion, #202)")
    return fails

def reachable(sha: str, ref: str, cwd) -> bool:
    """`sha` is an ancestor of `ref`; a ref that does not resolve here decides nothing."""
    try:
        git("merge-base", "--is-ancestor", sha, ref, cwd=cwd, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def done_recorded_not_closed(rows: list) -> list[str]:
    """The reading of the interval the order above opens: a row that records a completion disposition while
    its state is not terminal is a Done-`Y` whose merges are still owed. One warning line, never a failure —
    a failure here would refuse exactly the pushes the interval exists to permit — and it is read where it
    cannot be missed, since every push and every `check --evidence` runs this check and the evidence block
    the completion reply pastes carries its lines and their sha256. Whether the merge has run is not
    decidable from git alone at this moment (a merge subject naming a PR is not a merge of it: `Merge pull
    request #401: … PR #355 never landed`), which is why only the commit that writes `done` is fenced."""
    out = []
    for r in rows:
        if r.state in dyadlib.TERMINAL_STATES:
            continue
        done = [e for e in entries(r.disposed) if DONE_Y.search(e)]
        for e in done[-1:]:     # one line per row: the operative entry, as `landing_problems` reads it
            out.append(f"warning: row #{r.id} is {r.state} and records {e!r}: a Done-`Y` recorded whose "
                       f"merges are still owed — merge what it names, then `dyad dwork state {r.id} done` "
                       f"(Rule-3 Completion, #202)")
    return out

# ---- countersign mode (d-work #290)
def mode_changed(path: str, before, after, label: str) -> list[str]:
    """A row's `mode` never changes after the commit that adds the row. `implicit`→`explicit` would revoke a
    mandate by an edit — the escalate edge is a disposition on the row, not a rewrite of this field — and
    `explicit`→`implicit` would grant one after the Operator read the plan that bounds it. A row is born in
    its mode or not at all."""
    if before.mode == after.mode:
        return []
    why = ("a mandate is never revoked by an edit; the escalate edge is a disposition on the row"
           if before.mode == "implicit" else
           "a row is born implicit under its mandate, never made implicit later")
    return [f"FAIL [main-fence]: {label} changes mode of row file {path} {before.mode}→{after.mode} "
            f"(Rule-3: {why})"]

def born_implicit_problems(path: str, new, label: str) -> list[str]:
    """What an added `implicit`-mode row must look like: born `open`, since a `backlog` row carries no PR and
    moves only on the Operator's own prompt (Rule-3); and carrying exactly one `disposed` entry
    `<date> Y plan (mandate #<id>)`, since implicit mode is authorized by one mandate and takes no
    disposition of its own. Anything else is the shape no plan-`Y` covers."""
    if new.mode != "implicit":
        return []
    fails, es = [], entries(new.disposed)
    if new.state != "open":
        fails.append(f"FAIL [main-fence]: {label} adds implicit-mode row file {path} in state {new.state} "
                     f"(Rule-3: an implicit-mode row is born open — a backlog row carries no PR and moves "
                     f"only on the Operator's prompt)")
    if len(es) != 1 or not MANDATE.match(es[0]):
        fails.append(f"FAIL [main-fence]: {label} adds implicit-mode row file {path} with disposed "
                     f"{new.disposed!r}, not one entry `<date> Y plan (mandate #<id>)` (Rule-3: implicit "
                     f"mode is authorized by one mandate and takes no disposition of its own)")
    return fails

def check_disposed(root: Path, base: str, head: str) -> list[str]:
    """`disposed_problems` over every row file base..head changes, as a whole diff (a branch)."""
    prefix = f"{os.environ.get('DYAD_INSTANCE', 'agent-corpus')}/d-work/rows/"
    try:
        paths = git("diff", "--no-renames", "--name-only", "--diff-filter=AM", f"{base}..{head}", "--", prefix, cwd=root).split()
    except subprocess.CalledProcessError:
        return []
    fails = []
    for path in paths:
        if not Path(path).stem.isdigit():
            continue
        try:
            after_row = dyadlib.parse_row_file(git("show", f"{head}:{path}", cwd=root, stderr=subprocess.DEVNULL))
            after = after_row.disposed
        except (subprocess.CalledProcessError, ValueError):
            continue   # a malformed row file is check_package's report
        try:
            before_row = dyadlib.parse_row_file(git("show", f"{base}:{path}", cwd=root, stderr=subprocess.DEVNULL))
            before = before_row.disposed
        except (subprocess.CalledProcessError, ValueError):
            before_row, before = dyadlib.Row(after_row.id, after_row.title, after_row.opened, "open", "", ""), ""
        fails += disposed_problems(path, before, after, "range")
        fails += done_order_problems(path, before_row, after_row, "range")   # #202: the order, on a work branch too
    return fails

# ---- transaction check (the main fence)
def check_commit(sha: str, cwd, instance: str, base: str | None = None) -> list[str]:
    label = sha[:9]
    paths = git("diff-tree", "--root", "--no-commit-id", "-r", "--name-only", sha, cwd=cwd).split()
    bad = [p for p in paths if not p.startswith(f"{instance}/d-work/")]
    if bad:
        return [f"FAIL [main-fence]: direct commit {label} touches non-ledger paths: {' '.join(bad)}"]
    fails = []
    par = parent(sha, cwd)
    for st, path in (l.split("\t", 1) for l in git("diff-tree", "--root", "--no-commit-id", "-r", "--name-status", "--no-renames", sha, cwd=cwd).splitlines() if "\t" in l):
        if not path.startswith(f"{instance}/d-work/rows/"):
            continue
        if st.startswith("D"):
            fails.append(f"FAIL [main-fence]: {label} deletes row file {path}"); continue
        if st.startswith("M"):
            try:
                before = dyadlib.parse_row_file(git("show", f"{par}:{path}", cwd=cwd))
            except ValueError:
                continue    # a repair of a row that did not parse: nothing to compare against (the package check judges the result)
            try:
                after = dyadlib.parse_row_file(git("show", f"{sha}:{path}", cwd=cwd))
            except ValueError:
                fails.append(f"FAIL [main-fence]: {label} leaves row file {path} unparseable"); continue
            if before.id != after.id or before.title != after.title:
                fails.append(f"FAIL [main-fence]: {label} changes id or title of row file {path}"); continue
            if not dyadlib.allowed(before.state, after.state):
                how = "leaves the table" if after.state not in dyadlib.STATES else "regresses"
                fails.append(f"FAIL [main-fence]: {label} row file {path} state {how} {before.state}→{after.state}")
            fails += mode_changed(path, before, after, label)
            fails += disposed_problems(path, before.disposed, after.disposed, label)
            fails += done_order_problems(path, before, after, label)
            fails += landing_problems(path, before, after, label, sha, cwd, base)
        elif st.startswith("A"):
            try:
                new = dyadlib.parse_row_file(git("show", f"{sha}:{path}", cwd=cwd))
            except ValueError:
                fails.append(f"FAIL [main-fence]: {label} adds row file {path} that does not parse"); continue
            if new.state not in dyadlib.NEW_STATES:
                fails.append(f"FAIL [main-fence]: {label} adds row file {path} in state {new.state} (not one of {' '.join(sorted(dyadlib.NEW_STATES))})")
            fails += born_implicit_problems(path, new, label)
            fails += disposed_problems(path, "", new.disposed, label)
    return fails

def check_range(before: str, after: str, cwd=None) -> list[str]:
    """Row rules over every non-merge first-parent commit of before..after."""
    cwd = cwd or dyadlib.repo_root()
    instance = os.environ.get("DYAD_INSTANCE", "agent-corpus")
    fails = []
    for sha in git("rev-list", "--first-parent", "--no-merges", f"{before}..{after}", cwd=cwd).split():
        fails += check_commit(sha, cwd, instance, before)
    return fails

def check_transaction(root: Path, base: str, head: str) -> list[str]:
    """The fence judges direct commits to `main`; on any other branch it checks only that a new
    or modified row id does not collide with a different title already at `base` — two sessions
    independently allocating the same id for different work (d-work #32) — leaving everything
    else (the append-only rules) to this same fence once the branch reaches `main`."""
    if branch(root) != "main":
        # a ledger-only branch gets the fence per commit, which already judges each added `disposed` entry
        whole = check_ledger_branch if dyadlib.ledger_only(root, base, head) else check_disposed
        return check_id_collisions(root, base, head) + whole(root, base, head)
    return check_range(base, head, cwd=root)

def check_ledger_branch(root: Path, base: str, head: str) -> list[str]:
    """A ledger-only branch skips the plan gate (Rule-3, #191) because `main` would admit the same
    commits — so it gets what `main` gives them: the fence, per commit, over the branch's own
    non-merge commits. Without it a PR merge (`--no-ff`) lands commits the fence, walking
    `--first-parent`, never visits: a row regressed, deleted or retitled on a branch. A merge commit
    on the branch (origin/main brought in) is judged too, against both its parents, so a regression
    made while resolving it is not hidden in the one commit the per-commit walk skips."""
    rel = dyadlib.instance_rel(root) or os.environ.get("DYAD_INSTANCE", "agent-corpus")
    fails = []
    for sha in dyadlib.range_commits(root, base, head) or []:
        fails += check_commit(sha, root, rel, base)
    for sha in dyadlib.range_commits(root, base, head, merges=True) or []:
        fails += check_merge(sha, root, rel)
    return fails

def check_merge(sha: str, cwd, instance: str) -> list[str]:
    """Each row file of a merge commit against each parent: present in a parent means present here,
    id and title unchanged, state equal or a legal transition (Rule-16)."""
    label, prefix, fails = sha[:9], f"{instance}/d-work/rows/", []
    parents = git("rev-list", "--parents", "-n", "1", sha, cwd=cwd).split()[1:]
    for par in parents:
        for st, path in (l.split("\t", 1) for l in git("diff", "--no-renames", "--name-status", par, sha, "--", prefix, cwd=cwd).splitlines() if "\t" in l):
            if st.startswith("D"):
                fails.append(f"FAIL [main-fence]: merge {label} drops row file {path} that parent {par[:9]} has"); continue
            if not st.startswith("M"):
                continue
            try:
                before = dyadlib.parse_row_file(git("show", f"{par}:{path}", cwd=cwd))
                after = dyadlib.parse_row_file(git("show", f"{sha}:{path}", cwd=cwd))
            except ValueError:
                continue
            if before.id != after.id or before.title != after.title:
                fails.append(f"FAIL [main-fence]: merge {label} changes id or title of row file {path}")
            elif before.state != after.state and not dyadlib.allowed(before.state, after.state):
                fails.append(f"FAIL [main-fence]: merge {label} row file {path} state regresses {before.state}\u2192{after.state} against parent {par[:9]}")
            elif before.mode != after.mode:   # #290: a mode rewritten while resolving a merge is the same hole #191 closed for state
                fails.append(f"FAIL [main-fence]: merge {label} changes mode of row file {path} {before.mode}\u2192{after.mode} against parent {par[:9]}")
            # #202: the Done order is a property of the row edit, not of which commit carries it — a merge
            # resolution is where the per-commit walk never looks (the hole #191 closed for state).
            fails += done_order_problems(path, before, after, f"merge {label}")
            fails += landing_problems(path, before, after, f"merge {label}", sha, cwd, par)
    return fails

def check_id_collisions(root: Path, base: str, head: str) -> list[str]:
    """On a branch: a row file this range adds or modifies must not name an id that already
    exists at `base` under a *different* title — the signature of two sessions racing the
    allocator (d-work #32 F2). Silent otherwise: this is not the append-only fence, which only
    ever runs on `main`; a malformed row file is reported separately by `check_package`, so a
    parse failure here is skipped rather than crashing this guard."""
    instance = os.environ.get("DYAD_INSTANCE", "agent-corpus")
    prefix = f"{instance}/d-work/rows/"
    try:
        paths = git("diff", "--no-renames", "--name-only", f"{base}..{head}", "--", prefix, cwd=root).split()
    except subprocess.CalledProcessError:
        return []
    fails = []
    for path in paths:
        stem = Path(path).stem
        if not stem.isdigit():
            continue
        try:
            head_row = dyadlib.parse_row_file(git("show", f"{head}:{path}", cwd=root, stderr=subprocess.DEVNULL))
        except (subprocess.CalledProcessError, ValueError):
            continue
        try:
            # a brand-new row at head legitimately has no base:path — git's own "not in <sha>"
            # is expected here, not an error worth printing
            base_row = dyadlib.parse_row_file(git("show", f"{base}:{path}", cwd=root, stderr=subprocess.DEVNULL))
        except (subprocess.CalledProcessError, ValueError):
            continue
        if base_row.id == head_row.id and base_row.title != head_row.title:
            fails.append(f"FAIL [row-id]: {path} id {base_row.id} already names {base_row.title!r} "
                         f"at the base — a concurrent session likely allocated the same id "
                         f"for different work ({head_row.title!r})")
    return fails

# ---- entity card (the entities projector reads it; crafts/sysarch/templates/entity-card.md)
def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    rows = dyadlib.read_rows(root) if dyadlib.rows_dir(root).is_dir() else []
    ex = max(rows, key=lambda r: r.id) if rows else None
    trans = "; ".join(f"{a} → {', '.join(sorted(b)) or '∅'}" for a, b in sorted(dyadlib.TRANSITIONS.items()))
    types = {"id": "int", "title": "text", "opened": "date", "state": "enum", "disposed": "text", "refs": "text"}
    allowed = {"id": "unique, allocated by `package.py dwork new`", "opened": "YYYY-MM-DD",
               "state": f"{' | '.join(sorted(dyadlib.STATES))}; new rows: {' | '.join(sorted(dyadlib.NEW_STATES))}",
               "disposed": "`<date> <Y|N> <plan|done|merge #n|reason>` entries joined by `;` (Rule-3)", "refs": "`#<id>`, `parent #<id>`, `children #a–#b`, `PR #n` (Rule-3)"}
    rel = dyadlib.rows_dir(root); rel = rel.relative_to(root) if rel.is_relative_to(root) else rel
    # #290: the card lists FIELDS only. `mode` (dyadlib.OPTIONAL_FIELDS) is named in the note instead, because
    # the entities projector's contract reads field names out of parser constants it knows and the sysarch
    # craft's tests pin this card to `dyadlib.FIELDS`; giving OPTIONAL_FIELDS a card is that craft's own d-work.
    return {"store": f"{rel}/<id>.md", "parser": "`dyadlib.parse_row_file` / `read_rows`", "observed": len(rows),
            "note": f"append-only; id, title and mode immutable; optional `mode` ({' | '.join(sorted(dyadlib.MODES))}, "
                    f"written only when not `{dyadlib.DEFAULT_MODE}`); transitions (`dyadlib.TRANSITIONS`): {trans}",
            "fields": [(f, types[f], allowed.get(f, ""), True, str(getattr(ex, f)) if ex else "", "dyadlib.FIELDS") for f in FIELDS]}

def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    root = dyadlib.repo_root()
    ev = dyadlib.find_guard(dyadlib.HOST_CORPUS, "events")   # the logical host corpus, whatever zone holds it (#175)
    fails = check_range(argv[0], argv[1], cwd=root) + (ev.check_range(argv[0], argv[1], cwd=root) if ev else [])
    for f in fails:
        print(f, file=sys.stderr)
    print("main fence OK" if not fails else "main fence FAILED")
    return 1 if fails else 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1, #203)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
