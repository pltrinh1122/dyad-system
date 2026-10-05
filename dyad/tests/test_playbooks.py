"""The craft play-book and its run-book (#165): `dyad/playbooks/craft-instantiation.md` cites every criterion id
D1, D2, D3', D4, D5, D6 and the plan #153 file; `dyad/runbooks/craft.md` parses with the core runner into the
play-book's steps, declares its own section set, and passes the sysadmin craft's run-book check when that craft is
present; Rule-3 reads the play-book by path and the vocabulary carries `play-book` and `craft-instantiation-criteria`."""
import os, re, sys, unittest
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib, runbook as rb

PLAYBOOK = PKG / "playbooks" / "craft-instantiation.md"
RUNBOOK = PKG / "runbooks" / "craft.md"
CRITERIA = ("D1", "D2", "D3'", "D4", "D5", "D6")
STEPS = ("new", "check", "guards", "tests", "export", "install", "registry", "system-new")

class PlaybookTests(unittest.TestCase):
    def test_playbook_sections_and_criteria(self):
        text = PLAYBOOK.read_text()
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["Trigger", "Default", "craft-instantiation-criteria", "Steps: new craft", "Steps: new dyad system", "Evidence"])
        rows = [r for r in dyadlib.tables(text)[0][1]]
        self.assertEqual(tuple(r[0] for r in rows), CRITERIA)
        self.assertIn("agent-corpus/d-work/plans/153.md", text)
        self.assertIn("dyad/runbooks/craft.md", text)
        for s in STEPS[:2] + ("registry", "export", "system-new"):
            self.assertIn(f"`{s}`", text, s)
    def test_runbook_parses_into_the_steps(self):
        text = RUNBOOK.read_text()
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds], list(STEPS))
        self.assertEqual(rb.declared_sections(text), ["New", "Check", "Guards", "Tests", "Export", "Install", "Registry", "System"])
        self.assertEqual({c.section for c in cmds}, set(rb.declared_sections(text)))
        self.assertEqual(rb.prose_blocks(text), [])
        self.assertEqual([c.name for c in cmds if c.role == "operator"], ["system-new"])
        for c in cmds:
            self.assertTrue(c.cmd, c.name)
            if c.cls != "read-only":
                self.assertNotIn(c.undo, ("", rb.NONE), c.name); self.assertNotIn(c.postcondition, ("", rb.NONE), c.name)
        self.assertIn("craft", rb.core_runbooks(PKG.parent))
    def test_runbook_passes_the_craft_check_when_present(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        guard = dyadlib.find_guard("workstation", "runbooks")
        if guard is None or not hasattr(guard, "declared_sections"):
            self.skipTest("no craft provides a run-book check that reads `# sections:` (sysadmin craft PR of #165)")
        self.assertEqual([m for m in guard.check_runbook(RUNBOOK, PKG.parent) if not m.startswith("warning: ")], [])
    def test_rule_3_and_vocabulary_read_the_playbook(self):
        rule = (PKG / "rules" / "RULE-3-d-work.md").read_text()
        self.assertIn("dyad/playbooks/craft-instantiation.md", rule); self.assertIn("craft-instantiation-criteria", rule)
        voc = (PKG / "vocabulary" / "VOCABULARY.md").read_text()
        self.assertTrue(re.search(r"^\| play-book \|.*\| 3 \| 3 \|$", voc, re.M))
        self.assertTrue(re.search(r"^\| craft-instantiation-criteria \|.*\| 3 \| 3 \|$", voc, re.M))

TRACE_PLAYBOOK = PKG / "playbooks" / "dwork-trace.md"
TRACE_RUNBOOK = PKG / "runbooks" / "dwork-trace.md"

class DworkTracePlaybookTests(unittest.TestCase):
    """The d-work trace play-book and its run-book (#213, revision 2): sections, steps, store path, Rule-3's citation."""
    def test_playbook_sections_and_store(self):
        text = TRACE_PLAYBOOK.read_text()
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["Parameter", "Trigger", "Default", "Format", "Reading", "Evidence"])
        self.assertIn("dyad/runbooks/dwork-trace.md", text)
        self.assertIn("<instance>/d-work/traces/<id>.md", text)
        self.assertNotIn("audits/traces", text)
        for s in ("locate", "trace", "compare"):
            self.assertIn(f"`{s}`", text, s)
    def test_runbook_parses_into_the_steps(self):
        text = TRACE_RUNBOOK.read_text()
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds], ["locate", "trace", "compare"])
        self.assertEqual(rb.declared_sections(text), ["Locate", "Trace", "Compare"])
        self.assertEqual({c.section for c in cmds}, set(rb.declared_sections(text)))
        self.assertEqual(rb.prose_blocks(text), [])
        self.assertEqual({c.name: c.cls for c in cmds}, {"locate": "read-only", "trace": "reversible", "compare": "read-only"})
        trace = cmds[1]
        self.assertIn("dwork trace", trace.cmd); self.assertIn("--out", trace.cmd)
        self.assertTrue(trace.undo.startswith("rm ")); self.assertIn("d-work/traces/", trace.undo)
        self.assertIn("test -s", trace.postcondition); self.assertIn("d-work/traces/", trace.postcondition)
        for c in cmds:
            self.assertIn("DWORK", c.cmd, c.name)
        self.assertIn("dwork-trace", rb.core_runbooks(PKG.parent))
    def test_runbook_passes_the_craft_check_when_present(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        guard = dyadlib.find_guard("workstation", "runbooks")
        if guard is None or not hasattr(guard, "declared_sections"):
            self.skipTest("no craft provides a run-book check that reads `# sections:`")
        self.assertEqual([m for m in guard.check_runbook(TRACE_RUNBOOK, PKG.parent) if not m.startswith("warning: ")], [])
    def test_rule_3_and_vocabulary_read_the_playbook(self):
        rule = (PKG / "rules" / "RULE-3-d-work.md").read_text()
        self.assertIn("dyad/playbooks/dwork-trace.md", rule); self.assertIn("d-work trace", rule)
        self.assertIn("<instance>/d-work/traces/<id>.md", rule)
        self.assertIn("preference `dwork-trace`", rule)                  # conditional on the preference (revision 3)
        self.assertIn("`dwork-trace`", TRACE_PLAYBOOK.read_text().split("## Trigger", 1)[1].split("## Default", 1)[0])
        voc = (PKG / "vocabulary" / "VOCABULARY.md").read_text()
        self.assertTrue(re.search(r"^\| d-work trace \|.*\| 3 \| 3 \|$", voc, re.M))

if __name__ == "__main__":
    unittest.main()
