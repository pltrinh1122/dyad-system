"""tests.py (the syseng craft's guard, entity `test`; #162): the mapping moved from check_rule_12 — core scripts and guards,
craft guards (tests/guards/), craft projectors and scripts (tests/), exemptions — over a fixture and the live repo."""
import shutil, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
tg = dyadlib.load_guard_file(Path(__file__).resolve().parents[2] / "guards" / "tests.py")

class MappingTests(unittest.TestCase):
    def test_test_for(self):
        pkg = Path("/r/dyad"); crafts = Path("/r/crafts")
        self.assertEqual(tg.test_for(pkg / "scripts" / "dyadlib.py", pkg), pkg / "tests" / "test_dyadlib.py")
        self.assertEqual(tg.test_for(pkg / "guards" / "agent" / "rows.py", pkg), pkg / "tests" / "guards" / "agent" / "test_rows.py")
        self.assertEqual(tg.test_for(crafts / "sysadmin" / "guards" / "events.py", pkg), crafts / "sysadmin" / "tests" / "guards" / "test_events.py")
        self.assertEqual(tg.test_for(crafts / "x" / "scripts" / "tool.py", pkg), crafts / "x" / "tests" / "test_tool.py")
        self.assertEqual(tg.test_for(crafts / "sysarch" / "projectors" / "project_erd.py", pkg), crafts / "sysarch" / "tests" / "test_project_erd.py")
    def test_fixture_missing_test_fails_and_extra_test_is_legal(self):
        root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, root, ignore_errors=True); pkg = root / "dyad"
        for rel in ("dyad/scripts/a.py", "dyad/scripts/package.py", "dyad/scripts/_h.py", "dyad/guards/agent/g.py", "dyad/tests/test_a.py", "dyad/tests/test_extra.py",
                    "crafts/c/guards/w.py", "crafts/c/tests/guards/test_w.py", "crafts/c/projectors/project_x.py", "crafts/c/scripts/s.py", "crafts/c/VERSION"):
            f = root / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text("")
        self.assertEqual(tg.check_package(root, pkg), ["dyad/guards/agent/g.py: no dyad/tests/guards/agent/test_g.py (verifiable-code.md p4)",
                                                       "crafts/c/projectors/project_x.py: no crafts/c/tests/test_project_x.py (verifiable-code.md p4)",
                                                       "crafts/c/scripts/s.py: no crafts/c/tests/test_s.py (verifiable-code.md p4)"])
        self.assertEqual([m["module"] for m in tg.mapping(pkg)], ["dyad/scripts/a.py", "dyad/guards/agent/g.py", "crafts/c/guards/w.py", "crafts/c/projectors/project_x.py", "crafts/c/scripts/s.py"])
        self.assertEqual(tg.summary(root, pkg), "5 modules mapped, 2 tests present")

class LevelsSeedTests(unittest.TestCase):
    """#484: every core test module has a line in the core's levels seed, read by the core's own levels.py."""
    def fixture(self, seed_lines):
        root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, root, ignore_errors=True); pkg = root / "dyad"
        for rel in ("dyad/tests/test_a.py", "dyad/tests/guards/agent/test_g.py", "dyad/tests/helper.py"):
            f = root / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text("")
        (pkg / "scripts").mkdir(parents=True)
        shutil.copy(dyadlib.PKG / "scripts" / "levels.py", pkg / "scripts" / "levels.py")
        if seed_lines is not None:
            (pkg / "templates").mkdir(); (pkg / "templates" / "self-diagnostic-levels.txt").write_text("# seed\n" + "".join(l + "\n" for l in seed_lines))
        return root, pkg
    def test_an_unclassified_module_fails_and_a_complete_seed_passes(self):
        root, pkg = self.fixture(["unit dyad/tests/test_a.py  # a comment"])
        self.assertEqual(tg.unclassified(pkg), ["dyad/tests/guards/agent/test_g.py"])
        seeded = lambda: [m for m in tg.check_package(root, pkg) if "#484" in m]   # the fixture's levels.py has no test: a p4 line, not this one
        self.assertEqual(seeded(), ["dyad/tests/guards/agent/test_g.py: no line in dyad/templates/self-diagnostic-levels.txt "
                                                       "(a test module is classified unit or integration, #484)"])
        root, pkg = self.fixture(["unit dyad/tests/test_a.py", "integration dyad/tests/guards/agent/test_g.py"])
        self.assertEqual(seeded(), [])
    def test_no_seed_skips(self):
        root, pkg = self.fixture(None)
        self.assertEqual(tg.unclassified(pkg), [])
    def test_the_live_seed_is_complete(self):
        self.assertEqual(tg.unclassified(), [])

class LiveTests(unittest.TestCase):
    def test_live_repo_passes(self):
        self.assertEqual(tg.check_package(dyadlib.repo_root()), [])
        ms = tg.mapping(); self.assertTrue(all(m["present"] for m in ms)); self.assertNotIn("dyad/scripts/package.py", [m["module"] for m in ms])
        self.assertIn("crafts/syseng/guards/tests.py", [m["module"] for m in ms])
    def test_contract_card_and_invariants(self):
        self.assertEqual((tg.ENTITY, tg.CORPUS, tg.TRANSACTION), ("test", "craft", False))
        d = tg.describe(dyadlib.repo_root()); self.assertEqual([f[0] for f in d["fields"]], list(tg.FIELDS)); self.assertGreater(d["observed"], 0)
        self.assertEqual(dyadlib.check_invariants(tg, dyadlib.contract_invariants(tg, "craft", "syseng", {"craft"})), len(tg.INVARIANTS) + 4)

if __name__ == "__main__":
    unittest.main()
