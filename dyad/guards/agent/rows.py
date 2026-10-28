#!/usr/bin/env python3
"""Row-file guard (entity `row`, agent corpus; Rule-3 owns the content and the fence, Rule-16 the
store; placed per Rule-11 property 1). Kernel: Python 3.12+.

Package check (`check_package`): every `<instance>/d-work/rows/<id>.md` parses (dyadlib.FIELDS), its
id equals its file name, its state is one of dyadlib.STATES, no id is duplicated, and no `refs` holds `[`
or `]` (#439: the shape of a Python list, which the close path wrote into 28 rows; a comma is not judged
here, since 24 rows written before the fence hold comma-separated ids or prose).

Transaction check (`check_transaction`, TRANSACTION; the main fence, referenced by Rule-2): a commit
pushed directly to main (non-merge, first-parent) may touch only <instance>/d-work/ — or only
<host>/runbooks/events/, an events-only commit (`dyadlib.events_only`, d-work #438): monitoring's record,
clerical like the ledger, carrying no row for this fence to judge — and, for row
files, may only add a file or change state/disposed/refs: never delete a row file or change its id
or title (C3). A `refs` value a commit adds or changes is space-separated tokens (`7 parent #3 PR #9`) and
holds none of `[ ] ' " ,` (`refs_shape_problems`, #439); a row whose refs the commit leaves as it was is
never re-judged, so the legacy comma rows pass until their refs is edited. A state change must be a transition in dyadlib.TRANSITIONS (Rule-16: state never
regresses; d-work #112) and a new row file must start in dyadlib.NEW_STATES. The rendered
LEDGER.md is untracked (d-work #111) and is not diffed. This full fence applies on `main` only;
on a branch `check_transaction` instead runs `check_id_collisions` (d-work #32 F2): a row id this
range adds or modifies must not already exist at the base under a *different* title — the
signature of two sessions racing the allocator — leaving the append-only rules themselves to this
same fence once the branch reaches `main`, and the plan gate to `prs.py`. That hand-off held only for
a branch replayed onto `main`: a PR merge (`--no-ff`) lands commits this fence, walking
`--first-parent`, never visits. So a ledger-only branch, which the plan gate now skips (#191), is
fenced here, each of its own commits as `main` would fence it (`check_ledger_branch`); so is an
events-only branch, which the gate skips too (#438). A commit touching both stores is neither and fails. On both, every `disposed`
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
Under the preference `dwork-trace: always`, read at the commit's own tree, a commit that adds a `Y done` entry to row
N — not a mandate close, whose note holds `mandate #` (Rule-7 property 4) — must hold `<instance>/d-work/traces/N.md`
in that same tree, carried by the commit or already on the base (`trace_problems`, d-work #465): the Done record
commit carries the trace (Rule-3 Completion); a merge resolution is judged against each parent.
Under `merge-disposition: with-done`, read at the commit's own tree the same way, a `Y merge` entry a commit adds
warns — a `warning:` line, never a failure (`merge_disposition_warnings`, d-work #519): the Done-`Y` ratifies the
merge, so a separate merge question was asked against the preference (#486); a note naming a preference-zone or
charter PR (`per #427`, `preference`, `charter`, `MANDATES`) is exempt; a merge commit warns only on an entry no
parent holds. The transaction runners print `warning:` lines as `warn` and keep the push.
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
REFS_REFUSED = "[]'\","   # #439: no refs a commit writes holds these; `dwork` refuses them at -r (package.py)
REFS_BRACKETS = "[]"      # #439: the store-wide clause; zero rows hold one once the 28 are restored (0c8b260)
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
        if any(c in r.refs for c in REFS_BRACKETS):
            fails.append(f"{rel}: refs {r.refs!r} holds a bracket, the shape of a list written into the row, not "
                         f"space-separated references (#439)")
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

# ---- the Done record carries its trace (d-work #465)
TRACE_KEY, TRACE_ALWAYS = "dwork-trace", "always"

def preference_at(sha: str, key: str, cwd) -> str | None:
    """The value of one preference row in the commit's own tree — `dyadlib.preference`'s reading of the table,
    over `git show <sha>:preferences-corpus/PREFERENCES.md` — or None when the file or the row is absent there."""
    try:
        text = git("show", f"{sha}:{dyadlib.PREFERENCES_REL}", cwd=cwd, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None
    for r in dyadlib.table_rows(text):   # an escaped `\\|` stays inside its cell (#171)
        if len(r) >= 2 and dyadlib.plain(r[0]).strip() == key:
            return dyadlib.plain(r[1]).strip()
    return None

def trace_path(path: str, rid) -> str:
    """`<instance>/d-work/traces/<id>.md` beside the row file's own store."""
    return f"{Path(path).parent.parent.as_posix()}/traces/{rid}.md"

