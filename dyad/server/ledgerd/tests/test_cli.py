"""ledgerd/cli.py: `init` (both contracts validated before any write, the port chosen by walking up from the start
and skipping an occupied one, `ui-url:` the last line, `0 changes` the second time, different values refused
without --force, a schema missing a contract symbol refused), `serve` refusing an occupied recorded port with its
fix line, `query`'s client against the service and its in-process fallback against a closed port with its line,
`--md`, `view`/`board`/`schema`, `install` over a fake `run` (the pip line from the manifest's rows — one source),
the supervisor verbs over the proc adapter, `auth` refusing without a client id, and the installed-metadata licence
check. Importing the module runs its INVARIANTS (verifiable-code.md p5)."""
import importlib.metadata, json, re, socket, subprocess, sys, unittest, unittest.mock
from pathlib import Path
import support
from support import Case, http
import dyadlib
if not support.MISSING:
    from ledgerd import cli, core, supervisor
    from test_core import service_for

LENIENT = {"MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD", "PSF-2.0", "Unlicense", "CC0", "CC0-1.0"}

def run_cli(*argv) -> tuple[int, list[str]]:
    out = []
    rc = cli.main(list(argv), out=out.append)
    return rc, out

class ParseTests(Case):
    def test_parse_and_unknown_flag(self):
        self.assertEqual(cli.parse(["a", "--state", "s", "--md", "b"]), (["a", "b"], {"--state": "s"}, {"--md"}))
        with self.assertRaises(ValueError):
            cli.parse(["--bogus"])
        with self.assertRaises(ValueError):
            cli.parse(["--state"])
        rc, out = run_cli("nope"); self.assertEqual(rc, 2); self.assertIn("dyad ledger init --state", "\n".join(out))
        rc, out = run_cli("query", "--bogus"); self.assertEqual(rc, 2)
    def test_pins_come_from_the_manifest_rows(self):
        self.assertEqual(cli.pins(), ["pydantic==2.14.1", "fastapi==0.141.1", "uvicorn==0.54.0", "sqlalchemy==2.1.5", "jinja2==3.1.6"])   # table order; the kernel's pydantic rides along
        d = self.scratch(); m = d / "m.md"
        m.write_text("| component | partition | version | purpose | license | replacement | profile |\n|---|---|---|---|---|---|---|\n"
                     "| `Foo` | library | 1.2.3 pinned | installed by `dyad ledger install`; x | MIT | y | both |\n| bar | library | 9.9.9 | other | MIT | y | both |\n"
                     "| htmx | library | 2.0.4 pinned (vendored at z) | served by `dyad ledger install`; vendored | 0BSD | y | both |\n| K | kernel | 1.0.0 | with the rows by `dyad ledger install` | MIT | - | both |\n")
        self.assertEqual(cli.pins(m), ["foo==1.2.3", "k==1.0.0"])

class PortTests(Case):
    def test_port_selection_skips_an_occupied_port(self):
        with socket.socket() as busy:
            busy.bind(("127.0.0.1", 0)); busy.listen(1); p = busy.getsockname()[1]
            self.assertFalse(cli.port_free("127.0.0.1", p))
            chosen = cli.free_port("127.0.0.1", start=p, limit=50)
            self.assertGreater(chosen, p); self.assertTrue(cli.port_free("127.0.0.1", chosen))
        self.assertTrue(cli.port_free("127.0.0.1", p))
        with self.assertRaises(RuntimeError):
            with socket.socket() as busy2:
                busy2.bind(("127.0.0.1", 0)); busy2.listen(1); cli.free_port("127.0.0.1", start=busy2.getsockname()[1], limit=1)

