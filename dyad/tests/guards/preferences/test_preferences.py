"""Preference guard tests (preferences/preferences.py): header equals FIELDS (template too), unique
non-empty keys, non-empty cells, an enumerated `allowed` admits the value, `read by` names existing
Rules; an absent file passes; the live table passes; a template key missing from the live corpus
warns (`missing_keys`, #180); `allowed` is an enumeration only when every part is backticked — a mixed
cell is free text and a lone backticked value an enumeration of one (#512)."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
pf = dyadlib.load_guard("preferences", "preferences")

HEAD = "# prefs\n\n| key | value | allowed | read by |\n|-----|-------|---------|---------|\n"
ROWS = "| merge-disposition | with-done | `separate` \\| `with-done` | Rule-2 (binding), Rule-3 (form) |\n| import-support | release within 12 months | free text | Rule-13 (import criteria) |\n"

def fixture(text: str | None, template: str = HEAD, rules=(2, 3, 13)):
    root = Path(tempfile.mkdtemp()); pkg = root / "dyad"; (pkg / "templates").mkdir(parents=True); (pkg / "rules").mkdir()
    for n in rules: (pkg / "rules" / f"RULE-{n}-x.md").write_text(f"# Rule-{n}\n")
    (pkg / "templates" / "PREFERENCES.md").write_text(template)
    if text is not None:
        (root / "preferences-corpus").mkdir(); (root / "preferences-corpus" / "PREFERENCES.md").write_text(text)
    return root, pkg

class PreferenceTests(unittest.TestCase):
    def test_parse_keeps_escaped_pipes(self):
        header, rows = pf.parse(HEAD + ROWS)
        self.assertEqual(header, list(pf.FIELDS)); self.assertEqual(rows[0][2], "`separate` | `with-done`")
        self.assertEqual(pf.alternatives(rows[0][2]), ["separate", "with-done"]); self.assertIsNone(pf.alternatives("free text"))
    def test_enumeration_only_when_every_part_is_backticked(self):   # #512, #510's fix B
        self.assertEqual(pf.alternatives("`a` | `b` | `c`"), ["a", "b", "c"])          # all backticked: an enumeration
        self.assertEqual(pf.alternatives("`a`"), ["a"])                                # a lone backticked value: of one
        self.assertIsNone(pf.alternatives("`a` | free text"))                          # mixed: free text
        self.assertIsNone(pf.alternatives("`none` | seat names, or seat names without `-<hp>`"))   # #510's cell
        self.assertIsNone(pf.alternatives("`a` | "))                                   # an empty part is no value
        self.assertIsNone(pf.alternatives("SPDX identifiers"))
    def test_mixed_cell_admits_any_value(self):   # #510: `attended-seats` refused `communicate`
        row = "| attended-seats | communicate | `none` \\| seat names, or seat names without `-<hp>` | Rule-16 (Presence) |\n"
        root, pkg = fixture(HEAD + ROWS + row, rules=(2, 3, 13, 16)); self.assertEqual(pf.check_package(root, pkg), [])
    def test_enumeration_of_one_checks_the_value(self):
        row = "| only | other | `one` | Rule-2 |\n"
        root, pkg = fixture(HEAD + ROWS + row)
        msgs = pf.check_package(root, pkg); self.assertEqual(len(msgs), 1, msgs); self.assertIn("value `other` is not one of one", msgs[0])
        root, pkg = fixture(HEAD + ROWS + row.replace("| other |", "| `one` |")); self.assertEqual(pf.check_package(root, pkg), [])
    def test_good_table_passes(self):
        root, pkg = fixture(HEAD + ROWS); self.assertEqual(pf.check_package(root, pkg), []); self.assertEqual(pf.summary(root), "2 preferences")
    def test_absent_file_passes(self):
        root, pkg = fixture(None); self.assertEqual(pf.check_package(root, pkg), [])
    def test_wrong_header_fails(self):
        root, pkg = fixture(HEAD.replace("| read by |", "| rule |") + ROWS)
        msgs = pf.check_package(root, pkg); self.assertEqual(len(msgs), 1); self.assertIn("PREFERENCES.md: header", msgs[0])
    def test_value_outside_enumeration_fails(self):
        root, pkg = fixture(HEAD + ROWS.replace("| with-done |", "| sometimes |"))
        msgs = pf.check_package(root, pkg); self.assertEqual(len(msgs), 1); self.assertIn("value `sometimes` is not one of separate | with-done", msgs[0])
    def test_a_value_differing_only_by_case_warns_and_reads_canonical(self):
        """L6 (#553): the operator types a value directly, so case is not meaningful; the guard warns, the reader
        returns the canonical spelling, and a value matching no alternative still fails."""
        root, pkg = fixture(HEAD + ROWS.replace("| with-done |", "| With-Done |"))
        msgs = pf.check_package(root, pkg)
        self.assertEqual(msgs, ["warning: preferences-corpus/PREFERENCES.md: `merge-disposition` value `With-Done` is read as "
                                "`with-done`; write it `with-done` (L6, #553)"])
        self.assertEqual(dyadlib.preference("merge-disposition", root), "with-done")
        self.assertEqual(dyadlib.preference("import-support", root), "release within 12 months")   # free text: unchanged
        self.assertEqual(dyadlib.canonical_value("ALWAYS", "`off` | `always`"), "always")
        self.assertEqual(dyadlib.canonical_value("Communicate", "`none`, or seat names"), "Communicate")   # not an enumeration
        self.assertEqual(dyadlib.canonical_value("never", "`off` | `always`"), "never")
    def test_read_by_must_name_existing_rules(self):
        root, pkg = fixture(HEAD + ROWS.replace("Rule-13 (import criteria)", "Rule-42"))
        msgs = pf.check_package(root, pkg); self.assertEqual(len(msgs), 1); self.assertIn("read by Rule-42, which does not exist", msgs[0])
        root, pkg = fixture(HEAD + ROWS.replace("Rule-13 (import criteria)", "nobody"))
        msgs = pf.check_package(root, pkg); self.assertEqual(len(msgs), 1); self.assertIn("read by names no Rule", msgs[0])
    def test_duplicate_and_empty_cells_fail(self):
        root, pkg = fixture(HEAD + ROWS + "| merge-disposition |  |  | Rule-2 |\n")
        msgs = pf.check_package(root, pkg)
        self.assertEqual(len(msgs), 3, msgs); self.assertIn("defined twice", msgs[0]); self.assertIn("empty `value`", msgs[1]); self.assertIn("empty `allowed`", msgs[2])
    def test_template_checked_too(self):
        root, pkg = fixture(None, template=HEAD + ROWS.replace("Rule-13 (import criteria)", "Rule-99"))
        msgs = pf.check_package(root, pkg); self.assertEqual(len(msgs), 1); self.assertTrue(msgs[0].startswith("templates/PREFERENCES.md:"))
    def test_missing_key_warns(self):
        live = HEAD + "| merge-disposition | with-done | `separate` \\| `with-done` | Rule-2 (binding), Rule-3 (form) |\n"
        root, pkg = fixture(live, template=HEAD + ROWS)
        self.assertEqual(pf.missing_keys(root, pkg), ["import-support"])
        msgs = pf.check_package(root, pkg)
        self.assertEqual(len(msgs), 1); self.assertTrue(msgs[0].startswith("warning:"), msgs)
        self.assertIn("key `import-support` is in templates/PREFERENCES.md but has no row here", msgs[0])
    def test_missing_keys_needs_both_files(self):
        root, pkg = fixture(None, template=HEAD + ROWS)          # no live corpus: nothing to compare (a fresh install seeds it)
        self.assertEqual(pf.missing_keys(root, pkg), [])
        root, pkg = fixture(HEAD + ROWS, template=HEAD)           # template has no rows: nothing can be missing
        self.assertEqual(pf.missing_keys(root, pkg), [])
        self.assertEqual(pf.check_package(root, pkg), [])
    def test_describe(self):
        root, pkg = fixture(HEAD + ROWS); d = pf.describe(root, pkg)
        self.assertEqual([f[0] for f in d["fields"]], list(pf.FIELDS)); self.assertEqual(d["fields"][0][4], "merge-disposition"); self.assertEqual(d["observed"], 2)
    def test_a_tunable_value_its_record_does_not_allow_warns(self):   # #590: tunable() would read the default silently
        rules = {3: Path("RULE-3.md")}
        for bad in ("1.5", "0,4", "lots"):
            msgs = pf.check_text(HEAD + f"| hygiene-similar | {bad} | a number | Rule-3 |\n", "p", rules)
            self.assertEqual(len(msgs), 1, (bad, msgs))
            self.assertTrue(msgs[0].startswith("warning:") and "hygiene-similar" in msgs[0] and "0.35" in msgs[0], msgs)
        self.assertEqual(pf.check_text(HEAD + "| hygiene-similar | 0.4 | a number | Rule-3 |\n", "p", rules), [])
        self.assertEqual(pf.check_text(HEAD + "| sweep-ci-hours | 0 | a number | Rule-3 |\n", "p", rules)[0][:8], "warning:")
        self.assertEqual(pf.check_text(HEAD + ROWS, "p", {2: Path(), 3: Path(), 13: Path()}), [])   # not tunables: nothing

if __name__ == "__main__":
    unittest.main()
