"""Change-log guard tests (crafts/sysadmin/guards/changelog.py; the craft's host-mutation rule, Rule-8 kernel): header equals FIELDS (template too, always), or
FIELDS with OPTIONAL (`actor`) dropped for an instance mid-migration (#216); date form, `#<id>`
d-work, Rule-8 class, non-empty action, an actor in ACTORS where present, an undo for reversible
and destructive rows; an absent change log passes; the live change log passes."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
cl = dyadlib.load_guard("workstation", "changelog")

HEAD = "# Host change log (Rule-8)\n\n| date | d-work | class | action | undo | outcome | actor |\n|------|--------|-------|--------|------|---------|-------|\n"
ROW = "| 2026-09-13 | #7 | reversible | mkdir /x | rmdir /x | applied | agent |\n"
HEAD_NO_ACTOR = "# Host change log (Rule-8)\n\n| date | d-work | class | action | undo | outcome |\n|------|--------|-------|--------|------|---------|\n"
ROW_NO_ACTOR = "| 2026-09-13 | #7 | reversible | mkdir /x | rmdir /x | applied |\n"

def fixture(text: str | None, template: str = HEAD):
    """(root, craft): the template lives in the craft (`crafts/sysadmin/templates/CHANGELOG.md`), #155."""
    root = Path(tempfile.mkdtemp()); pkg = root / "crafts" / "sysadmin"; (pkg / "templates").mkdir(parents=True)
    (pkg / "templates" / "CHANGELOG.md").write_text(template)
    if text is not None:
        (root / "workstation-corpus").mkdir(); (root / "workstation-corpus" / "CHANGELOG.md").write_text(text)
    return root, pkg

class ChangelogTests(unittest.TestCase):
    def test_contract(self):
        self.assertEqual((cl.ENTITY, cl.CORPUS, cl.TRANSACTION, cl.FIELDS), ("changelog", "workstation", False, ("date", "d-work", "class", "action", "undo", "outcome", "actor")))
        self.assertIs(cl.CLASSES, dyadlib.HOST_CLASSES)
        self.assertEqual(cl.OPTIONAL, ("actor",)); self.assertEqual(cl.ACTORS, ("operator", "agent"))
    def test_good_rows_pass(self):
        root, pkg = fixture(HEAD + ROW + "| 2026-09-14 | #8 | destructive | rm -rf /y | none: throwaway data | done | operator |\n| 2026-09-14 | #9 | read-only | first runs | — | done; event: x-1 | agent |\n")
        self.assertEqual(cl.check_package(root, craft=pkg), []); self.assertEqual(cl.summary(root), "3 rows")
    def test_absent_log_passes_and_template_header_checked(self):
        root, pkg = fixture(None); self.assertEqual(cl.check_package(root, craft=pkg), [])
        root, pkg = fixture(None, template="# log\n\n| when | what |\n|---|---|\n")
        msgs = cl.check_package(root, craft=pkg); self.assertEqual(len(msgs), 1); self.assertIn("templates/CHANGELOG.md: header", msgs[0])
    def test_wrong_header_fails(self):
        root, pkg = fixture(HEAD.replace("| undo |", "| revert |") + ROW)
        msgs = cl.check_package(root, craft=pkg); self.assertEqual(len(msgs), 1); self.assertIn("CHANGELOG.md: header", msgs[0])
    def test_bad_cells_fail(self):
        root, pkg = fixture(HEAD + "| yesterday | 7 | harmless |  |  | x | agent |\n")
        msgs = cl.check_package(root, craft=pkg)
        self.assertEqual(len(msgs), 4, msgs)
        for w in ("not YYYY-MM-DD", "is not `#<id>`", "class `harmless`", "empty action"):
            self.assertTrue(any(w in m for m in msgs), w)
    def test_missing_undo_fails_for_reversible_and_destructive_only(self):
        root, pkg = fixture(HEAD + ROW.replace("rmdir /x", "") + "| 2026-09-14 | #8 | read-only | ls |  | ok | agent |\n")
        msgs = cl.check_package(root, craft=pkg); self.assertEqual(len(msgs), 1); self.assertIn("row 1: reversible action with an empty undo", msgs[0])
    def test_cell_count_fails(self):
        root, pkg = fixture(HEAD + "| 2026-09-13 | #7 | reversible |\n")
        msgs = cl.check_package(root, craft=pkg); self.assertEqual(len(msgs), 1); self.assertIn("3 cells, want 7", msgs[0])
    def test_bad_actor_fails(self):
        root, pkg = fixture(HEAD + ROW.replace("| agent |", "| contractor |"))
        msgs = cl.check_package(root, craft=pkg); self.assertEqual(len(msgs), 1); self.assertIn("actor `contractor` is not one of operator, agent", msgs[0])
    def test_instance_header_may_omit_optional_actor_but_template_may_not(self):
        # An instance mid-migration (craft PR merged, workstation PR not yet, #216): the 6-column
        # header and rows still pass, because `actor` is in OPTIONAL.
        root, pkg = fixture(HEAD_NO_ACTOR + ROW_NO_ACTOR)
        self.assertEqual(cl.check_package(root, craft=pkg), [])
        # The template itself is never allowed to lag: check_package's template check is exact FIELDS.
        root, pkg = fixture(HEAD_NO_ACTOR + ROW_NO_ACTOR, template=HEAD_NO_ACTOR)
        msgs = cl.check_package(root, craft=pkg); self.assertEqual(len(msgs), 1); self.assertIn("templates/CHANGELOG.md: header", msgs[0])
    def test_live_changelog_passes(self):
        self.assertEqual(cl.check_package(dyadlib.repo_root()), [])
    def test_describe(self):
        root, pkg = fixture(HEAD + ROW); d = cl.describe(root, pkg)
        self.assertEqual([f[0] for f in d["fields"]], list(cl.FIELDS)); self.assertEqual([f[4] for f in d["fields"]], ["2026-09-13", "#7", "reversible", "mkdir /x", "rmdir /x", "applied", "agent"])
        self.assertIn("observed: reversible", d["fields"][2][2])


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(cl, "craft", "sysadmin", {"workstation", "craft"})
        self.assertEqual(dyadlib.check_invariants(cl, extra), len(cl.INVARIANTS) + 4)
        names = [n for n, _ in cl.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
