#!/usr/bin/env python3
"""A play-book's profile (core script; d-work #642; the play-book `dyad/playbooks/playbook-optimize.md` runs it as its
run-book's one read-only step, `profile`). Kernel: Python 3.12+, stdlib.
`dyad playbook profile <name>` reads `dyad/playbooks/<name>.md` (and a craft's `crafts/<craft>/playbooks/<name>.md`
when no core one exists) and prints, in words (whitespace tokens, #626's measure):
- each step: a numbered item (`N. …`) of a section, or a section's own prose, with its words and the `dmc:<id>`s and
  the `dyad …` commands it cites;
- each record it cites: its words and its `dyad:judgedBy` kind;
- the run total: the play-book, its run-book (`dyad/runbooks/<name>.md`, if any) and every record it cites;
- the time side: from the d-work traces (`<instance>/d-work/traces/<id>.md`) of the rows whose plan file names the
  play-book's path, the median inference and mechanical seconds (the trace's Buckets table; mechanical is
  `trace.MECHANICAL`). A trace is per d-work, not per step, so the time is the play-book's, a limit it prints.
Read-only: it writes nothing, and it decides nothing (the classing is the play-book's, `dmc:judgement-complexity`).
  playbook_profile.py <name>      (reached as `dyad playbook profile`)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("playbook_profile.py: Python 3.12+ required")
import json, re, statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

USAGE = "usage: dyad playbook profile <name>"
NAME = re.compile(r"[a-z][a-z0-9-]*")
CITE = re.compile(r"(?<![\w:/-])dmc:([a-z0-9][a-z0-9-]*)")       # as the dmc guard reads a citation (#626)
COMMAND = re.compile(r"`((?:dyad/bin/)?dyad [^`\n]+)`")             # a backticked `dyad …` command
STEP = re.compile(r"^(\d+)\.\s+(.*)$")
BUCKET_ROW = re.compile(r"^\|\s*([a-z/]+)\s*\|\s*(operator|agent)\s*\|\s*(\d+)\s*\|")
LIMIT = "time is per d-work (a trace is the d-work's window, never one step's), so it is the play-book's, not a step's"

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("cite-reads-a-citation-not-a-urn", lambda: CITE.findall("`dmc:altitude`; urn:dyad:dmc:dyad-operator/x") == ["altitude"]),
    ("command-reads-a-dyad-command", lambda: COMMAND.findall("run `dyad board resume`, not `git log`") == ["dyad board resume"]),
    ("bucket-row-reads-seconds", lambda: BUCKET_ROW.match("| inference | agent | 336 | 5.4% | x |").groups() == ("inference", "agent", "336")),
]


def words(text: str) -> int:
    return len(text.split())


def steps(text: str) -> list[dict]:
    """[{section, step, title, text}] in order: each numbered top-level item of a `## ` section (its continuation lines
    with it), and each section's prose outside any item as the step `-`."""
    out, section, cur = [], "", None
    def open_(step, title):
        return {"section": section, "step": step, "title": title, "lines": []}
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip(); cur = open_("-", ""); out.append(cur); continue
        m = STEP.match(line)
        if m and section:
            title = re.sub(r"[*`]", "", m.group(2)).split(" — ")[0].strip()[:60]
            cur = open_(m.group(1), title); out.append(cur)
        if cur is None:
            cur = open_("-", ""); out.append(cur)
        cur["lines"].append(line)
    return [{**s, "text": "\n".join(s.pop("lines"))} for s in out if any(l.strip() for l in s["lines"])]


def find_playbook(root: Path, name: str) -> Path | None:
    core = dyadlib.PKG / "playbooks" / f"{name}.md"
    if core.is_file():
        return core
    found = sorted((Path(root) / "crafts").glob(f"*/playbooks/{name}.md"))
    return found[0] if found else None


def records(root: Path) -> dict[str, Path]:
    """{identifier: record file} over the core's, every craft's and the instance's DMC stores (the dmc guard's)."""
    dmc = dyadlib.load_guard("agent", "dmc")
    return {p.stem: p for _, p, _ in dmc.records(Path(root))}


