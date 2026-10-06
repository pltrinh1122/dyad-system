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
        # #186 replaced a floor of 18 justified as "one record per Rule (18 Rules)". Both were false:
        # `dyad/rules/RULE-*.md` is 19 files (1-16, 18-20; 17 and 21 were retired by #160), and
        # `dyad/falsification/rules/` holds 20 records of which only 17 are per-Rule — Rules 9 and 10
        # share `rules-9-10-promotion.md`, while `rule-sets.md` and `rules-2-3-batch-disposition.md`
        # are multi-Rule. The package partition is pinned exactly, not floored, because it ships with
        # the package and is identical in every install; the instance partition is not pinned at all,
        # because a scratch install has none (CI runs this suite inside one, `dyad-package.yml`), which
        # is why `record_files(repo_root())` reads 31 here and 20 there.
        root = dyadlib.repo_root()   # the live verdict itself is the agent/records guard's (#227)
        pkg_records = [f for f in rc.record_files(root) if f.parent == dyadlib.PKG / "falsification" / "rules"]
        self.assertEqual(len(pkg_records), 20)
    def test_describe(self):
        root, pkg = fixture({"rule-1-x.md": GOOD}, {"gap.md": AMEND})
        d = rc.describe(root, pkg)
        self.assertEqual([f[0] for f in d["fields"]], list(rc.FIELDS)); self.assertEqual(d["observed"], 2)
        self.assertTrue(d["fields"][2][2].startswith("refuted | survives"), d["fields"][2][2])

if __name__ == "__main__":
    unittest.main()
