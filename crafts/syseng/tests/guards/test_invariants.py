"""invariants.py (the syseng craft's guard, entity `invariant`; #162, amended #203): the ast scans over fixtures (assert
outside tests, model constants without INVARIANTS, exemptions with reasons, stale exemptions), the entry-shape check over
the runner's pass and both lists, the import-time `enforce` call, the audit-hook purity check, and the live repo passes
with zero asserts."""
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

def fake_runner(*modules):
    """Swap dyadlib.runner_module for one whose pass is `modules` ((label, module, extra) triples); returns the undo."""
    runner = types.SimpleNamespace(invariant_modules=lambda: list(modules))
    saved = dyadlib.runner_module; dyadlib.runner_module = lambda pkg=None: runner
    return lambda: setattr(dyadlib, "runner_module", saved)

class TreeInvariantsTests(unittest.TestCase):
    """(iii) over both lists (#203): TREE_INVARIANTS has the same entry shape, and a name is unique across the two."""
    def test_tree_list_shape_and_names_unique_across_lists(self):
        m = types.ModuleType("m"); m.INVARIANTS = [("a", lambda: True)]; m.TREE_INVARIANTS = [("a", lambda: True), ("b", lambda: False), ("Bad", lambda: True)]
        nl = types.ModuleType("nl"); nl.INVARIANTS = []; nl.TREE_INVARIANTS = {"x": lambda: True}
        self.addCleanup(fake_runner(("m", m, []), ("nl", nl, [])))
        self.assertEqual(inv.check_entries(), ["m: name 'a' declared twice", "m: name 'Bad' is not kebab-case", "nl: TREE_INVARIANTS is not a list"])
        self.assertEqual([e for e in inv.entries() if e[0] == "m"], [("m", "Bad", True), ("m", "a", True), ("m", "a", True), ("m", "b", False)])
    def test_a_tree_list_alone_declares(self):
        import ast
        self.assertTrue(inv.declares_invariants(ast.parse("X = (1,)\nTREE_INVARIANTS = [('x', lambda: True)]\n")))
        self.assertEqual(inv.model_constants(ast.parse("TREE_INVARIANTS = []\nINVARIANTS = []\n")), [])

ENFORCED = "INVARIANTS = [('x', lambda: True)]\ndyadlib.enforce(INVARIANTS, __name__)\n"

class EnforceTests(unittest.TestCase):
    """(iv) (#203): a module declaring INVARIANTS calls dyadlib.enforce(INVARIANTS, __name__) at module level, after the
    list's last binding; a summary warning while dyadlib.enforce does not exist; fails only under ENFORCE_FAILS_UNDER."""
    def problem(self, text):
        import ast
        return inv.enforcement_problem(ast.parse(text))
    def test_the_call_shapes(self):
        self.assertIsNone(self.problem(ENFORCED))
        self.assertIsNone(self.problem("INVARIANTS = []\nenforce(INVARIANTS, __name__)\n"))          # dyadlib's own form
        self.assertIsNone(self.problem("X = 1\n"))                                                    # declares nothing
        missing = "declares INVARIANTS but never calls dyadlib.enforce(INVARIANTS, __name__) at module level"
        self.assertEqual(self.problem("INVARIANTS = []\n"), missing)
        self.assertEqual(self.problem("INVARIANTS = []\nif True:\n    dyadlib.enforce(INVARIANTS, __name__)\n"), missing)   # may never run
        self.assertEqual(self.problem("INVARIANTS = []\ndef f():\n    dyadlib.enforce(INVARIANTS, __name__)\n"), missing)
        self.assertEqual(self.problem("INVARIANTS = []\ndyadlib.enforce(TREE_INVARIANTS, __name__)\n"), missing)   # the tree list never runs at import
        self.assertEqual(self.problem("INVARIANTS = []\ndyadlib.enforce(INVARIANTS, __name__)\nINVARIANTS.append(('y', lambda: True))\n"),
                         "dyadlib.enforce at line 2 precedes INVARIANTS' last binding at line 3: later entries are never enforced")
        self.assertIsNotNone(self.problem("INVARIANTS = []\ndyadlib.enforce(INVARIANTS, __name__)\nINVARIANTS += []\n"))
    def check(self, present, fails_under=()):
        root, pkg = tree({"dyad/scripts/a.py": "INVARIANTS = []\n", "dyad/scripts/ok.py": ENFORCED, "dyad/tests/test_a.py": "INVARIANTS = []\n",
                          "crafts/c/guards/g.py": "INVARIANTS = []\n", "crafts/c/scripts/s.py": "INVARIANTS = []\n", "crafts/c/guards/fine.py": ENFORCED})
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return inv.check_enforce(root, pkg, present, fails_under)
    def test_absent_enforce_is_one_summary_warning(self):
        self.assertEqual(self.check(False), ["warning: dyadlib.enforce does not exist yet (the core's protocol code, plan #203 P2): 1 module(s) under dyad/ "
                                             "and 2 under crafts/ declare INVARIANTS without the import-time call (invariants.md p1); not checked per module until it does"])
    def test_present_warns_per_core_module_and_per_craft(self):
        self.assertEqual(self.check(True), [
            "warning: dyad/scripts/a.py: declares INVARIANTS but never calls dyadlib.enforce(INVARIANTS, __name__) at module level (invariants.md p1; fails from plan #203 P3)",
            "warning: crafts/c: 2 module(s) do not enforce INVARIANTS at import (invariants.md p1; a craft follow-up): guards/g.py, scripts/s.py"])
    def test_fails_under_the_core_once_p3_names_it(self):
        msgs = self.check(True, ("dyad",))
        self.assertEqual(msgs[0], "dyad/scripts/a.py: declares INVARIANTS but never calls dyadlib.enforce(INVARIANTS, __name__) at module level (invariants.md p1)")
        self.assertTrue(msgs[1].startswith("warning: crafts/c: 2 module(s)"))                      # a craft's stays a warning
    def test_the_default_reads_dyadlib(self):
        root, pkg = tree({"dyad/scripts/a.py": ENFORCED}); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self.assertEqual(inv.check_enforce(root, pkg), [])                                          # compliant: no line whether or not enforce exists

