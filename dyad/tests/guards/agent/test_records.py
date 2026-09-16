"""Record guard tests (agent/records.py): an attack table headed attack / result / survivor (any case,
anywhere in the file) and a `Disposition:` line; package and instance records both read; the live
records pass."""
import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
rc = dyadlib.load_guard("agent", "records")

GOOD = "# Falsification record — x (ledger #7)\n\n**Claim:** c.\n\n| # | Attack | Result | Survivor |\n|---|---|---|---|\n| 1 | a1 | Refuted | s1 |\n\nDisposition: see ledger #7.\n"
AMEND = "# r\n\n| from | to |\n|---|---|\n| a | b |\n\n## amendment\n| # | attack | result | survivor |\n|---|---|---|---|\n| A | a | Survives, scoped | s |\nNo gap found. Disposition: see ledger #9.\n"

def fixture(pkg_records: dict[str, str], inst_records: dict[str, str] | None = None):
    root = Path(tempfile.mkdtemp()); pkg = root / "dyad"; (pkg / "falsification" / "rules").mkdir(parents=True)
    for n, t in pkg_records.items(): (pkg / "falsification" / "rules" / n).write_text(t)
    if inst_records is not None:
        (root / "agent-corpus" / "falsification").mkdir(parents=True)
        for n, t in inst_records.items(): (root / "agent-corpus" / "falsification" / n).write_text(t)
    return root, pkg

class RecordTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_contract(self):
        self.assertEqual((rc.ENTITY, rc.CORPUS, rc.TRANSACTION, rc.FIELDS), ("record", "agent", False, ("#", "Attack", "Result", "Survivor")))
    def test_good_records_pass(self):
        root, pkg = fixture({"rule-1-x.md": GOOD}, {"gap.md": GOOD, "amend.md": AMEND})
        self.assertEqual(rc.check_package(root, pkg), []); self.assertEqual(len(rc.record_files(root, pkg)), 3)
        self.assertEqual(rc.parse(AMEND), [["A", "a", "Survives, scoped", "s"]]); self.assertEqual(len(rc.attack_tables(AMEND)), 1)
    def test_missing_table_fails(self):
        root, pkg = fixture({"rule-1-x.md": GOOD.replace("| # | Attack | Result | Survivor |", "| # | Claim | Verdict | Note |")})
        msgs = rc.check_package(root, pkg); self.assertEqual(len(msgs), 1); self.assertIn("no attack table", msgs[0])
    def test_missing_disposition_fails(self):
        root, pkg = fixture({"rule-1-x.md": GOOD.replace("Disposition: see ledger #7.\n", "")}, {"gap.md": GOOD})
        msgs = rc.check_package(root, pkg); self.assertEqual(len(msgs), 1); self.assertIn("rule-1-x.md: no `Disposition:` line", msgs[0])
    def test_no_instance_dir_passes(self):
        root, pkg = fixture({"rule-1-x.md": GOOD}); self.assertEqual(rc.check_package(root, pkg), [])
    def test_live_records_pass(self):
        self.assertEqual(rc.check_package(dyadlib.repo_root()), []); self.assertGreaterEqual(len(rc.record_files(dyadlib.repo_root())), 18)   # the package ships one record per Rule (A6; 18 Rules since #160 retired 17 and 21); a scratch install has no instance records
    def test_describe(self):
        root, pkg = fixture({"rule-1-x.md": GOOD}, {"gap.md": AMEND})
        d = rc.describe(root, pkg)
        self.assertEqual([f[0] for f in d["fields"]], list(rc.FIELDS)); self.assertEqual(d["observed"], 2)
        self.assertTrue(d["fields"][2][2].startswith("refuted | survives"), d["fields"][2][2])


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(rc, "core", rc.CORPUS)
        self.assertEqual(dyadlib.check_invariants(rc, extra), len(rc.INVARIANTS) + 4)
        names = [n for n, _ in rc.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