class InitTests(Case):
    def test_init_validates_then_writes_builds_and_prints_the_url_last(self):
        repo = support.instance(self.scratch()); state = self.scratch() / "st"
        rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"file://{repo}", "--port", "18731", "--refresh-every", "7")
        self.assertEqual(rc, 0, out); self.assertEqual(out[-1], "ui-url: http://127.0.0.1:18731/")
        self.assertTrue(any(l.startswith("built ") for l in out)); self.assertTrue((state / "ledgerd.db").is_file())
        self.assertEqual((state / "ledgerd.conf").read_text(), f"schema: dwork\nschema_version: 1\nstore: file://{repo}\nbind: 127.0.0.1\nport: 18731\nrefresh_every: 7\n")
        self.assertEqual(sorted(p.name for p in (state / "views").iterdir()), ["backlog.md", "backlog.txt", "board.md", "board.txt", "unheld.md", "unheld.txt"])
        rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"file://{repo}", "--port", "18731", "--refresh-every", "7")
        self.assertEqual(rc, 0); self.assertIn("0 changes", out); self.assertEqual(out[-1], "ui-url: http://127.0.0.1:18731/")
        rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"file://{repo}", "--port", "18731", "--refresh-every", "8")
        self.assertEqual(rc, 1); self.assertIn("different values", out[0]); self.assertIn("refresh_every: 7 -> 8", "\n".join(out))
        rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"file://{repo}", "--port", "18731", "--refresh-every", "8", "--force")
        self.assertEqual(rc, 0); self.assertIn("refresh_every: 8", (state / "ledgerd.conf").read_text())
    def test_init_chooses_a_free_port_and_keeps_it(self):
        repo = support.instance(self.scratch()); state = self.scratch()
        with unittest.mock.patch.object(cli, "PORT_START", support.free_port()):
            rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"file://{repo}")
            self.assertEqual(rc, 0, out); port = int(re.search(r":(\d+)/$", out[-1]).group(1)); self.assertGreaterEqual(port, cli.PORT_START)
            rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"file://{repo}")
            self.assertEqual(rc, 0); self.assertIn("0 changes", out); self.assertEqual(out[-1], f"ui-url: http://127.0.0.1:{port}/")
    def test_init_refuses_before_any_write(self):
        state = self.scratch() / "st"; d = self.scratch(); bad = d / "bad.py"; bad.write_text("NAME = 'bad'\n")
        rc, out = run_cli("init", "--state", str(state), "--schema", f"module:{bad}", "--store", f"file://{d}")
        self.assertEqual(rc, 1); self.assertIn("lacks VERSION", out[0]); self.assertFalse(state.exists())
        rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"file://{d / 'nowhere'}")
        self.assertEqual(rc, 1); self.assertIn("not a directory", out[0]); self.assertFalse(state.exists())
        badstore = d / "badstore.py"; badstore.write_text("SCHEME = 'x'\n")
        rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"module:{badstore}")
        self.assertEqual(rc, 1); self.assertIn("lacks open", out[0]); self.assertFalse(state.exists())
        rc, out = run_cli("init", "--state", str(state), "--schema", "dwork"); self.assertEqual(rc, 2)
        rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"file://{d}", "--refresh-every", "x"); self.assertEqual(rc, 1); self.assertFalse(state.exists())
    def test_init_over_git_and_the_notes_schema(self):
        repo = support.instance(self.scratch()); state = self.scratch() / "st"
        rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"git+file://{repo}#main", "--port", str(support.free_port()))
        self.assertEqual(rc, 0, out); self.assertTrue((state / "repo.git" / "HEAD").is_file()); self.assertIn("from git:", "\n".join(out))
        d = self.scratch(); p = support.notes_schema(d); state2 = self.scratch() / "n"
        rc, out = run_cli("init", "--state", str(state2), "--schema", f"module:{p}", "--store", str(d), "--port", str(support.free_port()))
        self.assertEqual(rc, 0, out); self.assertEqual(sorted(x.name for x in (state2 / "views").iterdir()), ["open_notes.md", "open_notes.txt"])
    def test_init_without_the_libs_writes_the_conf_and_skips_the_build(self):
        repo = support.instance(self.scratch()); state = self.scratch() / "st"
        with unittest.mock.patch.object(cli, "libs_missing", lambda: ["sqlalchemy"]):
            rc, out = run_cli("init", "--state", str(state), "--schema", "dwork", "--store", f"file://{repo}", "--port", "18732")
        self.assertEqual(rc, 0); self.assertTrue((state / "ledgerd.conf").is_file()); self.assertFalse((state / "ledgerd.db").exists())
        self.assertTrue(any(l.startswith("build skipped: sqlalchemy not importable") for l in out)); self.assertEqual(out[-1], "ui-url: http://127.0.0.1:18732/")

