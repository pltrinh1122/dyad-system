"""Live-test support tests (d-work #171): the store predicates over a fixture instance (absent, seeded-only,
populated), the craft predicates over a fixture package, and each `require_*` skipping with its stated reason.
Every case here is a fixture case — this module is the one that must run identically in an empty install."""
import os, tempfile, unittest, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dyadlib, livetest


def instance(populated: bool, seeds: bool = True) -> Path:
    """A temp repo root whose `<instance>/d-work/` holds the install seeds and, when `populated`, one row
    and one plan."""
    root = Path(tempfile.mkdtemp())
    d = root / "inst" / "d-work"; (d / "rows").mkdir(parents=True); (d / "plans").mkdir()
    if seeds:
        (d / "VERSION").write_text("0.0.0\n"); (d / "rows" / "README.md").write_text("# rows\n")
    if populated:
        (d / "rows" / "7.md").write_text("id: 7\n"); (d / "plans" / "7.md").write_text("# plan\n")
    return root


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.prev = os.environ.get("DYAD_INSTANCE"); os.environ["DYAD_INSTANCE"] = "inst"
    def tearDown(self):
        os.environ.pop("DYAD_INSTANCE", None)
        if self.prev is not None: os.environ["DYAD_INSTANCE"] = self.prev

    def test_store_files_skips_absent_paths_and_sorts(self):
        root = instance(populated=True); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        rows = root / "inst" / "d-work" / "rows"
        self.assertEqual([p.name for p in livetest.store_files(rows)], ["7.md", "README.md"])
        self.assertEqual([p.name for p in livetest.store_files(rows, pattern=livetest.ROW_GLOB)], ["7.md"])
        self.assertEqual(livetest.store_files(root / "nope"), [])                       # absent == empty
        self.assertEqual(livetest.store_files(rows / "7.md"), [rows / "7.md"])          # a file counts as one
        self.assertEqual(livetest.store_files(root / "nope", rows, pattern=livetest.ROW_GLOB), [rows / "7.md"])

    def test_store_empty_is_the_negation(self):
        root = instance(populated=False); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        rows = root / "inst" / "d-work" / "rows"
        self.assertFalse(livetest.store_empty(rows))                                    # the seeded README is a file
        self.assertTrue(livetest.store_empty(rows, pattern=livetest.ROW_GLOB))
        self.assertTrue(livetest.store_empty(root / "nope"))

    def test_instance_is_empty_ignores_the_install_seeds(self):
        empty = instance(populated=False); self.addCleanup(shutil.rmtree, empty, ignore_errors=True)
        full = instance(populated=True); self.addCleanup(shutil.rmtree, full, ignore_errors=True)
        bare = instance(populated=False, seeds=False); self.addCleanup(shutil.rmtree, bare, ignore_errors=True)
        self.assertTrue(livetest.instance_is_empty(empty)); self.assertTrue(livetest.instance_is_empty(bare))
        self.assertFalse(livetest.instance_is_empty(full))
        (full / "inst" / "d-work" / "rows" / "7.md").unlink()
        self.assertFalse(livetest.instance_is_empty(full))                              # the plan file alone is enough
        (full / "inst" / "d-work" / "plans" / "7.md").unlink()
        self.assertTrue(livetest.instance_is_empty(full))


class CraftTests(unittest.TestCase):
    def test_craft_predicates_over_a_fixture_package(self):
        root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        pkg = root / "dyad"; pkg.mkdir()
        self.assertEqual(livetest.crafts_installed(pkg), [])                            # a core-only install
        self.assertFalse(livetest.craft_installed("sysadmin", pkg))
        for c in ("sysarch", "sysadmin"):
            (root / "crafts" / c).mkdir(parents=True); (root / "crafts" / c / "VERSION").write_text("0.1.0\n")
        self.assertEqual(livetest.crafts_installed(pkg), ["sysadmin", "sysarch"])       # sorted by name
        self.assertTrue(livetest.craft_installed("sysadmin", pkg))
        self.assertFalse(livetest.craft_installed("nope", pkg))

    def test_live_repo_state_matches_the_predicates(self):
        """The one live assertion of this module: whatever this install is, the predicates agree with it."""
        pkg = dyadlib.PKG
        self.assertEqual(livetest.crafts_installed(pkg), [p.name for p in dyadlib.craft_dirs(pkg)])
        self.assertEqual(livetest.instance_is_empty(), not dyadlib.read_rows() and
                         livetest.store_empty(dyadlib.instance() / "d-work" / "plans", pattern=livetest.ROW_GLOB))


class RequireTests(unittest.TestCase):
    """Each `require_*` raises unittest's skip with a reason that names its class (EMPTY or ABSENT)."""
    def case(self) -> livetest.LiveCase:
        class C(livetest.LiveCase):
            def runTest(self): pass
        return C()

    def skip_reason(self, fn, *a, **kw) -> str:
        with self.assertRaises(unittest.SkipTest) as cm:
            fn(*a, **kw)
        return str(cm.exception)

    def test_require_store_skips_with_the_empty_reason(self):
        c = self.case(); root = instance(populated=True); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        rows = root / "inst" / "d-work" / "rows"
        self.assertEqual(c.require_store("d-work row", rows, pattern=livetest.ROW_GLOB), [rows / "7.md"])
        r = self.skip_reason(c.require_store, "d-work row", root / "nope")
        self.assertTrue(r.startswith(livetest.EMPTY)); self.assertIn("d-work row", r)

    def test_require_instance_skips_on_an_empty_instance(self):
        c = self.case(); root = instance(populated=False); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        prev = os.environ.get("DYAD_INSTANCE"); os.environ["DYAD_INSTANCE"] = str(root / "inst")
        try:
            r = self.skip_reason(c.require_instance)
            self.assertTrue(r.startswith(livetest.EMPTY)); self.assertIn("d-work row", r)
            (root / "inst" / "d-work" / "rows" / "7.md").write_text("id: 7\n")
            c.require_instance()                                                        # no skip once a row exists
        finally:
            os.environ.pop("DYAD_INSTANCE", None)
            if prev is not None: os.environ["DYAD_INSTANCE"] = prev

    def test_require_craft_and_guard_skip_with_the_absent_reason(self):
        c = self.case()
        r = self.skip_reason(c.require_craft, "nope", "alsonope")
        self.assertTrue(r.startswith(livetest.ABSENT)); self.assertIn("nope, alsonope", r)
        c.require_craft(*livetest.crafts_installed())                                   # whatever is installed passes
        r = self.skip_reason(c.require_guard, "workstation", "nosuchentity")
        self.assertTrue(r.startswith(livetest.ABSENT)); self.assertIn("workstation/nosuchentity", r)
        self.assertIs(c.require_guard("agent", "rows"), dyadlib.load_guard("agent", "rows"))   # a core guard is always there


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/verifiable-code.md p5: one test asserts every invariant of the module holds."""
    def test_invariants_hold(self):
        self.assertEqual(dyadlib.check_invariants(livetest), len(livetest.INVARIANTS)); self.assertTrue(livetest.INVARIANTS)


if __name__ == "__main__":
    unittest.main()
