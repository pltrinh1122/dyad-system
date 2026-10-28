"""Row-file store tests over dyadlib (Rule-16): round trip, render/parse agreement, the live store,
Rule-16's transition bullet equals dyadlib.TRANSITIONS. The fence itself: tests/guards/agent/test_rows.py."""
import re, sys, unittest, unittest.mock
from dataclasses import fields
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
    def test_write_row_dry_run_checks_the_transition_and_writes_nothing(self):
        """#464: `dry_run` is the same transition check at the same point, then no `first`, no row file."""
        import tempfile
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.dict("os.environ", {"DYAD_INSTANCE": str(Path(t) / "inst")}):
            dyadlib.rows_dir(Path(t)).mkdir(parents=True)
            called = []
            p = dyadlib.write_row(Path(t), dyadlib.Row(1, "a", "d", "planned", "", ""), "open", first=lambda: called.append(1), dry_run=True)
            self.assertFalse(p.exists()); self.assertEqual(called, [])
            with self.assertRaises(dyadlib.TransitionError):
                dyadlib.write_row(Path(t), dyadlib.Row(1, "a", "d", "open", "", ""), "done", first=lambda: called.append(1), dry_run=True)
            self.assertEqual(called, []); self.assertEqual(list(dyadlib.rows_dir(Path(t)).iterdir()), [])
    def test_backlog_drains_to_archived(self):
        # d-work #290: `archived` was used 0 times in 280 rows because the table gave `backlog` only `open` —
        # 75 rows could not be retired without being worked. Rule-3 already defined `archived` as retirement
        # by an Operator disposition naming the rows; only the table forbade it from where those rows sit.
        self.assertTrue(dyadlib.allowed("backlog", "archived"))
        self.assertIsNone(dyadlib.require_transition("backlog", "archived"))
        self.assertIsNone(dyadlib.require_transition("done", "archived"))
        for a, b in (("backlog", "done"), ("archived", "open"), ("archived", "backlog"), ("open", "archived")):
            with self.subTest(a=a, b=b), self.assertRaises(dyadlib.TransitionError):
                dyadlib.require_transition(a, b)

class RowModeTests(unittest.TestCase):
    """d-work #290: `mode` is OPTIONAL_FIELDS, not FIELDS. It cannot be FIELDS — `parse_row_file` raises on a
    missing FIELDS key and the plan gate parses rows at historical commits, none of which carry the line."""
    SIX = "id: 1\ntitle: one\nopened: 2026-10-14\nstate: open\ndisposed: \nrefs: \n"
    def test_mode_is_optional_and_last(self):
        self.assertNotIn("mode", dyadlib.FIELDS)
        self.assertEqual(dyadlib.OPTIONAL_FIELDS, ("mode",))
        self.assertEqual(dyadlib.FIELDS + dyadlib.OPTIONAL_FIELDS, tuple(f.name for f in fields(dyadlib.Row)))
        self.assertEqual(dyadlib.DEFAULT_MODE, "explicit"); self.assertIn(dyadlib.DEFAULT_MODE, dyadlib.MODES)
    def test_six_positionals_still_build_a_row(self):
        r = dyadlib.Row(1, "one", "2026-10-14", "open", "", "")      # every construction in the tree
        self.assertEqual(r.mode, "explicit")
    def test_a_row_predating_the_field_parses_and_reformats_byte_identically(self):
        r = dyadlib.parse_row_file(self.SIX)
        self.assertEqual(r.mode, "explicit")
        self.assertEqual(dyadlib.format_row_file(r), self.SIX)        # no churn, so no migration of the store
    def test_implicit_is_written_and_round_trips(self):
        r = dyadlib.Row(2, "accreted", "2026-10-14", "open", "2026-10-14 Y plan (mandate #1)", "parent #1", "implicit")
        text = dyadlib.format_row_file(r)
        self.assertTrue(text.endswith("mode: implicit\n"))            # last line, after every FIELDS line
        self.assertEqual(dyadlib.parse_row_file(text), r)
    def test_a_mode_outside_the_set_raises(self):
        with self.assertRaises(ValueError) as cm:
            dyadlib.parse_row_file(self.SIX + "mode: automatic\n")
        self.assertIn("not one of explicit implicit", str(cm.exception))
    def test_a_missing_fields_key_still_raises(self):
        with self.assertRaises(ValueError):
            dyadlib.parse_row_file("id: 1\ntitle: t\nopened: d\nstate: open\nrefs: \nmode: implicit\n")

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
