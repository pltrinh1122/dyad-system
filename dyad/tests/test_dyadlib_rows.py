"""Row-file store tests over dyadlib (Rule-16): round trip, render/parse agreement, the live store,
Rule-16's transition bullet equals dyadlib.TRANSITIONS. The fence itself: tests/guards/agent/test_rows.py."""
import re, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dyadlib, livetest

class RowFileTests(unittest.TestCase):
    def test_roundtrip(self):
        r = dyadlib.Row(7, "seven | with pipe", "2026-09-13", "planned", "2026-09-13 Y plan", "parent #1")
        self.assertEqual(dyadlib.parse_row_file(dyadlib.format_row_file(r)), r)
    def test_missing_field(self):
        with self.assertRaises(ValueError): dyadlib.parse_row_file("id: 1\ntitle: t\n")
    def test_render_and_table_parse_agree(self):
        rows = [dyadlib.Row(1, "a", "d", "open", "", ""), dyadlib.Row(2, "b", "d", "done", "Y done", "PR #1")]
        self.assertEqual(dyadlib.ledger_rows(dyadlib.render(rows)), rows)
    def test_rule_16_bullet_enumerates_transitions(self):
        # d-work #112: code is the table; the Rule-16 Store bullet enumerates it and must agree.
        text = dyadlib.rule_files()[16].read_text()
        m_ = re.search(r"Transitions are exactly:(.*?)\(`dyadlib\.TRANSITIONS`", text, re.S)
        self.assertIsNotNone(m_, "Rule-16 Store bullet 'Transitions are exactly: ... (`dyadlib.TRANSITIONS`' missing")
        table = {}
        for clause in " ".join(m_.group(1).split()).split(";"):
            src, arrow, dst = clause.partition("\u2192")
            self.assertEqual(arrow, "\u2192", clause)
            targets = [t.strip() for t in dst.split(",")]
            table[src.strip()] = frozenset() if targets == ["none"] else frozenset(targets)
        self.assertEqual(table, dyadlib.TRANSITIONS)

class LiveTests(livetest.LiveCase):
    """The row store of the instance this install runs in parses (Rule-16). Empty instance: `read_rows`
    yields nothing and the rendered view is its header alone — documented behaviour, asserted not skipped."""
    def test_live_rows_read_and_unique(self):
        rows = dyadlib.read_rows()                                          # raises on a duplicate id
        self.assertEqual(len(rows), len({r.id for r in rows}))
        self.assertEqual([r for r in rows if r.state not in dyadlib.STATES], [])
        # the rendered view parses back to the same ids (a title holding `|` splits into extra cells — row #156;
        # render/parse agreement on well-formed titles is the fixture case above)
        self.assertEqual([r.id for r in dyadlib.ledger_rows(dyadlib.render(rows))], [r.id for r in rows])
        if livetest.instance_is_empty():
            self.assertEqual(rows, [])
            self.assertEqual(dyadlib.render(rows), dyadlib.render([]))       # the header-only view `dyad ledger` writes
            self.assertEqual(dyadlib.ledger_rows(dyadlib.render(rows)), [])  # nothing but the header and the separator
        else:
            self.assertGreaterEqual(len(rows), 1)

if __name__ == "__main__":
    unittest.main()
