#!/usr/bin/env python3
"""The intent reading's candidates (core script; d-work #615; Rule-3 Plan owns the intent question, the decision
criterion `dyad/dmc/intent-reading.jsonld` its outcomes). Kernel: Python 3.12+, stdlib.
`dyad dwork intent <id>` prints what a reading of row <id>'s prompts reads before it classifies them: the rows of any
state and the surface items (`dyad/surface.md`) nearest the prompts, by the TF-IDF `hygiene.tfidf` weighs the backlog
with, `INTENT_TOP` of each, best first, each row with its state and age. It applies no threshold (plan #615 F7: on
#615's own prompt the real neighbours scored about 0.16, under `hygiene-similar`): these are candidates to read, never
a verdict — new, overlap, supersede, adjacent, ambiguous or false-premise is the reading's, by inference. Read-only:
it writes nothing.
  intent.py <id>     (reached as `dyad dwork intent`)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("intent.py: Python 3.12+ required")
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

USAGE = "usage: dyad dwork intent <id>"
INTENT_TOP = 10                # rows, and surface items, printed: candidates to read, never a verdict (F7)
QUERY = "@prompt"              # the key of the reading's own document in the corpus
SECTIONS = ("intent as read", "definition of done")   # the parts of a plan a reading compares a prompt with


def hygiene():
    return dyadlib.load_module(dyadlib.PKG / "scripts" / "hygiene.py", "hygiene")


def plan_sections(text: str, heads=SECTIONS) -> str:
    """The body of every `## ` section of a plan file whose heading opens with one of `heads` (case folded): what the
    operator's intent was read as, never the mutation's machinery, whose shared vocabulary drowns the signal (F7)."""
    out, keep = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            keep = line[3:].strip().lower().startswith(heads)
        elif keep:
            out.append(line)
    return "\n".join(out)


def surface_items(text: str) -> dict[str, str]:
    """{`<section> <item>`: its whole table line} of `dyad/surface.md`: the first cell of every table row under an
    `S<n>` section, header rows (the line above a `|---` rule) and rules skipped."""
    out, sec, lines = {}, None, text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## "):
            sec = line[3:].split()[0] if line[3:4] == "S" else None
        elif sec and line.startswith("|") and not line.startswith("|---") \
                and not (i + 1 < len(lines) and lines[i + 1].startswith("|---")):
            cells = dyadlib.split_cells(line)
            if cells and cells[0]:
                out.setdefault(f"{sec} {cells[0]}", line)
    return out


def candidates(query: str, rows, texts: dict[int, str], surface: dict[str, str], rid: int | None = None,
               top: int = INTENT_TOP) -> tuple[list[tuple[float, int]], list[tuple[float, str]]]:
    """([(cosine, row id)], [(cosine, surface item)]), each best first and at most `top` long: every row but `rid`, of
    any state, and every surface item, ranked by cosine against `query` over one TF-IDF corpus. No threshold; a zero
    cosine shares no token and is dropped."""
    hy = hygiene()
    docs = {("r", r.id): texts.get(r.id, r.title) for r in rows if r.id != rid}
    docs |= {("s", k): v for k, v in surface.items()}
    docs[QUERY] = query
    vec, norm = hy.tfidf(docs)
    got = [(hy.cosine(vec, norm, QUERY, k), k) for k in docs if k != QUERY]
    got = sorted((g for g in got if g[0] > 0), key=lambda g: (-g[0], str(g[1][1])))
    return ([(c, k[1]) for c, k in got if k[0] == "r"][:top], [(c, k[1]) for c, k in got if k[0] == "s"][:top])


def age(opened: str, today: datetime.date) -> str:
    try:
        return f"{(today - datetime.date.fromisoformat(opened)).days}d"
    except ValueError:
        return "?"


def main(argv=None, root: Path | None = None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) != 1 or not a[0].isdigit():
        print(f"refused: {USAGE}", file=sys.stderr); return 1
    root = root or dyadlib.repo_root()
    rows = {r.id: r for r in dyadlib.read_rows(root)}
    rid = int(a[0])
    if rid not in rows:
        print(f"no row {rid}", file=sys.stderr); return 1
    pv = dyadlib.load_guard("agent", "provenance")
    store = dyadlib.instance(root) / "d-work"
    rec = store / "provenance" / f"{rid}.md"
    prompts = [e["text"] for e in pv.parse(rec.read_text()) if e["kind"] == "prompt"] if rec.is_file() else []
    query = "\n".join(prompts) if prompts else rows[rid].title     # an amend is a prompt entry too: the reading reads all
    texts = {}
    for r in rows.values():
        plan = store / "plans" / f"{r.id}.md"
        texts[r.id] = r.title + ("\n" + plan_sections(plan.read_text()) if plan.is_file() else "")
    surface = dyadlib.PKG / "surface.md"
    near_rows, near_items = candidates(query, rows.values(), texts,
                                       surface_items(surface.read_text()) if surface.is_file() else {}, rid)
    today = datetime.date.fromisoformat(dyadlib.utc_date())
    on = dyadlib.slugs_on(root)                                        # #622: read once
    lab = lambda i: dyadlib.row_label(i, rows, on)
    print(f"intent candidates for {lab(rid)} {rows[rid].title} (against its {'prompts' if prompts else 'title'}; "
          f"top {INTENT_TOP}, no threshold: candidates to read, never a verdict)")
    print("rows:" if near_rows else "rows: none shares a token")
    for c, i in near_rows:
        print(f"  {c:.2f}  {lab(i)} [{rows[i].state}, {age(rows[i].opened, today)}] {rows[i].title}")
    print("surface:" if near_items else "surface: none shares a token")
    for c, k in near_items:
        print(f"  {c:.2f}  {k}")
    return 0


INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("top-is-positive", lambda: INTENT_TOP > 0),
    ("query-key-is-no-doc-key", lambda: not isinstance(QUERY, tuple)),   # row and surface keys are tuples
    ("sections-are-plan-headings", lambda: all(h == h.lower() for h in SECTIONS) and "intent as read" in dyadlib.PLAN_PARTS),
    ("surface-header-skipped", lambda: surface_items("## S1 X\n| form | s |\n|---|---|\n| `a` | frozen |\n") == {"S1 `a`": "| `a` | frozen |"}),
]
dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
