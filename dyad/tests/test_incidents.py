"""Incident log parser tests (dyad/scripts/incidents.py): the log's table parsed as one entity — five cells, a
parseable date, a `#<id>` in the d-work cell, no empty prose cell — an absent log skipping rather
than failing, the month grouping keeping an unparseable date visible, and the live log passing."""
import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dyadlib, incidents as inc

HEAD = "# Incidents (Rule-3)\n\nprose.\n\n| date | d-work | what | cause | consequence |\n|------|--------|------|-------|-------------|\n"
ROW = "| 2026-09-25 | #161 | what happened | why it happened | what it cost |\n"
GOOD = HEAD + ROW + "| 2026-08-01 | #1, #2 | w | c | q |\n"

def fixture(text: str | None, inst: str = "agent-corpus"):
    root = Path(tempfile.mkdtemp())
    if text is not None:
        d = root / inst / "audits"; d.mkdir(parents=True); (d / "INCIDENTS.md").write_text(text)
    (root / "dyad").mkdir(exist_ok=True)
    return root

class ContractTests(unittest.TestCase):
    def test_contract(self):
        self.assertEqual(inc.FIELDS, ("date", "d-work", "what", "cause", "consequence"))
        self.assertFalse(hasattr(inc, "ENTITY"), "a script, not a guard: no registry entry (row #170)")
    def test_invariants_hold(self):
        for name, pred in inc.INVARIANTS:
            self.assertTrue(pred(), name)

class ParseTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_good_log_passes_and_parses(self):
        root = fixture(GOOD)
        self.assertEqual(inc.check(root), [])
        rows = inc.parse(root=root)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["date"], "2026-09-25"); self.assertEqual(rows[0]["ids"], ["161"])
        self.assertEqual(rows[1]["ids"], ["1", "2"])                      # every id of the cell, not just the first
        self.assertEqual(rows[0]["what"], "what happened")
    def test_absent_log_skips_and_never_fails(self):
        msgs = inc.check(fixture(None))
        self.assertEqual(len(msgs), 1); self.assertTrue(msgs[0].startswith("warning:"), msgs)
        self.assertEqual(inc.parse(root=fixture(None)), [])
    def test_wrong_header_fails(self):
        root = fixture(GOOD.replace("| date | d-work | what | cause | consequence |", "| when | dwork | what | why | cost |", 1))
        self.assertEqual(len(inc.check(root)), 1)
        self.assertIn("no incident table", inc.check(root)[0])
    def test_unparseable_date_fails_and_stays_visible_in_the_grouping(self):
        root = fixture(HEAD + "| 2026-09-14–15 | #13 | w | c | q |\n")     # the live log's own defect, d-work #166
        self.assertTrue(any("does not parse" in m for m in inc.check(root)), inc.check(root))
        self.assertIn("", inc.by_year_month(inc.parse(root=root)))          # grouped under "", never dropped
    def test_cell_count_and_empty_cells_fail(self):
        root = fixture(HEAD + "| 2026-09-25 | #1 | w | c | q | extra |\n")   # a sixth cell, not an escaped pipe: `dyadlib.tables` does not honour `\\|` (backlog, d-work #166)
        self.assertTrue(any("cells, not 5" in m for m in inc.check(root)), inc.check(root))
        root = fixture(HEAD + "| 2026-09-25 | #1 |  | c | q |\n")
        self.assertTrue(any("what is empty" in m for m in inc.check(root)), inc.check(root))
    def test_row_without_a_dwork_id_fails(self):
        root = fixture(HEAD + "| 2026-09-25 | none | w | c | q |\n")
        self.assertTrue(any("names no `#<id>`" in m for m in inc.check(root)), inc.check(root))
    def test_grouping_is_sorted_by_month(self):
        rows = inc.parse_text(GOOD)
        self.assertEqual(list(inc.by_year_month(rows)), ["2026-08", "2026-09"])

class LiveTests(unittest.TestCase):
    def test_live_log_passes(self):
        root = dyadlib.repo_root()
        msgs = [m for m in inc.check(root) if not m.startswith("warning:")]
        self.assertEqual(msgs, [], msgs)
        self.assertGreater(len(inc.parse(root=root)), 40)                  # the log this guard was written for

if __name__ == "__main__":
    unittest.main()
