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
