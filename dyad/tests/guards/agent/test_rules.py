import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
ri = dyadlib.load_guard("agent", "rules")

GOOD = """# Rule-X: t

**Intent:** Do the thing.
**Target:** a thing

## Boundaries (out of scope)
- not this

## Conditions (triggers)
- when that
- and that

## Other
- a bullet that must not count
"""

class RuleIntegrityTests(unittest.TestCase):
    def test_good(self):
        self.assertEqual(ri.check("g", GOOD), [])
        self.assertEqual(ri.counts(GOOD), {"intent": 1, "target": 1, "boundaries": 1, "conditions": 2})
    def test_missing_intent(self):
        self.assertIn("Intent count 0", ri.check("x", GOOD.replace("**Intent:** Do the thing.\n", ""))[0])
    def test_two_targets(self):
        self.assertIn("Target count 2", ri.check("x", GOOD + "**Target:** again\n")[0])
    def test_empty_boundaries(self):
        self.assertIn("Boundaries bullets 0", ri.check("x", GOOD.replace("- not this\n", ""))[0])
    def test_bullets_outside_sections_do_not_count(self):
        text = GOOD.replace("- when that\n- and that\n", "") + "- stray\n"
        self.assertIn("Conditions bullets 0", ri.check("x", text)[0])
    def test_live_package_all_ok(self):
        oks, fails = ri.check_rules()
        self.assertGreaterEqual(len(oks), 15)   # the live verdict itself is the agent/rules guard's (#227)

class TendedScanTests(unittest.TestCase):
    """#156: check_tended warns (never fails) on Agent-process tokens in a Tended craft's rules; README exempt."""
    def test_warns_per_file_readme_exempt(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "a.md").write_text("Before this the Agent asks a counter-prompt.\n"); (d / "b.md").write_text("The operator runs it.\n"); (d / "README.md").write_text("the Agent reads every file here\n")
        out = ri.check_tended(d, ["the Agent", "counter-prompt", "Y/N:"], rel_to=d.parent)
        self.assertEqual(len(out), 1); self.assertTrue(out[0].startswith("warning: ")); self.assertIn("a.md: mentions 'the Agent', 'counter-prompt'", out[0]); self.assertIn("inference decides", out[0])
        self.assertEqual(ri.check_tended(d, ["nothing-here"]), [])

if __name__ == "__main__":
    unittest.main()
