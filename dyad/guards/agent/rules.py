#!/usr/bin/env python3
"""Agent Rule guard (entity `rule`, agent corpus; Rule-4 owns the check, placed per Rule-11 property 1). Kernel: Python 3.12+.
Per Agent Rule: **Intent:** exactly 1 (5a; imperative mood 5b is inference), **Target:** exactly 1
(5c), bullets under ## Boundaries >= 1 (5d), bullets under ## Conditions >= 1 (5e).
  rules.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("rules.py: Python 3.12+ required")
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "rule", "agent", False
NAME, OWNER = "Agent Rule block", "Rule-4"
# The countable block (Rule-4 Criteria): field -> (min, max); None = unbounded. check() reads it.
BLOCK: dict[str, tuple[int, int | None]] = {"intent": (1, 1), "target": (1, 1), "boundaries": (1, None), "conditions": (1, None)}
FIELDS = tuple(BLOCK)
INVARIANTS = [("block-counts-positive", lambda: all(lo >= 1 and (hi is None or hi >= lo) for lo, hi in BLOCK.values()) and FIELDS == tuple(BLOCK))]   # crafts/syseng/rules/invariants.md

def bullets_under(text: str, heading: str) -> int:
    n, insec = 0, False
    for line in text.splitlines():
        if line.startswith("## "):
            insec = line.startswith(heading)
        elif insec and line.startswith("- "):
            n += 1
    return n

def counts(text: str) -> dict[str, int]:
    lines = text.splitlines()
    return {"intent": sum(l.startswith("**Intent:**") for l in lines),
            "target": sum(l.startswith("**Target:**") for l in lines),
            "boundaries": bullets_under(text, "## Boundaries"),
            "conditions": bullets_under(text, "## Conditions")}

def check(name: str, text: str) -> list[str]:
    c = counts(text); fails = []
    for k, (lo, hi) in BLOCK.items():
        what = f"{k.capitalize()} count" if hi == 1 else f"{k.capitalize()} bullets"
        if c[k] < lo or (hi is not None and c[k] > hi):
            fails.append(f"FAIL [rule-4] {name}: {what} {c[k]} (want {lo if hi == lo else f'>={lo}'})")
    return fails

def check_rules(pkg: Path = dyadlib.PKG) -> tuple[list[str], list[str]]:
    """(ok lines, failures) over every Rule file of `pkg`."""
    oks, fails = [], []
    for n, p in sorted(dyadlib.rule_files(pkg).items()):
        f = check(p.name, p.read_text())
        if f: fails += f
        else:
            c = counts(p.read_text())
            oks.append(f"ok   [rule-4] {p.name} (intent {c['intent']}, target {c['target']}, boundaries {c['boundaries']}, conditions {c['conditions']})")
    return oks, fails

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    return [f[5:] if f.startswith("FAIL ") else f for f in check_rules(pkg)[1]]

def check_tended(rules_dir: Path, tokens, rel_to: Path | None = None) -> list[str]:
    """Rule-4 guard (Boundaries): a Tended rule that binds the Agent's process belongs in the core craft. Scans
    every `<rules_dir>/*.md` (README exempt) for the Agent-process `tokens` (data: the caller's, the craft
    guard's `crafts_rules.txt` `agent-token:` lines; #156) and returns one `warning:` line per file that
    mentions any — a candidate for inference, never a failure (plan #156 attack A12: the classification is
    inference and a Tended Rule is never edited to satisfy a guard, Rule-8)."""
    out = []
    for p in sorted(Path(rules_dir).glob("*.md")):
        if p.name == "README.md":
            continue
        text = p.read_text(errors="ignore")
        hits = [t for t in tokens if t in text]
        if hits:
            rel = p.relative_to(rel_to) if rel_to and p.is_relative_to(rel_to) else p
            out.append(f"warning: {rel}: mentions {', '.join(repr(h) for h in hits)} — binds the Agent's process? (Rule-4 guard: inference decides)")
    return out

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    return f"{len(dyadlib.rule_files(pkg))} Rules"

def _line_after(text: str, prefix: str) -> str:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""

def _first_bullet_under(text: str, heading: str) -> str:
    insec = False
    for line in text.splitlines():
        if line.startswith("## "):
            insec = line.startswith(heading)
        elif insec and line.startswith("- "):
            return line[2:].strip()
    return ""

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    rules = dyadlib.rule_files(pkg)
    ex_n = max(rules) if rules else None
    ex_t = rules[ex_n].read_text() if ex_n else ""
    examples = {"intent": _line_after(ex_t, "**Intent:**"), "target": _line_after(ex_t, "**Target:**"),
                "boundaries": _first_bullet_under(ex_t, "## Boundaries"), "conditions": _first_bullet_under(ex_t, "## Conditions")}
    rel = pkg.relative_to(root) if pkg.is_relative_to(root) else pkg
    return {"store": f"{rel}/rules/RULE-<n>-<slug>.md", "parser": "`rules.counts` / `dyadlib.rule_files`", "observed": len(rules),
            "note": "the countable block after the title; wording is inference (Rule-4)",
            "fields": [(k, "line" if hi == 1 else "bullets", f"exactly {lo}" if hi == lo else f">= {lo}", True, examples.get(k, ""), "rules.BLOCK") for k, (lo, hi) in BLOCK.items()]}

def main():
    oks, fails = check_rules()
    for o in oks: print(o)
    for f in fails: print(f, file=sys.stderr)
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
