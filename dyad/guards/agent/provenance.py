#!/usr/bin/env python3
"""Provenance-record guard (entity `provenance`, agent corpus; Rule-7 owns the form, Rule-21 places it). Kernel: Python 3.12+.
Every `<instance>/d-work/provenance/<id>.md` opens `# Provenance #<id>` with the id of its file
name and holds entries `## <n> <kind> <YYYY-MM-DD>[ <note>]`, numbered from 1 without gaps, `kind`
in KINDS, each followed by a fenced block carrying the Operator's text as data (Rule-7 property 1).
The `disposition` entries count equal to the row's `disposed` entries (property 5), no credential
shape reaches a body (property 2), and no `*.jsonl` is tracked under the store.

Two checks, split by what a failure costs (d-work #191):
- Transaction (`check_transaction`, TRANSACTION, `commits` mode): each non-merge commit being pushed
  (merge base..head), against its parent, as property 3 says — an entry is written in the commit of
  the event it records. A row the commit adds brings at least one new entry in its record — a
  `disposition` when it is born `backlog` (Rule-3: backlog is opened by a disposition); a row going
  backlog -> open brings a `prompt` (Rule-3: the Operator prompts for it); a row whose `disposed`
  gains k entries gains k `disposition` entries; and a record only grows — its earlier entries stay,
  word for word, and it is never deleted. This fails only the push that creates the gap, on the
  session that wrote it.
- Package (`check_package`): a row with no record fails, unless the instance names it in
  `<instance>/provenance_legacy.local.txt` (LEGACY; `<id> <n> <reason>` per line: the rows that
  predate this enforcement, n the dispositions each held whose words were never written and cannot
  be, property 3). A listed row's record holds exactly n fewer disposition entries than the row; a
  listed row with no record passes only while its `disposed` holds n. A gap that reaches the tree
  around the hook therefore fails here in every session until it is recorded or listed: the alarm
  for that bypass, accepted. The list is instance data, never the core's (Rule-11 property 1; the
  `SINCE_ID` cut-off it replaces named an earlier ledger's id). An instance with no list yet — a
  system installing this version — gets one warning per unrecorded row until it writes one.
Whether an entry is a faithful transcription is inference (Rule-7 Enforcement).
  provenance.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("provenance.py: Python 3.12+ required")
import re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "provenance", "agent", True
TRANSACTION_MODE = "commits"   # #166's vocabulary: each commit of the range, as property 3 binds a commit
NAME, OWNER = "provenance record (entry)", "Rule-7"
FIELDS = ("n", "kind", "date", "note", "text")
KINDS = ("prompt", "disposition")
LEGACY = "provenance_legacy.local.txt"   # <instance>/: rows that predate enforcement (#191), named like dyadlib.RULES_LOCAL
_LEGACY_LINE = re.compile(r"^(\d+)\s+(\d+)\s+(\S.*)$")
_LEGACY_LOOKALIKE = re.compile(r"^#\s*\d+\b")

_TITLE = re.compile(r"^# Provenance #(\d+)\b")
_ENTRY = re.compile(r"^## (\d+) (\S+) (\d{4}-\d{2}-\d{2})(?:\s+(.*))?$")
_FENCE = re.compile(r"^(`{3,}|~{3,})")
# Rule-7 property 2 residue: shapes that are a credential and nothing else. A bare 40-hex is a
# commit sha as often as a token, so it warns instead (WARN_SHAPES).
FAIL_SHAPES = [("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}")),
               ("GitHub PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}")),
               ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
               ("Authorization header", re.compile(r"(?i)authorization:\s*(bearer|token)\s+\S+"))]
WARN_SHAPES = [("40-hex string (commit sha or token)", re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{40}(?![0-9a-fA-F])"))]
INVARIANTS = [("kind-field-in-fields", lambda: "kind" in FIELDS),
              ("legacy-list-is-instance-local", lambda: LEGACY.endswith(".local.txt") and "/" not in LEGACY),
              ("transaction-mode-is-commits", lambda: TRANSACTION_MODE == "commits"),
              ("kinds-are-two", lambda: set(KINDS) == {"prompt", "disposition"}),
              ("shape-lists-are-compiled-patterns", lambda: all(isinstance(p, re.Pattern) for _, p in FAIL_SHAPES + WARN_SHAPES))]   # crafts/syseng/rules/invariants.md

def store(root: Path | None = None) -> Path:
    return dyadlib.instance(root) / "d-work" / "provenance"

def records(root: Path | None = None) -> list[Path]:
    d = store(root)
    return sorted((p for p in d.glob("*.md") if p.stem.isdigit()), key=lambda p: int(p.stem)) if d.is_dir() else []

def parse(text: str) -> list[dict[str, str]]:
    """The entries of one record, in file order: n, kind, date, note, text (the fenced body)."""
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        m = _ENTRY.match(lines[i])
        if not m:
            i += 1; continue
        n, kind, date, note = m.group(1), m.group(2), m.group(3), (m.group(4) or "").strip()
        body, i = [], i + 1
        while i < len(lines) and not _FENCE.match(lines[i]) and not lines[i].startswith("## "):
            i += 1
        if i < len(lines) and (f := _FENCE.match(lines[i])):
            close, i = f.group(1)[0] * 3, i + 1
            while i < len(lines) and not lines[i].startswith(close):
                body.append(lines[i]); i += 1
            i += 1 if i < len(lines) else 0
            out.append({"n": n, "kind": kind, "date": date, "note": note, "text": "\n".join(body)})
        else:
            out.append({"n": n, "kind": kind, "date": date, "note": note, "text": ""})
    return out

def dispositions(disposed: str) -> list[str]:
    """The row's `disposed` cell as its ordered entries (Rule-3)."""
    return [s.strip() for s in disposed.split(";") if s.strip()]

