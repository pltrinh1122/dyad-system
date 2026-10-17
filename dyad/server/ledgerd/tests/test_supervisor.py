"""ledgerd/supervisor.py: each adapter's rendered unit or plist and the native command lines it prints, over a fake
host (an injected `run` records argv; nothing real is driven), `0 changes` on a second install, the linger refusal
reported; `proc` start/stop for real (a child, a pid file, "not persistent"). Importing the module runs its
INVARIANTS (verifiable-code.md p5); its TREE_INVARIANTS are run here."""
import os, subprocess, sys, time, unittest, unittest.mock
from pathlib import Path
import support
from support import Case
import dyadlib
if not support.MISSING:
    from ledgerd import supervisor as sup

class Fake:
    """A recording `run`: every argv, with scripted return codes per command word."""
    def __init__(self, fail=()):
        self.calls, self.fail = [], set(fail)
    def __call__(self, argv, **kw):
        self.calls.append(list(argv))
        rc = 1 if (argv[0] in self.fail or " ".join(argv[:2]) in self.fail or " ".join(argv[:3]) in self.fail) else 0
        if kw.get("check") and rc:
            raise subprocess.CalledProcessError(rc, argv)
        return subprocess.CompletedProcess(argv, rc, "state = running\n" if argv[:2] == ["launchctl", "print"] and rc == 0 else "", "")

class ContractTests(Case):
    def test_contract_and_tree_invariants(self):
        self.assertEqual(sup.SUPERVISOR_CONTRACT, ("NAME", "install", "uninstall", "start", "stop", "restart", "status", "is_active", "logs"))
        self.assertEqual(tuple(sup.ADAPTERS), sup.NAMES)
        dyadlib.check_invariants(sup)                           # TREE_INVARIANTS: the templates exist and hold every placeholder
        with self.assertRaises(ValueError):
            sup.adapter("cron", self.scratch())
    def test_templates_hold_no_host_path(self):
        for p in sup.TEMPLATES.values():
            text = p.read_text()
            self.assertNotIn("/home", text); self.assertNotIn("/Users", text); self.assertIn("{state}", text)

class SystemdTests(Case):
    def test_rendered_unit_and_install_lines(self):
        state, home = self.scratch(), self.scratch(); fake = Fake(fail=("loginctl",)); out = []
        (state / "ledgerd.conf").write_text("bind: 127.0.0.1\nport: 8731\n")
        a = sup.adapter("systemd", state, python="/v/bin/python3", run=fake, home=home, out=out.append)
        with EnvPatch({"XDG_CONFIG_HOME": "", "USER": "op"}):
            self.assertEqual(a.install(), 0)
        unit = home / ".config" / "systemd" / "user" / sup.UNIT
        text = unit.read_text()
        self.assertIn(f"ExecStart=/v/bin/python3 {sup.RUNNER} ledger serve --state {state}", text)
        self.assertIn("Restart=always", text); self.assertIn("WantedBy=default.target", text); self.assertNotIn("{", text)
        self.assertEqual(fake.calls, [["systemctl", "--user", "daemon-reload"], ["systemctl", "--user", "enable", "--now", sup.UNIT], ["loginctl", "enable-linger", "op"]])
        self.assertTrue(any(l.startswith("$ systemctl --user enable --now") for l in out), "the native line is printed before it runs")
        self.assertTrue(any("loginctl enable-linger refused" in l for l in out)); self.assertEqual(out[-1], "ui-url: http://127.0.0.1:8731/")
        fake.calls.clear()
        with EnvPatch({"XDG_CONFIG_HOME": "", "USER": "op"}):
            self.assertEqual(a.install(), 0)                    # unchanged unit, active -> 0 changes
        self.assertIn("0 changes", out); self.assertEqual(fake.calls, [["systemctl", "--user", "is-active", "--quiet", sup.UNIT]])
        fake.calls.clear(); a.start(); a.stop(); a.status(); a.logs(7); a.uninstall()
        self.assertEqual([c[:3] for c in fake.calls][:4], [["systemctl", "--user", "start"], ["systemctl", "--user", "stop"], ["systemctl", "--user", "status"], ["journalctl", "--user", "-u"]])
        self.assertIn(["systemctl", "--user", "disable", "--now", sup.UNIT], fake.calls); self.assertFalse(unit.exists())
    def test_xdg_config_home_moves_the_unit(self):
        state, home, cfg = self.scratch(), self.scratch(), self.scratch()
        a = sup.adapter("systemd", state, run=Fake(), home=home, out=lambda s: None)
        with EnvPatch({"XDG_CONFIG_HOME": str(cfg)}):
            self.assertEqual(a.unit_path(), cfg / "systemd" / "user" / sup.UNIT)

