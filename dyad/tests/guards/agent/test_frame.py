"""Frame guard tests (agent/frame.py): every `@rules/` import exists and every Rule file is imported
(the #137 gap), every other `@` import resolves; the live frame passes."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
fr = dyadlib.load_guard("agent", "frame")

def fixture(frame: str):
    pkg = Path(tempfile.mkdtemp()) / "dyad"; (pkg / "rules").mkdir(parents=True); (pkg / "vocabulary").mkdir()
    for n in (1, 2): (pkg / "rules" / f"RULE-{n}-x.md").write_text(f"# Rule-{n}\n")
    (pkg / "vocabulary" / "VOCABULARY.md").write_text("| term |\n"); (pkg.parent / "preferences-corpus").mkdir(); (pkg.parent / "preferences-corpus" / "PREFERENCES.md").write_text("p\n")
    (pkg / "CLAUDE.md").write_text(frame); return pkg

GOOD = "# frame\n@rules/RULE-1-x.md\n@rules/RULE-2-x.md\n\n@vocabulary/VOCABULARY.md\n@../preferences-corpus/PREFERENCES.md\n"

class FrameTests(unittest.TestCase):
    def test_contract(self):
        self.assertEqual((fr.ENTITY, fr.CORPUS, fr.TRANSACTION, fr.FIELDS), ("frame", "agent", False, ("@rules/", "@")))
    def test_good_frame_passes(self):
        pkg = fixture(GOOD); self.assertEqual(fr.check_package(pkg.parent, pkg), [])
        self.assertEqual(fr.imports(GOOD), ["rules/RULE-1-x.md", "rules/RULE-2-x.md", "vocabulary/VOCABULARY.md", "../preferences-corpus/PREFERENCES.md"])
    def test_missing_rule_file_fails(self):
        pkg = fixture(GOOD.replace("@rules/RULE-2-x.md", "@rules/RULE-3-x.md"))
        msgs = fr.check_package(pkg.parent, pkg)
        self.assertEqual(len(msgs), 2, msgs); self.assertIn("`@rules/RULE-3-x.md` which does not exist", msgs[0]); self.assertIn("does not import `@rules/RULE-2-x.md` (Rule-2)", msgs[1])
    def test_unimported_rule_fails(self):
        pkg = fixture(GOOD.replace("@rules/RULE-2-x.md\n", ""))
        msgs = fr.check_package(pkg.parent, pkg); self.assertEqual(len(msgs), 1); self.assertIn("(Rule-2)", msgs[0])
    def test_other_import_must_resolve(self):
        pkg = fixture(GOOD.replace("@vocabulary/VOCABULARY.md", "@vocabulary/NOPE.md"))
        msgs = fr.check_package(pkg.parent, pkg); self.assertEqual(len(msgs), 1); self.assertIn("`@vocabulary/NOPE.md`", msgs[0])
    def test_missing_frame_fails(self):
        pkg = fixture(GOOD); (pkg / "CLAUDE.md").unlink(); self.assertEqual(fr.check_package(pkg.parent, pkg), ["CLAUDE.md missing (the frame)"])
    def test_live_frame_passes(self):
        self.assertEqual(fr.check_package(dyadlib.repo_root()), [])
        self.assertIn("Rules", fr.summary())


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(fr, "core", fr.CORPUS)
        self.assertEqual(dyadlib.check_invariants(fr, extra), len(fr.INVARIANTS) + 4)
        names = [n for n, _ in fr.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
