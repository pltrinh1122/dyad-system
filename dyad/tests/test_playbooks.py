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
        self.assertEqual(heads, ["Trigger", "Default", "craft-instantiation-criteria", "Steps: a craft here", "Steps: another dyad system", "Evidence"])   # #626 C8
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
AUDIT_RUNBOOK_STEPS = ("report", "hooks", "host", "record")   # #619: the coded checks are the automaton sweep's report
AUDIT_STEPS = AUDIT_RUNBOOK_STEPS   # the play-book names the run-book's steps (#619 PR 2)

class AuditPlaybookTests(unittest.TestCase):
    """The standing audit play-book and its run-book (#223): headings, steps, the watermark's one invariant, vocabulary."""
    def test_playbook_sections_and_watermark(self):
        text = AUDIT_PLAYBOOK.read_text()
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["Trigger", "Steps", "Question", "Evidence", "The self-diagnostic"])   # #626 C2: the cited form
        self.assertIn("dyad/runbooks/audit.md", text)
        self.assertIn("dyad/runbooks/self-diagnostic.md", text)
        self.assertIn("self-diagnostic", rb.core_runbooks(PKG.parent))   # its steps are a core run-book, checked with its own section set
        self.assertIn("**Audited:** tree <hash> \u00b7 python <v> \u00b7 git <v> \u00b7 covered through <sha>, <YYYY-MM-DD>", text)
        self.assertIn("**Fences:** registry <n> lines", text)
        self.assertIn("dyad automaton sweep", text)
        for s in AUDIT_STEPS:
            self.assertIn(f"`{s}`", text, s)
        inc = text.split("### Phase 3b", 1)[1].split("### Phase 4", 1)[0]       # one owner per concern: hardening classifies, the audit does not
        self.assertIn("incident-hardening", inc); self.assertIn("Does not classify", inc)
    def test_runbook_parses_into_the_steps_all_read_only(self):
        text = AUDIT_RUNBOOK.read_text()
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds], list(AUDIT_RUNBOOK_STEPS))
        self.assertEqual(rb.declared_sections(text), ["Report", "Fences", "Drift", "Record"])
        cmd = {c.name: c.cmd for c in cmds}
        self.assertEqual(cmd["report"].strip(), "dyad/bin/dyad automaton sweep")     # no --row: posts and lands nothing
        self.assertIn("audits.py record", cmd["record"])
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
    def test_vocabulary_carries_the_terms(self):
        voc = (PKG / "vocabulary" / "VOCABULARY.md").read_text()
        self.assertTrue(re.search(r"^\| play-book \|.*\| 3 \| 3 \|$", voc, re.M))
        self.assertTrue(re.search(r"^\| audit \|.*\| frame \|", voc, re.M))

DWORK_PLAYBOOK = PKG / "playbooks" / "d-work.md"
DWORK_RUNBOOK = PKG / "runbooks" / "d-work.md"
DWORK_STEPS = ("open", "plan", "authorize", "execute", "verify-prs", "evidence", "record", "done-record", "complete",
               "close-landed", "defer", "resume", "sync-mirror")   # #556: four harvested steps
DWORK_GUARDS = ("rows", "plans", "provenance", "sessions", "traces")   # the agent guards whose stores lie under <instance>/d-work/

def _ticks(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)