def check_record(path: Path, text: str | None = None, row: dyadlib.Row | None = None, lost: int = 0) -> list[str]:
    """One record's shape, and property 5 against its row: its disposition entries equal the row's
    `disposed` entries less `lost`, the dispositions a legacy row (LEGACY) held before enforcement
    whose words were never written (#191)."""
    text = path.read_text(errors="ignore") if text is None else text
    msgs, first = [], text.splitlines()[0] if text else ""
    m = _TITLE.match(first)
    if not m:
        msgs.append(f"{path.name}: first line is not `# Provenance #<id>`")
    elif m.group(1) != path.stem:
        msgs.append(f"{path.name}: title id #{m.group(1)} differs from the file name")
    entries = parse(text)
    if not entries:
        msgs.append(f"{path.name}: no entries (`## <n> <kind> <YYYY-MM-DD>`)")
    for i, e in enumerate(entries, 1):
        if int(e["n"]) != i:
            msgs.append(f"{path.name}: entry {i} is numbered {e['n']} (number from 1, no gaps)")
        if e["kind"] not in KINDS:
            msgs.append(f"{path.name}: entry {e['n']} kind {e['kind']!r} (one of {', '.join(KINDS)})")
        if not e["text"].strip():
            msgs.append(f"{path.name}: entry {e['n']} has no fenced body (Rule-7 property 1)")
        for what, pat in FAIL_SHAPES:
            if pat.search(e["text"]):
                msgs.append(f"{path.name}: entry {e['n']} carries a {what} (Rule-7 property 2)")
        for what, pat in WARN_SHAPES:
            if pat.search(e["text"]):
                msgs.append(f"warning: {path.name}: entry {e['n']} carries a {what}")
    if row is not None:
        want, got = len(dispositions(row.disposed)), sum(e["kind"] == "disposition" for e in entries)
        if got != want - lost:
            msgs.append(f"{path.name}: {got} disposition entr{'y' if got == 1 else 'ies'}, row #{row.id} records {want}"
                        f"{f' of which {lost} predate enforcement ({LEGACY})' if lost else ''} (Rule-7 property 5)")
    return msgs

