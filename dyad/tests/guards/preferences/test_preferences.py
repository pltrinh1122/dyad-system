"""Preference guard tests (preferences/preferences.py): header equals FIELDS (template too), unique
non-empty keys, non-empty cells, an enumerated `allowed` admits the value, `read by` names existing
Rules; an absent file passes; the live table passes; a template key missing from the live corpus
warns (`missing_keys`, #180)."""
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
    def test_contract(self):
        self.assertEqual((pf.ENTITY, pf.CORPUS, pf.TRANSACTION, pf.FIELDS), ("preference", "preferences", False, ("key", "value", "allowed", "read by")))
    def test_parse_keeps_escaped_pipes(self):
        header, rows = pf.parse(HEAD + ROWS)
        self.assertEqual(header, list(pf.FIELDS)); self.assertEqual(rows[0][2], "`separate` | `with-done`")
        self.assertEqual(pf.alternatives(rows[0][2]), ["separate", "with-done"]); self.assertIsNone(pf.alternatives("free text"))
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
    def test_live_table_passes(self):
        self.assertEqual(pf.check_package(dyadlib.repo_root()), [])
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


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(pf, "core", pf.CORPUS)
        self.assertEqual(dyadlib.check_invariants(pf, extra), len(pf.INVARIANTS) + 4)
        names = [n for n, _ in pf.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