class DworkPlaybookTests(unittest.TestCase):
    """The d-work play-book and its run-book (#309): headings, steps, and the two tables pinned to the code and the
    guards — the entity table's fields to each guard's FIELDS, the machine table to dyadlib.INPUTS edge by edge."""
    def test_playbook_sections(self):
        text = DWORK_PLAYBOOK.read_text()
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["Parameter", "Trigger", "Entity records", "The machine", "Steps", "Question", "Evidence"])   # #626 C1: the cited form
        self.assertIn("dyad/runbooks/d-work.md", text)
        for s in DWORK_STEPS:
            self.assertIn(f"`{s}`", text, s)
        for name in ("dyadlib.INPUTS", "dyadlib.INPUT_KINDS", "dyadlib.TRANSITIONS", "dyadlib.NEW_STATES", "dyadlib.STATES"):
            self.assertIn(f"`{name}`", text, name)
    def test_entity_table_is_the_guards_fields(self):
        entities = next(t for h, t in dyadlib.tables(DWORK_PLAYBOOK.read_text()) if h[0] == "entity")
        self.assertEqual([_ticks(r[2])[0] for r in entities], list(DWORK_GUARDS))
        for row in entities:
            guard = dyadlib.load_guard("agent", _ticks(row[2])[0])
            want = list(guard.FIELDS) + (list(dyadlib.OPTIONAL_FIELDS) if guard.FIELDS is dyadlib.FIELDS else [])
            self.assertEqual(_ticks(row[3]), want, row[0])
            self.assertTrue(row[1].startswith("`"), row[0])                   # a store path, in the d-work store
    def test_machine_table_is_dyadlib_inputs(self):
        machine = next(t for h, t in dyadlib.tables(DWORK_PLAYBOOK.read_text()) if h[:2] == ["from", "to"])
        table = {}
        for row in machine:
            src = None if row[0] == "\u2014" else row[0]
            table[(src, row[1])] = frozenset(k.strip() for k in row[3].split("\u00b7"))
        self.assertEqual(set(table), set(dyadlib.INPUTS))
        for edge, kinds in table.items():
            self.assertEqual(kinds, dyadlib.INPUTS[edge][1], edge)
        self.assertEqual(len(machine), len({(a, b) for a, t in dyadlib.TRANSITIONS.items() for b in t}) + len(dyadlib.NEW_STATES))
    def test_runbook_parses_into_the_steps(self):
        text = DWORK_RUNBOOK.read_text()
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds], list(DWORK_STEPS))
        self.assertEqual(rb.declared_sections(text), ["Open", "Plan", "Authorize", "Execute", "Evidence", "Record", "Complete", "Defer", "Resume", "Mirror"])
        self.assertEqual({c.section for c in cmds}, set(rb.declared_sections(text)))
        self.assertEqual(rb.prose_blocks(text), [])
        self.assertEqual({c.name for c in cmds if c.cls == "read-only"}, {"plan", "execute", "verify-prs", "evidence"})
        for c in cmds:
            self.assertTrue(c.cmd, c.name); self.assertEqual(c.role, "any", c.name)
            if c.cls != "read-only":
                self.assertNotIn(c.undo, ("", rb.NONE), c.name); self.assertNotIn(c.postcondition, ("", rb.NONE), c.name)
                self.assertIn({"open": "TITLE", "sync-mirror": "MIRROR"}.get(c.name, "DWORK"), c.cmd + c.postcondition, c.name)
        self.assertIn("d-work", rb.core_runbooks(PKG.parent))
    def test_runbook_passes_the_craft_check_when_present(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        guard = dyadlib.find_guard("workstation", "runbooks")
        if guard is None or not hasattr(guard, "declared_sections"):
            self.skipTest("no craft provides a run-book check that reads `# sections:`")
        self.assertEqual([m for m in guard.check_runbook(DWORK_RUNBOOK, PKG.parent) if not m.startswith("warning: ")], [])
    def test_rule_3_reads_the_playbook(self):
        rule = (PKG / "rules" / "RULE-3-d-work.md").read_text()
        self.assertIn("dyad/playbooks/d-work.md", rule); self.assertIn("`dyadlib.INPUTS`", rule)
        voc = (PKG / "vocabulary" / "VOCABULARY.md").read_text()
        self.assertTrue(re.search(r"^\| play-book \|.*\| 3 \| 3 \|$", voc, re.M))

PORT_PLAYBOOK = PKG / "playbooks" / "port.md"
PORT_RUNBOOK = PKG / "runbooks" / "port.md"
PORT_STEPS = ("install", "crafts", "guards", "diff", "patch", "port")

class PortPlaybookTests(unittest.TestCase):
    """The port play-book and its run-book (#353): headings, the three procedures, the steps pinned to the run-book's
    blocks, the bar on a mirror (Rule-2) and the citations the play-book rests on instead of restating them."""
    def test_playbook_sections_procedures_and_citations(self):
        text = PORT_PLAYBOOK.read_text()
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["Parameter", "Trigger", "Default", "Procedures", "Steps", "Evidence"])
        self.assertEqual([l[4:].split(" (")[0] for l in text.splitlines() if l.startswith("### ")], ["Forward", "Diff", "Back"])
        for s in PORT_STEPS:
            self.assertIn(f"`{s}`", text, s)
        for cite in ("dyad/runbooks/port.md", "crafts/sysarch/rules/distribution.md", "crafts/sysadmin/rules/host-install.md",
                     "dyad/rules/RULE-2-no-self-ratify.md", "dyad/rules/RULE-11-distribution-structure.md", "dyad craft diff", "--from", "--relayed-via"):
            self.assertIn(cite, text, cite)
        self.assertIn("nothing is mirrored", text); self.assertIn("never a sync", text)
        self.assertIn("retired craft", text); self.assertIn("never removes it", text)   # #369 C8: retirement ports nothing
    def test_runbook_parses_into_the_steps(self):
        text = PORT_RUNBOOK.read_text()
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds], list(PORT_STEPS))
        self.assertEqual(rb.declared_sections(text), ["Install", "Crafts", "Guards", "Diff", "Patch", "Port"])
        self.assertEqual({c.section for c in cmds}, set(rb.declared_sections(text)))
        self.assertEqual(rb.prose_blocks(text), [])
        self.assertEqual({c.name for c in cmds if c.cls == "read-only"}, {"guards", "diff", "patch"})
        for c in cmds:
            self.assertTrue(c.cmd, c.name); self.assertEqual(c.role, "any", c.name)
            if c.cls != "read-only":
                self.assertNotIn(c.undo, ("", rb.NONE), c.name); self.assertNotIn(c.postcondition, ("", rb.NONE), c.name)
        self.assertIn("SRC", next(c.cmd for c in cmds if c.name == "install")); self.assertIn("--from", next(c.cmd for c in cmds if c.name == "install"))
        self.assertIn("--patch", next(c.cmd for c in cmds if c.name == "patch"))
        self.assertIn("port", rb.core_runbooks(PKG.parent))
    def test_runbook_passes_the_craft_check_when_present(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        guard = dyadlib.find_guard("workstation", "runbooks")
        if guard is None or not hasattr(guard, "declared_sections"):
            self.skipTest("no craft provides a run-book check that reads `# sections:`")
        self.assertEqual([m for m in guard.check_runbook(PORT_RUNBOOK, PKG.parent) if not m.startswith("warning: ")], [])

if __name__ == "__main__":
    unittest.main()

RELEASE_PLAYBOOK = PKG / "playbooks" / "release.md"
RELEASE_RUNBOOK = PKG / "runbooks" / "release.md"
RELEASE_CLASSES = ("critical-fix", "capability", "enhancement", "breaking", "maintenance")

class ReleasePlaybookTests(unittest.TestCase):
    """The release play-book and its run-book (#493): headings, the five classes and their number, the bundle rule,
    the run-book's two read-only steps, and `number`'s mapping run against a scratch repo's tags."""
    def test_playbook_sections_classes_and_citations(self):
        text = RELEASE_PLAYBOOK.read_text()
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["Parameter", "Trigger", "Classes", "Numbers", "Steps", "Evidence"])
        classes = next(t for h, t in dyadlib.tables(text) if h[0] == "class")
        self.assertEqual(tuple(r[1].strip("`") for r in classes), RELEASE_CLASSES)
        self.assertEqual([r[4] for r in classes][:3], ["patch", "minor", "minor"])
        for cite in ("dyad/runbooks/release.md", "dyad/rules/RULE-11-distribution-structure.md", "`Y/N: release <tag>?`",
                     "highest class", "drift guard", "dyad/playbooks/port.md"):
            self.assertIn(cite, text, cite)
    def test_runbook_parses_into_two_read_only_steps(self):
        text = RELEASE_RUNBOOK.read_text()
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds], ["changes", "number"])
        self.assertEqual(rb.declared_sections(text), ["Changes", "Number"])
        self.assertEqual(rb.prose_blocks(text), [])
        self.assertEqual({c.cls for c in cmds}, {"read-only"})
        number = next(c.cmd for c in cmds if c.name == "number")
        for cls in RELEASE_CLASSES:
            self.assertIn(cls, number, cls)
        self.assertIn("release", rb.core_runbooks(PKG.parent))
    def test_number_maps_each_class_from_the_last_tag(self):
        number = next(c.cmd for c in rb.parse_text(RELEASE_RUNBOOK.read_text()) if c.name == "number")
        with tempfile.TemporaryDirectory() as d:
            env = {**os.environ, **dyadlib.git_env(), "GIT_CONFIG_GLOBAL": os.devnull}
            run = lambda *a: subprocess.run(a, cwd=d, env=env, capture_output=True, text=True, check=True)
            run("git", "init", "-q"); run("git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
            for tag in ("dyad-operator-v0.12.2", "dyad-operator-v0.9.9", "v0.16.2", "cabinet-v1.4.2"):
                run("git", "tag", tag)
            def num(craft, cls):
                r = subprocess.run(["bash", "-c", number], cwd=d, env={**env, "CRAFT": craft, "CLASS": cls}, capture_output=True, text=True)
                return r.returncode, r.stdout.split(" ")[0]
            self.assertEqual(num("dyad-operator", "capability"), (0, "dyad-operator-v0.13.0"))
            self.assertEqual(num("dyad-operator", "enhancement"), (0, "dyad-operator-v0.13.0"))
            self.assertEqual(num("dyad-operator", "critical-fix"), (0, "dyad-operator-v0.12.3"))
            self.assertEqual(num("dyad-operator", "breaking"), (0, "dyad-operator-v0.13.0"))   # 0 major: minor
            self.assertEqual(num("cabinet", "breaking"), (0, "cabinet-v2.0.0"))
            self.assertEqual(num("bundle", "capability"), (0, "v0.17.0"))
            self.assertEqual(num("sysarch", "critical-fix"), (0, "sysarch-v0.0.1"))            # no tag yet
            self.assertEqual(num("bundle", "maintenance")[0], 0)
            self.assertEqual(num("dyad-operator", "bogus")[0], 2)
    def test_runbook_passes_the_craft_check_when_present(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        guard = dyadlib.find_guard("workstation", "runbooks")
        if guard is None or not hasattr(guard, "declared_sections"):
            self.skipTest("no craft provides a run-book check that reads `# sections:`")
        self.assertEqual([m for m in guard.check_runbook(RELEASE_RUNBOOK, PKG.parent) if not m.startswith("warning: ")], [])

GROOM_PLAYBOOK = PKG / "playbooks" / "backlog-groom.md"
GROOM_RUNBOOK = PKG / "runbooks" / "backlog-groom.md"
GROOM_CRITERIA = ("groom-trigger", "backlog-hygiene", "retirement-candidate", "retirement-sweep", "altitude", "promotion",
                  "release-plan", "release-class", "release-number")

class BacklogGroomPlaybookTests(unittest.TestCase):
    """The backlog-grooming play-book and its run-book (#625): headings, every criterion it cites exists and is named, none
    redefined (no outcome table of its own), the record homes it holds, and the run-book's one read-only step."""
    def test_playbook_sections_and_criteria(self):
        text = GROOM_PLAYBOOK.read_text()
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["Parameter", "Trigger", "Steps", "Question", "Evidence"])   # #626 C9
        cited = set(re.findall(r"dyad/dmc/([a-z0-9-]+)\.jsonld", text)) | set(re.findall(r"`dmc:([a-z0-9-]+)`", text))
        self.assertEqual(cited, set(GROOM_CRITERIA))
        for c in cited:
            self.assertTrue((PKG / "dmc" / f"{c}.jsonld").is_file(), c)
        self.assertEqual(dyadlib.tables(text), [])                     # redefines none: the outcomes are the records'
        self.assertIn("dyad/runbooks/backlog-groom.md", text)
        self.assertIn("`report`", text)
        self.assertIn("`Y/N: archive #a, #b, … #k?`", text)          # the one question a run may ask
    def test_records_homed_here_are_cited_masters(self):          # #626 C9: the record is the master, cited by id
        import json
        text = GROOM_PLAYBOOK.read_text()
        for c in ("groom-trigger", "release-plan"):
            rec = json.loads((PKG / "dmc" / f"{c}.jsonld").read_text())
            self.assertEqual(rec["dyad:home"], "playbooks/backlog-groom.md", c)
            self.assertIn(f"dmc:{c}", text, c)
            self.assertFalse(all(t["name"] in text for t in rec["hasDefinedTerm"]), c)   # never restated
    def test_promotion_reads_the_release_plan(self):
        import json
        rec = json.loads((PKG / "dmc" / "promotion.jsonld").read_text())
        self.assertIn("dmc/release-plan.jsonld", rec["dyad:alsoIn"])
        self.assertIn("release plan places in the next release comes first", rec["dyad:precedence"])
        self.assertIn("release plan", DWORK_PLAYBOOK.read_text())
    def test_runbook_parses_into_one_read_only_step(self):
        text = GROOM_RUNBOOK.read_text()
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds], ["report"])
        self.assertEqual(rb.declared_sections(text), ["Report"])
        self.assertEqual(rb.prose_blocks(text), [])
        self.assertEqual((cmds[0].cls, cmds[0].role), ("read-only", "any"))
        self.assertEqual(cmds[0].cmd.strip(), "dyad/bin/dyad board groom")
        self.assertIn("backlog-groom", rb.core_runbooks(PKG.parent))
    def test_runbook_passes_the_craft_check_when_present(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        guard = dyadlib.find_guard("workstation", "runbooks")
        if guard is None or not hasattr(guard, "declared_sections"):
            self.skipTest("no craft provides a run-book check that reads `# sections:`")
        self.assertEqual([m for m in guard.check_runbook(GROOM_RUNBOOK, PKG.parent) if not m.startswith("warning: ")], [])
