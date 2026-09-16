import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
v = dyadlib.load_guard("agent", "vocabulary")

TABLE = """| term | definition | owner | used by |
|------|------------|-------|---------|
| plan-Y | the Y | 3 | 3 |
| blocking question | stop | 8 | 8 |
| coherent | no clash | 5 | 5 |
"""
RULES = {3: "the plan-`Y` binds", 5: "keep *coherent*", 8: "is a blocking\n  question: stop"}

class VocabularyTests(unittest.TestCase):
    def test_passes_with_emphasis_and_line_break(self):
        self.assertEqual(v.check(TABLE, RULES), (3, []))
    def test_malformed_row(self):
        self.assertIn("malformed", v.check(TABLE + "| x | | 3 | 3 |\n", RULES)[1][0])
    def test_defined_twice(self):
        self.assertIn("defined twice", v.check(TABLE + "| plan-Y | again | 3 | 3 |\n", RULES)[1][0])
    def test_bad_owner_and_missing_rule(self):
        fails = v.check(TABLE + "| t | d | 42 | 43 |\n", RULES)[1]
        self.assertTrue(any("owner '42'" in f for f in fails)); self.assertTrue(any("Rule 43 does not exist" in f for f in fails))
    def test_unmentioned(self):
        self.assertIn("does not mention", v.check(TABLE + "| orphan | d | frame | 5 |\n", RULES)[1][0])
    def test_live_package(self):
        n, fails = v.check_vocabulary()
        self.assertEqual(fails, []); self.assertGreaterEqual(n, 67)
        self.assertEqual(v.check_package(dyadlib.repo_root()), [])
    def test_contract(self):
        self.assertEqual((v.ENTITY, v.CORPUS, v.TRANSACTION, v.FIELDS), ("term", "agent", False, v.COLUMNS))

class CraftVocabularyTests(unittest.TestCase):
    """#156: check_craft — a craft's CRAFT.md is namespaced: well-formed, no duplicate, rule exists, no Agent term."""
    def craft(self, table):
        import tempfile
        d = Path(tempfile.mkdtemp()) / "crafts" / "fx"; (d / "vocabulary").mkdir(parents=True); (d / "rules").mkdir()
        (d / "rules" / "r.md").write_text("# r\n"); (d / "vocabulary" / "CRAFT.md").write_text(table); return d
    def test_good(self):
        d = self.craft("| term | definition | rule |\n|---|---|---|\n| widget | a thing | r |\n")
        self.assertEqual(v.check_craft(dyadlib.PKG, d), []); self.assertEqual(v.craft_terms(d), {"widget"})
    def test_agent_term_and_shape(self):
        d = self.craft("| term | definition | rule |\n|---|---|---|\n| *Plan* | mine | r |\n| widget | a | r |\n| widget | b | nope |\n")
        f = v.check_craft(dyadlib.PKG, d)
        self.assertTrue(any("'*Plan*': equals the Agent vocabulary term 'plan'" in m for m in f), f)
        self.assertTrue(any("'widget': defined twice" in m for m in f), f); self.assertTrue(any("rule 'nope' is not crafts/fx/rules/nope.md" in m for m in f), f)
        d = self.craft("| word | meaning |\n|---|---|\n| x | y |\n")
        self.assertTrue(any("is not term | definition | rule" in m for m in v.check_craft(dyadlib.PKG, d)))
    def test_live_sysadmin_craft(self):
        d = dyadlib.crafts_dir() / "sysadmin"
        if not d.is_dir(): self.skipTest("no sysadmin craft")
        self.assertEqual(v.check_craft(dyadlib.PKG, d), [])


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(v, "core", v.CORPUS)
        self.assertEqual(dyadlib.check_invariants(v, extra), len(v.INVARIANTS) + 4)
        names = [n for n, _ in v.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