def tracked_jsonl(root: Path) -> list[str]:
    """Rule-7 property 2: a raw transcript must never be tracked under the d-work store."""
    rel = (dyadlib.instance(root) / "d-work").relative_to(root)
    try:
        out = subprocess.run(["git", "ls-files", "--", f"{rel}/*.jsonl"], cwd=root, text=True,
                             capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    return [l for l in out.stdout.splitlines() if l.strip()]

def legacy_path(root: Path | None = None) -> Path:
    return dyadlib.instance(root) / LEGACY

def legacy(root: Path | None = None) -> tuple[dict[int, tuple[int, str]] | None, list[str]]:
    """The instance's legacy list: {id: (n, reason)}, or None when the file is absent; plus line
    problems, and a warning for a comment that looks like a listed id (`#38 …`: the ledger's citation
    style, silently a comment here)."""
    p = legacy_path(root)
    if not p.is_file():
        return None, []
    ids, problems = {}, []
    for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if _LEGACY_LOOKALIKE.match(line):
                problems.append(f"warning: {LEGACY}:{n}: a comment that looks like a row id; a listed row is `<id> <n> <reason>`, no `#`")
            continue
        m = _LEGACY_LINE.match(line)
        if not m:
            problems.append(f"{LEGACY}:{n}: not `<id> <n> <reason>`"); continue
        rid = int(m.group(1))
        if rid in ids:
            problems.append(f"{LEGACY}:{n}: row #{rid} named twice")
        ids[rid] = (int(m.group(2)), m.group(3))
    return ids, problems

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    rows = {r.id: r for r in dyadlib.read_rows(root)}
    listed, problems = legacy(root)
    msgs, seen = list(problems), set()
    for p in records(root):
        rid = int(p.stem); seen.add(rid)
        if rid not in rows:
            msgs.append(f"{p.name}: no row #{rid} in the ledger")
        msgs += check_record(p, row=rows.get(rid), lost=(listed or {}).get(rid, (0, ""))[0])
    missing = sorted(r for r in rows if r not in seen)
    if listed is None:
        for rid in missing:
            msgs.append(f"warning: row #{rid} has no provenance record, and this instance has no {LEGACY} "
                        f"naming the rows that predate enforcement (Rule-7 property 1, #191)")
    else:
        for rid in missing:
            want = len(dispositions(rows[rid].disposed))
            if rid not in listed:
                msgs.append(f"row #{rid} has no provenance record (Rule-7 property 1). A new row is written with its "
                            f"record (`dwork new --prompt-file`, `dwork new --backlog -d … --said-file`); on a row already "
                            f"here the words are lost unless the session that heard them writes them now — otherwise "
                            f"name the row in {LEGACY}, in a reviewed PR")
            elif want != listed[rid][0]:
                msgs.append(f"row #{rid} records {want} disposition(s), {LEGACY} lists {listed[rid][0]} whose words predate "
                            f"enforcement, and no record holds the rest (Rule-7 property 5)")
        for rid, (lost, _) in sorted(listed.items()):
            if rid not in rows:
                msgs.append(f"{LEGACY}: row #{rid} is not in the ledger")
            elif lost > len(dispositions(rows[rid].disposed)):
                msgs.append(f"{LEGACY}: row #{rid} lists {lost} lost disposition(s) but records only {len(dispositions(rows[rid].disposed))}")
    for f in tracked_jsonl(root):
        msgs.append(f"{f}: a raw transcript is tracked under the d-work store (Rule-7 property 2)")
    return msgs

# ---- transaction check (#191): the row and its record move together, commit by commit
def _git(root: Path, *a: str) -> str | None:
    try:
        return subprocess.check_output(["git", *a], cwd=root, text=True, stderr=subprocess.DEVNULL, env=dyadlib.git_env())
    except subprocess.CalledProcessError:
        return None

def _show(root: Path, ref: str, path: str) -> str | None:
    return _git(root, "show", f"{ref}:{path}")

def _row(text: str | None) -> dyadlib.Row | None:
    try:
        return dyadlib.parse_row_file(text) if text is not None else None
    except ValueError:
        return None

def _count(entries: list[dict[str, str]], kind: str) -> int:
    return sum(e["kind"] == kind for e in entries)

def _canonical_id(path: str) -> int | None:
    stem = Path(path).stem
    return int(stem) if path.endswith(".md") and stem.isdigit() and stem == str(int(stem)) else None

RECOVER = "fix it before the push: drop the unpushed commits (`git reset --keep origin/main`) and rewrite them with `dwork`"

def _grows(before: list[dict[str, str]], after: list[dict[str, str]]) -> bool:
    """A record only grows: `before`'s entries stay, word for word, at the head of `after`."""
    key = lambda e: (e["kind"], e["date"], e["text"])
    return [key(e) for e in after[:len(before)]] == [key(e) for e in before]

def check_commit(root: Path, sha: str, rows_rel: str, rec_rel: str) -> list[str]:
    """One non-merge commit against its first parent (nothing, for a root commit)."""
    parent = (_git(root, "rev-parse", "--verify", "-q", f"{sha}^") or "").strip() or None
    paths = [p for p in (dyadlib.commit_paths(root, sha) or []) if p.startswith((f"{rows_rel}/", f"{rec_rel}/"))]
    ids = sorted({i for p in paths if (i := _canonical_id(p)) is not None})
    label, fails = sha[:9], []
    show = lambda ref, path: _show(root, ref, path) if ref else None
    for rid in ids:
        row_path, rec_path = f"{rows_rel}/{rid}.md", f"{rec_rel}/{rid}.md"
        rec_before, rec_after = show(parent, rec_path), show(sha, rec_path)
        eb, ea = parse(rec_before or ""), parse(rec_after or "")
        if rec_before is not None and rec_after is None:
            fails.append(f"FAIL [provenance]: {label} deletes the record of row #{rid} (Rule-7 property 3: the words stay)"); continue
        if not _grows(eb, ea):
            fails.append(f"FAIL [provenance]: {label} rewrites or removes entries of row #{rid}'s record; a record only grows "
                         f"(Rule-7 property 3) — {RECOVER}")
            continue
        after = _row(show(sha, row_path))
        if after is None:
            continue        # a row deleted or unparseable at this commit is the row guard's report
        before = _row(show(parent, row_path))   # absent or unparseable before: this commit is its birth as a row
        added = [e["kind"] for e in ea[len(eb):]]
        if before is None:
            if not added:
                fails.append(f"FAIL [provenance]: {label} adds row #{rid} and its record gains no entry: the words that opened it "
                             f"are written with it (Rule-7 property 3; `dwork new --prompt-file`, `dwork new --backlog -d … --said-file`)")
                continue
            if after.state == "backlog" and "disposition" not in added:
                fails.append(f"FAIL [provenance]: {label} adds row #{rid} as backlog, which only a disposition opens (Rule-3), "
                             f"and its record gains no disposition entry")
        elif before.state == "backlog" and after.state == "open" and "prompt" not in added:
            fails.append(f"FAIL [provenance]: {label} opens backlog row #{rid}, which the Operator's prompt does (Rule-3), "
                         f"and its record gains no prompt entry (`dwork state {rid} open --prompt-file`)")
        k = len(dispositions(after.disposed)) - len(dispositions(before.disposed if before else ""))
        dk = added.count("disposition")
        if k != dk:
            fails.append(f"FAIL [provenance]: {label} row #{rid} gains {k} disposed entr{'y' if k == 1 else 'ies'} and its record "
                         f"gains {dk} disposition entr{'y' if dk == 1 else 'ies'} (Rule-7 property 5, per commit) — {RECOVER}")
    return fails

def check_merge(root: Path, sha: str, rec_rel: str) -> list[str]:
    """A merge commit's records against each parent: each parent's entries stay at the head of the
    result, so words rewritten while resolving a merge are not hidden in the one commit the per-commit
    walk skips. Only growth is judged here; the per-commit rules judge each side's own commits."""
    parents = (_git(root, "rev-list", "--parents", "-n", "1", sha) or "").split()[1:]
    fails = []
    for par in parents:
        out = _git(root, "diff", "--no-renames", "-z", "--name-only", par, sha, "--", rec_rel) or ""
        for rid in sorted({i for p in out.split("\0") if p and (i := _canonical_id(p)) is not None}):
            before, after = _show(root, par, f"{rec_rel}/{rid}.md"), _show(root, sha, f"{rec_rel}/{rid}.md")
            if before is not None and (after is None or not _grows(parse(before), parse(after))):
                fails.append(f"FAIL [provenance]: merge {sha[:9]} rewrites, removes or deletes entries of row #{rid}'s record "
                             f"against parent {par[:9]} (Rule-7 property 3)")
    return fails

def check_transaction(root: Path, base: str, head: str) -> list[str]:
    """Every commit `head` has that `base` lacks (what `main` gained is never this range's): each
    non-merge commit against its parent, each merge commit's records against both parents. An
    instance outside the work tree holds nothing git tracks, so there is nothing to judge."""
    rel = dyadlib.instance_rel(root)
    if rel is None:
        return []
    rows_rel, rec_rel, fails = f"{rel}/d-work/rows", f"{rel}/d-work/provenance", []
    for sha in dyadlib.range_commits(root, base, head) or []:
        fails += check_commit(root, sha, rows_rel, rec_rel)
    for sha in dyadlib.range_commits(root, base, head, merges=True) or []:
        fails += check_merge(root, sha, rec_rel)
    return fails

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    root = root or dyadlib.repo_root()
    recs = records(root)
    return f"{len(recs)} records, {sum(len(parse(p.read_text(errors='ignore'))) for p in recs)} entries"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    recs = records(root)
    ex = next((e for p in recs for e in parse(p.read_text(errors="ignore"))), None)
    rel = str(store(root).relative_to(root)) if store(root).is_relative_to(root) else str(store(root))
    allowed = {"n": "1, 2, 3 … no gaps", "kind": " | ".join(KINDS), "date": "YYYY-MM-DD",
               "note": "free text (a disposition's kind, as the row's `disposed` records it)",
               "text": "the Operator's words, verbatim, inside a fence"}
    return {"store": f"{rel}/<id>.md", "parser": "`provenance.parse` (entry headings and their fenced bodies)",
            "observed": len(recs),
            "note": "one record per d-work id; the Operator's prompts and dispositions only, written clerically as they happen; raw transcripts never enter (Rule-7 property 2)",
            "fields": [(f, "enum" if f == "kind" else "text", allowed.get(f, ""), f != "note",
                        (ex or {}).get(f, ""), "provenance.FIELDS") for f in FIELDS]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        if m.startswith("warning:"):
            print(f"warn [rule-7] {m.removeprefix('warning:').strip()}")
        else:
            print(f"FAIL [rule-7] {m}", file=sys.stderr)
    if not fails:
        print(f"ok   [rule-7] {summary(root)}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
