#!/usr/bin/env python3
"""Provenance-record guard (entity `provenance`, agent corpus; Rule-7 owns the form, Rule-21 places it). Kernel: Python 3.12+.
Every `<instance>/d-work/provenance/<id>.md` opens `# Provenance #<id>` with the id of its file
name and holds entries `## <n> <kind> <YYYY-MM-DD>[ <note>]`, numbered from 1 without gaps, `kind`
in KINDS, each followed by a fenced block carrying the Operator's text as data (Rule-7 property 1).
The `disposition` entries count equal to the row's `disposed` entries (property 5), no credential
shape reaches a body (property 2), and no `*.jsonl` is tracked under the store. A row at or above
SINCE_ID without a record warns rather than fails: a concurrent session (Rule-16) opens rows
without having loaded Rule-7, and a red `main` is the wrong way to teach it. Whether an entry is a
faithful transcription is inference (Rule-7 Enforcement).
  provenance.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("provenance.py: Python 3.12+ required")
import re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "provenance", "agent", False
NAME, OWNER = "provenance record (entry)", "Rule-7"
FIELDS = ("n", "kind", "date", "note", "text")
KINDS = ("prompt", "disposition")
SINCE_ID = 164                  # the d-work that landed Rule-7; earlier rows may carry a record, none must

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

def check_record(path: Path, text: str | None = None, row: dyadlib.Row | None = None) -> list[str]:
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
        if want != got:
            msgs.append(f"{path.name}: {got} disposition entr{'y' if got == 1 else 'ies'}, row #{row.id} records {want} (Rule-7 property 5)")
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

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    rows = {r.id: r for r in dyadlib.read_rows(root)}
    msgs, seen = [], set()
    for p in records(root):
        rid = int(p.stem); seen.add(rid)
        if rid not in rows:
            msgs.append(f"{p.name}: no row #{rid} in the ledger")
        msgs += check_record(p, row=rows.get(rid))
    for rid in sorted(r for r in rows if r >= SINCE_ID and r not in seen):
        msgs.append(f"warning: row #{rid} (>= SINCE_ID {SINCE_ID}) has no provenance record (Rule-7 property 1)")
    for f in tracked_jsonl(root):
        msgs.append(f"{f}: a raw transcript is tracked under the d-work store (Rule-7 property 2)")
    return msgs

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