class LaunchdTests(Case):
    def test_rendered_plist_and_lines(self):
        state, home = self.scratch(), self.scratch(); fake = Fake(); out = []
        a = sup.adapter("launchd", state, python="/v/bin/python3", run=fake, home=home, out=out.append)
        self.assertEqual(a.install(), 0)
        plist = home / "Library" / "LaunchAgents" / sup.PLIST; text = plist.read_text()
        self.assertIn("<string>com.dyad.ledgerd</string>", text); self.assertIn("<string>/v/bin/python3</string>", text)
        self.assertIn(f"<string>{sup.RUNNER}</string>", text); self.assertIn(f"<string>{state}</string>", text)
        self.assertIn(f"<string>{state / sup.LOG_FILE}</string>", text); self.assertIn("<key>KeepAlive</key>", text); self.assertNotIn("{", text)
        self.assertEqual(fake.calls, [["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist)]])
        fake.calls.clear(); a.start(); a.stop(); self.assertTrue(a.is_active()); a.status(); a.uninstall()
        self.assertEqual([c[:2] for c in fake.calls], [["launchctl", "kickstart"], ["launchctl", "kill"], ["launchctl", "print"], ["launchctl", "print"], ["launchctl", "bootout"]])
        self.assertFalse(plist.exists())
        (state / sup.LOG_FILE).write_text("a\nb\nc\n"); out.clear(); a.logs(2); self.assertEqual(out[-1], "b\nc")

class ProcTests(Case):
    def test_start_and_stop_for_real(self):
        """A real child under the pid file: `serve` cannot run without a conf, so the child is `python3 -c` through a stand-in
        runner — the adapter's own argv shape, its pid file and its stop are what is tested."""
        state = self.scratch(); out = []
        (state / "ledgerd.conf").write_text("bind: 127.0.0.1\nport: 8731\n")
        runner = state / "runner.py"; runner.write_text("import time, sys\nprint('serving', sys.argv[1:], flush=True)\ntime.sleep(60)\n")
        a = sup.adapter("proc", state, python=sys.executable, out=out.append)
        with unittest.mock.patch.object(sup, "RUNNER", runner):
            self.assertFalse(a.is_active()); self.assertEqual(a.status(), 3)
            self.assertEqual(a.install(), 0)
            pid = a.pid(); self.assertIsNotNone(pid); self.assertTrue(a.is_active())
            self.assertIn(sup.NOT_PERSISTENT, out[-2]); self.assertEqual(out[-1], "ui-url: http://127.0.0.1:8731/")
            self.assertEqual(a.start(), 0); self.assertIn("already running", out[-1])
            for _ in range(50):
                if (state / sup.LOG_FILE).is_file() and "serving" in (state / sup.LOG_FILE).read_text():
                    break
                time.sleep(0.1)
            self.assertIn("['ledger', 'serve', '--state'", (state / sup.LOG_FILE).read_text())
            self.assertEqual(a.status(), 0); self.assertIn("running", out[-1]); self.assertIn("not persistent", out[-1])
            self.assertEqual(a.stop(), 0); self.assertFalse(a.is_active()); self.assertFalse(a.pid_path().exists())
            self.assertEqual(a.uninstall(), 0)

class EnvPatch:
    def __init__(self, values):
        self.values, self.saved = values, {}
    def __enter__(self):
        for k, v in self.values.items():
            self.saved[k] = os.environ.get(k)
            if v == "":
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        return self
    def __exit__(self, *a):
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

if __name__ == "__main__":
    unittest.main()