def trace_problems(path: str, before, after, label: str, sha: str, cwd) -> list[str]:
    """Rule-3 Completion: under `dwork-trace: always` the trace is written before the Done **record** commit,
    which carries it. Each `Y done` entry this commit adds to the row (`before` None: a new row) — a mandate close
    excepted, whose note holds `mandate #`, since an accreted row's Done rides the mandate's and the mandate's own
    trace covers the set (Rule-3 Scope, Rule-7 property 4) — needs `<instance>/d-work/traces/<id>.md` in this
    commit's own tree: carried by it, or already on the base. The preference is read at that tree too, so a
    commit is judged under the value it was written under; `on-demand`, or no preference file, disables the
    clause. Only added entries are judged, so no row's history is re-read: six Done records (#455–#460) carried
    none because a refused `dwork trace` went unseen, and nothing refused the record (#465)."""
    added = [e for e in added_entries(before.disposed if before is not None else "", after.disposed)
             if DONE_Y.match(e) and "mandate #" not in e]
    if not added or preference_at(sha, TRACE_KEY, cwd) != TRACE_ALWAYS:
        return []
    tp = trace_path(path, after.id)
    try:
        git("cat-file", "-e", f"{sha}:{tp}", cwd=cwd, stderr=subprocess.DEVNULL)
        return []
    except subprocess.CalledProcessError:
        pass
    return [f"FAIL [main-fence]: {label} records {e!r} on row file {path} without its trace {tp} in the same "
            f"tree (Rule-3 Completion, `dwork-trace: always`: the Done record commit carries the trace — write it "
            f"with `dyad dwork trace {after.id} --out`, then carry it in the same commit: `dyad dwork batch` with a "
            f"`land {tp}` line before the `state` line; #465)" for e in added]

# ---- a merge question asked against `merge-disposition: with-done` (d-work #519, the audit's F2)
MERGE_KEY, MERGE_WITH_DONE = "merge-disposition", "with-done"
MERGE_Y = re.compile(r"\d{4}-\d{2}-\d{2} Y merge\b")    # a *separate* merge disposition: `<date> Y merge PR #n at <head> (...)`
MERGE_EXEMPT = re.compile(r"\bper #427\b|\bpreferences?\b|\bcharter\b|MANDATES", re.IGNORECASE)

def merge_disposition_warnings(path: str, old: set[str], after, label: str, sha: str, cwd) -> list[str]:
    """Rule-2 Binding: under `merge-disposition: with-done` a merge is ratified by the Done-`Y` that names it, so a
    separate `Y merge` entry records a merge question asked against the Operator's own preference ("i don't
    disposition merge, only d-work", #486). Each `Y merge` entry the row holds and `old` does not — the entries
    already there are never re-judged — warns, read under the value at the commit's own tree; `separate`, or no
    preference file, disables the clause. Exempt: a merge the Operator disposes as its own question because the PR
    is the Operator's own — a preference-zone PR or a charter (`MANDATES.md`) PR (#427) — recognized by the entry's
    note, which names it: `per #427`, `preference`/`preferences`, `charter` or `MANDATES` (case-insensitive; the
    2026-10-25 entries of #432, #433, #436 and #441 read "its own question per #427"). A warning, never a failure:
    the `Y` was given and the record is true; what it shows is an Operator asked a question the preference says
    not to ask."""
    added = [e for e in entries(after.disposed) if e not in old and MERGE_Y.match(e) and not MERGE_EXEMPT.search(e)]
    if not added or preference_at(sha, MERGE_KEY, cwd) != MERGE_WITH_DONE:
        return []
    return [f"warning: {label} records {e!r} on row file {path} (row #{after.id}) under `merge-disposition: with-done`: "
            f"the Done-`Y` that names the PR ratifies its merge, so no separate merge question is asked (Rule-2 "
            f"Binding; #486) — a preference-zone or charter PR, asked as its own question, names that in the note "
            f"(`its own question per #427`); #519" for e in added]

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

# ---- the shape of refs (d-work #439)
# ---- the head a Done-`Y` was given on (d-work #495, F1 of #487)
PR_AT = re.compile(r"(?:\bPR #(\d+) )?\bat ([0-9a-f]{7,40})\b")   # `merges PR #a at <head-a>, PR #b at <head-b>`

def named_heads(rows: list) -> list[tuple[int, str | None, str, str]]:
    """Every head an operative `Y done` names on a row not yet terminal: (row id, PR number or None, head as
    written, the entry). The operative entry only — the last, as `landing_problems` reads it — since a later
    `Y` given on a new head supersedes the earlier (Rule-2, Binding). Pure: what the pre-push gate
    (`package.py done_head_refusals`) matches a pushed ref's old sha against, by prefix."""
    out = []
    for r in rows:
        if r.state in dyadlib.TERMINAL_STATES:
            continue
        done = [e for e in entries(r.disposed) if DONE_Y.search(e)]
        for e in done[-1:]:
            out += [(r.id, pr or None, s, e) for pr, s in PR_AT.findall(e)]
    return out

def heads_naming(sha: str, rows: list) -> list[tuple[int, str | None, str, str]]:
    """The `named_heads` entries that name `sha` (full 40-hex): an entry's head may be written short (7+ hex),
    so it names `sha` when `sha` starts with it."""
    return [h for h in named_heads(rows) if sha.startswith(h[2])]

