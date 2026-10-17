"""ledgerd: the supervisor-adapter seam (plan #336 revision 7). Kernel: Python 3.12+, stdlib.
A supervisor keeps the daemon running on the host that persists. An adapter is a class meeting
SUPERVISOR_CONTRACT — `NAME`, `install`, `uninstall`, `start`, `stop`, `restart`, `status`, `is_active`,
`logs` — and every adapter prints the native command line before running it (Rule-19: a reader can run
it by hand). Shipped: `systemd` (a user unit `~/.config/systemd/user/dyad-ledgerd.service` rendered from
the template with the real paths; `systemctl --user daemon-reload / enable --now / disable --now /
is-active / status`, `journalctl --user -u`; `loginctl enable-linger` attempted so the unit runs at
boot, a refusal reported, never fatal); `launchd` (`~/Library/LaunchAgents/com.dyad.ledgerd.plist` from
the template; `launchctl bootstrap gui/<uid>`, `bootout`, `print`; logs to `<state>/ledgerd.log`);
`proc` (`serve` detached with a pid file under the state directory: survives the session's turn, not the
host — it says so in `status` and `/health`, so a prototype is never mistaken for a deployment). Which
one a host gets is `hostadapter.supervisor()`'s answer. The commands run through `run` (default
`subprocess.run`) and the home directory through `home`, both injectable so a test renders the unit and
the command lines over a fake host without driving systemd or launchd. No home-directory literal is
tracked (package_rules.txt refuses one): every host path is computed here at install time.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("supervisor.py: Python 3.12+ required")
import os, signal, subprocess, time
from pathlib import Path
COMPONENT = Path(__file__).resolve().parents[1]
for _p in (str(COMPONENT), str(COMPONENT.parents[1] / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dyadlib

SUPERVISOR_CONTRACT = ("NAME", "install", "uninstall", "start", "stop", "restart", "status", "is_active", "logs")
NAMES = ("systemd", "launchd", "proc")
UNIT = "dyad-ledgerd.service"
PLIST = "com.dyad.ledgerd.plist"
LABEL = "com.dyad.ledgerd"
PID_FILE = "ledgerd.pid"
LOG_FILE = "ledgerd.log"
TEMPLATES = {"systemd": COMPONENT / UNIT, "launchd": COMPONENT / PLIST}   # the tracked templates; placeholders filled at install
PLACEHOLDERS = ("python", "runner", "state", "log")
NOT_PERSISTENT = "proc (not persistent: survives this session, not the host)"
RUNNER = COMPONENT.parents[1] / "scripts" / "package.py"                   # `dyad ledger serve` through the runner's dispatch

INVARIANTS: list[dyadlib.Invariant] = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("contract-names-distinct", lambda: len(set(SUPERVISOR_CONTRACT)) == len(SUPERVISOR_CONTRACT)),
    ("contract-has-the-lifecycle", lambda: {"install", "uninstall", "start", "stop", "restart", "status", "is_active", "logs"} <= set(SUPERVISOR_CONTRACT)),
    ("names-are-the-three-adapters", lambda: NAMES == ("systemd", "launchd", "proc")),
    ("templates-for-the-persistent-two", lambda: set(TEMPLATES) == {"systemd", "launchd"} and all(n in NAMES for n in TEMPLATES)),
    ("placeholders-distinct", lambda: len(set(PLACEHOLDERS)) == len(PLACEHOLDERS)),
    ("label-matches-plist", lambda: PLIST == LABEL + ".plist"),
]

def contract_problem(cls) -> str | None:
    missing = [n for n in SUPERVISOR_CONTRACT if not hasattr(cls, n)]
    return f"lacks {', '.join(missing)} (supervisor contract)" if missing else None

def render(template: Path, fields: dict[str, str]) -> str:
    """The template with every `{placeholder}` filled (the tracked file holds no host path)."""
    text = template.read_text()
    for k in PLACEHOLDERS:
        text = text.replace("{" + k + "}", fields[k])
    return text

def fields_for(state: Path, python: str) -> dict[str, str]:
    state = Path(state).resolve()
    return {"python": python, "runner": str(RUNNER), "state": str(state), "log": str(state / LOG_FILE)}

class _Base:
    """What the adapters share: the state directory, the interpreter the unit runs, the injected `run` and
    `home`, and `say`, which prints the native line before `run` executes it."""
    NAME = ""
    def __init__(self, state: Path, python: str | None = None, run=subprocess.run, home: Path | None = None, out=print):
        self.state, self.python = Path(state).resolve(), python or sys.executable
        self.run, self.home, self.out = run, Path(home) if home else Path.home(), out
    def say(self, argv: list[str], check: bool = False, **kw):
        self.out("$ " + " ".join(argv))
        return self.run(argv, capture_output=True, text=True, check=check, **kw)
    def restart(self) -> int:
        rc = self.stop()
        return self.start() if rc == 0 else rc
    def ui_url(self) -> str:
        conf = dyadlib.parse_kv((self.state / "ledgerd.conf").read_text()) if (self.state / "ledgerd.conf").is_file() else {}
        return f"http://{conf.get('bind', '127.0.0.1')}:{conf.get('port', '?')}/"

class Systemd(_Base):
    NAME = "systemd"
    def unit_path(self) -> Path:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or (self.home / ".config"))
        return base / "systemd" / "user" / UNIT
    def rendered(self) -> str:
        return render(TEMPLATES["systemd"], fields_for(self.state, self.python))
    def install(self) -> int:
        p, text = self.unit_path(), self.rendered()
        if p.is_file() and p.read_text() == text and self.is_active():
            self.out("0 changes"); return 0
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
        self.out(f"wrote {p}")
        self.say(["systemctl", "--user", "daemon-reload"], check=True)
        self.say(["systemctl", "--user", "enable", "--now", UNIT], check=True)
        r = self.say(["loginctl", "enable-linger", os.environ.get("USER") or os.environ.get("LOGNAME") or ""])
        if r.returncode:
            self.out(f"loginctl enable-linger refused (exit {r.returncode}): the unit starts at login, not at boot, until the "
                     f"Operator runs it with the needed privilege (Rule-18 ops script; plan #336 H4)")
        self.out(f"ui-url: {self.ui_url()}")
        return 0
    def uninstall(self) -> int:
        self.say(["systemctl", "--user", "disable", "--now", UNIT])
        p = self.unit_path()
        if p.is_file():
            p.unlink(); self.out(f"removed {p}")
        self.say(["systemctl", "--user", "daemon-reload"])
        return 0
    def start(self) -> int:
        return self.say(["systemctl", "--user", "start", UNIT]).returncode
    def stop(self) -> int:
        return self.say(["systemctl", "--user", "stop", UNIT]).returncode
    def is_active(self) -> bool:
        return self.say(["systemctl", "--user", "is-active", "--quiet", UNIT]).returncode == 0
    def status(self) -> int:
        r = self.say(["systemctl", "--user", "status", "--no-pager", UNIT])
        self.out((r.stdout or "").rstrip()); self.out(f"ui-url: {self.ui_url()}")
        return r.returncode
    def logs(self, lines: int = 50) -> int:
        r = self.say(["journalctl", "--user", "-u", UNIT, "-n", str(lines), "--no-pager"])
        self.out((r.stdout or "").rstrip()); return r.returncode

class Launchd(_Base):
    NAME = "launchd"
    def plist_path(self) -> Path:
        return self.home / "Library" / "LaunchAgents" / PLIST
    def domain(self) -> str:
        return f"gui/{os.getuid()}"
    def rendered(self) -> str:
        return render(TEMPLATES["launchd"], fields_for(self.state, self.python))
    def install(self) -> int:
        p, text = self.plist_path(), self.rendered()
        if p.is_file() and p.read_text() == text and self.is_active():
            self.out("0 changes"); return 0
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
        self.out(f"wrote {p}")
        self.say(["launchctl", "bootstrap", self.domain(), str(p)], check=True)
        self.out(f"ui-url: {self.ui_url()}")
        return 0
    def uninstall(self) -> int:
        self.say(["launchctl", "bootout", f"{self.domain()}/{LABEL}"])
        p = self.plist_path()
        if p.is_file():
            p.unlink(); self.out(f"removed {p}")
        return 0
    def start(self) -> int:
        return self.say(["launchctl", "kickstart", f"{self.domain()}/{LABEL}"]).returncode
    def stop(self) -> int:
        return self.say(["launchctl", "kill", "SIGTERM", f"{self.domain()}/{LABEL}"]).returncode
    def is_active(self) -> bool:
        r = self.say(["launchctl", "print", f"{self.domain()}/{LABEL}"])
        return r.returncode == 0 and "state = running" in (r.stdout or "")
    def status(self) -> int:
        r = self.say(["launchctl", "print", f"{self.domain()}/{LABEL}"])
        self.out((r.stdout or "").rstrip()); self.out(f"ui-url: {self.ui_url()}")
        return r.returncode
    def logs(self, lines: int = 50) -> int:
        log = self.state / LOG_FILE
        self.out("\n".join(log.read_text(errors="replace").splitlines()[-lines:]) if log.is_file() else f"no log at {log}")
        return 0

class Proc(_Base):
    """A detached child with a pid file: the fallback for a host with neither systemd nor launchd (a container).
    Not persistent, and says so."""
    NAME = "proc"
    def pid_path(self) -> Path:
        return self.state / PID_FILE
    def pid(self) -> int | None:
        p = self.pid_path()
        try:
            return int(p.read_text().strip()) if p.is_file() else None
        except ValueError:
            return None
    def is_active(self) -> bool:
        pid = self.pid()
        if pid is None:
            return False
        try:
            os.kill(pid, 0); return True
        except (ProcessLookupError, PermissionError):
            return False
    def start(self) -> int:
        if self.is_active():
            self.out(f"already running (pid {self.pid()}); {NOT_PERSISTENT}"); return 0
        argv = [self.python, str(RUNNER), "ledger", "serve", "--state", str(self.state)]
        self.out("$ " + " ".join(argv) + f" > {self.state / LOG_FILE} 2>&1 &")
        log = open(self.state / LOG_FILE, "ab")
        child = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True, env=dyadlib.git_env())
        log.close()
        self.pid_path().write_text(f"{child.pid}\n")
        self.out(f"started pid {child.pid}; {NOT_PERSISTENT}")
        return 0
    def stop(self, wait: float = 10.0) -> int:
        pid = self.pid()
        if pid is None or not self.is_active():
            self.out("not running")
            if self.pid_path().is_file():
                self.pid_path().unlink()
            return 0
        self.out(f"$ kill -TERM {pid}")
        os.kill(pid, signal.SIGTERM)
        deadline = time.monotonic() + wait
        while self.is_active() and time.monotonic() < deadline:
            time.sleep(0.1)
        if self.is_active():
            os.kill(pid, signal.SIGKILL)
        self.pid_path().unlink(missing_ok=True)
        self.out(f"stopped pid {pid}")
        return 0
    def install(self) -> int:
        self.out(f"supervisor: {NOT_PERSISTENT}")
        rc = self.start()
        self.out(f"ui-url: {self.ui_url()}")
        return rc
    def uninstall(self) -> int:
        return self.stop()
    def status(self) -> int:
        active = self.is_active()
        self.out(f"{'running' if active else 'stopped'}{f' (pid {self.pid()})' if active else ''}; {NOT_PERSISTENT}; ui-url: {self.ui_url()}")
        return 0 if active else 3
    def logs(self, lines: int = 50) -> int:
        log = self.state / LOG_FILE
        self.out("\n".join(log.read_text(errors="replace").splitlines()[-lines:]) if log.is_file() else f"no log at {log}")
        return 0

ADAPTERS = {"systemd": Systemd, "launchd": Launchd, "proc": Proc}
TREE_INVARIANTS: list[dyadlib.Invariant] = [
    ("adapters-meet-the-contract", lambda: all(contract_problem(c) is None for c in ADAPTERS.values())),
    ("adapters-are-the-names", lambda: tuple(ADAPTERS) == NAMES),
    ("templates-exist", lambda: all(p.is_file() for p in TEMPLATES.values())),
    ("templates-hold-every-placeholder", lambda: all(("{" + k + "}") in p.read_text() for p in TEMPLATES.values() for k in ("python", "runner", "state"))),
]

def adapter(name: str, state: Path, **kw):
    """The adapter `name` selects (`hostadapter.supervisor()` chooses the name), over `state`."""
    if name not in ADAPTERS:
        raise ValueError(f"no supervisor adapter {name!r}; one of {', '.join(NAMES)}")
    return ADAPTERS[name](state, **kw)

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding
