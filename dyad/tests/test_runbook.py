"""Rule-19 run-book runner tests (d-work #150): a read-only command yields an event line of the right
shape, a satisfied postcondition short-circuits with `already`, a failed postcondition is recorded, a
role mismatch and a destructive command without a tty refuse with exit 2 and no event; the CLI; `new`
seeds a run-book from the sysadmin craft's template and refuses to overwrite; live: the instance's
run-books pass the guard. Since #155 the parser and the event store's primitives are the runner's (core,
so `dyad runbook` works with no craft) and the sysadmin craft's guards re-export them; the check is the
craft guard's (crafts/sysadmin/tests/guards/test_runbooks.py)."""
import contextlib, io, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import runbook as rb
import dyadlib, livetest
rbg = dyadlib.find_guard("workstation", "runbooks")     # the sysadmin craft's guard (crafts/sysadmin/guards/runbooks.py);
                                                        # None on a core-only install, where the cases using it skip (#171)

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
    text = "# Run-book: x\n\nSee `crafts/lan-git/server/compose.yaml`.\n\n"
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

class RunTests(livetest.LiveCase):
    def setUp(self):
        os.environ.pop("DYAD_RUNBOOKS", None); self.root = fixture(); self.out = io.StringIO()
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], check=True)
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
    def events(self):
        return rb.read_events(rb.events_path(self.root, "x"))
    def test_read_only_command_yields_an_event_of_the_right_shape(self):
        ev = rb.run(self.root, "x", "logs", "agent", out=self.out)
        self.assertEqual(rb.exit_code(ev), 0)
        lines = self.events(); self.assertEqual(len(lines), 1); e = lines[0]
        self.assertEqual(list(e), list(rb.EVENT_FIELDS))                       # key order = EVENT_FIELDS
        self.assertEqual((e["role"], e["instance"], e["name"], e["class"], e["exit"], e["postcondition"]), ("agent", "x", "logs", "read-only", 0, "n/a"))
        self.assertEqual(e["cmd"], "printf 'l1\\nl2\\nl3\\nl4\\nl5\\nl6\\nl7\\n'"); self.assertEqual(e["scope"], "nothing")
        self.assertEqual(e["output_tail"], "l3\nl4\nl5\nl6\nl7")                # last five lines
        self.assertEqual(e["output_sha256"], __import__("hashlib").sha256(b"l1\nl2\nl3\nl4\nl5\nl6\nl7\n").hexdigest())
        self.assertRegex(e["ts"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"); self.assertRegex(e["id"], r"^x-\d{8}T\d{6}Z-logs$")
        self.assertRegex(e["commit"], r"^[0-9a-f]{7,}$"); self.assertEqual(len(e["runbook_sha256"]), 64)
        self.assertIsInstance(e["duration_ms"], int)
        text = self.out.getvalue()
        self.assertIn("commit: ", text); self.assertIn(e["runbook_sha256"], text)
        self.assertIn("$ printf 'l1", text)                                     # the native line, printed before it runs
        self.assertIn("event x-", text)
    def test_read_only_postcondition_is_tested_after(self):
        ev = rb.run(self.root, "x", "health", "operator", out=self.out)
        self.assertEqual(ev.postcondition, "ok"); self.assertEqual(ev.role, "operator")
    def test_postcondition_already_satisfied_skips_the_command(self):
        (self.root / "started").write_text("")
        ev = rb.run(self.root, "x", "start", "agent", out=self.out)
        self.assertEqual((ev.exit, ev.postcondition, ev.output_tail), (0, "already", "")); self.assertIn("already satisfied", self.out.getvalue())
        self.assertEqual(rb.exit_code(ev), 0); self.assertEqual(self.events()[0]["postcondition"], "already")
    def test_postcondition_tested_after_a_state_change(self):
        ev = rb.run(self.root, "x", "start", "agent", out=self.out)
        self.assertEqual((ev.exit, ev.postcondition), (0, "ok")); self.assertTrue((self.root / "started").exists())
        ev = rb.run(self.root, "x", "restart", "agent", out=self.out)                # postcondition `false` never holds
        self.assertEqual((ev.exit, ev.postcondition), (0, "failed")); self.assertEqual(rb.exit_code(ev), 1)
        self.assertEqual(len(self.events()), 2)                                      # append-only, in order
    def test_role_refused_no_event(self):
        with self.assertRaises(rb.Refused) as cm:
            rb.run(self.root, "x", "rotate", "agent", out=self.out)
        self.assertEqual(cm.exception.code, 2); self.assertIn("role `operator`", str(cm.exception))
        self.assertFalse(rb.events_path(self.root, "x").exists())
        with self.assertRaises(rb.Refused):
            rb.run(self.root, "x", "status", "root", out=self.out)
    def test_unknown_runbook_or_command_refused(self):
        with self.assertRaises(rb.Refused): rb.run(self.root, "nope", "status", "agent", out=self.out)
        with self.assertRaises(rb.Refused) as cm: rb.run(self.root, "x", "nope", "agent", out=self.out)
        self.assertIn("commands: ", str(cm.exception))
    def test_destructive_without_tty_exits_2_no_event(self):
        # unittest's stdin is not a terminal: the runner fails closed (Rule-18 property 7e)
        prev, sys.stdin = sys.stdin, io.StringIO("Y\n")
        try:
            with self.assertRaises(rb.Refused) as cm:
                rb.run(self.root, "x", "restore", "operator", out=self.out)
        finally:
            sys.stdin = prev
        self.assertEqual(cm.exception.code, 2); self.assertIn("no tty", self.out.getvalue())
        self.assertFalse(rb.events_path(self.root, "x").exists())
    def test_destructive_runs_when_confirmed(self):
        ev = rb.run(self.root, "x", "restore", "operator", confirm_tty=False, out=self.out)   # the test stands in for the tty `Y`
        self.assertEqual((ev.exit, ev.postcondition, ev.cls), (0, "ok", "destructive")); self.assertEqual(rb.exit_code(ev), 0)
        self.assertEqual(self.events()[0]["output_tail"], "r")
    def test_event_line_is_one_json_object(self):
        rb.run(self.root, "x", "status", "agent", out=self.out)
        raw = rb.events_path(self.root, "x").read_text()
        self.assertEqual(raw.count("\n"), 1); self.assertTrue(raw.endswith("\n")); json.loads(raw)
        self.assertEqual(rb.all_events(self.root), {"x": self.events()})
    def test_malformed_event_line_raises(self):
        p = rb.events_path(self.root, "x"); p.parent.mkdir(parents=True); p.write_text('{"id": 1}\nnot json\n')
        with self.assertRaises(ValueError) as cm: rb.read_events(p)
        self.assertIn(":2:", str(cm.exception))
    def test_tail_limits(self):
        self.assertEqual(rb.tail("a\nb\n"), "a\nb"); self.assertEqual(len(rb.tail("x" * 1000)), rb.TAIL_CHARS)
    def test_cli(self):
        self.require_guard("workstation", "runbooks")   # `runbook check` is the craft's guard and exits 2 with no craft (#155)
        env = dict(os.environ, DYAD_RUNBOOKS=str(self.root / rb.DEFAULT_RUNBOOKS)); env.pop("DYAD_ROLE", None)   # the CLI resolves the git root from the package
        py = [sys.executable, str(Path(rb.__file__))]
        r = subprocess.run(py + ["check"], cwd=self.root, env=env, capture_output=True, text=True)
        core = rb.core_runbooks(dyadlib.repo_root())                     # the package's own run-books count too (#165)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), f"ok   [rule-19] {1 + len(core)} run-book(s), {11 + sum(len(rb.parse(p)) for p in core.values())} commands")
        r = subprocess.run(py + ["list", "x"], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0); self.assertIn("rotate", r.stdout); self.assertIn("Credential rotation", r.stdout)
        r = subprocess.run(py + ["run", "x", "rotate"], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2); self.assertIn("refused", r.stderr)                   # default role agent
        r = subprocess.run(py + ["run", "x", "status", "--as", "operator"], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("$ echo up", r.stdout); self.assertEqual(self.events()[0]["role"], "operator")
        r = subprocess.run(py + ["run", "x", "restore", "--as", "operator"], cwd=self.root, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 2); self.assertIn("no tty", r.stdout)
        r = subprocess.run(py + ["check"], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)                                                         # events do not disturb the check
        (self.root / rb.DEFAULT_RUNBOOKS / "x.md").write_text(runbook_text("```bash\nx\n```\n"))
        r = subprocess.run(py + ["check"], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1); self.assertIn("FAIL [rule-19] x.md:", r.stderr)

class ReexportTests(livetest.LiveCase):
    """The craft guards re-export the runner's parser. Absent craft (a core-only install): nothing to
    re-export, so the case skips with its reason (#171)."""
    def test_the_craft_guards_reexport_the_runners_names(self):
        self.require_guard("workstation", "runbooks"); self.require_guard("workstation", "events")
        # #155 amendment: one parser, in the core runner; the craft guards import it (the reverse of #151's direction)
        self.assertIs(rbg.parse_text, rb.parse_text); self.assertIs(rbg.FIELDS, rb.FIELDS); self.assertIs(rbg.Command, rb.Command); self.assertIs(rbg.counts, rb.counts)
        self.assertEqual(rbg.CORPUS, "workstation"); self.assertTrue(str(Path(rbg.__file__)).endswith("crafts/sysadmin/guards/runbooks.py"))
        ev = dyadlib.load_guard("workstation", "events")
        self.assertIs(ev.EVENT_FIELDS, rb.EVENT_FIELDS); self.assertIs(ev.read_events, rb.read_events); self.assertIs(ev.all_events, rb.all_events)
        self.assertEqual(len(rb.EVENT_FIELDS), 15); self.assertEqual(rb.FIELDS, ("name", "class", "role", "undo", "postcondition", "scope"))
        self.assertIs(rb.CLASSES, dyadlib.HOST_CLASSES); self.assertFalse(hasattr(rb, "check_package"))   # the check is the craft's, not the runner's

class NewTests(livetest.LiveCase):
    """`runbook new <instance>` seeds `<runbooks>/<instance>.md` from crafts/*/templates/runbook.md (#155, attack 7):
    the template lives outside <runbooks>, so its placeholders never fail the check; once instantiated the
    check is the guide until every `<…>` is replaced; a second run refuses to overwrite."""
    def setUp(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        self.root = Path(tempfile.mkdtemp(prefix="dyad-rbnew-")); subprocess.run(["git", "init", "-q", str(self.root)], check=True)
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
    def craft_template(self):
        """The installed craft's run-book template, or skip: a core-only install has no craft to seed from."""
        t = rb.template()
        if t is None:
            self.skipTest(f"{livetest.ABSENT}: no installed craft provides crafts/*/templates/runbook.md")
        return t
    def test_template_is_the_crafts(self):
        self.craft_template()
        t = rb.template(); self.assertIsNotNone(t); self.assertTrue(str(t).endswith("crafts/sysadmin/templates/runbook.md"))
        self.assertEqual(rb.template(self.root / "dyad"), None)                                    # no crafts/ beside a bare core
    def test_new_seeds_the_template_then_the_check_guides(self):
        self.craft_template(); self.require_guard("workstation", "runbooks")
        dst = rb.new(self.root, "svc")
        self.assertEqual(dst, self.root / rb.DEFAULT_RUNBOOKS / "svc.md"); self.assertEqual(dst.read_bytes(), rb.template().read_bytes())
        cmds = {c.name for c in rb.parse(dst)}
        self.assertTrue({"status", "health", "start", "stop", "restart", "logs", "backup", "restore", "upgrade", "data"} <= cmds)
        for s in rbg.SECTIONS: self.assertTrue(any(rb.in_section(h, s) for h in rb.sections(dst.read_text())), s)
        msgs = [m for m in rbg.check_package(self.root) if not m.startswith("warning: ")]
        self.assertTrue(msgs, "placeholders must fail the shape check until replaced")                # `rotate-<credential>` is not a name
        self.assertTrue(any("rotate-<credential>" in m for m in msgs))
        with self.assertRaises(rb.Refused) as cm: rb.new(self.root, "svc")
        self.assertIn("not overwritten", str(cm.exception)); self.assertEqual(cm.exception.code, 2)
        self.assertEqual(dst.read_bytes(), rb.template().read_bytes())
    def test_new_without_a_craft_refuses(self):
        with self.assertRaises(rb.Refused) as cm: rb.new(self.root, "svc", pkg=self.root / "dyad")
        self.assertIn("no craft provides a run-book template", str(cm.exception))
    def test_cli_new(self):
        self.craft_template()
        env = dict(os.environ, DYAD_RUNBOOKS=str(self.root / rb.DEFAULT_RUNBOOKS))
        py = [sys.executable, str(Path(rb.__file__))]
        r = subprocess.run(py + ["new", "svc"], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("seeded", r.stdout); self.assertIn("replace every <…> placeholder", r.stdout)
        r = subprocess.run(py + ["new", "svc"], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2); self.assertIn("not overwritten", r.stderr)

class CoreRunbookTests(unittest.TestCase):
    """#165: a core run-book (`dyad/runbooks/<name>.md`) resolves for list/run when the instance has none; its
    events go to the instance's store; `declared_sections` reads the `# sections:` header line."""
    def setUp(self):
        os.environ.pop("DYAD_RUNBOOKS", None); self.root = fixture(); self.out = io.StringIO()
        d = self.root / rb.CORE_RUNBOOKS; d.mkdir(parents=True)
        (d / "craft.md").write_text("# Run-book: craft\n# sections: One, Two\n\n## One\n" + block("one", "echo one") + "## Two\n" + block("two", "echo two"))
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], check=True)
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
    def test_core_runbook_resolves_and_events_go_to_the_instance(self):
        self.assertEqual(sorted(rb.runbooks(self.root)), ["x"]); self.assertEqual(sorted(rb.core_runbooks(self.root)), ["craft"])
        self.assertEqual(sorted(rb.all_runbooks(self.root)), ["craft", "x"]); self.assertEqual(rb.counts(self.root), (2, 13))
        self.assertEqual(rb.runbook_path(self.root, "craft"), self.root / rb.CORE_RUNBOOKS / "craft.md")
        self.assertEqual(rb.runbook_path(self.root, "x"), self.root / rb.DEFAULT_RUNBOOKS / "x.md")
        self.assertEqual([c.name for c in rb.list_commands(self.root, "craft")], ["one", "two"])
        ev = rb.run(self.root, "craft", "one", "agent", out=self.out)
        self.assertEqual((ev.instance, ev.exit), ("craft", 0)); self.assertTrue((self.root / rb.DEFAULT_RUNBOOKS / "events" / "craft.jsonl").exists())
    def test_instance_runbook_shadows_core(self):
        (self.root / rb.DEFAULT_RUNBOOKS / "craft.md").write_text(runbook_text())
        self.assertEqual(rb.runbook_path(self.root, "craft"), self.root / rb.DEFAULT_RUNBOOKS / "craft.md")
    def test_declared_sections(self):
        self.assertEqual(rb.declared_sections("# T\n# sections: A, B ,C\n\n## A\n"), ["A", "B", "C"])
        self.assertEqual(rb.declared_sections("# T\nsections: A\n## A\n"), ["A"])
        self.assertIsNone(rb.declared_sections("# T\n\n## A\n# sections: A\n"))     # after the first section: not a header
        self.assertIsNone(rb.declared_sections(runbook_text()))

class LiveTests(livetest.LiveCase):
    """The instance's run-books pass the guard. Empty instance (a fresh install): no run-book, and no craft
    to check one with, so the case skips with its reason (#171). Skipped too while a run-book still holds
    prose blocks (the workstation-zone conversion of #150 lands in its own PR)."""
    def test_live_runbooks_pass(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        root = dyadlib.repo_root()
        self.require_guard("workstation", "runbooks")
        books = rb.runbooks(root)
        if not books:
            self.skipTest(f"{livetest.EMPTY}: no run-book in this instance")
        if any(not rb.parse(p) for p in books.values()):
            self.skipTest("a run-book is not yet converted to dyad-cmd blocks (workstation PR of #150)")
        msgs = [m for m in rbg.check_package(root) if not m.startswith("warning: ")]   # the check is the craft guard's (#155)
        self.assertEqual(msgs, [])
        for name, p in books.items():
            cmds = {c.name: c for c in rb.parse(p)}
            self.assertIn("health", cmds, name); self.assertNotEqual(cmds["health"].postcondition, rb.NONE, "health postcondition is the pass criterion")
            for c in cmds.values():
                self.assertIn(c.cmd.splitlines()[0].split()[0], c.cmd)   # the native line is the block body


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the runner's INVARIANTS hold; run() refuses before running anything when one is false."""
    def test_invariants_hold(self):
        self.assertEqual(dyadlib.check_invariants(rb), len(rb.INVARIANTS)); self.assertGreaterEqual(len(rb.INVARIANTS), 5)
    def test_run_refuses_on_a_false_invariant_and_writes_no_event(self):
        os.environ.pop("DYAD_RUNBOOKS", None); root = fixture(); out = io.StringIO()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        saved = rb.INVARIANTS; rb.INVARIANTS = saved + [("never", lambda: False)]
        try:
            with self.assertRaises(dyadlib.InvariantError) as cm:
                rb.run(root, "x", "logs", "agent", out=out)
        finally:
            rb.INVARIANTS = saved
        self.assertEqual(cm.exception.failed, ["never"]); self.assertEqual(rb.read_events(rb.events_path(root, "x")), []); self.assertEqual(out.getvalue(), "")

if __name__ == "__main__":
    unittest.main()