def trace_seconds(text: str) -> tuple[int, int] | None:
    """(inference, mechanical) seconds from a trace's Buckets table; None when it has no buckets."""
    tr = dyadlib.load_module(dyadlib.PKG / "scripts" / "trace.py", "trace")
    got = {m.group(1): int(m.group(3)) for m in (BUCKET_ROW.match(l) for l in text.splitlines()) if m}
    if not got:
        return None
    return got.get("inference", 0), sum(got.get(b, 0) for b in tr.MECHANICAL)


def times(root: Path, rel: str) -> list[tuple[int, int, int]]:
    """[(row id, inference s, mechanical s)] over the traces of rows whose plan file names `rel`."""
    store = dyadlib.instance(Path(root)) / "d-work"
    out = []
    for plan in sorted((store / "plans").glob("*.md"), key=lambda p: int(p.stem) if p.stem.isdigit() else 0):
        trace = store / "traces" / plan.name
        if plan.stem.isdigit() and trace.is_file() and rel in plan.read_text(errors="replace"):
            s = trace_seconds(trace.read_text(errors="replace"))
            if s is not None:
                out.append((int(plan.stem), *s))
    return out


def profile(root: Path, name: str) -> list[str]:
    pb = find_playbook(root, name)
    if pb is None:
        raise FileNotFoundError(f"no play-book {name} (dyad/playbooks/{name}.md, crafts/*/playbooks/{name}.md)")
    rel = pb.relative_to(Path(root)).as_posix() if pb.is_relative_to(Path(root)) else pb.as_posix()
    text = pb.read_text()
    rb = pb.parent.parent / "runbooks" / f"{name}.md"
    rb_words = words(rb.read_text()) if rb.is_file() else 0
    out = [f"play-book {name}: {rel}, {words(text)} words; run-book "
           + (f"{rb.parent.parent.name}/runbooks/{name}.md, {rb_words} words" if rb.is_file() else "none")]
    cited: list[str] = []
    for s in steps(text):
        ids, cmds = list(dict.fromkeys(CITE.findall(s["text"]))), list(dict.fromkeys(COMMAND.findall(s["text"])))
        cited += [i for i in ids if i not in cited]
        head = f"{s['section']} {s['step']}" + (f" {s['title']}" if s["title"] else "")
        out.append(f"  step {head}: {words(s['text'])} words; dmc: {', '.join(ids) or '-'}; commands: "
                   + (", ".join(f"`{c}`" for c in cmds) or "-"))
    recs, total = records(root), words(text) + rb_words
    out.append("records:" if cited else "records: none cited")
    for i in cited:
        p = recs.get(i)
        if p is None:
            out.append(f"  dmc:{i} not found"); continue
        kind = (json.loads(p.read_text()).get("dyad:judgedBy") or {}).get("dyad:kind", "?")
        n = words(p.read_text()); total += n
        out.append(f"  dmc:{i} {kind}, {n} words")
    out.append(f"run total: {total} words (the play-book, its run-book and the {len(cited)} record(s) it cites)")
    ts = times(root, rel)
    if ts:
        out.append(f"time: {len(ts)} trace(s) of rows whose plan names {rel} (#{', #'.join(str(t[0]) for t in ts)}): "
                   f"median inference {statistics.median(t[1] for t in ts):.0f} s, mechanical "
                   f"{statistics.median(t[2] for t in ts):.0f} s; {LIMIT}")
    else:
        out.append(f"time: no trace with buckets of a row whose plan names {rel}; {LIMIT}")
    return out


def main(argv=None, root: Path | None = None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) != 1 or not NAME.fullmatch(a[0]):
        print(f"refused: {USAGE}", file=sys.stderr); return 1
    try:
        print("\n".join(profile(root or dyadlib.repo_root(), a[0])))
    except FileNotFoundError as e:
        print(f"refused: {e}", file=sys.stderr); return 1
    return 0


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
