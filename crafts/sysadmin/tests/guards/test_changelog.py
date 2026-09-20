"""Change-log guard tests (crafts/sysadmin/guards/changelog.py; the craft's host-mutation rule, Rule-8 kernel): header equals FIELDS (template too, always), or
FIELDS with OPTIONAL (`actor`) dropped for an instance mid-migration (#216); date form, `#<id>`
d-work, Rule-8 class, non-empty action, an actor in ACTORS where present, an undo for reversible
and destructive rows; an absent change log passes; the live change log passes."""
import shutil, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
cl = dyadlib.load_guard("workstation", "changelog")

class FakeCorpus:
    """The shape `REFERENCES_CONTRIB` extractors and resolvers need from `references.Corpus`,
    without building the real thing: `changelog`/`ops`/`events`/`rows` and `rel()`."""
    def __init__(self, root, changelog=((), ()), ops=None, events=None, rows=None):
        self.root, self.pkg = Path(root), dyadlib.PKG
        self.changelog, self.ops, self.events, self.rows = changelog, ops or {}, events or {}, rows or set()
    def rel(self, p):
        p = Path(p)
        return str(p.relative_to(self.root)) if p.is_relative_to(self.root) else str(p)

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


class ReferencesContribTests(unittest.TestCase):
    """Rule-11 property 2 (`agent-corpus/falsification/extensibility.md` #101, d-work #100 PR 5):
    the two rows this craft now contributes, moved from the core register in PR 2."""
    def test_shape(self):
        self.assertEqual([r[0] for r in cl.REFERENCES_CONTRIB], ["changelog.action->ops", "changelog.event->event"])
        for kind, src, field, ext, tgt, res in cl.REFERENCES_CONTRIB:
            self.assertTrue(callable(ext), kind); self.assertTrue(callable(res), kind)
    def test_action_ops_extracts_the_path(self):
        header = ["date", "d-work", "class", "action", "undo", "outcome"]
        row = ["2026-09-13", "#7", "reversible", "Operator-run: `bash workstation-corpus/ops/7-h1-x.sh`", "rmdir", "ok"]
        c = FakeCorpus(Path("."), changelog=(header, [row]))
        self.assertEqual(cl.changelog_action_ops(c), [("workstation-corpus/CHANGELOG.md row 1 action", "workstation-corpus/ops/7-h1-x.sh")])
    def test_action_ops_no_action_column_yields_nothing(self):
        c = FakeCorpus(Path("."), changelog=(["date"], [["x"]]))
        self.assertEqual(cl.changelog_action_ops(c), [])
    def test_ops_path_resolver_checks_the_real_path(self):
        root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "workstation-corpus" / "ops").mkdir(parents=True)
        (root / "workstation-corpus" / "ops" / "7-h1-x.sh").write_text("#!/bin/bash\n")
        c = FakeCorpus(root)
        self.assertTrue(cl._ops_path_exists(c, "workstation-corpus/ops/7-h1-x.sh"))
        self.assertFalse(cl._ops_path_exists(c, "workstation-corpus/ops/nope.sh"))
    def test_event_outcome_extracts_the_id(self):
        header = ["date", "d-work", "class", "action", "undo", "outcome"]
        row = ["2026-09-14", "#7", "reversible", "x", "stop", "ok; event: x-20260914T120000Z-start"]
        c = FakeCorpus(Path("."), changelog=(header, [row]))
        self.assertEqual(cl.changelog_event_outcome(c), [("workstation-corpus/CHANGELOG.md row 1 outcome", "x-20260914T120000Z-start")])
    def test_event_outcome_no_outcome_column_yields_nothing(self):
        c = FakeCorpus(Path("."), changelog=(["date"], [["x"]]))
        self.assertEqual(cl.changelog_event_outcome(c), [])
    def test_event_id_resolver_checks_the_events_store(self):
        c = FakeCorpus(Path("."), events={"x": [{"id": "x-20260914T120000Z-start"}]})
        self.assertTrue(cl._event_id_exists(c, "x-20260914T120000Z-start"))
        self.assertFalse(cl._event_id_exists(c, "x-20260914T120001Z-start"))
class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(cl, "craft", "sysadmin", {"workstation", "craft"})
        self.assertEqual(dyadlib.check_invariants(cl, extra), len(cl.INVARIANTS) + 4)
        names = [n for n, _ in cl.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
