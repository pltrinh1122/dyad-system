"""<module>.py: its behaviour; the module is in the runner's pass (crafts/syseng/rules/invariants.md).
Copy to dyad/tests/test_<module>.py (or crafts/<craft>/tests/test_<module>.py) beside the module's other tests.
No per-module hold test: importing the module below runs `dyadlib.enforce(INVARIANTS, __name__)`, so the import is
the assertion (verifiable-code.md p5). A test that only exercises a condition a fail-loud check now guards goes; a
behaviour test — an output, a message, a side effect — stays. A test may `assert`; production code never does (p3)."""
import shutil, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))   # adjust to reach dyad/scripts
import dyadlib
mod = dyadlib.load_module(Path(__file__).resolve().parents[1] / "scripts" / "<module>.py", "<module>")   # enforces INVARIANTS

class PassTests(unittest.TestCase):
    def test_module_is_in_the_runners_pass(self):
        """TREE_INVARIANTS never run at import; the pass is where they run, so the module must be in it."""
        runner = dyadlib.runner_module()
        self.assertIn("<module>", [label for label, _, _ in runner.invariant_modules()])

class BehaviourTests(unittest.TestCase):
    def test_write_state_writes_the_new_state(self):
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        mod.write_state(d / "row", "a", "b")
        self.assertEqual((d / "row").read_text(), "b\n")

if __name__ == "__main__":
    unittest.main()