IMPURE = '''import os
from pathlib import Path
class dyadlib:                                   # a stand-in, so the fixture imports without the core's enforce
    enforce = staticmethod(lambda invariants, name: None)
HERE = Path(__file__)
INVARIANTS = [
    ("pure", lambda: (1, 2) == (1, 2)),
    ("raises-but-pure", lambda: 1 / 0),
    ("opens-a-file", lambda: bool(HERE.read_text())),
    ("stats-a-file", lambda: HERE.is_file()),
    ("reads-the-environment", lambda: os.environ.get("HOME") is not None or True),
    ("lists-a-directory", lambda: bool(os.listdir(HERE.parent))),
]
'''

class AuditTests(unittest.TestCase):
    """(v) (#203): every INVARIANTS predicate runs in a child under an audit hook; I/O fails where the module enforces
    at import and warns where it does not yet. A fixture whose invariants open, stat, list and read the environment."""
    def fixture(self, enforced: bool, name: str) -> types.ModuleType:
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        f = d / f"{name}.py"; f.write_text(IMPURE + ("dyadlib.enforce(INVARIANTS, __name__)\n" if enforced else ""))
        self.addCleanup(sys.modules.pop, name, None)
        return dyadlib.load_module(f, name)
    def test_audit_names_each_impure_predicate_and_its_events(self):
        mod = self.fixture(False, "dyad_test_impure_a")
        broken = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, broken, ignore_errors=True)
        (broken / "broken.py").write_text("raise RuntimeError('no import')\nINVARIANTS = []\n")
        impure, problems = inv.audit([("fx", mod.__name__, mod.__file__), ("br", "dyad_test_broken", str(broken / "broken.py"))])
        self.assertEqual(impure, [("fx", "lists-a-directory", ["os.listdir"]), ("fx", "opens-a-file", ["open"]),
                                  ("fx", "reads-the-environment", ["os.environ"]), ("fx", "stats-a-file", ["os.stat"])])
        self.assertEqual(problems, ["warning: br: the audit child could not load it: RuntimeError: no import"])
        self.assertEqual(inv.audit([]), ([], []))                                                    # nothing to audit: no child
    def test_severity_follows_enforcement(self):
        on, off = self.fixture(True, "dyad_test_impure_on"), self.fixture(False, "dyad_test_impure_off")
        pure = types.ModuleType("nofile"); pure.INVARIANTS = [("x", lambda: open(__file__).close() or True)]   # no __file__: never audited
        self.addCleanup(fake_runner(("on", on, []), ("off", off, []), ("nofile", pure, [])))
        msgs = inv.check_audit()
        self.assertIn("on: invariant 'opens-a-file' does I/O (open); move it to TREE_INVARIANTS (invariants.md p1)", msgs)
        self.assertIn("warning: off: invariant 'opens-a-file' does I/O (open); move it to TREE_INVARIANTS (invariants.md p1); not enforced at import yet", msgs)
        self.assertEqual(len(msgs), 8)                                                               # four impure predicates per module
        self.assertFalse(any("pure'" in m or "nofile" in m for m in msgs))