def refs_shape_problems(path: str, before, after, label: str) -> list[str]:
    """A `refs` value a commit adds (`before` None: a new row) or changes is space-separated tokens — `7`,
    `#7`, `parent #3`, `PR #9`, `workstation-252` — and holds none of `REFS_REFUSED`. The close path of
    `dwork state <id> done` wrote `['origin/main', 'main', 'HEAD']` over 28 rows' refs between 2026-10-15 and
    2026-10-25 and nothing read the value's shape (#439). A row whose refs this commit leaves unchanged is
    never re-judged: 24 rows written before this clause hold commas or prose (`109, 110`), and they fail only
    when their refs is edited, which must then rewrite it as tokens."""
    if before is not None and before.refs == after.refs:
        return []
    bad = sorted({c for c in after.refs if c in REFS_REFUSED})
    if not bad:
        return []
    return [f"FAIL [main-fence]: {label} writes refs {after.refs!r} to row file {path}, holding {' '.join(bad)}: "
            f"refs is space-separated tokens, e.g. '7 parent #3 PR #9' (#439)"]

# ---- the row's mode (the countersign model's term, `dyad/playbooks/countersign-model.md`; d-work #290)
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
    events = dyadlib.events_rel(Path(cwd))
    if paths and events and all(p.startswith(f"{events}/") for p in paths):
        return []   # #438: an events-only commit is clerical and holds no row; append-only is `sysadmin/events`'
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
            fails += refs_shape_problems(path, before, after, label)
            fails += disposed_problems(path, before.disposed, after.disposed, label)
            fails += done_order_problems(path, before, after, label)
            fails += landing_problems(path, before, after, label, sha, cwd, base)
            fails += trace_problems(path, before, after, label, sha, cwd)       # #465: the record carries its trace
            fails += merge_disposition_warnings(path, set(entries(before.disposed)), after, label, sha, cwd)   # #519: warns
        elif st.startswith("A"):
            try:
                new = dyadlib.parse_row_file(git("show", f"{sha}:{path}", cwd=cwd))
            except ValueError:
                fails.append(f"FAIL [main-fence]: {label} adds row file {path} that does not parse"); continue
            if new.state not in dyadlib.NEW_STATES:
                fails.append(f"FAIL [main-fence]: {label} adds row file {path} in state {new.state} (not one of {' '.join(sorted(dyadlib.NEW_STATES))})")
            fails += born_implicit_problems(path, new, label)
            fails += refs_shape_problems(path, None, new, label)
            fails += disposed_problems(path, "", new.disposed, label)
            fails += trace_problems(path, None, new, label, sha, cwd)
            fails += merge_disposition_warnings(path, set(), new, label, sha, cwd)
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
        # a ledger-only or events-only branch gets the fence per commit, which already judges each added `disposed` entry
        clerical = dyadlib.ledger_only(root, base, head) or dyadlib.events_only(root, base, head)
        whole = check_ledger_branch if clerical else check_disposed
        return check_id_collisions(root, base, head) + whole(root, base, head)
    return check_range(base, head, cwd=root)

def check_ledger_branch(root: Path, base: str, head: str) -> list[str]:
    """A ledger-only branch — or an events-only one (#438) — skips the plan gate (Rule-3, #191) because `main` would admit the same
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
    touched: set[str] = set()        # #519: row files the merge differs on from some parent
    for par in parents:
        for st, path in (l.split("\t", 1) for l in git("diff", "--no-renames", "--name-status", par, sha, "--", prefix, cwd=cwd).splitlines() if "\t" in l):
            if st.startswith("D"):
                fails.append(f"FAIL [main-fence]: merge {label} drops row file {path} that parent {par[:9]} has"); continue
            touched.add(path)
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
            fails += refs_shape_problems(path, before, after, f"merge {label}")   # #439: a refs rewritten while resolving
            fails += trace_problems(path, before, after, f"merge {label}", sha, cwd)   # #465: a Done record resolved in without its trace
    # #519: a `Y merge` entry the resolution itself adds — held by no parent — warns once; one that arrived from
    # either side was judged by the commit that added it, and is never re-judged here.
    for path in sorted(touched):
        old: set[str] = set()
        try:
            after = dyadlib.parse_row_file(git("show", f"{sha}:{path}", cwd=cwd, stderr=subprocess.DEVNULL))
            for par in parents:
                try:
                    old |= set(entries(dyadlib.parse_row_file(git("show", f"{par}:{path}", cwd=cwd, stderr=subprocess.DEVNULL)).disposed))
                except subprocess.CalledProcessError:
                    pass   # absent from this parent: it holds none of the entries
        except (subprocess.CalledProcessError, ValueError):
            continue
        fails += merge_disposition_warnings(path, old, after, f"merge {label}", sha, cwd)
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
    msgs = check_range(argv[0], argv[1], cwd=root) + (ev.check_range(argv[0], argv[1], cwd=root) if ev else [])
    for f in msgs:
        print(f, file=sys.stderr)
    fails = [f for f in msgs if not f.startswith("warning:")]   # #519: a warning never fails the fence
    print("main fence OK" if not fails else "main fence FAILED")
    return 1 if fails else 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1, #203)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
