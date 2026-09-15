import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
d = dyadlib.load_guard("agent", "prs")

LEDGER = """| id | title | opened | state | disposed | refs |
|----|-------|--------|-------|----------|------|
| 1 | done one | 2026-09-12 | done | 2026-09-12 Y plan; 2026-09-12 Y done | |
| 2 | open planned | 2026-09-12 | open | 2026-09-12 Y plan | |
| 3 | open unplanned | 2026-09-12 | open | | |
| 4 | blocked planned | 2026-09-12 | blocked | 2026-09-12 Y plan; 2026-09-12 N | |
| 5 | backlog | 2026-09-12 | backlog | | |
| 6 | planned | 2026-09-13 | planned | 2026-09-13 Y plan | |
"""

class DworkLinkTests(unittest.TestCase):
    def test_passes_open_and_blocked_with_plan(self):
        self.assertEqual(d.check("fix. d-work #2, d-work #4, d-work #6.", LEDGER), [])
    def test_no_citation(self):
        self.assertIn("cites no", d.check("no ref here; d-work#2 malformed", LEDGER)[0])
    def test_not_in_ledger(self):
        self.assertIn("#99 not in ledger", d.check("d-work #99", LEDGER)[0])
    def test_done_and_backlog_refused(self):
        self.assertIn("is done", d.check("d-work #1", LEDGER)[0])
        self.assertIn("is backlog", d.check("d-work #5", LEDGER)[0])
    def test_plan_gate(self):
        self.assertIn("no 'Y plan'", d.check("d-work #3", LEDGER)[0])
    def test_duplicate_citation_counted_once(self):
        self.assertEqual(d.cited("d-work #2 and again d-work #2"), [2])
    def test_contract_and_package_check(self):
        self.assertEqual((d.ENTITY, d.CORPUS, d.TRANSACTION, d.FIELDS), ("pr", "agent", True, ("body",)))
        self.assertEqual(d.check_package(dyadlib.repo_root()), [])   # a PR lives in The World: nothing in a store
    def test_transaction_check_reads_branch_messages(self):
        import os, subprocess, tempfile
        root = Path(tempfile.mkdtemp()); sh = lambda *a: subprocess.run(a, cwd=root, check=True, capture_output=True, text=True)
        sh("git", "init", "-q", "-b", "main"); sh("git", "config", "user.email", "t@t"); sh("git", "config", "user.name", "t")
        rows = root / "agent-corpus" / "d-work" / "rows"; rows.mkdir(parents=True)
        (rows / "2.md").write_text("id: 2\ntitle: two\nopened: d\nstate: planned\ndisposed: d Y plan\nrefs: \n")
        sh("git", "add", "-A"); sh("git", "commit", "-qm", "root"); base = sh("git", "rev-parse", "HEAD").stdout.strip()
        os.environ.pop("DYAD_INSTANCE", None)
        self.assertEqual(d.check_transaction(root, base, base), [])          # on main: nothing to say
        sh("git", "checkout", "-q", "-b", "agent/2-x"); (root / "f").write_text("f"); sh("git", "add", "-A"); sh("git", "commit", "-qm", "work (d-work #2)")
        head = sh("git", "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(d.check_transaction(root, base, head), [])
        (root / "g").write_text("g"); sh("git", "add", "-A"); sh("git", "commit", "-qm", "more (d-work #3)")
        self.assertIn("#3 not in ledger", d.check_transaction(root, base, sh("git", "rev-parse", "HEAD").stdout.strip())[0])


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(d, "core", d.CORPUS)
        self.assertEqual(dyadlib.check_invariants(d, extra), len(d.INVARIANTS) + 4)
        names = [n for n, _ in d.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
