"""Run-book guard tests (crafts/sysadmin/guards/runbooks.py, the craft's server-instances rule; moved from dyad/tests/guards/workstation/ in #155): the
dyad-cmd parser over fixtures; check_package fails on a missing section, a missing field, a prose
shell block, `sudo` under role any, a bad class, a duplicate name; the check output is deterministic;
the constants; the guard's CLI line."""
import contextlib, io, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
rb = dyadlib.load_guard("workstation", "runbooks")

def block(name, cmd, cls="read-only", role="any", undo="none", post="none", scope="nothing"):
    return f"```dyad-cmd\nname: {name}\nclass: {cls}\nrole: {role}\nundo: {undo}\npostcondition: {post}\nscope: {scope}\n\n{cmd}\n```\n"

def runbook_text(extra="", drop_section=None):
    secs = {"Status/health": block("status", "echo up") + block("health", "echo healthy", post="true"),
            "Start": block("start", "touch started", "reversible", undo="rm started", post="[ -f started ]", scope="file started"),
            "Stop": block("stop", "rm -f started", "reversible", undo="touch started", post="! [ -f started ]", scope="file started"),
            "Restart": block("restart", "echo restart", "reversible", undo="none needed", post="false", scope="x"),
            "Logs": block("logs", "printf 'l1\\nl2\\nl3\\nl4\\nl5\\nl6\\nl7\\n'"),
            "Backup": block("backup", "echo b", "reversible", undo="rm b", post="false", scope="x"),
            "Restore": block("restore", "echo r; touch restored", "destructive", "operator", undo="none", post="[ -f restored ]", scope="file restored"),
            "Upgrade": block("upgrade", "echo u", "reversible", undo="x", post="false", scope="x"),
            "Credential rotation": block("rotate", "sudo echo rotate", "reversible", "operator", undo="x", post="false", scope="x"),
            "Data": block("data", "echo d")}
    text = "# Run-book: x\n\nSee `crafts/sysadmin/server/compose.yaml`.\n\n"
    for s, b in secs.items():
        if s == drop_section:
            continue
        text += f"## {s}\nProse before.\n{b}Prose after.\n\n"
    return text + extra

def fixture(text=None, instance="x", server=True):
    root = Path(tempfile.mkdtemp(prefix="dyad-rb-"))
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    d = root / rb.DEFAULT_RUNBOOKS; d.mkdir(parents=True)
    (d / f"{instance}.md").write_text(runbook_text() if text is None else text)
    if server:
        (root / "crafts" / "sysadmin" / "server").mkdir(parents=True)
        (root / "crafts" / "sysadmin" / "server" / "compose.yaml").write_text("services: {}\n")
    return root

class ParseTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
    def test_parse_fields_sections_and_multiline_command(self):
        text = runbook_text(block("multi", "a\nb\nc", "reversible", undo="u", post="p", scope="s"))
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds][:3], ["status", "health", "start"])
        by = {c.name: c for c in cmds}
        self.assertEqual(by["start"].section, "Start"); self.assertEqual(by["start"].cls, "reversible")
        self.assertEqual(by["start"].undo, "rm started"); self.assertEqual(by["start"].postcondition, "[ -f started ]")
        self.assertEqual(by["start"].scope, "file started"); self.assertEqual(by["start"].cmd, "touch started")
        self.assertEqual(by["multi"].cmd, "a\nb\nc"); self.assertEqual(by["multi"].section, "Data")
        self.assertTrue(all(c.line > 0 for c in cmds))
    def test_parse_ignores_other_fences_and_tolerates_missing_keys(self):
        text = "## Data\n```text\nname: nope\n\necho no\n```\n```dyad-cmd\nname: only\n\necho x\n```\n```dyad-cmd\nname: empty\nclass: read-only\n```\n"
        cmds = rb.parse_text(text)
        self.assertEqual([c.name for c in cmds], ["only", "empty"])
        self.assertEqual(cmds[0].cls, ""); self.assertEqual(cmds[0].cmd, "echo x"); self.assertEqual(cmds[1].cmd, "")
    def test_prose_blocks_and_credential_words(self):
        self.assertEqual(rb.prose_blocks("```bash\nx\n```\n```\ny\n```\n```text\nz\n```\n```dyad-cmd\nname: a\n\nb\n```\n"), [(1, "bash"), (4, "untagged")])
        self.assertEqual(rb.needs_operator("sudo ls"), "sudo"); self.assertEqual(rb.needs_operator("echo PASSWORD"), "password")
        self.assertIsNone(rb.needs_operator("echo tokens")); self.assertIsNone(rb.needs_operator("echo pseudo"))
    def test_constants_and_contract(self):
        self.assertEqual(rb.FIELDS, ("name", "class", "role", "undo", "postcondition", "scope"))
        self.assertEqual(set(rb.CLASSES), {"read-only", "reversible", "destructive"}); self.assertIs(rb.CLASSES, dyadlib.HOST_CLASSES)
        self.assertEqual(len(rb.SECTIONS), 10)
        self.assertEqual((rb.ENTITY, rb.CORPUS, rb.TRANSACTION), ("command", "workstation", False))

class CheckTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("DYAD_RUNBOOKS", None); self.roots = []
    def tearDown(self):
        for r in self.roots: shutil.rmtree(r, ignore_errors=True)
    def check(self, text=None, **kw):
        root = fixture(text, **kw); self.roots.append(root)
        return rb.check_package(root)
    def test_good_runbook_passes(self):
        self.assertEqual(self.check(), [])
    def test_no_runbooks_dir_passes(self):
        root = Path(tempfile.mkdtemp()); self.roots.append(root)
        self.assertEqual(rb.check_package(root), [])
    def test_missing_section_fails(self):
        msgs = self.check(runbook_text(drop_section="Backup"))
        self.assertEqual(len(msgs), 1); self.assertIn("section `Backup` missing", msgs[0])
    def test_section_without_command_fails(self):
        msgs = self.check(runbook_text().replace(block("logs", "printf 'l1\\nl2\\nl3\\nl4\\nl5\\nl6\\nl7\\n'"), ""))
        self.assertEqual(len(msgs), 1); self.assertIn("section `Logs` holds no dyad-cmd command", msgs[0])
    def test_missing_field_fails(self):
        msgs = self.check(runbook_text().replace("scope: file started\n", "", 1))
        self.assertEqual(len(msgs), 1); self.assertIn("command start lacks `scope:`", msgs[0])
    def test_prose_block_fails(self):
        msgs = self.check(runbook_text("## Extra\n```bash\ndocker ps\n```\n"))
        self.assertEqual(len(msgs), 1); self.assertIn("bash block is prose", msgs[0])
        msgs = self.check(runbook_text("```\ndocker ps\n```\n"))
        self.assertEqual(len(msgs), 1); self.assertIn("untagged block is prose", msgs[0])
    def test_sudo_with_role_any_fails(self):
        msgs = self.check(runbook_text().replace('role: operator\nundo: x\npostcondition: false\nscope: x\n\nsudo echo rotate', 'role: any\nundo: x\npostcondition: false\nscope: x\n\nsudo echo rotate'))
        self.assertEqual(len(msgs), 1); self.assertIn("names `sudo` but role is `any`; must be `operator`", msgs[0])
    def test_credential_word_with_role_any_fails(self):
        msgs = self.check(runbook_text(block("tok", "cat token")))
        self.assertEqual(len(msgs), 1); self.assertIn("names `token`", msgs[0])
    def test_bad_class_role_name_and_duplicate_fail(self):
        msgs = self.check(runbook_text(block("Bad_Name", "x", cls="harmless", role="root")))
        self.assertEqual(len(msgs), 3, msgs)
        self.assertTrue(any("class `harmless` is not one of" in m for m in msgs))
        self.assertTrue(any("role `root` is not one of" in m for m in msgs))
        self.assertTrue(any("is not [a-z][a-z0-9-]*" in m for m in msgs))
        msgs = self.check(runbook_text(block("status", "echo again")))
        self.assertEqual(len(msgs), 1); self.assertIn("name `status` defined twice", msgs[0])
    def test_state_change_needs_undo_and_postcondition(self):
        msgs = self.check(runbook_text(block("rev", "x", "reversible", undo="none", post="none", scope="s")))
        self.assertEqual(len(msgs), 2); self.assertTrue(any("names no undo" in m for m in msgs)); self.assertTrue(any("names no postcondition" in m for m in msgs))
        msgs = self.check(runbook_text(block("des", "x", "destructive", "operator", undo="none", post="none", scope="s")))
        self.assertEqual(len(msgs), 1); self.assertIn("destructive command des names no postcondition", msgs[0])
    def test_empty_command_fails(self):
        msgs = self.check(runbook_text("## Extra\n```dyad-cmd\nname: e\nclass: read-only\nrole: any\nundo: none\npostcondition: none\nscope: s\n```\n"))
        self.assertEqual(len(msgs), 1); self.assertIn("has no command line", msgs[0])
    def test_no_server_counterpart_warns(self):
        msgs = self.check(server=False)
        self.assertEqual(len(msgs), 1); self.assertTrue(msgs[0].startswith("warning: ")); self.assertIn("no server counterpart", msgs[0])
    def test_check_output_deterministic(self):
        root = fixture(runbook_text(block("tok", "cat token") + "```bash\nx\n```\n", drop_section="Data")); self.roots.append(root)
        a = rb.check_package(root); b = rb.check_package(root)
        self.assertEqual(a, b); self.assertGreaterEqual(len(a), 3)
    def test_declared_section_set_replaces_the_default(self):
        """#165: `# sections:` in the header names the run-book's own set; the server-directory warning is skipped."""
        text = "# Run-book: craft\n# sections: One, Two\n\n## One\n" + block("one", "echo one") + "## Two\n" + block("two", "echo two")
        self.assertEqual(self.check(text, server=False), [])
        msgs = self.check(text.replace("## Two\n", "## Other\n"), server=False)
        self.assertEqual(len(msgs), 1); self.assertIn("section `Two` missing (declared in its header)", msgs[0])
    def test_core_runbooks_are_checked_too(self):
        root = fixture(); self.roots.append(root)
        d = root / rb.CORE_RUNBOOKS; d.mkdir(parents=True)
        (d / "craft.md").write_text("# Run-book: craft\n# sections: One\n\n## One\n" + block("one", "echo one"))
        self.assertEqual(rb.check_package(root), []); self.assertEqual(rb.counts(root), (2, 12))
        (d / "craft.md").write_text("# Run-book: craft\n# sections: One, Two\n\n## One\n" + block("one", "echo one"))
        self.assertEqual([m for m in rb.check_package(root) if "craft.md" in m], ["craft.md: section `Two` missing (declared in its header)"])
    def test_runbooks_env_and_summary(self):
        root = fixture(); self.roots.append(root)
        self.assertEqual(rb.counts(root), (1, 11)); self.assertEqual(rb.summary(root), "1 run-books, 11 commands")
        os.environ["DYAD_RUNBOOKS"] = "elsewhere"
        try:
            self.assertEqual(rb.runbooks(root), {}); self.assertEqual(rb.check_package(root), [])
        finally:
            os.environ.pop("DYAD_RUNBOOKS")

class CliTests(unittest.TestCase):
    def test_cli_prints_the_rule_19_line(self):
        root = fixture()
        r = subprocess.run([sys.executable, str(Path(rb.__file__)), str(root)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "ok   [rule-19] 1 run-book(s), 11 commands")
        (root / rb.DEFAULT_RUNBOOKS / "x.md").write_text(runbook_text("```bash\nx\n```\n"))
        r = subprocess.run([sys.executable, str(Path(rb.__file__)), str(root)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1); self.assertIn("FAIL [rule-19] x.md:", r.stderr)
        shutil.rmtree(root, ignore_errors=True)


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(rb, "craft", "sysadmin", {"workstation", "craft"})
        self.assertEqual(dyadlib.check_invariants(rb, extra), len(rb.INVARIANTS) + 4)
        names = [n for n, _ in rb.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
