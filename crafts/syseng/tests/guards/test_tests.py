"""tests.py (the syseng craft's guard, entity `test`; #162, amended #336): the mapping moved from check_rule_12 — core scripts
and guards, craft guards (tests/guards/), craft projectors and scripts (tests/), exemptions — over a fixture and the live
repo; and the component clause (#336): a `dyad/<kind>/<component>/` or `crafts/<craft>/<kind>/<component>/` holding its own
`tests/` maps every module under it, sub-packages included, to `<component>/tests/test_<stem>.py`, a shared stem failing."""
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
        self.assertEqual(tg.summary(root, pkg), "5 modules mapped, 2 tests present, 0 components")

class ComponentTests(unittest.TestCase):
    """The component clause (#336): a packaged component under any kind, core or craft, with its own tests/."""
    def tree(self, files):
        root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        for rel in files:
            f = root / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text("")
        return root, root / "dyad"
    FIXTURE = ("dyad/server/ledgerd/README.md", "dyad/server/ledgerd/ledgerd/__init__.py", "dyad/server/ledgerd/ledgerd/core.py",
               "dyad/server/ledgerd/ledgerd/store.py", "dyad/server/ledgerd/ledgerd/schemas/__init__.py", "dyad/server/ledgerd/ledgerd/schemas/dwork.py",
               "dyad/server/ledgerd/ledgerd/_private.py", "dyad/server/ledgerd/cli.py",
               "dyad/server/ledgerd/tests/__init__.py", "dyad/server/ledgerd/tests/test_core.py", "dyad/server/ledgerd/tests/test_dwork.py",
               "dyad/server/ledgerd/tests/test_cli.py", "dyad/server/ledgerd/tests/helper.py",
               "dyad/scripts/a.py", "dyad/tests/test_a.py", "dyad/tests/guards/agent/test_g.py")
    def test_component_is_discovered_and_its_modules_map_to_its_own_tests(self):
        root, pkg = self.tree(self.FIXTURE)
        self.assertEqual(tg.components(pkg), [pkg / "server" / "ledgerd"])
        comp = pkg / "server" / "ledgerd"
        # recursively, sub-packages included; `_`-prefixed (so __init__.py) dropped; nothing under tests/
        self.assertEqual([str(m.relative_to(comp)) for m in tg.component_modules(comp)], ["cli.py", "ledgerd/core.py", "ledgerd/schemas/dwork.py", "ledgerd/store.py"])
        self.assertEqual(tg.test_for(comp / "ledgerd" / "schemas" / "dwork.py", pkg), comp / "tests" / "test_dwork.py")
        self.assertEqual(tg.test_for(comp / "cli.py", pkg), comp / "tests" / "test_cli.py")
        self.assertIsNone(tg.component_of(comp / "tests" / "helper.py", pkg))                 # a test is never a mapped module
        self.assertIsNone(tg.component_of(pkg / "scripts" / "a.py", pkg))                     # flat mappings are untouched
        self.assertEqual(tg.test_for(pkg / "scripts" / "a.py", pkg), pkg / "tests" / "test_a.py")
        # one missing test fails, with the component path in the message; the flat core module still maps flat
        self.assertEqual(tg.check_package(root, pkg), ["dyad/server/ledgerd/ledgerd/store.py: no dyad/server/ledgerd/tests/test_store.py (verifiable-code.md p4)"])
        self.assertEqual([m["module"] for m in tg.mapping(pkg)],
                         ["dyad/scripts/a.py", "dyad/server/ledgerd/cli.py", "dyad/server/ledgerd/ledgerd/core.py", "dyad/server/ledgerd/ledgerd/schemas/dwork.py", "dyad/server/ledgerd/ledgerd/store.py"])
        self.assertEqual(tg.summary(root, pkg), "5 modules mapped, 4 tests present, 1 components")
    def test_stem_collision_across_sub_packages_fails_clearly(self):
        root, pkg = self.tree(self.FIXTURE + ("dyad/server/ledgerd/ledgerd/schemas/core.py", "dyad/server/ledgerd/tests/test_store.py"))
        self.assertEqual(tg.check_package(root, pkg),
                         ["dyad/server/ledgerd: modules dyad/server/ledgerd/ledgerd/core.py, dyad/server/ledgerd/ledgerd/schemas/core.py share the stem 'core': "
                          "both map to dyad/server/ledgerd/tests/test_core.py (verifiable-code.md p4, the component clause)"])
    def test_a_directory_without_tests_is_not_a_component_and_a_tests_tree_never_is(self):
        root, pkg = self.tree(("dyad/server/plain/plain/core.py", "dyad/server/plain/README.md",            # no tests/: not a component — unmapped, as before #336
                               "dyad/tests/guards/tests/test_x.py", "dyad/tests/guards/x.py",             # a tests tree holding a `tests/` is not a kind
                               "crafts/c/tests/guards/tests/test_y.py", "crafts/c/tests/guards/y.py", "crafts/c/VERSION"))
        self.assertEqual(tg.components(pkg), []); self.assertEqual(tg.check_package(root, pkg), [])
        self.assertIsNone(tg.component_of(pkg / "server" / "plain" / "plain" / "core.py", pkg))
    def test_craft_component_maps_the_same_way(self):
        root, pkg = self.tree(("crafts/c/VERSION", "crafts/c/server/relay/relay/__init__.py", "crafts/c/server/relay/relay/main.py",
                               "crafts/c/server/relay/tests/test_main.py", "crafts/c/server/relay/util.py",
                               "crafts/c/guards/w.py", "crafts/c/tests/guards/test_w.py"))
        comp = root / "crafts" / "c" / "server" / "relay"
        self.assertEqual(tg.components(pkg), [comp])
        self.assertEqual(tg.test_for(comp / "relay" / "main.py", pkg), comp / "tests" / "test_main.py")
        self.assertEqual(tg.test_for(root / "crafts" / "c" / "guards" / "w.py", pkg), root / "crafts" / "c" / "tests" / "guards" / "test_w.py")
        self.assertEqual(tg.check_package(root, pkg), ["crafts/c/server/relay/util.py: no crafts/c/server/relay/tests/test_util.py (verifiable-code.md p4)"])

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
