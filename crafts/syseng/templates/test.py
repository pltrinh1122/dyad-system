"""<module>.py: every invariant holds and is unique by name; the module is in the runner's pass (crafts/syseng/rules/invariants.md).
Copy to dyad/tests/test_<module>.py (or crafts/<craft>/tests/test_<module>.py) beside the module's other tests.
A test may `assert`; production code never does (p3) — the unittest methods below are the form used here."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))   # adjust to reach dyad/scripts
import dyadlib
mod = dyadlib.load_module(Path(__file__).resolve().parents[1] / "scripts" / "<module>.py", "<module>")

class InvariantTests(unittest.TestCase):
    def test_invariants_hold_once_each(self):
        self.assertEqual(dyadlib.check_invariants(mod), len(mod.INVARIANTS))
        names = [n for n, _ in mod.INVARIANTS]
        self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)
        for n in names: self.assertRegex(n, r"^[a-z0-9][a-z0-9_-]*$")
    def test_module_is_in_the_runners_pass(self):
        runner = dyadlib.runner_module()
        self.assertIn("<module>", [label for label, _, _ in runner.invariant_modules()])

if __name__ == "__main__":
    unittest.main()
