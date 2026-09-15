"""invariants.py (the syseng craft's guard, entity `invariant`; #162): the ast scans over fixtures (assert outside tests,
model constants without INVARIANTS, exemptions with reasons, stale exemptions), the entry-shape check over the runner's
pass, and the live repo passes with zero asserts."""
import shutil, sys, tempfile, types, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
inv = dyadlib.load_guard_file(Path(__file__).resolve().parents[2] / "guards" / "invariants.py")

def tree(files: dict[str, str]) -> tuple[Path, Path]:
    root = Path(tempfile.mkdtemp()); pkg = root / "dyad"
    for rel, text in files.items():
        f = root / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
    return root, pkg

class ScanTests(unittest.TestCase):
    def scan(self, files, exempt=()):
        root, pkg = tree(files); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return inv.scan(root, pkg, list(exempt))[0]
    def test_clean_tree_passes(self):
        self.assertEqual(self.scan({"dyad/scripts/a.py": "X = (1, 2)\nINVARIANTS = [('x', lambda: True)]\n", "dyad/tests/test_a.py": "assert True\n",
                                    "crafts/c/guards/g.py": "S = 'no model'\n", "crafts/c/tests/guards/test_g.py": "assert 1\n"}), [])
    def test_assert_outside_tests_fails_by_ast_not_grep(self):
        msgs = self.scan({"dyad/scripts/a.py": "# assert in a comment\ns = 'assert in a string'\ndef f():\n    assert s, 'real'\n", "crafts/c/projectors/p.py": "assert 1\n"})
        self.assertEqual(msgs, ["crafts/c/projectors/p.py:1: `assert` in craft code (invariants.md p3: an invariant, never assert)",
                                "dyad/scripts/a.py:4: `assert` in craft code (invariants.md p3: an invariant, never assert)"])
    def test_model_constant_without_invariants_fails(self):
        msgs = self.scan({"dyad/scripts/a.py": "FIELDS = ('a',)\nSTATES = frozenset({'x'})\nname = [1]\nHEAD = '<html>'\n", "dyad/scripts/b.py": "T: dict = {}\nINVARIANTS = []\n"})
        self.assertEqual(msgs, ["dyad/scripts/a.py: defines FIELDS, STATES but no INVARIANTS (invariants.md p1)"])
    def test_exemptions_need_a_reason_and_must_match(self):
        files = {"crafts/c/server/r.py": "GUARDS = ('x',)\n"}
        self.assertEqual(self.scan(files, [("crafts/*/server/*.py", "container code")]), [])
        self.assertEqual(self.scan(files, [("crafts/*/server/*.py", "")]), ["invariants_rules.txt: exempt crafts/*/server/*.py has no reason"])
        # a crafts/ glob matching no file at all belongs to a craft not installed here: a warning (dyad-system #1); one that matches files none of which needs it is stale
        self.assertEqual(self.scan({"dyad/scripts/a.py": "x = 1\n"}, [("crafts/*/server/*.py", "r")]), ["warning: invariants_rules.txt: exempt crafts/*/server/*.py matches no file here (a craft not installed); not checked"])
        self.assertEqual(self.scan({"crafts/c/server/plain.py": "x = 1\n"}, [("crafts/*/server/*.py", "r")]), ["invariants_rules.txt: exempt crafts/*/server/*.py matches no module that needs it (stale)"])
        self.assertEqual(self.scan({"dyad/scripts/a.py": "x = 1\n"}, [("dyad/scripts/gone.py", "r")]), ["invariants_rules.txt: exempt dyad/scripts/gone.py matches no module that needs it (stale)"])
    def test_syntax_error_reported(self):
        self.assertTrue(self.scan({"dyad/scripts/a.py": "def (\n"})[0].startswith("dyad/scripts/a.py: does not parse"))
    def test_model_constants_and_declares(self):
        import ast
        t = ast.parse("A = [1]\nB: tuple = (1,)\nC = set()\nD = 'str'\nE = re.compile('x')\nf = {}\nINVARIANTS: list = []\n")
        self.assertEqual(inv.model_constants(t), ["A", "B", "C"]); self.assertTrue(inv.declares_invariants(t))
        self.assertFalse(inv.declares_invariants(ast.parse("X = 1\n")))

class EntryTests(unittest.TestCase):
    def test_entry_shape_over_a_fake_runner(self):
        good = types.ModuleType("good"); good.INVARIANTS = [("a-b", lambda: True)]
        bad = types.ModuleType("bad"); bad.INVARIANTS = [("Bad Name", lambda: True), ("x", lambda: True), ("x", lambda: False), "not-a-pair", ("y", 3)]
        notlist = types.ModuleType("nl"); notlist.INVARIANTS = {"a": lambda: True}
        runner = types.SimpleNamespace(invariant_modules=lambda: [("good", good, [("z", lambda: True)]), ("bad", bad, []), ("nl", notlist, [])])
        saved = dyadlib.runner_module; dyadlib.runner_module = lambda pkg=None: runner
        try:
            msgs = inv.check_entries(); es = inv.entries()
        finally:
            dyadlib.runner_module = saved
        self.assertEqual(msgs, ["bad: name 'Bad Name' is not kebab-case", "bad: name 'x' declared twice", "bad: entry 'not-a-pair' is not a (name, callable) pair",
                                "bad: entry ('y', 3) is not a (name, callable) pair", "nl: INVARIANTS is not a list"])
        self.assertEqual([e for e in es if e[0] == "good"], [("good", "a-b", True), ("good", "z", True)])
        self.assertIn(("bad", "x", False), es)

class LiveTests(unittest.TestCase):
    def test_live_repo_passes(self):
        msgs = inv.check_package(dyadlib.repo_root())
        self.assertEqual([m for m in msgs if not m.startswith("warning:")], [])   # an absent craft's exempt line warns (dyad-system #1)
        self.assertRegex(inv.summary(), r"^\d+ invariants in \d+ modules, 0 asserts outside tests$")
        es = inv.entries(); self.assertGreaterEqual(len(es), 100); self.assertTrue(all(h for _, _, h in es), [e for e in es if not e[2]])
        self.assertEqual(sorted(inv.exemptions()), [("crafts/*/server/*.py", inv.exemptions()[0][1])])
    def test_contract_card_and_invariants(self):
        self.assertEqual((inv.ENTITY, inv.CORPUS, inv.TRANSACTION), ("invariant", "craft", False))
        d = inv.describe(dyadlib.repo_root()); self.assertEqual([f[0] for f in d["fields"]], list(inv.FIELDS)); self.assertGreater(d["observed"], 0)
        self.assertEqual(dyadlib.check_invariants(inv, dyadlib.contract_invariants(inv, "craft", "syseng", {"craft"})), len(inv.INVARIANTS) + 4)

if __name__ == "__main__":
    unittest.main()
