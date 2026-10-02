#!/usr/bin/env python3
"""PR guard (entity `pr`, agent corpus; Rule-3 owns the plan gate, placed per Rule-11 property 1). Kernel: Python 3.12+.
A PR must cite at least one `d-work #N`; every cited N must be a ledger row at the base commit with
state open, planned or blocked and a `Y plan` disposition (plan gate, E3). A PR lives in The World
(hosting), so the package check has nothing to read; the transaction check (TRANSACTION) reads the
branch's commit messages as the body on any branch but `main`, and skips a range that touches only
`<instance>/d-work/` (`ledger_only`, d-work #191): Rule-2 and Rule-3 class a ledger-only commit as
clerical — it records a prompt or a disposition, it claims no d-work — so the gate never applies to
one. Before #191 it did, and a session fenced off `main` (Rule-1, #23) could push a ledger-only branch
only around the hook, which skipped every other guard too. The row and provenance guards still judge
the range.
  PR_BODY="..." BASE_SHA=<sha> prs.py
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("prs.py: Python 3.12+ required")
import os, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "pr", "agent", True
NAME, OWNER = "pull request", "Rule-3 (plan gate); The World holds it"
FIELDS = ("body",)
CITE = re.compile(r"d-work #(\d+)")
INVARIANTS = [("cite-has-one-group", lambda: CITE.groups == 1)]   # crafts/syseng/rules/invariants.md

def cited(body: str) -> list[int]:
    return sorted({int(m) for m in CITE.findall(body or "")})

def check(body: str, ledger_text: str | None = None, rows: list | None = None) -> list[str]:
    """rows: parsed Row list (Rule-16); ledger_text: a table, kept for tests."""
    ids = cited(body)
    if not ids:
        return ["FAIL [d-work]: PR body cites no 'd-work #N'"]
    if rows is None:
        rows = dyadlib.ledger_rows(ledger_text or "")
    by_id = {r.id: r for r in rows}
    fails = []
    for n in ids:
        row = by_id.get(n)
        if row is None:
            fails.append(f"FAIL [d-work]: #{n} not in ledger"); continue
        if row.state not in ("open", "planned", "blocked"):
            fails.append(f"FAIL [d-work]: #{n} is {row.state}, not open"); continue
        if "Y plan" not in row.disposed:
            fails.append(f"FAIL [d-work]: #{n} has no 'Y plan' disposition (plan gate)")
    return fails

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """Nothing in a store: a PR is in The World (Rule-14)."""
    return []

def ledger_only(root: Path, base: str, head: str) -> bool:
    """The range's own commits (three-dot) touch only `<instance>/d-work/` — `dyadlib.ledger_only`,
    rename detection off, so a move of code into the ledger is never read as ledger-only (#191)."""
    return dyadlib.ledger_only(root, base, head)

def check_transaction(root: Path, base: str, head: str) -> list[str]:
    """On a branch: the commit messages of base..head are the body; rows read at the base. A
    ledger-only range is clerical and cites nothing (`ledger_only`, #191)."""
    if subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root, text=True).strip() == "main":
        return []
    if ledger_only(root, base, head):
        return []
    body = subprocess.check_output(["git", "log", "--format=%B", f"{base}..{head}"], cwd=root, text=True)
    return check(body, rows=dyadlib.read_rows(root, at=base))

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    return {"store": "The World (hosting): a PR against `main`", "parser": "`prs.cited` over the PR body (or a branch's commit messages)",
            "observed": 0, "note": "cites `d-work #<id>`; the gate reads the row at the base commit (state open, planned or blocked; `Y plan`)",
            "fields": [("body", "text", "at least one `d-work #<id>` citation", True, "", "prs.FIELDS")]}

def main():
    root = dyadlib.repo_root()
    base = os.environ.get("BASE_SHA", "HEAD")
    try:
        rows = dyadlib.read_rows(root, at=base)
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"FAIL [d-work]: no ledger rows at base ({e})", file=sys.stderr); return 1
    fails = check(os.environ.get("PR_BODY", ""), rows=rows)
    for f in fails:
        print(f, file=sys.stderr)
    if not fails:
        print("d-work link OK:", " ".join(str(i) for i in cited(os.environ.get("PR_BODY", ""))))
    return 1 if fails else 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1, #203)

if __name__ == "__main__":
    sys.exit(main())