class ContribExemptionTests(unittest.TestCase):
    """d-work #15: an installed craft's own invariants_contrib.txt is discovered and merged into
    the scan — a contributed exempt is honoured like a native one, but a malformed or stale
    contributed line names its own craft, never invariants_rules.txt; a craft that ships none, or
    is not installed at all, contributes nothing (its would-be rows are simply absent, never a
    stale native row)."""
    def craft_root(self, name: str, contrib_text: str | None, files: dict[str, str]) -> tuple[Path, Path]:
        """One tree holding a fake installed craft (`name`) plus `files`. `python_files` derives
        the crafts tree from `pkg`'s own parent, so `pkg` and the scanned files must share one
        root — unlike `craft_pkg`/`tree()` as two independent temp dirs, which silently scans an
        empty tree and was this d-work's own first draft bug, caught by these very tests."""
        root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        pkg = root / "dyad"; pkg.mkdir()
        cdir = root / "crafts" / name / "guards"; cdir.mkdir(parents=True)
        (root / "crafts" / name / "VERSION").write_text("0.1.0\n")
        if contrib_text is not None:
            (cdir / "invariants_contrib.txt").write_text(contrib_text)
        for rel, text in files.items():
            f = root / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
        return root, pkg
    def check(self, root: Path, pkg: Path) -> list[str]:
        """check_package minus check_entries's own concern (a runner to introspect, #162's own
        job): a fake runner with nothing to enter, so these tests stay about contrib_exemptions.
        `exemptions()` (no path) always reads the *real*, live invariants_rules.txt regardless of
        `pkg` — check_package takes no `data` param, unlike naming.py's — so its one live row
        (`crafts/*/server/*.py`, absent from every scratch tree here) always warns too; filtered
        out, since it is not this contribution mechanism's concern."""
        runner = types.SimpleNamespace(invariant_modules=lambda: [])
        saved = dyadlib.runner_module; dyadlib.runner_module = lambda pkg=None: runner
        try:
            msgs = inv.check_package(root, pkg)
        finally:
            dyadlib.runner_module = saved
        return [m for m in msgs if "crafts/*/server/*.py" not in m]
    def test_contributed_exempt_is_honoured(self):
        root, pkg = self.craft_root("fake", "exempt: crafts/fake/x.py # reference code\n", {"crafts/fake/x.py": "M = (1,)\n"})
        self.assertEqual(self.check(root, pkg), [])
    def test_contributed_exempt_stale_names_its_craft(self):
        root, pkg = self.craft_root("fake", "exempt: crafts/fake/x.py # r\n", {"crafts/fake/x.py": "x = 1\n"})   # exists, but needs no exempt: stale
        msgs = self.check(root, pkg)
        self.assertIn("crafts/fake/guards/invariants_contrib.txt: exempt crafts/fake/x.py matches no module that needs it (stale)", msgs)
    def test_contributed_exempt_without_reason_names_its_craft(self):
        root, pkg = self.craft_root("fake", "exempt: crafts/fake/x.py\n", {"crafts/fake/x.py": "M = (1,)\n"})
        msgs = self.check(root, pkg)
        self.assertIn("crafts/fake/guards/invariants_contrib.txt: exempt crafts/fake/x.py has no reason", msgs)
    def test_craft_without_a_contrib_file_contributes_nothing(self):
        root, pkg = self.craft_root("fake", None, {"crafts/fake/x.py": "M = (1,)\n"})   # installed, but ships no invariants_contrib.txt
        self.assertEqual(inv.contrib_exemptions(pkg), [])
        # its own model constant is unexempted and fails natively, exactly as any craft's would
        self.assertEqual(self.check(root, pkg), ["crafts/fake/x.py: defines M but no INVARIANTS (invariants.md p1)"])
    def test_no_crafts_dir_contributes_nothing(self):
        root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        pkg = root / "dyad"; pkg.mkdir()
        self.assertEqual(inv.contrib_exemptions(pkg), [])

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
