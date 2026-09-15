"""registry.py (the sysarch craft's guard, entity `projector`; #160): discovery order, test present, main
defined, one craft per surface, core entities reachable or listed as leaves; the live repo passes."""
import shutil, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
registry = dyadlib.load_guard_file(Path(__file__).resolve().parents[2] / "guards" / "registry.py")

def fixture(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        f = root / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
    return root

GOOD = {"crafts/b/projectors/project_erd.py": "def main():\n    return 0\n", "crafts/b/tests/test_project_erd.py": "# t\n",
        "crafts/a/projectors/project_zed.py": "def main():\n    return 0\n", "crafts/a/tests/test_project_zed.py": "# t\n"}

class Projectors(unittest.TestCase):
    def test_discovery_sorted_by_craft_then_surface(self):
        root = fixture(GOOD)
        self.addCleanup(shutil.rmtree, root)
        ps = registry.projectors(root)
        self.assertEqual([(p["surface"], p["craft"]) for p in ps], [("zed", "a"), ("erd", "b")])
        self.assertEqual(ps[1], {"surface": "erd", "craft": "b", "module": "crafts/b/projectors/project_erd.py", "test": "crafts/b/tests/test_project_erd.py"})
        self.assertEqual(registry.check_projectors(root, ps), [])
        self.assertEqual(registry.projectors(root / "nowhere"), [])
    def test_missing_test_fails(self):
        root = fixture({k: v for k, v in GOOD.items() if "test_project_erd" not in k})
        self.addCleanup(shutil.rmtree, root)
        self.assertEqual(registry.check_projectors(root, registry.projectors(root)), ["crafts/b/projectors/project_erd.py: no crafts/b/tests/test_project_erd.py (projection.md p2)"])
    def test_no_main_fails(self):
        root = fixture({**GOOD, "crafts/b/projectors/project_erd.py": "x = 1\n"})
        self.addCleanup(shutil.rmtree, root)
        self.assertEqual(registry.check_projectors(root, registry.projectors(root)), ["crafts/b/projectors/project_erd.py: defines no main() (projection.md p4)"])
    def test_two_crafts_one_surface_fails(self):
        root = fixture({**GOOD, "crafts/a/projectors/project_erd.py": "def main():\n    return 0\n", "crafts/a/tests/test_project_erd.py": "# t\n"})
        self.addCleanup(shutil.rmtree, root)
        fails = registry.check_projectors(root, registry.projectors(root))
        self.assertEqual(fails, ["surface 'erd' provided by crafts/a and crafts/b (projection.md p4: one craft per surface)"])

class Entities(unittest.TestCase):
    def test_leaves_parsed_from_the_rule(self):
        root = fixture({"references.md": "# r\n\n## Leaves\nkeys `zone` and `craft`, and `reference`.\n\n## When\n`row` is not a leaf.\n"})
        self.addCleanup(shutil.rmtree, root)
        self.assertEqual(registry.leaves(root / "references.md"), {"zone", "craft", "reference"})
        self.assertEqual(registry.leaves(root / "absent.md"), set())
    def test_unreachable_entity_fails(self):
        fails = registry.check_entities({"row": "dyad/guards/agent/rows.py", "zone": "dyad/guards/infra/containment.py", "ghost": "dyad/guards/x/ghost.py"},
                                        {"row", "rule"}, {"zone"})
        self.assertEqual(fails, ["dyad/guards/x/ghost.py: entity 'ghost' is neither a source nor a target in references.REFERENCES nor a leaf in crafts/sysarch/rules/references.md"])
    def test_live_leaves_are_the_unreferenced_core_entities(self):
        ents = registry.core_entities(dyadlib.PKG); refd = registry.referenced_keys(dyadlib.PKG)
        self.assertEqual({e for e in ents if e not in refd}, registry.leaves())

class Live(unittest.TestCase):
    def test_live_repo_passes(self):
        msgs = registry.check_package(dyadlib.repo_root())
        self.assertEqual([m for m in msgs if not m.startswith("warning:")], [])
        self.assertRegex(registry.summary(dyadlib.repo_root()), r"^\d+ projectors in \d+ craft\(s\)$")
    def test_contract_and_card(self):
        self.assertIsNone(dyadlib.contract_problem(registry, "craft", "sysarch", {"craft", "agent"}))
        d = registry.describe(dyadlib.repo_root())
        self.assertEqual([f[0] for f in d["fields"]], list(registry.FIELDS))


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(registry, "craft", "sysarch", {"workstation", "craft"})
        self.assertEqual(dyadlib.check_invariants(registry, extra), len(registry.INVARIANTS) + 4)
        names = [n for n, _ in registry.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
