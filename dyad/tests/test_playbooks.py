"""The craft play-book and its run-book (#165): `dyad/playbooks/craft-instantiation.md` cites every criterion id
D1, D2, D3', D4, D5, D6 and the plan #153 file; `dyad/runbooks/craft.md` parses with the core runner into the
play-book's steps, declares its own section set, and passes the sysadmin craft's run-book check when that craft is
present; Rule-3 reads the play-book by path and the vocabulary carries `play-book` and `craft-instantiation-criteria`."""
import os, re, subprocess, sys, tempfile, unittest
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

AUDIT_PLAYBOOK = PKG / "playbooks" / "audit.md"
AUDIT_RUNBOOK = PKG / "runbooks" / "audit.md"
AUDIT_STEPS = ("survey", "regression", "fences", "drift", "incidents", "record")

class AuditPlaybookTests(unittest.TestCase):
    """The standing audit play-book and its run-book (#223): headings, steps, the watermark's one invariant, vocabulary."""
    def test_playbook_sections_and_watermark(self):
        text = AUDIT_PLAYBOOK.read_text()
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["Trigger", "Phase 0 \u2014 Survey (the idempotence gate)", "Phase 1 \u2014 Regression",
                                 "Phase 2 \u2014 Fences (ungated)", "Phase 3 \u2014 Drift (detect only)", "Phase 3b \u2014 Incidents",
                                 "Phase 4 \u2014 Record", "Conduct"])
        self.assertIn("dyad/runbooks/audit.md", text)
        self.assertIn("**Audited:** tree <hash> \u00b7 python <v> \u00b7 git <v> \u00b7 covered through <sha>, <YYYY-MM-DD>", text)
        self.assertIn("**Fences:** registry <n> lines", text)
        self.assertIn("dyad check --evidence", text)
        for s in AUDIT_STEPS:
            self.assertIn(f"`{s}`", text, s)
        inc = text.split("## Phase 3b", 1)[1].split("## Phase 4", 1)[0]       # one owner per concern: hardening classifies, the audit does not
        self.assertIn("incident-hardening", inc); self.assertIn("Does not classify", inc)
    def test_runbook_parses_into_the_steps_all_read_only(self):
        text = AUDIT_RUNBOOK.read_text()
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds], list(AUDIT_STEPS))
        self.assertEqual(rb.declared_sections(text), ["Survey", "Regression", "Fences", "Drift", "Incidents", "Record"])
        self.assertEqual({c.section for c in cmds}, set(rb.declared_sections(text)))
        self.assertEqual(rb.prose_blocks(text), [])
        for c in cmds:
            self.assertTrue(c.cmd, c.name); self.assertEqual((c.cls, c.role), ("read-only", "any"), c.name)
        self.assertIn("audit", rb.core_runbooks(PKG.parent))
    def test_runbook_passes_the_craft_check_when_present(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        guard = dyadlib.find_guard("workstation", "runbooks")
        if guard is None or not hasattr(guard, "declared_sections"):
            self.skipTest("no craft provides a run-book check that reads `# sections:`")
        self.assertEqual([m for m in guard.check_runbook(AUDIT_RUNBOOK, PKG.parent) if not m.startswith("warning: ")], [])
    def test_survey_watermark_ignores_dated_records_and_counts_everything_else(self):
        """Plan #223 A1: the record an audit commits must not change the tree it hashes, or no audit is ever unchanged."""
        survey = next(c for c in rb.parse_text(AUDIT_RUNBOOK.read_text()) if c.name == "survey")
        env = {k: v for k, v in os.environ.items() if k not in ("DYAD_INSTANCE", "DYAD_RUNBOOKS")}
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            def git(*a):
                subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", t, *a], check=True, capture_output=True)
            def write(rel, text):
                (d / rel).parent.mkdir(parents=True, exist_ok=True); (d / rel).write_text(text)
            def run():
                r = subprocess.run(["bash", "-o", "pipefail", "-c", survey.cmd], cwd=t, env=env, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                live = re.search(r"^live: (tree \w+ \u00b7 python \S+ \u00b7 git \S+) \u00b7 head", r.stdout, re.M)
                self.assertTrue(live, r.stdout)
                return live.group(1), re.search(r"^verdict: (\w+)", r.stdout, re.M).group(1)
            git("init", "-q"); (d / "dyad" / "bin").mkdir(parents=True)
            os.symlink(PKG / "bin" / "dyad-python", d / "dyad" / "bin" / "dyad-python")          # untracked: never in the hash
            write("agent-corpus/audits/INCIDENTS.md", "| 2026-10-05 | #1 | a | b | c |\n"); write("code.txt", "x\n")
            git("add", "-A"); git("commit", "-qm", "base")
            base, verdict = run(); self.assertEqual(verdict, "no")                               # no record: first exercise
            write("agent-corpus/audits/2026-10-05-audit.md", f"**Audited:** {base} \u00b7 covered through abc, 2026-10-05\n")
            git("add", "-A"); git("commit", "-qm", "the record")
            self.assertEqual(run(), (base, "unchanged"))                                         # the record is not in the hash
            write("agent-corpus/audits/2026-10-06-sweep.md", "another dated record\n"); git("add", "-A"); git("commit", "-qm", "dated")
            self.assertEqual(run(), (base, "unchanged"))
            write("agent-corpus/audits/INCIDENTS.md", "| 2026-10-05 | #1 | a | b | c |\n| 2026-10-06 | #2 | d | e | f |\n")
            git("add", "-A"); git("commit", "-qm", "an incident")
            self.assertEqual(run()[1], "changed")                                                # INCIDENTS.md is undated: it counts
            self.assertNotEqual(run()[0], base)
    def test_vocabulary_carries_the_terms(self):
        voc = (PKG / "vocabulary" / "VOCABULARY.md").read_text()
        self.assertTrue(re.search(r"^\| play-book \|.*\| 3 \| 3 \|$", voc, re.M))
        self.assertTrue(re.search(r"^\| audit \|.*\| frame \|", voc, re.M))

if __name__ == "__main__":
    unittest.main()