class ServeTests(Case):
    def test_serve_refuses_an_occupied_recorded_port_with_the_fix_line(self):
        svc, _ = service_for(self, git=False)
        with socket.socket() as busy:
            busy.bind(("127.0.0.1", 0)); busy.listen(1); port = busy.getsockname()[1]
            core.write_conf(svc.state, {**svc.conf, "port": str(port)})
            rc, out = run_cli("serve", "--state", str(svc.state))
        self.assertEqual(rc, 1); self.assertRegex(out[0], rf"^port {port} in use; run dyad ledger init --port \d+ --force$")
    def test_serve_runs_the_server(self):
        """`serve` in a child process on a free port: /health answers with the supervisor it was told, then SIGTERM."""
        svc, _ = service_for(self, git=False)
        port = support.free_port(); core.write_conf(svc.state, {**svc.conf, "port": str(port)})
        child = subprocess.Popen([sys.executable, str(supervisor.RUNNER), "ledger", "serve", "--state", str(svc.state), "--supervisor", "proc"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=dyadlib.git_env())
        self.addCleanup(child.kill)
        import time
        for _ in range(200):
            try:
                code, body, _ = http(f"http://127.0.0.1:{port}", "/health"); break
            except OSError:
                time.sleep(0.05)
        else:
            self.fail("serve never answered: " + (child.stdout.read() if child.poll() is not None else "still running"))
        self.assertEqual((code, json.loads(body)["supervisor"], json.loads(body)["ui_url"]), (200, "proc", f"http://127.0.0.1:{port}/"))
        rc, out = run_cli("query", "SELECT id FROM board ORDER BY id", "--state", str(svc.state))
        self.assertEqual(rc, 0, out); self.assertFalse(any("unreachable" in l for l in out)); self.assertIn("asof dir:", out[-1])
        rc, out = run_cli("board", "--state", str(svc.state)); self.assertEqual(rc, 0); self.assertTrue(out[-1].startswith("# board (built from dir:"))
        child.terminate(); child.wait(10)

class ClientTests(Case):
    def test_query_falls_back_in_process_against_a_closed_port_with_its_line(self):
        port = support.free_port()
        with unittest.mock.patch.object(dyadlib, "repo_root", lambda *a, **k: self.repo):
            rc, out = run_cli("query", "SELECT id, status FROM board ORDER BY id", "--url", f"http://127.0.0.1:{port}")
        self.assertEqual(rc, 0, out)
        self.assertRegex(out[0], r"^service unreachable \(URLError: .*\): built in-process from dir:[0-9a-f]{16}$")
        self.assertIn("1   open", out[1]); self.assertTrue(out[-1].splitlines()[-1].startswith("asof dir:"))
    def test_query_md_shape_and_refusal(self):
        with unittest.mock.patch.object(dyadlib, "repo_root", lambda *a, **k: self.repo):
            rc, out = run_cli("query", "SELECT id, what FROM backlog", "--md", "--state", str(self.scratch()))
            self.assertEqual(rc, 0); self.assertEqual(out[1], "| id | what |\n|---|---|\n| 4 | a backlog row |\nasof " + out[1].split("asof ")[1])
            rc, out = run_cli("query", "DELETE FROM rows", "--state", str(self.scratch()))
            self.assertEqual(rc, 1); self.assertTrue(out[-1].startswith("refused: read-only"))
            rc, out = run_cli("query"); self.assertEqual(rc, 2)
    def test_query_at_a_commit_reads_that_commit(self):
        head1 = support.git(self.repo, "rev-parse", "HEAD").strip()
        support.add_row(self.repo, 7, "later")
        with unittest.mock.patch.object(dyadlib, "repo_root", lambda *a, **k: self.repo):
            rc, out = run_cli("query", "SELECT count(*) FROM rows", "--at", head1)
            self.assertEqual(rc, 0, out); self.assertIn(f"built in-process from git:{head1}", out[0]); self.assertIn("6", out[1])
            rc, out = run_cli("query", "SELECT count(*) FROM rows", "--at", "HEAD"); self.assertIn("7", out[1])
    def test_view_board_and_schema_fallback(self):
        with unittest.mock.patch.object(dyadlib, "repo_root", lambda *a, **k: self.repo):
            rc, out = run_cli("view", "backlog", "--md", "--state", str(self.scratch()))
            self.assertEqual(rc, 0); self.assertTrue(out[0].startswith("service unreachable (no service configured)")); self.assertIn("| 4 | a backlog row |", out[1])
            rc, out = run_cli("board", "--state", str(self.scratch())); self.assertEqual(rc, 0); self.assertTrue(out[1].startswith("# board (built from dir:"))
            rc, out = run_cli("view", "rows", "--state", str(self.scratch())); self.assertEqual(rc, 1); self.assertIn("not a rendered view", out[0])
        rc, out = run_cli("schema"); self.assertEqual(rc, 0); self.assertEqual(out[0], "schema dwork 1; stores: agent-corpus/d-work, workstation-corpus/runbooks/events")
        self.assertTrue(any(l.startswith("  view board [rendered] [default]:") for l in out))
    def setUp(self):
        self.repo = support.instance(self.scratch())

class InstallTests(Case):
    def test_install_makes_the_venv_from_the_manifest_rows_then_the_supervisor(self):
        svc, _ = service_for(self, git=False)
        calls = []
        def run(argv, **kw):
            calls.append(list(argv))
            if argv[1:3] == ["-m", "venv"]:
                (Path(argv[3]) / "bin").mkdir(parents=True); (Path(argv[3]) / "bin" / "python3").write_text("")
            return subprocess.CompletedProcess(argv, 0, "built\n", "")
        out = []
        with unittest.mock.patch.object(cli.hostadapter, "supervisor", lambda: "proc"), unittest.mock.patch.object(supervisor.Proc, "install", lambda self: out.append("installed") or 0):
            self.assertEqual(cli.cmd_install({"--state": str(svc.state)}, out=out.append, run=run), 0)
        venv = svc.state / "venv"
        self.assertEqual(calls[0], [sys.executable, "-m", "venv", str(venv)])
        self.assertEqual(calls[1], [str(venv / "bin" / "python3"), "-m", "pip", "install", "--quiet", *cli.pins()])
        self.assertEqual(calls[2], [str(venv / "bin" / "python3"), str(supervisor.RUNNER), "ledger", "build", "--state", str(svc.state)])
        self.assertEqual(core.read_conf(svc.state)["venv"], str(venv)); self.assertIn("installed", out); self.assertIn("supervisor: proc", out)
    def test_install_with_an_interpreter_skips_pip(self):
        svc, _ = service_for(self, git=False)
        calls = []
        run = lambda argv, **kw: calls.append(list(argv)) or subprocess.CompletedProcess(argv, 0, "", "")
        with unittest.mock.patch.object(cli.hostadapter, "supervisor", lambda: "proc"), unittest.mock.patch.object(supervisor.Proc, "install", lambda self: 0):
            self.assertEqual(cli.cmd_install({"--state": str(svc.state), "--python": sys.executable}, out=lambda s: None, run=run), 0)
        self.assertEqual(calls, [[sys.executable, str(supervisor.RUNNER), "ledger", "build", "--state", str(svc.state)]])
        rc, out = run_cli("install", "--state", str(self.scratch())); self.assertEqual(rc, 1); self.assertIn("needs an initialized state", out[0])
    def test_supervisor_verbs_dispatch_to_the_adapter(self):
        svc, _ = service_for(self, git=False)
        rc, out = run_cli("status", "--state", str(svc.state), "--supervisor", "proc")
        self.assertEqual(rc, 3); self.assertIn("stopped", out[-1]); self.assertIn("ui-url: http://127.0.0.1:8731/", out[-1])
        rc, out = run_cli("stop", "--state", str(svc.state), "--supervisor", "proc"); self.assertEqual(rc, 0); self.assertEqual(out[-1], "not running")
        rc, out = run_cli("logs", "--state", str(svc.state), "--supervisor", "proc"); self.assertEqual(rc, 0); self.assertIn("no log at", out[-1])

class AuthTests(Case):
    def test_auth_verbs(self):
        svc, _ = service_for(self, git=False)
        rc, out = run_cli("auth", "login", "--state", str(svc.state)); self.assertEqual(rc, 2); self.assertIn("Enable Device Flow", "\n".join(out))
        rc, out = run_cli("auth", "status", "--state", str(svc.state)); self.assertEqual(rc, 0); self.assertEqual(out[-1], "anonymous (no credentials stored)")
        rc, out = run_cli("auth", "logout", "--state", str(svc.state)); self.assertEqual(rc, 0); self.assertEqual(out[-1], "nothing to log out")
        rc, out = run_cli("auth", "bogus"); self.assertEqual(rc, 2)

class LicenceTests(Case):
    """Revision 9's bar — MIT or more lenient — over what is installed: every distribution the component's four
    imports resolve to, and their transitive dependencies, as `importlib.metadata` reports them. A future pin that
    pulls a non-lenient package fails here, mechanically."""
    def test_every_installed_dependency_is_lenient(self):
        def licence(dist) -> str:
            m = dist.metadata
            expr = m.get("License-Expression") or ""
            if not expr:
                cls = [c for c in m.get_all("Classifier", []) if c.startswith("License :: OSI Approved :: ")]
                expr = " OR ".join(c.rsplit(" :: ", 1)[1].replace(" License", "") for c in cls) or (m.get("License") or "")
            return expr
        def lenient(expr: str) -> bool:
            toks = {t.strip("() ") for t in re.split(r"\b(?:AND|OR|and|or)\b", expr) if t.strip("() ")}
            toks = {{"BSD": "BSD-3-Clause", "Apache Software": "Apache-2.0", "Python Software Foundation": "PSF-2.0", "MIT License": "MIT"}.get(t, t) for t in toks}
            return bool(toks) and toks <= LENIENT
        seen, queue, report = {}, list(cli.LIBS), []
        while queue:
            name = queue.pop()
            try:
                dist = importlib.metadata.distribution(name)
            except importlib.metadata.PackageNotFoundError:
                continue
            key = dist.metadata["Name"].lower()
            if key in seen:
                continue
            seen[key] = licence(dist)
            for req in dist.requires or []:
                if ";" in req and "extra ==" in req:
                    continue
                queue.append(re.split(r"[\s<>=!~\[;]", req, maxsplit=1)[0])
        self.assertGreaterEqual(len(seen), 8, seen)
        bad = {k: v for k, v in seen.items() if not lenient(v)}
        # A package outside the bar passes only when a manifest row names it with its licence in its purpose cell — declared
        # to the Operator in the one manifest (Rule-14), never pulled silently. Today no row declares one: FastAPI is pinned at
        # 0.141.1, the last release before opentelemetry-api (Apache-2.0) became a required dependency (0.142.0, 2026-09-29;
        # the INCIDENTS.md row of 2026-10-17 #336). The declared-exception fence stays for a future upgrade.
        manifest = (support.PKG / "infrastructure" / "INFRASTRUCTURE.md").read_text()
        purposes = " ".join(r[3] for r in dyadlib.table_rows(manifest) if len(r) >= 4)
        undeclared = {k: v for k, v in bad.items() if f"{k} {v}" not in purposes}
        self.assertEqual(undeclared, {}, f"not MIT-or-more-lenient and not declared in a manifest row (plan #336 revision 9, L4): {undeclared}; installed set: {seen}")

if __name__ == "__main__":
    unittest.main()
