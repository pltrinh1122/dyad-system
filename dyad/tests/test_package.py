import contextlib, importlib.util, inspect, io, os, shutil, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); import dyadlib, livetest
CORE = ["agent/frame", "agent/plans", "agent/provenance", "agent/prs", "agent/records", "agent/references", "agent/rows", "agent/rules", "agent/sessions", "agent/vocabulary",
        "craft/crafts", "infra/bundle", "infra/containment", "infra/manifest", "preferences/preferences"]   # craft/crafts: the craft guard (#156); infra/bundle: Rule-11 p7 (#196)
KNOWN_CRAFTS = {"sysadmin": ["changelog", "events", "ops_scripts", "runbooks"], "sysarch": ["registry"], "syseng": ["invariants", "naming", "tests"], "lan-git": ["image"]}   # #155, #160, #162, #181
def craft_guards(name: str, pkg: Path = PKG) -> list[str]:
    """The documented entities for a known craft (so one silently dropping a guard still fails this
    test), else derived from crafts/<name>/guards/*.py — never a KeyError for a craft this literal
    dict has not caught up to yet (#213 d-work #46)."""
    if name in KNOWN_CRAFTS:
        return KNOWN_CRAFTS[name]
    d = pkg.parent / "crafts" / name / "guards"
    return sorted(p.stem for p in d.glob("*.py") if not p.name.startswith("_")) if d.is_dir() else []
CRAFT = [f"{c.name}/{e}" for c in dyadlib.craft_dirs() for e in craft_guards(c.name)]   # the crafts present, in registry order (a craft the sequence has not yet added is absent)
CRAFTS = livetest.crafts_installed()   # #171: a core-only install has none; the cases that need one skip with a stated reason

def env(**kw):
    return {**os.environ, "DYAD_NO_NESTED_TESTS": "1", "PYTHONDONTWRITEBYTECODE": "1", **kw}

SCRATCH = livetest.ScratchInstalls()   # one real install per variant per module run, copied per case (#163, d-work #199 N3a)
tearDownModule = SCRATCH.cleanup       # removes every scratch install and every SCRATCH.mkdtemp() dir; atexit is the backstop

def scratch_install(with_craft: bool) -> Path:
    """A scratch git repo with the core craft installed (package.py install) and, optionally, every crafts/<craft>/ copied in
    (whatever this repo currently has, discovered dynamically): an independent copy of this module's one install of that
    variant (`livetest.ScratchInstalls`). The install path itself runs once per variant, and again in every case below that
    re-installs into its copy (`install twice`, `prunes`, `gitignore`)."""
    return SCRATCH.copy(with_craft)

def load_package():
    spec = importlib.util.spec_from_file_location("package", PKG / "scripts" / "package.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod   # package.py's own invariant_modules() looks itself up via sys.modules[__name__]
    spec.loader.exec_module(mod); return mod

def scratch_repo(paths, tracked=True):
    """A temp git repo holding `paths` (added and committed when tracked, else left untracked)."""
    d = SCRATCH.mkdtemp()
    subprocess.run(["git", "init", "-q", str(d)], check=True)
    for rel in paths:
        f = d / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes(b"\x00cafe")
    if tracked:
        subprocess.run(["git", "-C", str(d), "add", "-f", "."], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], check=True)
    return d

class PackageTests(livetest.LiveCase):
    def run_py(self, *a):
        return subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), *a], capture_output=True, text=True)
    def test_check_runs_and_reports_rules_and_guards(self):
        r = self.run_py("check")
        self.assertIn("[Rule-11]", r.stdout); self.assertIn("[Rule-12]", r.stdout)
        pkg = load_package()
        self.assertEqual(list(pkg.CHECKS)[:2], ["Rule-11", "Rule-12"])
        # crafts/sysarch/rules/guards.md p4: CHECKS is derived from the registry (dyad/guards/<corpus>/<entity>.py, then crafts/<craft>/guards/<entity>.py; #155), never hand-listed
        expected = [f"{dyadlib.guard_key(py)[1]}/{py.stem}" for py in dyadlib.guard_files()]
        self.assertEqual(list(pkg.CHECKS)[2:], expected)
        self.assertEqual(expected, CORE + CRAFT)
        for g in expected:   # every registered guard reports a line, whichever crafts this install carries (#171)
            self.assertIn(f"[{g}]", r.stdout, g)
    def test_registry_contract(self):
        pkg = load_package()
        reg = pkg.registry()
        self.assertEqual([e[5] for e in reg], [""] * len(reg), [e[5] for e in reg if e[5]])
        zones = pkg.zone_names(); self.assertIn("workstation", zones)
        for group, entity, rel, tx, mod, _ in reg:
            if rel.startswith("crafts/"):
                self.assertEqual(rel, f"crafts/{group}/guards/{entity}.py"); self.assertIn(mod.CORPUS, zones); self.assertEqual(pkg.guard_root(rel), "craft")   # a craft guard: CORPUS is its store's zone
            else:
                self.assertEqual((mod.CORPUS, rel), (group, f"dyad/guards/{group}/{entity}.py")); self.assertEqual(pkg.guard_root(rel), "core")
            self.assertIsInstance(mod.ENTITY, str); self.assertTrue(mod.FIELDS); self.assertTrue(callable(mod.check_package))
            self.assertEqual(tx, mod.TRANSACTION); self.assertEqual(tx, hasattr(mod, "check_transaction") and tx)
            self.assertTrue(callable(mod.describe), f"{rel}: no describe()")
        self.assertEqual({e[1] for e in reg if e[3]}, {"containment", "rows", "prs", "provenance"} | ({"events"} if "sysadmin" in CRAFTS else set()))   # events: the sysadmin craft's (#171); provenance: #191
        self.assertEqual(pkg.CONTRACT, dyadlib.CONTRACT)   # one contract definition, shared with the craft guard (#156)
        self.assertEqual(len({mod.ENTITY for *_, mod, _ in reg}), len(reg), "one ENTITY per guard")
    def test_list_prints_registry(self):
        r = self.run_py("check", "--list")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertEqual(lines[0].split(), ["corpus", "entity", "module", "transaction", "root"])
        self.assertIn(["agent", "rows", "dyad/guards/agent/rows.py", "yes", "core"], [l.split() for l in lines])
        self.assertIn(["infra", "manifest", "dyad/guards/infra/manifest.py", "no", "core"], [l.split() for l in lines])
        self.assertEqual(len(lines) - 1, len(load_package().registry()))
        # the craft root lists exactly the installed crafts' guards — none on a core-only install (#171), whichever crafts are here (dyad-system #1)
        craft_rows = {(l.split()[0], l.split()[1]) for l in lines[1:] if l.split()[4] == "craft"}
        self.assertEqual(craft_rows, {(c, g) for c in CRAFTS for g in craft_guards(c)})
        if "sysadmin" in CRAFTS:
            self.assertIn(["sysadmin", "events", "crafts/sysadmin/guards/events.py", "yes", "craft"], [l.split() for l in lines])   # the second root (#155)
    def test_broken_guard_fails_the_run(self):
        """A module under guards/ lacking check_package is a failing check, not a silent skip (plan #151, attack 6)."""
        import os, shutil
        pkg = load_package()
        d = SCRATCH.mkdtemp(); shutil.copytree(PKG, d / "dyad", ignore=shutil.ignore_patterns("__pycache__"))
        (d / "dyad" / "guards" / "agent" / "zzz.py").write_text("ENTITY = 'zzz'\n")
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--list"], capture_output=True, text=True, env={**os.environ, "DYAD_NO_NESTED_TESTS": "1"})
        self.assertNotEqual(r.returncode, 0); self.assertIn("agent/zzz.py", r.stdout); self.assertIn("lacks CORPUS, FIELDS, TRANSACTION, check_package", r.stdout)
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--guards"], capture_output=True, text=True, env={**os.environ, "DYAD_NO_NESTED_TESTS": "1"})
        self.assertIn("FAIL [guards] agent/zzz:", r.stdout)
    def test_guards_entry_point(self):
        """`cmd_guards` (the `check --guards` entry point) reports a line for each named guard. In-process over
        the registry narrowed to those guards (#163, d-work #199 N3a): the assertion reads their lines only, so
        the real-repo child and every other guard it paid for (`craft/crafts` above all) bought nothing here.
        The argv dispatch to `cmd_guards` stays covered by the scratch-install children and PrePushTests."""
        pkg = load_package(); full = pkg.registry
        named = ("infra/containment", "agent/rules", "agent/vocabulary", "agent/references", *CRAFT)   # every craft guard this install carries (#171)
        buf = io.StringIO()
        with unittest.mock.patch.object(pkg, "registry", lambda: [e for e in full() if f"{e[0]}/{e[1]}" in named]), \
             unittest.mock.patch.dict(os.environ, {"DYAD_NO_NESTED_TESTS": "1"}), contextlib.redirect_stdout(buf):
            pkg.cmd_guards()
        out = buf.getvalue()
        for g in named:
            self.assertTrue(any(l.startswith(("ok   [guards] " + g, "FAIL [guards] " + g)) for l in out.splitlines()), g)
        self.assertRegex(out, r"\[guards\] agent/rules \(\d+ Rules\)")
    def test_rule_12_runs_the_suites_and_maps_nothing(self):
        """#162: the mapping is the syseng craft's guard (`syseng/tests`); the runner keeps the suites."""
        pkg = load_package(); crafts = dyadlib.crafts_dir(PKG)
        self.assertEqual(pkg.test_suites(), [PKG / "tests"] + [c / "tests" for c in dyadlib.craft_dirs()])
        self.assertEqual(crafts / "sysarch" / "tests" in pkg.test_suites(), "sysarch" in CRAFTS)   # a core-only install runs the core suite alone (#171)
        self.assertEqual(pkg.check_rule_12(), [])   # under DYAD_NO_NESTED_TESTS: no mapping, no failure
    # d-work #155: the local gate never ran the suite (the pre-push hook is `check --guards`, 61
    # checks and no tests), so the Agent ran it by hand 134 times in one session (#154's audit).
    # `cmd_tests` is that run as one verb, always with DYAD_NO_NESTED_TESTS; `cmd_guards` runs it
    # too, gated on the pushed range being more than ledger-only.
    def test_tests_verb_runs_one_dotted_target_with_the_nested_flag(self):
        r = subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "check", "--tests",
                            "dyad.tests.test_playbooks"], capture_output=True, text=True,
                           env={k: v for k, v in os.environ.items() if k != "DYAD_NO_NESTED_TESTS"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[Rule-12] dyad.tests.test_playbooks: Ran 8 tests OK", r.stdout)   # 4 + the d-work trace play-book's 4 (#213)
        # the target only, never the whole root: `cmd_tests` prints one `[Rule-12] … Ran` line for one
        # dotted target, where a rootful run prints one per test root (six as this repo stands). #186
        # replaced `assertNotIn("Ran 479", …)`: 479 was a whole-root total from an older tree, and the
        # root has held several hundred methods more for many d-works, so the literal could not appear
        # in any run and the assertion could not fail. A count does not rot the same way — it fails
        # both if the roots are run and if the line stops being printed at all — and it pins no total.
        ran = [l for l in r.stdout.splitlines() if "[Rule-12]" in l and "Ran" in l]
        self.assertEqual(len(ran), 1, r.stdout)
        pkg = load_package()
        self.assertIn("DYAD_NO_NESTED_TESTS", inspect.getsource(pkg.run_suite))   # the flag is the point (120 s -> 39 s)

    def test_tests_verb_exits_non_zero_on_a_failing_target(self):
        r = subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "check", "--tests",
                            "dyad.tests.no_such_module_155"], capture_output=True, text=True,
                           env={k: v for k, v in os.environ.items() if k != "DYAD_NO_NESTED_TESTS"})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_tests_verb_and_guard_suite_do_not_recurse_inside_a_test_run(self):
        """Both return early under DYAD_NO_NESTED_TESTS — without it a suite that invokes `check`
        re-enters the suite (observed live in #155: 44 orphaned unittest processes)."""
        pkg = load_package()
        self.assertEqual(pkg.cmd_tests(), 0)            # env() sets the flag for this whole suite
        for src in (inspect.getsource(pkg.cmd_tests), inspect.getsource(pkg.suite_gate)):   # cmd_guards' gate: suite_gate (#164)
            self.assertIn("DYAD_NO_NESTED_TESTS", src)
        self.assertIn("suite_gate(", inspect.getsource(pkg.cmd_guards))

    def test_evidence_runs_the_suite_once(self):
        """`cmd_evidence` calls `cmd_check` and then `cmd_guards`; the suite belongs to the first
        of them only, or the evidence block pays for the whole suite twice (#155, caught by the
        pre-merge evidence run). Asserted in-process: spawning `check --evidence` from here would
        re-enter this very suite, which is the recursion the same d-work already logged."""
        pkg = load_package()
        pkg._SUITE_RAN = True
        calls = []
        buf = io.StringIO()
        # #163 (d-work #199 N3a): the gate is what is asserted, not the guards, so the registry is emptied rather
        # than run in full over the real repo; and the nesting flag is dropped so `_SUITE_RAN` alone must stop it
        with unittest.mock.patch.object(pkg, "registry", lambda: []), \
             unittest.mock.patch.object(pkg, "cmd_tests", lambda *a, **k: calls.append(a) or 0), \
             unittest.mock.patch.dict(os.environ, {}, clear=False), contextlib.redirect_stdout(buf):
            os.environ.pop("DYAD_NO_NESTED_TESTS", None)
            pkg.cmd_guards()
        self.assertNotIn("[Rule-12]", buf.getvalue())
        self.assertEqual(calls, [], buf.getvalue())     # the suite was not reached a second time
        self.assertIn("_SUITE_RAN", inspect.getsource(pkg.suite_gate))   # the gate cmd_guards consults (#164)
        self.assertIn("_SUITE_RAN = True", inspect.getsource(pkg.check_rule_12))
        self.assertIn("_SUITE_RAN = True", inspect.getsource(pkg.cmd_tests))

    def test_guards_run_the_suite_when_the_base_ref_does_not_resolve(self):
        """#158: the transaction guards need the base ref and say so; the suite does not. It used to
        sit after an early `return`, so a fresh install, a system with no remote, or one whose
        default branch is not `main` never ran Rule-12's suite at push at all — the release's
        headline, inert exactly where a downstream installation starts. An unknown range cannot be
        shown ledger-only, so the safe default is to test."""
        pkg = load_package(); pkg._SUITE_RAN = False
        calls = []
        # #163 (d-work #199 N3a): the suite gate is asserted, not the guards, so the registry is emptied rather
        # than run in full over the real repo; rc 0 then reads the gate's own result, not every guard's
        with unittest.mock.patch.object(pkg, "registry", lambda: []), \
             unittest.mock.patch.object(pkg, "cmd_tests", lambda *a, **k: calls.append(a) or 0), \
             unittest.mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DYAD_NO_NESTED_TESTS", None)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = pkg.cmd_guards(base="refs/heads/no-such-base-158")
            out = buf.getvalue()
        self.assertIn("skip [guards] transaction guards: no refs/heads/no-such-base-158", out)
        self.assertNotIn("skip [guards] Rule-12 suite", out)   # unknown range -> run it, never skip
        self.assertEqual(len(calls), 1, out)                   # the suite was reached
        self.assertEqual(rc, 0, out)

    def gate_repo(self):
        """A scratch repo: `seed` (one file), then `ledger` (a row under `<instance>/d-work/`). Returns
        (repo, seed sha, git). Built without GIT_VARS, removed at module teardown."""
        inst = os.environ.get("DYAD_INSTANCE", "agent-corpus")
        d = SCRATCH.mkdtemp()
        git = lambda *a: subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True, env=dyadlib.git_env()).stdout.strip()
        git("init", "-q", "-b", "main")
        for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
            git("config", k, v)
        (d / "seed.txt").write_text("seed\n"); git("add", "-A"); git("commit", "-qm", "seed")
        seed = git("rev-parse", "HEAD")
        rows = d / inst / "d-work" / "rows"; rows.mkdir(parents=True)
        (rows / "1.md").write_text("id: 1\n"); git("add", "-A"); git("commit", "-qm", "ledger")
        return d, seed, git

    def gate_run(self, pkg, base, evidence=False):
        """`cmd_guards` (or `cmd_evidence`) over the real gate with the registry emptied and `cmd_tests`
        recorded (#163 idiom, d-work #199 N3a), the invariant pass stubbed (it loads modules under `REPO`,
        here a scratch repo); returns (suite calls, output)."""
        calls, buf = [], io.StringIO()
        pkg._SUITE_RAN = False
        def rule_12():
            pkg._SUITE_RAN = True; calls.append(("check",)); return []
        with unittest.mock.patch.object(pkg, "registry", lambda: []), \
             unittest.mock.patch.object(pkg, "cmd_invariants", lambda: 0), \
             unittest.mock.patch.object(pkg, "cmd_tests", lambda *a, **k: calls.append(a) or 0), \
             unittest.mock.patch.object(pkg, "CHECKS", {"Rule-12": rule_12}), \
             unittest.mock.patch.dict(os.environ, {}, clear=False), contextlib.redirect_stdout(buf):
            os.environ.pop("DYAD_NO_NESTED_TESTS", None)
            if evidence:
                pkg.cmd_evidence()
            else:
                pkg.cmd_guards(base=base)
        return calls, buf.getvalue()

    def test_suite_gate_truth_table(self):
        """#164 (d-work #199 N1): `suite_gate`'s decision order, each row over a real range."""
        pkg = load_package(); d, seed, git = self.gate_repo()
        old = pkg.REPO; pkg.REPO = d
        try:
            with unittest.mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("DYAD_NO_NESTED_TESTS", None)
                pkg._SUITE_RAN = False
                self.assertEqual(pkg.suite_gate("HEAD", "HEAD"), (False, "skip [guards] Rule-12 suite: HEAD..HEAD is empty (d-work #164)"))
                self.assertEqual(pkg.suite_gate(seed, "HEAD"), (False, f"skip [guards] Rule-12 suite: {seed}..HEAD is ledger-only (d-work #155)"))
                self.assertEqual(pkg.suite_gate("refs/heads/no-such-164", "HEAD"), (True, None))   # unreadable range -> run
                self.assertEqual(pkg.suite_gate("HEAD", "HEAD", base_ok=False), (True, None))      # base unresolved -> run, before the range
                with unittest.mock.patch.object(dyadlib, "range_paths", lambda *a, **k: None):
                    self.assertEqual(pkg.suite_gate(seed, "HEAD"), (True, None))                   # None, never read as empty
                pkg._SUITE_RAN = True
                self.assertEqual(pkg.suite_gate("HEAD", "HEAD"), (False, None))                    # already ran: silent
                pkg._SUITE_RAN = False
                os.environ["DYAD_NO_NESTED_TESTS"] = "1"
                self.assertEqual(pkg.suite_gate(seed, "HEAD"), (False, None))                      # nested: silent
                os.environ.pop("DYAD_NO_NESTED_TESTS")
                (d / "note.md").write_text("a play-book, not a .py\n"); git("add", "-A"); git("commit", "-qm", "md")
                self.assertEqual(pkg.suite_gate(seed, "HEAD"), (True, None))                       # markdown counts -> run
        finally:
            pkg.REPO = old

    def test_guards_gate_the_suite_on_a_ledger_only_range(self):
        """The wiring of `suite_gate`'s decision to the suite call, over one gate repo
        (`test_suite_gate_truth_table` holds the decisions themselves). The prefix, never the suffix:
        a `.py` filter would have passed #137's markdown run-book, which broke the core suite by
        falsifying a pinned count. Merged from the empty- and unreadable-range tests (d-work #203 N2)."""
        pkg = load_package(); d, seed, git = self.gate_repo()
        old = pkg.REPO; pkg.REPO = d
        try:
            with self.subTest("empty range -> skip"):
                # #164 (d-work #199 N1): `HEAD == base` changes nothing, so it cannot change a suite's outcome
                # (#190: 115 s for that). The plan gate and the fence still read an empty range as not ledger-only.
                calls, out = self.gate_run(pkg, "HEAD")
                self.assertIn("skip [guards] Rule-12 suite: HEAD..HEAD is empty (d-work #164)", out)
                self.assertEqual(calls, [], out)
                self.assertFalse(dyadlib.ledger_only(d, "HEAD", "HEAD"))   # unchanged for the plan gate and the fence
            with self.subTest("unreadable range -> run"):
                # #164: `range_paths` answering None (git could not say) is never read as empty — run.
                with unittest.mock.patch.object(dyadlib, "range_paths", lambda *a, **k: None):
                    calls, out = self.gate_run(pkg, "HEAD")
                self.assertNotIn("skip [guards] Rule-12 suite", out)
                self.assertEqual(len(calls), 1, out)
            with self.subTest("ledger-only range -> skip"):
                calls, out = self.gate_run(pkg, seed)
                self.assertIn(f"skip [guards] Rule-12 suite: {seed}..HEAD is ledger-only (d-work #155)", out)
                self.assertEqual(calls, [], out)
            with self.subTest("markdown range -> run"):
                (d / "note.md").write_text("a play-book, not a .py\n"); git("add", "-A"); git("commit", "-qm", "md")
                calls, out = self.gate_run(pkg, seed)                              # non-empty, not ledger-only -> run
                self.assertNotIn("skip [guards] Rule-12 suite", out)
                self.assertEqual(len(calls), 1, out)
        finally:
            pkg.REPO = old

    def test_evidence_runs_the_suite_on_an_empty_range(self):
        """#164: `check --evidence` is the merge evidence (Rule-14 p3) and observes; its `cmd_check` runs
        the suite before `cmd_guards` meets the gate, so an empty range never skips it there."""
        pkg = load_package(); d, seed, git = self.gate_repo()
        old = pkg.REPO; pkg.REPO = d
        try:
            calls, out = self.gate_run(pkg, "HEAD", evidence=True)
            self.assertEqual(calls, [("check",)], out)             # the suite ran, once, through cmd_check
            self.assertNotIn("skip [guards] Rule-12 suite", out)   # the gate's skip line never enters evidence
        finally:
            pkg.REPO = old

    # Rule-19 (d-work #150): the run-book subcommand dispatches to scripts/runbook.py (core; #155 amendment)
    def test_runbook_subcommand_dispatches(self):
        r = self.run_py("runbook")
        self.assertNotEqual(r.returncode, 0); self.assertIn("runbook.py check", r.stderr)
        r = self.run_py("runbook", "list", "no-such-instance")
        self.assertEqual(r.returncode, 2); self.assertIn("refused: no run-book", r.stderr)
        r = self.run_py("runbook", "check")
        if dyadlib.find_guard("workstation", "runbooks") is None:   # no craft provides the check: the documented refusal (#155)
            self.assertEqual(r.returncode, 2); self.assertIn("no craft provides the run-book check", r.stderr)
        else:
            self.assertIn("[rule-19]", r.stdout + r.stderr)
        d = SCRATCH.mkdtemp(); (d / "x.md").write_text("# x\n")   # `new` refuses to overwrite an existing run-book (#155, attack 7)
        r = subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "runbook", "new", "x"], capture_output=True, text=True, env=env(DYAD_RUNBOOKS=str(d)))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        # both refusals are documented: no craft to seed from (core-only install), else the existing file (#171)
        self.assertIn("exists; not overwritten" if dyadlib.craft_glob("templates/runbook.md") else "no craft provides a run-book template", r.stderr)   # keyed on the template, not on any craft being present (dyad-system #1)
        self.assertEqual((d / "x.md").read_text(), "# x\n")
        shutil.rmtree(d, ignore_errors=True)
    def test_usage(self):
        self.assertNotEqual(self.run_py().returncode, 0)
    # #156: build and install go through scripts/distribute.py — deterministic archive, idempotent install (Rule-11 p5)
    def test_build_deterministic(self):
        import hashlib
        d = SCRATCH.mkdtemp()
        a, b = self.run_py("build", str(d / "a.tar.gz")), self.run_py("build", str(d / "b.tar.gz"))
        self.assertEqual(a.returncode, 0, a.stderr); self.assertIn(f"built {d}/a.tar.gz (version {load_package().version()})", a.stdout)
        self.assertEqual(hashlib.sha256((d / "a.tar.gz").read_bytes()).hexdigest(), hashlib.sha256((d / "b.tar.gz").read_bytes()).hexdigest())
        import tarfile
        with tarfile.open(d / "a.tar.gz") as tar:
            names = tar.getnames()
        # #114: `build` archives `release_roots()` — the core tree plus every bundled craft's — so the expectation
        # is derived from it, not from `package_files()` (still core-only: that is what `check`'s own scan judges).
        pkg = load_package(); roots = pkg.release_roots()
        self.assertEqual(names, pkg.distribute.files(pkg.REPO, roots, pkg.core_extra()))
        self.assertTrue(all(any(n.startswith(f"{r}/") for r in roots) or n.startswith(".github/workflows/dyad-") for n in names))
        shutil.rmtree(d, ignore_errors=True)
    # #178 (G3): an upgrade must not leave behind a file the new version dropped — `cmd_install` forgot
    # `prune=True` (distribute.install defaults it False); distribute's own prune mechanics are
    # test_distribute.InstallTests.test_prune_removes_dropped_file_and_empty_dir, this is the CLI wiring.
    # Simulates a retirement (#160's Rule-17/21) by installing the current tree, then planting a file
    # the current source does not have (an older receiving instance's leftover) and installing again.
    def test_install_prunes_a_file_the_new_version_dropped(self):
        d = scratch_install(with_craft=False)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        retired_file = d / "dyad" / "rules" / "RULE-999-retired.md"
        retired_file.write_text("# a Rule an older version of the core shipped; this version dropped it\n")
        retired_dir = d / "dyad" / "scripts" / "old_subsystem"      # an emptied-out directory must go too
        (retired_dir).mkdir(); (retired_dir / "legacy.py").write_text("# retired module\n")
        r = self.run_py("install", str(d))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(retired_file.exists(), "prune=True must remove a file the new version dropped")
        self.assertFalse((retired_dir / "legacy.py").exists())
        self.assertFalse(retired_dir.exists(), "an emptied directory must be pruned too")
        self.assertGreaterEqual(int(r.stdout.split(": ", 1)[1].split(" changes", 1)[0]), 2)   # >=2: both files pruned
        r2 = self.run_py("install", str(d))                          # idempotent: pruning is not a permanent diff
        self.assertIn(f"installed into {d}: 0 changes", r2.stdout, r2.stdout)
        shutil.rmtree(d, ignore_errors=True)
    # d-work #179, G9: a fresh install seeds .gitignore so the first `dyad` command's own bytecode
    # (dyad/scripts/__pycache__/, nested — not a repo-root artifact) is never tracked
    def test_install_seeds_gitignore_and_pycache_is_not_tracked(self):
        d = scratch_install(with_craft=False)
        self.assertTrue((d / ".gitignore").exists())
        ignore_text = (d / ".gitignore").read_text()
        self.assertIn("__pycache__/", ignore_text); self.assertIn("*.pyc", ignore_text)
        pkg = load_package(); self.assertTrue(pkg.CORE_HOOKS.gitignore)
        # a second install changes nothing: the seed is never overwritten (hostadapter.write_gitignore)
        r = self.run_py("install", str(d))
        # cmd_install prints the resolved destination (hostadapter.resolve; d-work #179, G5) — d itself
        # may be a symlink (e.g. macOS /var -> /private/var) even though it never is on this kernel,
        # which is exactly how this assertion passed here by coincidence before the fix (#179 plan, attack 3)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn(f"installed into {Path(d).resolve()}: 0 changes", r.stdout)
        self.assertEqual((d / ".gitignore").read_text(), ignore_text)
        with self.subTest("install twice: import line once, templates, core roots and hooks"):   # merged from test_install_twice_is_zero_changes (d-work #203 N2)
            self.assertEqual((d / "CLAUDE.md").read_text().count("@dyad/CLAUDE.md"), 1)
            for t, rel in pkg.TEMPLATES.items(): self.assertTrue((d / rel).exists(), rel)
            self.assertEqual(pkg.CORE_ROOTS, ["dyad"]); self.assertEqual(pkg.CORE_HOOKS.templates, pkg.TEMPLATES); self.assertEqual(pkg.CORE_HOOKS.import_line, pkg.IMPORT_LINE)
        # the artifact G9 describes: nested bytecode, the shape a real `python3 …/package.py` run leaves
        pyc = d / "dyad" / "scripts" / "__pycache__" / "distribute.cpython-312.pyc"
        pyc.parent.mkdir(parents=True, exist_ok=True); pyc.write_bytes(b"\x00")
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
        tracked = subprocess.run(["git", "-C", str(d), "ls-files"], capture_output=True, text=True, check=True).stdout.split()
        self.assertFalse(any("__pycache__" in t for t in tracked), tracked)
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check"], capture_output=True, text=True, env=env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        shutil.rmtree(d, ignore_errors=True)
    # #166: `check --guards` judges a push (each commit), `check --pr` a PR (the whole diff too)
    def test_check_pr_refuses_a_two_zone_pr_that_the_push_path_accepts(self):
        d = scratch_install(with_craft=False)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        py = [sys.executable, str(d / "dyad" / "scripts" / "package.py")]
        git = lambda *a: subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True).stdout
        def commit(msg, **files):
            for rel, text in files.items():
                p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
            git("add", "-A"); git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", msg)
            return git("rev-parse", "HEAD").strip()
        git("checkout", "-q", "-B", "main")
        rid = subprocess.run(py + ["dwork", "new", "t", "-d", "Y plan", "--said", "Y"], capture_output=True, text=True, env=env(), cwd=d).stdout.strip()
        base = commit(f"ledger: open #{rid}")
        git("remote", "add", "origin", str(d)); git("fetch", "-q", "origin")   # so `check --guards` has an origin/main base
        git("checkout", "-q", "-b", "zone-span")
        commit(f"agent: a file (d-work #{rid})", **{"dyad/a.md": "x"})
        head = commit(f"infra: a file (d-work #{rid})", **{"CLAUDE.md": (d / "CLAUDE.md").read_text() + "\nx\n"})
        g = subprocess.run(py + ["check", "--guards"], capture_output=True, text=True, env=env(), cwd=d)
        self.assertIn("ok   [guards] infra/containment transaction [commits]", g.stdout)   # the push: each commit is one zone
        r = subprocess.run(py + ["check", "--pr", base, head], capture_output=True, text=True, env=env(), cwd=d)
        self.assertNotEqual(r.returncode, 0, r.stdout)                                     # the PR: the whole diff spans two
        self.assertIn("FAIL [pr] infra/containment", r.stdout); self.assertIn("multiple zones: agent infra", r.stdout)
        self.assertIn("ok   [pr] agent/prs", r.stdout)                                     # the plan gate runs in PR mode too
        git("checkout", "-q", "-b", "one-zone", base)                                      # the same work as two single-zone PRs
        one = commit(f"agent: two files, one zone (d-work #{rid})", **{"dyad/a.md": "x", "dyad/b.md": "y"})
        r = subprocess.run(py + ["check", "--pr", base, one], capture_output=True, text=True, env=env(), cwd=d)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ok   [pr] infra/containment range (", r.stdout); self.assertIn("ok   [pr] agent/rows", r.stdout)
    def test_check_pr_refuses_an_unresolvable_ref(self):
        r = self.run_py("check", "--pr", "no-such-ref-166", "HEAD")
        self.assertEqual(r.returncode, 2); self.assertIn("does not resolve to a commit", r.stderr)
        self.assertNotIn("[pr]", r.stdout)
        self.assertEqual(self.run_py("check", "--pr").returncode, 2)
    def test_craft_subcommand_dispatches(self):
        r = self.run_py("craft")
        self.assertEqual(r.returncode, 2); self.assertIn("dyad craft list", r.stderr)
        r = self.run_py("craft", "list")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("dyad-operator", r.stdout)   # the core craft, always
        for c in CRAFTS: self.assertIn(c, r.stdout, c)                                          # and every Tended craft installed (#171)
    # #155: the second guard root, in a scratch install with and without the sysadmin craft (attack 6)
    def test_scratch_install_without_a_craft_runs_the_core_registry(self):
        """A core install's own registry is the core guards plus every **bundled** craft's, and
        nothing else (Rule-11 p2, d-work #114). Before bundling that set was exactly `CORE`; the
        assertions below derive the craft half from `bundled_crafts()` instead of assuming it is
        empty, so this holds on a tree where no craft declares itself as well as on one where
        sysadmin does. The conditional blocks are the same statement seen from either side: what a
        core install can and cannot do depends on whether anything came with it."""
        pkg = load_package()
        bundled = pkg.bundled_crafts()
        d = scratch_install(with_craft=False)
        py = [sys.executable, str(d / "dyad" / "scripts" / "package.py")]
        r = subprocess.run(py + ["check", "--list"], capture_output=True, text=True, env=env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        labels = [l.split()[0] + "/" + l.split()[1] for l in r.stdout.splitlines()[1:]]
        self.assertEqual(labels, CORE + [f"{c}/{e}" for c in bundled for e in craft_guards(c)])
        self.assertEqual(livetest.crafts_installed(d / "dyad"), bundled, "a core install carries exactly the bundled crafts")
        r = subprocess.run(py + ["check", "--guards"], capture_output=True, text=True, env=env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # Rule-11 property 2's contribution mechanism (#101) retired these four core rows in favor of
        # the sysadmin craft's own `REFERENCES_CONTRIB`. With no craft installed they print nothing
        # at all, never a skip line — there is no core row left to skip. With that craft *bundled*,
        # they print again, each tagged with the contributing craft's own name: the same property
        # from the other side, and the sharper check of the two, since it proves the row travels
        # with its craft rather than merely vanishing (Rule-11 p2, d-work #114). Which craft
        # contributes which kind is read from the register, never assumed.
        contrib = {row[0]: craft for craft, row in
                   dyadlib.load_guard("agent", "references").craft_references_contrib()}
        for kind in ("changelog.action->ops", "ops.dwork->row", "ops.changelog->changelog", "changelog.event->event"):
            craft = contrib.get(kind)
            self.assertIsNotNone(craft, f"{kind} is a craft contribution, not a core row")
            if craft in bundled:
                # It is the craft's row, so it may print (a skip, when its store is empty) or stay
                # silent (when it resolves) — but it is never an untagged *core* row again.
                if kind in r.stdout:
                    self.assertIn(f"{kind} (crafts/{craft})", r.stdout, kind)
            else:
                self.assertNotIn(kind, r.stdout, kind)   # the craft is gone and its row went with it
        self.assertNotIn("skip event.command->command", r.stdout)   # no craft needed: the core run-book (dyad/runbooks/craft.md) resolves alone; nothing prints with no events store to check against it (#213 d-work #46)
        if bundled:   # a crafts/ tree exists, so the whole-tree skip no longer fires and each craft resolves on its own (#167)
            self.assertNotIn("no crafts/ tree is installed", r.stdout)
        else:
            self.assertIn("skip rule.text->path: `crafts/…` tokens; no crafts/ tree is installed", r.stdout)   # Rules 1, 11 name crafts/ paths
        self.assertFalse((d / "workstation-corpus" / "CHANGELOG.md").exists())   # no core seed since #155; the craft's install seeds it (#156)
        r = subprocess.run(py + ["runbook", "check"], capture_output=True, text=True, env=env())
        if any("runbooks" in craft_guards(c) for c in bundled):   # a bundled craft supplies the check, so it runs instead of refusing
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        else:
            self.assertEqual(r.returncode, 2); self.assertIn("no craft provides the run-book check", r.stderr)
        r = subprocess.run(py + ["runbook", "list", "x"], capture_output=True, text=True, env=env())
        self.assertEqual(r.returncode, 2); self.assertIn("refused: no run-book", r.stderr)   # the runner itself works without a craft (#155 amendment)
        shutil.rmtree(d, ignore_errors=True)
    def test_scratch_install_with_the_sysadmin_craft_discovers_its_guards(self):
        self.require_craft("sysadmin")
        d = scratch_install(with_craft=True)
        py = [sys.executable, str(d / "dyad" / "scripts" / "package.py")]
        r = subprocess.run(py + ["check", "--list"], capture_output=True, text=True, env=env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rows = [l.split() for l in r.stdout.splitlines()[1:]]
        self.assertEqual([f"{a}/{b}" for a, b, *_ in rows], CORE + CRAFT)
        self.assertEqual({r_[4] for r_ in rows if r_[0] == "sysadmin"}, {"craft"}); self.assertEqual({r_[2] for r_ in rows if r_[0] == "sysadmin"}, {f"crafts/sysadmin/guards/{e}.py" for e in ("changelog", "events", "ops_scripts", "runbooks")})
        r = subprocess.run(py + ["check", "--guards"], capture_output=True, text=True, env=env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for g in CRAFT: self.assertIn(f"ok   [guards] {g}", r.stdout)
        self.assertIn(f"ok   [guards] craft/crafts ({len(dyadlib.craft_dirs())} craft(s))", r.stdout)   # the craft guard checks the copied crafts (#156; sysarch since #160; syseng #162)
        self.assertNotIn("guard sysadmin/", r.stdout)   # nothing skipped for an absent guard
        r = subprocess.run(py + ["runbook", "check"], capture_output=True, text=True, env=env())
        self.assertEqual(r.returncode, 0, r.stderr)
        core_rbs = sorted(p_.stem for p_ in (dyadlib.PKG / "runbooks").glob("*.md"))
        self.assertIn(f"ok   [rule-19] {len(core_rbs)} run-book(s), ", r.stdout)   # every core run-book ships with the package (#165, #137); the count is derived, never pinned (backlog #10)
        for name in core_rbs: self.assertIn(name, subprocess.run(py + ["runbook", "list", name], capture_output=True, text=True, env=env()).stdout + name)
        shutil.rmtree(d, ignore_errors=True)
    # #177 (Rule-11 property 5): the scratch install above only ever ran `check --guards` with an
    # EMPTY ledger — property 4's empty-store skip made that trivially green. The moment a single
    # d-work exists, this install's *own* package (`dyad/`'s and every craft's `ledger #N` /
    # `d-work #N` citations in Rule text and falsification records) used to fail `agent/references`
    # forever (109 record.ledger->row + 9 rule.text->row, reproduced identically against #176's
    # report). Regression test for that fix (references.py: those kinds resolve `world`, not
    # against this install's own rows).
    def test_scratch_install_with_one_row_survives_referential_integrity(self):
        d = scratch_install(with_craft=True)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        py = [sys.executable, str(d / "dyad" / "scripts" / "package.py")]
        git = lambda *a: subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True).stdout
        r = subprocess.run(py + ["dwork", "new", "t", "-d", "Y plan", "--said", "Y"], capture_output=True, text=True, env=env(), cwd=d)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rid = r.stdout.strip()
        self.assertTrue((d / "agent-corpus" / "d-work" / "rows" / f"{rid}.md").exists())
        git("add", "-A"); git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", f"ledger: open #{rid}")
        g = subprocess.run(py + ["check", "--guards"], capture_output=True, text=True, env=env(), cwd=d)
        self.assertEqual(g.returncode, 0, g.stdout + g.stderr)
        self.assertNotIn("FAIL", g.stdout)
        self.assertIn("ok   [guards] agent/references", g.stdout)
        # #191: the pre-push path refuses a row pushed without the words that opened it
        git("checkout", "-q", "-B", "main"); git("remote", "add", "origin", str(d)); git("fetch", "-q", "origin")
        git("checkout", "-q", "-b", "gap")
        row = d / "agent-corpus" / "d-work" / "rows" / f"{int(rid) + 1}.md"
        row.write_text(f"id: {int(rid) + 1}\ntitle: t\nopened: 2026-09-29\nstate: open\ndisposed: \nrefs: \n")
        git("add", "-A"); git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "ledger: a row by hand")
        g = subprocess.run(py + ["check", "--guards"], capture_output=True, text=True, env=env(), cwd=d)
        self.assertNotEqual(g.returncode, 0, g.stdout)
        self.assertIn("FAIL [guards] agent/provenance", g.stdout); self.assertIn("its record gains no entry", g.stdout)
        c = subprocess.run(py + ["check"], capture_output=True, text=True, env=env(), cwd=d)
        self.assertEqual(c.returncode, 0, c.stdout + c.stderr)
        self.assertNotIn("FAIL", c.stdout)
    def test_craft_guard_with_a_bad_corpus_fails_the_run(self):
        self.require_craft("sysadmin")
        d = scratch_install(with_craft=True)
        g = d / "crafts" / "sysadmin" / "guards" / "runbooks.py"; g.write_text(g.read_text().replace('"command", "workstation", False', '"command", "nowhere", False'))
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--list"], capture_output=True, text=True, env=env())
        self.assertNotEqual(r.returncode, 0); self.assertIn("declares CORPUS 'nowhere', not a zone in containment.ZONES", r.stdout)
        shutil.rmtree(d, ignore_errors=True)
    # Rule-14 property 3 (d-work #138): the evidence block. d-work #108 (separation of concerns):
    # the shape assertions still exercise a real `cmd_evidence()` traversal (unavoidably
    # integration-flavored — head/tree/dirty and the guard lines come from the real repo), but
    # in-process (load_package() + redirect_stdout, no subprocess) and with DYAD_NO_NESTED_TESTS
    # forced for the call's duration so Rule-12's own nested-suite recursion guard applies exactly
    # as it does for run_py's subprocess env. The hash property itself is unit-tested separately,
    # on fixed fake lines, in test_evidence_sha256_is_pure_and_deterministic below.
    def test_evidence_block_shape_and_hash(self):
        import contextlib, io
        pkg = load_package()
        buf = io.StringIO()
        with unittest.mock.patch.dict(os.environ, {"DYAD_NO_NESTED_TESTS": "1"}), contextlib.redirect_stdout(buf):
            pkg.cmd_evidence()
        lines = buf.getvalue().splitlines()
        self.assertRegex(lines[0], r"^head=[0-9a-f]{40}$"); self.assertRegex(lines[1], r"^tree=[0-9a-f]{40}$")
        self.assertRegex(lines[2], r"^dirty=(yes|no)$")
        self.assertTrue(any("[Rule-11]" in l for l in lines) and any("[guards] infra/containment" in l for l in lines), buf.getvalue())
        self.assertRegex(lines[-1], r"^evidence-sha256=[0-9a-f]{64}$")
        self.assertEqual(lines[-1], "evidence-sha256=" + pkg.evidence_sha256(lines[:-1]))
    def test_evidence_block_deterministic(self):
        pkg = load_package()
        lines = ["head=deadbeef", "dirty=no", "ok   [Rule-11]"]
        self.assertEqual(pkg.evidence_sha256(lines), pkg.evidence_sha256(list(lines)))
        self.assertNotEqual(pkg.evidence_sha256(lines), pkg.evidence_sha256(lines + ["extra"]))

    # Rule-11 property 6 (generated files, d-work #108)
    def test_generated_entries_parse(self):
        g = load_package().rules()["generated"]
        self.assertIn("*.pyc", g); self.assertIn("__pycache__/*", g)
    def test_tracked_pyc_refused_in_package_and_instance(self):
        pkg = load_package()
        paths = ["dyad/scripts/__pycache__/a.cpython-312.pyc", "agent-corpus/tools/__pycache__/b.cpython-312.pyc",
                 "agent-corpus/deep/__pycache__/nested/c.txt", "dyad/README.md"]
        d = scratch_repo(paths)
        fails = pkg.check_generated(d, pkg.rules()["generated"])
        self.assertEqual(len(fails), 3, fails)
        for rel in paths[:3]:
            self.assertTrue(any(f.startswith(rel + ":") for f in fails), rel)
    def test_untracked_pyc_not_refused(self):
        pkg = load_package()
        d = scratch_repo(["dyad/scripts/__pycache__/a.cpython-312.pyc"], tracked=False)
        self.assertEqual(pkg.check_generated(d, pkg.rules()["generated"]), [])
    def test_tracked_ledger_render_refused(self):
        # d-work #111: LEDGER.md is a rendered view (Rule-16); tracking it anywhere is refused
        pkg = load_package()
        d = scratch_repo(["agent-corpus/d-work/LEDGER.md", "agent-corpus/d-work/rows/1.md"])
        fails = pkg.check_generated(d, pkg.rules()["generated"])
        self.assertEqual(len(fails), 1, fails); self.assertIn("generated file tracked", fails[0])
        self.assertTrue(fails[0].startswith("agent-corpus/d-work/LEDGER.md:"))
    # d-work #112: `dwork state` refuses targets outside dyadlib.STATES and disallowed transitions
    def dwork_repo(self):
        """A scratch git repo with its own instance dir; DYAD_INSTANCE keeps the real rows untouched."""
        d = scratch_repo(["README.md"])
        rows = d / "inst" / "d-work" / "rows"; rows.mkdir(parents=True)
        rows.joinpath("1.md").write_text("id: 1\ntitle: one\nopened: d\nstate: open\ndisposed: \nrefs: \n")
        rows.joinpath("2.md").write_text("id: 2\ntitle: two\nopened: d\nstate: done\ndisposed: Y done\nrefs: \n")
        return d, rows
    def dwork_state(self, d, *a):
        import os
        env = dict(os.environ, DYAD_INSTANCE=str(d / "inst"))  # absolute: package.py resolves REPO from its own location
        return subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "dwork", "state", *a],
                              cwd=d, env=env, capture_output=True, text=True)
    def dwork_new(self, d, *a):
        import os
        env = dict(os.environ, DYAD_INSTANCE=str(d / "inst"))
        return subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "dwork", "new", *a],
                              cwd=d, env=env, capture_output=True, text=True)
    # d-work #140: `dwork new` may create a row in any dyadlib.NEW_STATES state
    def test_dwork_new_defaults_to_open(self):
        d, rows = self.dwork_repo()
        r = self.dwork_new(d, "three", "#1", "--prompt", "open three")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "3")
        text = rows.joinpath("3.md").read_text()
        self.assertIn("state: open\n", text); self.assertIn("refs: #1\n", text)
    def test_dwork_new_backlog_flag(self):
        d, rows = self.dwork_repo()
        r = self.dwork_new(d, "four", "--backlog", "-d", "Y backlog, on #2 Done", "--said", "Y", "#2")
        self.assertEqual(r.returncode, 0, r.stderr)
        text = rows.joinpath("3.md").read_text()
        self.assertIn("state: backlog\n", text); self.assertIn("refs: #2\n", text)
        self.assertIn("Y backlog, on #2 Done", text)
    # d-work #133: a `;` in -d text splits one disposed entry in two; a flag in the title slot became a title
    def test_dwork_refuses_semicolon_in_disposition_text(self):
        d, rows = self.dwork_repo()
        for r in (self.dwork_state(d, "1", "planned", "-d", "N plan (a; b)"), self.dwork_new(d, "three", "-d", "Y x; y")):
            with self.subTest(args=r.args[3:]):
                self.assertNotEqual(r.returncode, 0); self.assertIn("contains ';'", r.stderr)
        self.assertIn("state: open\n", rows.joinpath("1.md").read_text()); self.assertFalse(rows.joinpath("3.md").exists())
    def test_dwork_new_never_takes_a_flag_as_title(self):
        """#133 wrote `--backlog` as a title; #191 parses flags by position, so a flag before the title is a
        flag, and a flag before the verb is refused rather than read as the title (the title is immutable)."""
        d, rows = self.dwork_repo()
        r = self.dwork_new(d, "--backlog", "four", "-d", "Y backlog", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("title: four\n", rows.joinpath("3.md").read_text()); self.assertIn("state: backlog\n", rows.joinpath("3.md").read_text())
        import os
        env = dict(os.environ, DYAD_INSTANCE=str(d / "inst"))
        r = subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "dwork", "--prompt", "the words", "new", "five"],
                           cwd=d, env=env, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0); self.assertIn("the verb first", r.stderr)
        self.assertFalse(rows.joinpath("4.md").exists())
    # d-work #191: the row and its provenance record are written in one step, or not at all
    def test_dwork_writes_the_record_with_the_row(self):
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv = dyadlib.load_guard("agent", "provenance")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"
        words = d / "p.txt"; words.write_text("do it\n```\nfenced\n```\n")
        r = self.dwork_new(d, "three", "#1", "--prompt-file", str(words))
        self.assertEqual(r.returncode, 0, r.stderr)
        e = pv.parse(rec.joinpath("3.md").read_text())
        self.assertEqual([(x["kind"], x["text"]) for x in e], [("prompt", "do it\n```\nfenced\n```")])   # verbatim, fenced as data
        r = self.dwork_state(d, "3", "planned", "-d", "Y plan", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
        e = pv.parse(rec.joinpath("3.md").read_text())
        self.assertEqual([(x["n"], x["kind"], x["note"], x["text"]) for x in e][1], ("2", "disposition", "Y plan", "Y"))
        row = dyadlib.parse_row_file(rows.joinpath("3.md").read_text())
        self.assertEqual(pv.check_record(rec / "3.md", row=row), [])                        # property 5 holds by construction
        r = self.dwork_new(d, "four", "--backlog", "-d", "Y backlog, from #3", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([x["kind"] for x in pv.parse(rec.joinpath("4.md").read_text())], ["disposition"])
        r = self.dwork_state(d, "1", "open", "--prompt", "go on with one")                   # a prompt received on an existing row
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([x["kind"] for x in pv.parse(rec.joinpath("1.md").read_text())], ["prompt"])
    def test_dwork_refuses_a_row_or_a_disposition_without_its_words(self):
        d, rows = self.dwork_repo(); before = rows.joinpath("1.md").read_text()
        cases = [(self.dwork_new, ("three",), "opened by the Operator's words"),
                 (self.dwork_new, ("three", "-d", "Y open"), "--said"),
                 (self.dwork_new, ("three", "--backlog", "--prompt", "p"), "opens a row by disposition"),
                 (self.dwork_new, ("three", "--said", "Y"), "name it in the row with -d"),
                 (self.dwork_new, ("three", "--said", "Y", "--said-file", "x", "-d", "Y"), "not both"),
                 (self.dwork_state, ("1", "planned", "-d", "Y plan"), "--said"),
                 (self.dwork_state, ("1", "planned", "-d"), "needs a value"),
                 (self.dwork_state, ("1", "planned", "-d", "Y plan", "--said", "  "), "empty"),
                 (self.dwork_new, ("three", "--prompt", "real words", "-d", "Y open", "--said", " "), "empty"),   # nothing half-written
                 (self.dwork_new, ("three", "--prompt", "```\n~~~\n"), "no fence can hold it")]
        for fn, args, msg in cases:
            with self.subTest(args=args):
                r = fn(d, *args)
                self.assertNotEqual(r.returncode, 0); self.assertIn(msg, r.stderr)
        self.assertEqual(rows.joinpath("1.md").read_text(), before, "nothing written")
        self.assertFalse(rows.joinpath("3.md").exists()); self.assertFalse((rows.parent / "provenance").exists())
    def test_dwork_backlog_opens_only_on_a_prompt(self):
        d, rows = self.dwork_repo()
        rows.joinpath("5.md").write_text("id: 5\ntitle: five\nopened: d\nstate: backlog\ndisposed: \nrefs: \n")
        r = self.dwork_state(d, "5", "open")
        self.assertNotEqual(r.returncode, 0); self.assertIn("opens on the Operator's prompt", r.stderr)
        self.assertIn("state: backlog", rows.joinpath("5.md").read_text())
        r = self.dwork_state(d, "5", "open", "--prompt", "work five")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("state: open", rows.joinpath("5.md").read_text())
    def test_dwork_record_entries_are_verbatim_and_complete(self):
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv = dyadlib.load_guard("agent", "provenance")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"
        f = d / "w.txt"; f.write_bytes("  indented\r\n\r\n  ```\n  fenced, indented: data\n  ```\n~~~ at column 0\nend\r\n".encode())
        r = self.dwork_new(d, "three", "--prompt-file", str(f), "-d", "Y open, intake", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
        e = pv.parse(rec.joinpath("3.md").read_text())
        self.assertEqual([(x["kind"], x["note"]) for x in e], [("prompt", ""), ("disposition", "Y open, intake")])
        self.assertTrue(e[0]["text"].startswith("  indented"))            # leading whitespace kept
        self.assertIn("  ```", e[0]["text"]); self.assertIn("~~~ at column 0", e[0]["text"])   # an indented fence is data
        self.assertTrue(e[0]["text"].endswith("end"))                    # one final line ending dropped, no more
        rows.joinpath("3.md").unlink()                                   # an orphan record for the next id
        r = self.dwork_new(d, "again", "--prompt", "p")
        self.assertNotEqual(r.returncode, 0); self.assertIn("already exists for the new id", r.stderr)
        g = d / "latin1.txt"; g.write_bytes("caf\xe9".encode("latin-1"))
        r = self.dwork_new(d, "four", "--prompt-file", str(g))
        self.assertNotEqual(r.returncode, 0); self.assertIn("refused: --prompt-file", r.stderr); self.assertNotIn("Traceback", r.stderr)
    def test_dwork_refuses_what_it_would_drop_or_forge(self):
        """#191: a line break in -d forges structure in the row and the record heading; an unknown flag,
        a stray argument or a non-numeric id is refused before any write, never silently dropped."""
        d, rows = self.dwork_repo(); before = rows.joinpath("1.md").read_text()
        cases = [(self.dwork_state, ("1", "planned", "-d", "Y plan\n## 9 prompt 2026-01-01", "--said", "Y"), "line break"),
                 (self.dwork_new, ("three", "--prompt", "p", "--promt-file", "x"), "does not take --promt-file"),
                 (self.dwork_new, ("three", "#1", "extra", "--prompt", "p"), "unexpected argument"),
                 (self.dwork_new, ("three", "#1", "-r", "#2", "--prompt", "p"), "refs given twice"),
                 (self.dwork_new, ("three", "--relayed-via", "peer", "-d", "Y", "--said", "Y"), "give the prompt too"),
                 (self.dwork_state, ("x", "open"), "is not a number")]
        for fn, args, msg in cases:
            with self.subTest(args=args):
                r = fn(d, *args)
                self.assertNotEqual(r.returncode, 0); self.assertIn(msg, r.stderr); self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(rows.joinpath("1.md").read_text(), before, "nothing written")
        self.assertFalse(rows.joinpath("3.md").exists()); self.assertFalse((rows.parent / "provenance").exists())
    def test_dwork_new_takes_refs_by_flag_and_notes_a_relayed_prompt(self):
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv = dyadlib.load_guard("agent", "provenance")
        d, rows = self.dwork_repo()
        f = d / "p.txt"; f.write_text("keep the blank line\n\n")
        r = self.dwork_new(d, "three", "-r", "#1", "--prompt-file", str(f), "--relayed-via", "peer-session")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("refs: #1\n", rows.joinpath("3.md").read_text())
        e = pv.parse((rows.parent / "provenance" / "3.md").read_text())[0]
        self.assertEqual((e["note"], e["text"]), ("relayed via peer-session", "keep the blank line\n"))   # one line ending dropped, not two
    def test_dwork_flag_values_are_never_positionals(self):
        pkg = load_package()
        self.assertEqual(pkg.dwork_args(["new", "t", "-d", "#1", "#2", "--said", "Y", "--backlog"]),
                         (["new", "t", "#2"], {"-d": "#1", "--said": "Y"}, {"--backlog"}))   # -d's value is not the refs
    # F3, d-work #32: cmd_dwork's fetch of origin/main used to fail silently; it now warns loudly
    # and states that allocation fell back to local ids, before still allocating from what it has.
    def test_dwork_new_warns_loudly_when_origin_main_is_unreadable(self):
        import io, contextlib
        from unittest import mock
        d, rows = self.dwork_repo()
        pkg = load_package()
        real_read_rows = dyadlib.read_rows
        def fake(root, at=None):
            if at == "origin/main":
                raise RuntimeError("simulated: origin unreachable")
            return real_read_rows(root, at=at)
        env = dict(os.environ, DYAD_INSTANCE=str(d / "inst"))
        with mock.patch.dict(os.environ, env), mock.patch.object(dyadlib, "read_rows", side_effect=fake):
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = pkg.cmd_dwork(["new", "three", "#1", "--prompt", "open three"])
        self.assertEqual(rc, 0)
        self.assertIn("warning: could not read origin/main's rows", stderr.getvalue())
        self.assertIn("local ids only", stderr.getvalue())
        self.assertIn("d-work #32", stderr.getvalue())
        text = rows.joinpath("3.md").read_text()   # allocation still proceeds, from what it has locally
        self.assertIn("id: 3\n", text); self.assertIn("state: open\n", text)
    def test_dwork_state_accepts_open_to_planned(self):
        d, rows = self.dwork_repo()
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("1: planned", r.stdout)
        text = rows.joinpath("1.md").read_text()
        self.assertIn("state: planned", text); self.assertIn("Y plan", text)
    # projector registry (crafts/sysarch/rules/projection.md p4; #160): discovered over crafts/*/projectors/, the generated projections/ pattern
    def test_project_list_prints_discovered_registry(self):
        self.require_craft("sysadmin", "sysarch")   # the surfaces below are theirs; the core-only case is its own test
        r = self.run_py("project", "--list")
        self.assertEqual(r.returncode, 0, r.stderr)
        for surface, craft in (("erd", "sysarch"), ("schema", "sysarch"), ("entities", "sysarch"), ("events", "sysadmin"), ("kanban", "sysarch"), ("instances", "sysarch")):
            self.assertRegex(r.stdout, rf"(?m)^{craft}/{surface}\s+crafts/{craft}/projectors/project_{surface}\.py$")
        pkg = load_package(); reg = pkg.projectors()
        # Registry derived from the tree, not a literal set (#156 I1, the #46/#98 class): any craft may ship
        # a projector. The known surfaces above stay asserted, so one silently dropped still fails.
        on_disk = {f"{p.parents[1].name}/{p.stem.removeprefix('project_')}" for p in (PKG.parent / "crafts").glob("*/projectors/project_*.py")}
        self.assertEqual(set(reg), on_disk)
        self.assertLessEqual({f"{c}/{s}" for c, s in (("sysarch", "entities"), ("sysarch", "erd"), ("sysadmin", "events"), ("sysarch", "schema"), ("sysarch", "kanban"), ("sysarch", "instances"))}, set(reg))
        import re
        listed = {m.group(1) for m in re.finditer(r"(?m)^(\S+/\S+)\s+crafts/\S+/projectors/project_\S+\.py$", r.stdout)}
        self.assertEqual(listed, on_disk, "--list prints exactly the discovered registry")
        self.assertEqual(pkg.PROJECTORS, {k: rel for k, (c, rel) in reg.items()})
        for key, (craft, rel) in reg.items():
            self.assertTrue((pkg.REPO / rel).exists(), rel); self.assertEqual(rel.split("/")[1], craft); self.assertEqual(key, f"{craft}/{key.split('/', 1)[1]}")
    def test_project_unknown_surface_fails(self):
        self.require_craft("sysarch")   # with no projector the line names the install instead (test below)
        r = self.run_py("project", "nope")
        self.assertEqual(r.returncode, 2); self.assertIn("no projector for 'nope': registered:", r.stderr)
    def test_project_on_a_bundled_crafts_only_install_reports_the_registry(self):
        """The minimal install is no longer empty: it is exactly the bundled crafts (Rule-11 p2, d-work #114).
        Asked for a surface no installed craft provides, it still exits 2 and still says what is available --
        the registry when a craft is bundled, the install line when none is. Both sides derive from
        `bundled_crafts()`, so this holds on a tree where no craft declares itself as well as on one where
        sysadmin does. Successor to the core-only case, whose premise (an install with no craft at all) a
        bundled craft ends by design."""
        pkg = load_package()
        d = scratch_install(with_craft=False)
        self.addCleanup(shutil.rmtree, d)
        bundled = pkg.bundled_crafts()
        self.assertEqual(livetest.crafts_installed(d / "dyad"), bundled, "a core install carries exactly the bundled crafts")
        reg = sorted(k for k, (craft, _rel) in pkg.projectors().items() if craft in bundled)
        surface = "no-such-surface"   # named by no craft in this tree, bundled or not
        self.assertNotIn(surface, {k.split("/", 1)[1] for k in pkg.projectors()})
        self.assertIn("dyad craft install", pkg.NO_PROJECTOR, "the empty-registry line names the remedy")
        run = lambda *a: subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "project", *a], capture_output=True, text=True, env=env(), cwd=d)
        r = run(surface)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn(f"no projector for {surface!r}: " + (f"registered: {' '.join(reg)}" if reg else pkg.NO_PROJECTOR), r.stderr)
        r = run("--list")
        self.assertEqual(r.returncode, 0, r.stderr)
        if reg:
            self.assertEqual([l.split()[0] for l in r.stdout.splitlines()], reg)
        else:
            self.assertEqual(r.stdout.strip(), f"no projector: {pkg.NO_PROJECTOR}")
    def test_project_surface_in_two_crafts_disambiguates(self):
        # D3 (#100, #99): two crafts naming the same surface now coexist in the registry — a bare
        # name lists the qualified candidates and exits 2 rather than failing the registry itself
        self.require_craft("sysadmin")
        d = scratch_install(with_craft=True)
        self.addCleanup(shutil.rmtree, d)
        for c in ("a", "b"):
            (d / "crafts" / c / "projectors").mkdir(parents=True); (d / "crafts" / c / "projectors" / "project_x.py").write_text("def main(): return 0\n")
        run = lambda *a: subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "project", *a], capture_output=True, text=True, env=env(), cwd=d)
        r = run("x")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("'x' is provided by more than one craft: a/x, b/x — name one", r.stderr)
        r = run("a/x")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run("--list")
        self.assertIn("a/x", r.stdout); self.assertIn("b/x", r.stdout)
    def test_tracked_projection_refused(self):
        pkg = load_package()
        d = scratch_repo(["agent-corpus/projections/erd.html", "agent-corpus/d-work/rows/1.md"])
        fails = pkg.check_generated(d, pkg.rules()["generated"])
        self.assertEqual(len(fails), 1, fails); self.assertTrue(fails[0].startswith("agent-corpus/projections/erd.html:"))
        self.assertIn("'projections/*'", fails[0])


class BundledCraftTests(unittest.TestCase):
    """Rule-11 property 2's bundled craft (d-work #114). The core keeps no list: a craft is bundled
    only by its own `BUNDLED_WITH_CORE` declaration in one of its guard modules, so these tests
    drive the mechanism through a real craft guard file rather than patching the function."""

    def setUp(self):
        sys.path.insert(0, str(PKG / "scripts"))
        import package
        self.package = package

    def test_release_roots_is_core_plus_bundled(self):
        """`release_roots` is `CORE_ROOTS` plus one `crafts/<name>` per bundled craft, in that order."""
        with unittest.mock.patch.object(self.package, "bundled_crafts", lambda pkg=None: ["zeta", "alpha"]):
            self.assertEqual(self.package.release_roots(), self.package.CORE_ROOTS + ["crafts/zeta", "crafts/alpha"])

    def test_no_declaration_means_core_only(self):
        """A tree whose crafts declare nothing yields exactly the core's own roots — so adding the
        mechanism changes nothing until a craft opts in (the compatibility this d-work relies on)."""
        with unittest.mock.patch.object(self.package, "bundled_crafts", lambda pkg=None: []):
            self.assertEqual(self.package.release_roots(), self.package.CORE_ROOTS)

    def test_declaration_is_discovered_from_a_craft_guard(self):
        """The real discovery path: a craft guard module setting `BUNDLED_WITH_CORE = True` is found
        through `dyadlib.guard_files()`, and one setting it `False`/omitting it is not. Measured
        against the craft stripped of whatever declaration it ships today, never against absolute
        membership of the tree as it stands, so the case holds whether no craft, one craft or every
        craft here declares itself bundled (d-work #114)."""
        crafts = dyadlib.craft_dirs()
        if not crafts:
            self.skipTest("no Tended craft in this tree")
        guards = sorted((crafts[0] / "guards").glob("*.py"))
        if not guards:
            self.skipTest(f"{crafts[0].name} ships no guard module")
        target, name = guards[0], crafts[0].name
        originals = {py: py.read_text() for py in guards}   # every module of this craft: its declaration may live in any of them
        bare = {py: "".join(l for l in t.splitlines(keepends=True) if not l.startswith("BUNDLED_WITH_CORE")) for py, t in originals.items()}

        def fresh():
            """`dyadlib.load_module` caches by name, as it should — two loaders of one file must
            share a module. A test that rewrites the file on disk is the one caller that needs the
            cache dropped, so it drops it here rather than weakening the loader."""
            for key in [k for k in sys.modules if k.startswith("dyad_crafts_")]:
                del sys.modules[key]
            return self.package.bundled_crafts()

        baseline = fresh()
        try:
            for py, text in bare.items():
                py.write_text(text)
            without = fresh()
            self.assertNotIn(name, without)                       # omitted: not discovered
            target.write_text(bare[target] + "\nBUNDLED_WITH_CORE = True\n")
            self.assertEqual(fresh(), sorted([*without, name]))   # declared: discovered, and no other craft moves
            target.write_text(bare[target] + "\nBUNDLED_WITH_CORE = False\n")
            self.assertEqual(fresh(), without)                    # declared False: not discovered
        finally:
            for py, text in originals.items():
                py.write_text(text)
            shutil.rmtree(target.parent / "__pycache__", ignore_errors=True)
            for key in [k for k in sys.modules if k.startswith("dyad_crafts_")]:
                del sys.modules[key]
        self.assertEqual(fresh(), baseline)   # restored: read from disk again, so this tree's own answer returns


class InvariantPassTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md p1, p4 (amended #203): the pass runs both lists before any check in `check` and
    `check --guards`, prints one line per model module in a fixed order, never runs under --list/--help; a false
    TREE_INVARIANTS entry is a red line, a false INVARIANTS entry fails its module's import (one red line, the other
    checks still run), and in the runner's own modules it stops every command with one line and no traceback."""
    def run_py(self, *a):
        return subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), *a], capture_output=True, text=True, env=env())
    def test_pass_order_and_lines(self):
        pkg = load_package()
        labels = [l for l, _, _ in pkg.invariant_modules()]
        guards = [f"{dyadlib.guard_key(py)[1]}/{py.stem}" for py in dyadlib.guard_files()]
        projectors = [f"project_{s.replace('/', '_')}" for s in sorted(pkg.PROJECTORS)]
        self.assertEqual(labels, ["dyadlib", "package"] + guards + projectors + ["runbook", "craft", "distribute"])
        self.assertEqual(len(set(labels)), len(labels))
        for label, mod, extra in pkg.invariant_modules():
            self.assertEqual([n for n, _ in extra], ["entity-non-empty", "corpus-matches-directory", "fields-unique-strings", "transaction-implies-check_transaction"] if "/" in label else [])
            dyadlib.check_invariants(mod, extra, label)
        for name, fn in (("check --guards", pkg.cmd_guards), ("check", pkg.cmd_check)):
            import contextlib, io
            buf = io.StringIO()
            with unittest.mock.patch.dict(os.environ, {"DYAD_NO_NESTED_TESTS": "1"}), contextlib.redirect_stdout(buf):
                fn()
            out = buf.getvalue()
            lines = [l for l in out.splitlines() if "[invariant]" in l]
            self.assertEqual(lines[: len(labels)], [f"ok   [invariant] {l} ({dyadlib.check_invariants(m, e)})" for l, m, e in pkg.invariant_modules()], name)
            self.assertTrue(out.splitlines()[0].startswith("ok   [invariant] dyadlib ("), name)   # before any check
        self.assertNotIn("invariants", pkg.CHECKS)   # the pass is not a check entry; it precedes them
    def test_list_and_help_do_not_run_the_pass(self):
        self.assertNotIn("[invariant]", self.run_py("check", "--list").stdout)
        r = self.run_py(); self.assertNotRegex(r.stdout + r.stderr, r"(?m)^(ok  |FAIL) \[invariant\]")   # usage text only
    def test_false_invariant_is_red_but_checks_still_run(self):
        d = scratch_install(with_craft=False)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = ('import dyadlib\nENTITY, CORPUS, TRANSACTION = "{e}", "agent", False\nFIELDS = ("a",)\n{lists}\ndyadlib.enforce(INVARIANTS, __name__)\n'
                'def check_package(root=None, pkg=None): return []\ndef describe(root, pkg): return {{"store": "", "parser": "", "fields": [("a", "text", "", True, "", "{e}.FIELDS")]}}\n')
        guards = {"zzz": 'INVARIANTS = [("holds", lambda: True)]\nTREE_INVARIANTS = [("never-holds", lambda: False)]',   # tree list: red in the pass
                  "zzy": 'INVARIANTS = [("never-holds", lambda: False), ("holds", lambda: True)]'}                       # pure list: the import fails
        for e, lists in guards.items():
            (d / "dyad" / "guards" / "agent" / f"{e}.py").write_text(body.format(e=e, lists=lists))
            (d / "dyad" / "tests" / "guards" / "agent" / f"test_{e}.py").write_text("import unittest\n")
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check"], capture_output=True, text=True, env=env())
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("FAIL [invariant] agent/zzz: never-holds", r.stdout); self.assertNotIn("ok   [invariant] agent/zzz", r.stdout)
        self.assertIn("FAIL [invariant] agent/zzy: does not load: dyad_guards_agent_zzy: invariant(s) failed: never-holds", r.stdout)   # one red line, named
        self.assertIn("ok   [Rule-11]", r.stdout); self.assertIn("ok   [agent/zzz]", r.stdout)   # the checks still run: evidence stays complete
        self.assertNotIn("Traceback", r.stdout + r.stderr)
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--guards"], capture_output=True, text=True, env=env())
        self.assertNotEqual(r.returncode, 0); self.assertIn("FAIL [invariant] agent/zzz: never-holds", r.stdout); self.assertIn("ok   [guards] agent/zzz", r.stdout)
        self.assertIn("FAIL [invariant] agent/zzy: does not load", r.stdout)
    def test_dwork_refuses_when_dyadlib_invariants_break(self):
        d = scratch_install(with_craft=False)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        lib = d / "dyad" / "scripts" / "dyadlib.py"
        lib.write_text(lib.read_text().replace('"archived": frozenset(),', '"archived": frozenset({"open"}),'))   # archived is no longer terminal
        for argv in (["dwork", "new", "t"], ["check", "--list"]):   # fail-closed: every command stops at the runner's own import (p4, #203)
            with self.subTest(argv=argv):
                r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), *argv], capture_output=True, text=True, env=env(), cwd=d)
                self.assertNotEqual(r.returncode, 0)
                self.assertEqual(r.stderr.strip().splitlines(), ["InvariantError: dyadlib: invariant(s) failed: archived-is-terminal"])   # one line, no traceback
        self.assertEqual(list((d / "agent-corpus" / "d-work" / "rows").glob("[0-9]*.md")), [])

class PrePushTests(unittest.TestCase):
    """d-work #194 (Rule-14 property 3): the pre-push hook judges the refs git pushes (its stdin), not
    `origin/main..HEAD` and whatever tree is on disk. Real `git push` to a bare remote, so the installed
    hook itself runs; one install shared by every case (each case leaves the checkout on `main`, clean)."""
    @classmethod
    def setUpClass(cls):
        cls.d = scratch_install(with_craft=False)
        cls.bare = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", "--bare", str(cls.bare)], check=True)
        for a in (("checkout", "-q", "-B", "main"), ("remote", "add", "origin", str(cls.bare)), ("config", "core.hooksPath", "dyad/hooks")):
            cls.git(*a)
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True); shutil.rmtree(cls.bare, ignore_errors=True)
    @classmethod
    def git(cls, *a):
        return subprocess.run(["git", "-C", str(cls.d), *a], check=True, capture_output=True, text=True, env=env()).stdout
    def push(self, *a):
        return subprocess.run(["git", "-C", str(self.d), "push", "origin", *a], capture_output=True, text=True, env=env())
    def commit_on(self, branch, name):
        """A new commit on `branch` (created from main, left checked out) touching one host-zone file."""
        self.git("checkout", "-q", "-B", branch, "main")
        f = self.d / "workstation-corpus" / f"{name}.md"; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(f"# {name}\n")
        self.git("add", "-A"); self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", f"{name}")
    def ensure_main_pushed(self):
        if subprocess.run(["git", "-C", str(self.d), "rev-parse", "-q", "--verify", "origin/main"], capture_output=True).returncode:
            r = self.push("main"); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
    def tearDown(self):
        subprocess.run(["git", "-C", str(self.d), "checkout", "-q", "main"], capture_output=True)
        subprocess.run(["git", "-C", str(self.d), "clean", "-qfd"], capture_output=True)
    def test_a_clean_head_push_passes(self):
        r = self.push("main")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("[pre-push]", r.stdout + r.stderr)          # judged, not waved through
        self.assertIn("ok   [guards] infra/containment", r.stdout + r.stderr)
    def test_b_another_branch_than_head_is_refused(self):
        self.ensure_main_pushed()
        self.commit_on("other", "other"); self.git("checkout", "-q", "main")
        r = self.push("other")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("FAIL [pre-push] refs/heads/other", r.stdout + r.stderr)
        self.assertIn("git switch other && git push", r.stdout + r.stderr)
        self.assertNotIn("[guards]", r.stdout + r.stderr)             # refused before any guard runs
    def test_c_a_dirty_tree_is_refused(self):
        self.ensure_main_pushed()
        self.commit_on("dirty", "dirty")
        (self.d / "stray.txt").write_text("x\n")
        r = self.push("dirty")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("FAIL [pre-push] the working tree has changes the push does not carry (stray.txt)", r.stdout + r.stderr)
        (self.d / "stray.txt").unlink()
        (self.d / "scratch.pyc").write_text("x\n")                     # ignored (.gitignore `*.pyc`): not a change
        r = self.push("dirty")
        self.assertNotIn("FAIL [pre-push]", r.stdout + r.stderr)      # judged now: the guards run over the pushed commit,
        self.assertIn("FAIL [guards] agent/prs", r.stdout + r.stderr)  # whose uncited message the plan gate refuses
        (self.d / "scratch.pyc").unlink()
    def test_d_a_deletion_passes(self):
        self.ensure_main_pushed()
        r = self.push("main:refs/heads/side")                           # a ref on a commit origin/main holds
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ok   [pre-push] nothing new to judge", r.stdout + r.stderr)
        r = self.push("--delete", "side")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ok   [pre-push] nothing new to judge", r.stdout + r.stderr)
    def test_e_a_tag_on_main_passes_while_head_is_elsewhere(self):
        self.ensure_main_pushed()
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "tag", "-a", "-m", "t", "rel-v0.0.1", "main")   # annotated: its sha is the tag object
        self.commit_on("elsewhere", "elsewhere")
        (self.d / "stray.txt").write_text("x\n")                        # nothing new leaves, so the tree is not judged
        r = self.push("rel-v0.0.1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ok   [pre-push] nothing new to judge", r.stdout + r.stderr)
    def test_pushed_refs_skips_lines_it_cannot_read(self):
        pkg = load_package()
        z = "0" * 40
        self.assertEqual(pkg.pushed_refs(["", "garbage", f"(delete) {z} refs/heads/x {'1' * 40}"]), (None, []))

class SuiteEnvTests(unittest.TestCase):
    """#152: a test child never inherits a hook's GIT_VARS (an absolute GIT_DIR from a linked worktree)."""
    def test_git_vars_dropped_and_nesting_marked(self):
        pkg = load_package()
        with unittest.mock.patch.dict(os.environ, {"GIT_DIR": "/elsewhere/.git", "GIT_WORK_TREE": "/elsewhere",
                                                   "GIT_INDEX_FILE": "/elsewhere/.git/index",
                                                   "GIT_COMMON_DIR": "/elsewhere/.git"}):   # #169: a linked worktree's hook exports it
            env = pkg.suite_env()
        self.assertFalse(set(dyadlib.GIT_VARS) & set(env), env.keys() & set(dyadlib.GIT_VARS))
        self.assertNotIn("GIT_COMMON_DIR", env)
        self.assertEqual(env["DYAD_NO_NESTED_TESTS"], "1")
    def test_fixture_commits_unsigned_and_caller_config_kept(self):
        """#206: a test child's scratch-repo commits are never signed, whatever the host's global config;
        a `GIT_CONFIG_*` entry the caller set survives, the signing entry appended after it."""
        pkg = load_package()
        with unittest.mock.patch.dict(os.environ, {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.autocrlf",
                                                   "GIT_CONFIG_VALUE_0": "false"}):
            env = pkg.suite_env()
        self.assertEqual((env["GIT_CONFIG_COUNT"], env["GIT_CONFIG_KEY_0"], env["GIT_CONFIG_KEY_1"], env["GIT_CONFIG_VALUE_1"]),
                         ("2", "core.autocrlf", "commit.gpgsign", "false"))
        with tempfile.TemporaryDirectory() as d:
            git = lambda *a: subprocess.run(["git", *a], cwd=d, env=env, check=True, capture_output=True, text=True).stdout
            git("init", "-q"); git("config", "commit.gpgsign", "true")   # the local config asks; the env entry wins
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "c")
            self.assertNotIn("gpgsig", git("cat-file", "-p", "HEAD"))

class SuiteEnvWorktreeTests(unittest.TestCase):
    """#165 end to end (d-work #199 N0): a pre-push hook in a linked worktree exports
    `GIT_DIR=<common>/worktrees/<wt>` and `GIT_PREFIX` (observed, git 2.43.0). A test child that
    inits and configures its own scratch repo under `suite_env()` leaves the shared repository
    untouched; under the raw hook env the same child writes `core.bare`, `user.*` and a branch
    into it — the #152 damage, reproduced here as the control."""
    CHILD = ("import subprocess as s\n"
             "for a in (['init', '-q', '.'], ['config', 'user.name', 'x'], ['config', 'user.email', 'x@x'],\n"
             "          ['commit', '-q', '--allow-empty', '-m', 'c'], ['branch', 'feature']):\n"
             "    s.run(['git', *a], check=True, capture_output=True)\n")
    def fixture(self):
        """A shared scratch repo with one commit and a linked worktree `wt`, built without any GIT_VARS;
        returns (shared, hook vars as the worktree's pre-push hook receives them, a snapshot function)."""
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        root, clean = Path(td.name), dyadlib.git_env()
        git = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True, text=True, env=clean).stdout
        shared = root / "shared"; git("init", "-q", str(shared))
        git("-C", str(shared), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base")
        git("-C", str(shared), "worktree", "add", "-q", str(root / "wt"), "-b", "wt")
        hook = {"GIT_DIR": str(shared / ".git" / "worktrees" / "wt"), "GIT_PREFIX": ""}
        snap = lambda: (git("-C", str(shared), "config", "--local", "--list"), git("-C", str(shared), "for-each-ref"))
        other = root / "other"; other.mkdir()
        return shared, hook, snap, other
    def test_child_under_suite_env_leaves_shared_repo_untouched(self):
        pkg = load_package()
        shared, hook, snap, other = self.fixture()
        before = snap()
        self.assertIn("core.bare=false", before[0])
        with unittest.mock.patch.dict(os.environ, hook):
            env = pkg.suite_env()
        r = subprocess.run([sys.executable, "-c", self.CHILD], cwd=other, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(snap(), before)   # core.bare, user.*, every ref: unchanged
        self.assertTrue((other / ".git").is_dir())   # the child wrote its own repo instead
    def test_control_child_under_raw_hook_env_writes_into_shared_repo(self):
        shared, hook, snap, other = self.fixture()
        before = snap()
        r = subprocess.run([sys.executable, "-c", self.CHILD], cwd=other, env={**dyadlib.git_env(), **hook},
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        config, refs = snap()
        self.assertNotEqual((config, refs), before)
        self.assertIn("core.bare=true", config); self.assertIn("user.name=x", config)
        self.assertIn("refs/heads/feature", refs)

class SpawnSiteTests(unittest.TestCase):
    """#165 fence (d-work #199 N0): every process `package.py` spawns is classified. A python child (a test
    root, a target) runs with `env=suite_env()`; every other site is a git call the runner makes for itself,
    listed here with why it may inherit `os.environ` — so a new spawn site fails until it is judged."""
    SPAWN = {"run", "Popen", "check_output", "check_call", "call", "system", "popen", "execv", "execve", "execvp",
             "execvpe", "execl", "execle", "execlp", "execlpe", "spawnv", "spawnve", "spawnl", "spawnle", "posix_spawn"}
    GIT_ALLOWED = {   # enclosing function -> why its git call(s) run with the parent's environment
        "<module>": "REPO discovery; strips the hook's GIT_DIR itself (#142) so --show-toplevel finds the true root",
        "core_extra": "ls-files of the repo the runner judges; a hook's GIT_DIR names that same repo",
        "tracked_files": "ls-files of the repo the runner judges; a hook's GIT_DIR names that same repo",
        "pushed_refs": "reads the refs the hook is pushing, in the repo the hook runs for (#194)",
        "cmd_guards": "rev-parse of base and HEAD in the repo being pushed; no write",
        "cmd_pr": "rev-parse of the PR's refs in the repo judged; no write",
        "cmd_evidence": "head sha, tree hash and status of the head being evidenced; no write",
        "cmd_dwork": "fetches origin/main into the operator's own repo before allocating an id (Rule-16)",
        "_git": "the suite memo's reads (status, trees, tags, common dir, merge-base) of the repo judged, "
                "under dyadlib.git_env() so a hook's GIT_VARS never redirect them; no write (#162)",
    }
    def sites(self):
        import ast
        tree = ast.parse((PKG / "scripts" / "package.py").read_text())
        out = []
        def walk(node, fn):
            for c in ast.iter_child_nodes(node):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name) \
                        and c.func.value.id in ("subprocess", "os") and c.func.attr in self.SPAWN:
                    out.append((c.lineno, fn, c))
                walk(c, c.name if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn)
        walk(tree, "<module>")
        return out
    def test_python_children_use_suite_env_and_git_sites_are_listed(self):
        import ast
        python, git_fns, problems = [], set(), []
        for line, fn, call in self.sites():
            argv = call.args[0] if call.args else None
            head = ast.unparse(argv.elts[0]) if isinstance(argv, ast.List) and argv.elts else None
            env = next((k.value for k in call.keywords if k.arg == "env"), None)
            if head == "sys.executable" or (head or "").strip("'\"").startswith("python"):
                python.append(line)
                if not (isinstance(env, ast.Call) and ast.unparse(env.func).endswith("suite_env")):
                    problems.append(f"l.{line} {fn}: python child without env=suite_env()")
            elif head == "'git'":
                git_fns.add(fn)
                if fn not in self.GIT_ALLOWED:
                    problems.append(f"l.{line} {fn}: git call not listed in GIT_ALLOWED")
            else:
                problems.append(f"l.{line} {fn}: unclassified spawn {ast.unparse(call)[:80]}")
        self.assertEqual(problems, [])
        self.assertGreaterEqual(len(python), 2, "check_rule_12 and run_suite spawn the suite")
        self.assertEqual(set(self.GIT_ALLOWED) - git_fns, set(), "stale GIT_ALLOWED entry")

class SuiteMemoTests(unittest.TestCase):
    """#162 (d-work #199 N2): the suite memo. Written after a full, all-roots pass on a clean tree, under the
    git common dir; read by `suite_gate` only under `pre_push`; never by `check --evidence` nor by
    `check --guards` without `--pre-push`. Every case runs over a scratch repo with `pkg.REPO` pointed at it
    and `test_suites` pinned to one root inside it, so the key's `roots` part is the scratch repo's."""
    PARTS = {"tree", "executable", "python", "git", "roots", "env", "tags", "local", "date"}

    def setUp(self):
        self.pkg = load_package()
        self.old = self.pkg.REPO
        self.addCleanup(setattr, self.pkg, "REPO", self.old)
        p = unittest.mock.patch.object(self.pkg, "test_suites", lambda: [self.pkg.REPO / "dyad" / "tests"])
        p.start(); self.addCleanup(p.stop)
        e = unittest.mock.patch.dict(os.environ, {}, clear=False); e.start(); self.addCleanup(e.stop)
        os.environ.pop("DYAD_NO_NESTED_TESTS", None)
        self.pkg._SUITE_RAN = False

    def repo(self):
        """`seed` (one file), `ledger` (a row), `code` (a non-ledger file) on `main`; REPO points at it.
        Returns (repo, seed sha, git)."""
        d, seed, git = PackageTests.gate_repo(self)
        (d / "code.txt").write_text("code\n"); (d / ".gitignore").write_text("*.local.txt\n")   # as the real repo ignores its legacy list
        git("add", "-A"); git("commit", "-qm", "code")
        self.pkg.REPO = d
        return d, seed, git

    def memos(self, d):
        m = Path(d) / ".git" / self.pkg.SUITE_MEMO_DIR
        return sorted(f.name for f in m.iterdir() if self.pkg.SUITE_MEMO_NAME.fullmatch(f.name)) if m.is_dir() else []

    def guards(self, base, pre_push, evidence=False):
        """`cmd_guards` (or `cmd_evidence`) with the registry emptied, `cmd_tests` recorded and every memo
        read recorded; under `pre_push`, stdin carries the hook's line for HEAD. Returns (suite calls, memo
        reads, output)."""
        pkg, calls, reads, buf = self.pkg, [], [], io.StringIO()
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=pkg.REPO, capture_output=True, text=True, env=dyadlib.git_env()).stdout.strip()
        real_hit = pkg.suite_memo_hit
        def rule_12():
            pkg._SUITE_RAN = True; calls.append(("check",)); return []
        with unittest.mock.patch.object(pkg, "registry", lambda: []), \
             unittest.mock.patch.object(pkg, "cmd_invariants", lambda: 0), \
             unittest.mock.patch.object(pkg, "cmd_tests", lambda *a, **k: calls.append(("tests",) + a) or 0), \
             unittest.mock.patch.object(pkg, "CHECKS", {"Rule-12": rule_12}), \
             unittest.mock.patch.object(pkg, "suite_memo_hit", lambda parts: reads.append(parts) or real_hit(parts)), \
             unittest.mock.patch.object(sys, "stdin", io.StringIO(f"refs/heads/main {head} refs/heads/main {'0' * 40}\n")), \
             contextlib.redirect_stdout(buf):
            pkg._SUITE_RAN = False
            if evidence:
                pkg.cmd_evidence()
            else:
                pkg.cmd_guards(base=base, pre_push=pre_push)
        return calls, reads, buf.getvalue()

    def test_key_changes_with_every_part(self):
        d, seed, git = self.repo()
        parts = self.pkg.suite_memo_parts()
        self.assertEqual(set(parts), self.PARTS)
        self.assertEqual(set(parts["env"]), set(self.pkg.SUITE_MEMO_ENV))
        self.assertEqual(parts["roots"], ["dyad/tests"])
        key = self.pkg.suite_memo_key(parts)
        self.assertEqual(key, self.pkg.suite_memo_key(dict(reversed(list(parts.items())))))   # canonical: order never matters
        for k in sorted(self.PARTS - {"env"}):
            changed = {**parts, k: ["x"] if k == "roots" else parts[k] + "x"}
            self.assertNotEqual(self.pkg.suite_memo_key(changed), key, k)
        for k in self.pkg.SUITE_MEMO_ENV:
            changed = {**parts, "env": {**parts["env"], k: (parts["env"][k] or "") + "x"}}
            self.assertNotEqual(self.pkg.suite_memo_key(changed), key, k)
        self.assertNotEqual(self.pkg.suite_memo_key({**parts, "roots": parts["roots"] + ["crafts/x/tests"]}), key)

    def test_hit_under_pre_push_skips(self):
        d, seed, git = self.repo()
        memo = self.pkg.suite_memo_write(self.pkg.suite_memo_parts())
        self.assertIsNotNone(memo)
        tree = git("rev-parse", "HEAD^{tree}")
        calls, reads, out = self.guards(seed, pre_push=True)
        self.assertIn(f"skip [guards] Rule-12 suite: tree {tree[:9]} already passed on this checkout (d-work #162)", out)
        self.assertEqual(calls, [], out)
        calls, reads, out = self.guards(seed, pre_push=True)   # a second push of the same tree: still a hit
        self.assertEqual(calls, [], out)
        (Path(memo)).unlink()                                  # cold: the suite runs for real
        calls, reads, out = self.guards(seed, pre_push=True)
        self.assertNotIn("skip [guards] Rule-12 suite", out)
        self.assertEqual(calls, [("tests",)], out)

    def test_planted_memo_is_ignored_by_evidence_and_by_guards_without_pre_push(self):
        d, seed, git = self.repo()
        self.assertIsNotNone(self.pkg.suite_memo_write(self.pkg.suite_memo_parts()))
        calls, reads, out = self.guards(seed, pre_push=False)
        self.assertEqual(calls, [("tests",)], out)            # check --guards: cmd_tests is called
        self.assertEqual(reads, [], "check --guards without --pre-push read the memo")
        self.assertNotIn("skip [guards] Rule-12 suite", out)
        calls, reads, out = self.guards(seed, pre_push=False, evidence=True)
        self.assertEqual(calls, [("check",)], out)            # evidence: the suite ran, through cmd_check
        self.assertEqual(reads, [], "check --evidence read the memo")
        self.assertNotIn("skip [guards] Rule-12 suite", out)
        self.assertNotIn("already passed", out)

    def test_any_key_part_changed_is_a_miss(self):
        d, seed, git = self.repo()
        gate = lambda: self.pkg.suite_gate(seed, "HEAD", pre_push=True)
        write = lambda: self.pkg.suite_memo_write(self.pkg.suite_memo_parts())
        write(); self.assertFalse(gate()[0])                                        # the control: a hit
        git("tag", "v9.9.9"); self.assertEqual(gate(), (True, None))                # tags (check_drift reads them)
        write(); self.assertFalse(gate()[0])
        os.environ["DYAD_HOST_ZONE"] = "infra"; self.assertEqual(gate(), (True, None))   # an env knob
        write(); self.assertFalse(gate()[0])
        with unittest.mock.patch.object(self.pkg, "utc_date", lambda: "2999-01-01"):
            self.assertEqual(gate(), (True, None))                                  # the UTC day
        with unittest.mock.patch.object(self.pkg, "test_suites", lambda: [d / "dyad" / "tests", d / "crafts" / "x" / "tests"]):
            self.assertEqual(gate(), (True, None))                                  # the roots
        with unittest.mock.patch.object(sys, "executable", sys.executable + "x"):
            self.assertEqual(gate(), (True, None))                                  # the interpreter
        with unittest.mock.patch.object(sys, "version", sys.version + "x"):
            self.assertEqual(gate(), (True, None))
        real = self.pkg._git
        with unittest.mock.patch.object(self.pkg, "_git", lambda *a: "git version 0.0.0" if a == ("--version",) else real(*a)):
            self.assertEqual(gate(), (True, None))                                  # git
        inst = os.environ.get("DYAD_INSTANCE", "agent-corpus")
        (d / inst / "provenance_legacy.local.txt").write_text("1 0 predates\n")
        self.assertEqual(self.pkg.suite_memo_parts()["tree"], git("rev-parse", "HEAD^{tree}"))   # ignored: still clean
        self.assertEqual(gate(), (True, None))                                      # instance-local data git ignores
        write(); self.assertFalse(gate()[0])
        (d / "code.txt").write_text("changed\n"); git("commit", "-qam", "tree")
        self.assertEqual(gate(), (True, None))                                      # the tree

    def test_dirty_tree_partial_run_or_failure_never_writes(self):
        d, seed, git = self.repo()
        ok = lambda *a, **k: (0, ["Ran 1 test", "OK"], "")
        with unittest.mock.patch.object(self.pkg, "run_suite", ok), contextlib.redirect_stdout(io.StringIO()):
            (d / "stray.txt").write_text("untracked\n")                  # dirty: an untracked file counts
            self.assertIsNone(self.pkg.suite_memo_parts())
            self.assertEqual(self.pkg.cmd_tests(), 0)
            self.assertEqual(self.memos(d), [])
            (d / "stray.txt").unlink()
            self.assertEqual(self.pkg.cmd_tests("dyad.tests.test_x"), 0)  # a targeted run
            self.assertEqual(self.pkg.cmd_tests(str(d / "dyad" / "tests")), 0)   # one root by path
            self.assertEqual(self.memos(d), [])
            with unittest.mock.patch.object(self.pkg, "run_suite", lambda *a, **k: (1, ["FAILED"], "boom")), \
                 contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(self.pkg.cmd_tests(), 1)                # a failure
            self.assertEqual(self.memos(d), [])
            self.assertEqual(self.pkg.cmd_tests(), 0)                    # the control: clean, full, passing
        self.assertEqual(self.memos(d), [self.pkg.suite_memo_key(self.pkg.suite_memo_parts())])

    def test_check_rule_12_writes_only_on_a_clean_full_pass(self):
        """`check_rule_12` (hence `check` and `--evidence`) spawns the real child over a one-test root."""
        d, seed, git = self.repo()
        t = d / "dyad" / "tests"; t.mkdir(parents=True)
        (t / "test_one.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test_ok(self): pass\n")
        (d / ".gitignore").write_text("*.local.txt\n__pycache__/\n")   # the child's bytecode, ignored as the real repo ignores it
        git("add", "-A"); git("commit", "-qm", "tests")
        with contextlib.redirect_stdout(io.StringIO()):
            (d / "stray.txt").write_text("x\n")
            self.assertEqual(self.pkg.check_rule_12(), []); self.assertEqual(self.memos(d), [])
            (d / "stray.txt").unlink(); self.pkg._SUITE_RAN = False
            self.assertEqual(self.pkg.check_rule_12(), [])
            self.assertEqual(self.memos(d), [self.pkg.suite_memo_key(self.pkg.suite_memo_parts())])
            (t / "test_one.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test_no(self): self.fail()\n")
            git("commit", "-qam", "red"); self.pkg._SUITE_RAN = False
            self.assertNotEqual(self.pkg.check_rule_12(), [])
        self.assertFalse(self.pkg.suite_memo_hit(self.pkg.suite_memo_parts()))

    def test_write_from_a_linked_worktree_lands_in_the_common_dir(self):
        shared, hook, snap, other = SuiteEnvWorktreeTests.fixture(self)
        wt = shared.parent / "wt"
        self.pkg.REPO = wt
        with unittest.mock.patch.dict(os.environ, hook):                 # as the worktree's pre-push hook runs it
            memo = self.pkg.suite_memo_write(self.pkg.suite_memo_parts())
        self.assertEqual(Path(memo).parent, (shared / ".git" / self.pkg.SUITE_MEMO_DIR).resolve())
        self.assertFalse((shared / ".git" / "worktrees" / "wt" / self.pkg.SUITE_MEMO_DIR).exists())
        self.pkg.REPO = shared                                          # the main worktree, same tree: shared
        self.assertTrue(self.pkg.suite_memo_hit(self.pkg.suite_memo_parts()))

    def test_prune_keeps_the_newest_64(self):
        d, seed, git = self.repo()
        m = d / ".git" / self.pkg.SUITE_MEMO_DIR; m.mkdir()
        old = [f"{i:064x}" for i in range(70)]
        for i, name in enumerate(old):
            (m / name).write_text("{}\n"); os.utime(m / name, ns=(10**18 + i, 10**18 + i))
        (m / "README").write_text("not a memo\n")
        new = Path(self.pkg.suite_memo_write(self.pkg.suite_memo_parts())).name
        self.assertEqual(self.pkg.SUITE_MEMO_KEEP, 64)
        kept = self.memos(d)
        self.assertEqual(len(kept), 64)
        self.assertIn(new, kept)
        self.assertEqual(set(old) - set(kept), set(old[:7]))           # 71 written, the 7 oldest pruned
        self.assertTrue((m / "README").exists())
        self.assertEqual([f for f in os.listdir(m) if f.endswith(".tmp")], [])   # os.replace left no temp file

    def test_ledger_branch_behind_main_skips_only_on_a_memoized_merge_base(self):
        d, seed, git = self.repo()
        inst = os.environ.get("DYAD_INSTANCE", "agent-corpus")
        fork = git("rev-parse", "HEAD")
        git("switch", "-qc", "ledger")
        (d / inst / "d-work" / "rows" / "2.md").write_text("id: 2\n"); git("add", "-A"); git("commit", "-qm", "row 2")
        git("switch", "-q", "main")
        (d / "code.txt").write_text("main moved\n"); git("commit", "-qam", "main moves")
        git("switch", "-q", "ledger")
        gate = lambda: self.pkg.suite_gate("main", "HEAD", pre_push=True)
        self.assertEqual(gate(), (True, None))                          # two-dot main..HEAD carries main's code
        self.assertEqual(self.pkg.suite_gate("main", "HEAD", pre_push=False), (True, None))
        self.pkg.suite_memo_write(self.pkg.suite_memo_parts(fork))      # the merge-base's tree passed
        tree = git("rev-parse", f"{fork}^{{tree}}")
        self.assertEqual(gate(), (False, f"skip [guards] Rule-12 suite: main...HEAD is ledger-only and its merge-base tree "
                                         f"{tree[:9]} already passed on this checkout (d-work #162)"))
        self.assertEqual(self.pkg.suite_gate("main", "HEAD", pre_push=False), (True, None))   # never without --pre-push
        (d / "code.txt").write_text("branch code\n"); git("commit", "-qam", "not ledger")
        self.assertEqual(gate(), (True, None))                          # one non-ledger commit: the clause is off

class InstalledRootTests(unittest.TestCase):
    """#176 (d-work #199 N5): `dyad install` records the core's tree in the craft registry, and the pre-push
    path skips a test root whose craft tree is byte-identical to its row — never `check --evidence`, never
    `check --guards` without `--pre-push`, never a modified tree, a missing row, or a range that changes the
    registry; a partial run writes no suite memo. Every case runs over a scratch install with `pkg.REPO`
    pointed at it and `test_suites` pinned to its own roots."""

    def setUp(self):
        self.pkg = load_package()
        self.craft = self.pkg.craft_cli()
        self.addCleanup(setattr, self.pkg, "REPO", self.pkg.REPO)
        e = unittest.mock.patch.dict(os.environ, {}, clear=False); e.start(); self.addCleanup(e.stop)
        os.environ.pop("DYAD_NO_NESTED_TESTS", None)
        self.pkg._SUITE_RAN = False

    def repo(self, craft_row=False):
        """A scratch install (core row written by the install), optionally a row for its bundled craft, then
        one pushed commit outside every craft. Returns (repo, base sha, git)."""
        d = scratch_install(with_craft=False)
        git = lambda *a: subprocess.run(["git", "-C", str(d), *livetest.IDENTITY, *a], check=True, capture_output=True,
                                        text=True, env=dyadlib.git_env()).stdout.strip()
        self.bundled = sorted(c.name for c in dyadlib.craft_dirs(d / "dyad"))
        if craft_row:
            rows = self.craft.registry_rows(d)
            for c in self.bundled:
                rows[c] = {"craft": c, "version": "0.0.0", "source": "t", "sha256": self.craft.tree_sha(d, c), "d-work": ""}
            self.craft.write_registry(d, rows); git("add", "-A"); git("commit", "-qm", "rows")
        base = git("rev-parse", "HEAD")
        (d / "notes.txt").write_text("not a craft\n"); git("add", "-A"); git("commit", "-qm", "notes")
        self.pkg.REPO = d
        p = unittest.mock.patch.object(self.pkg, "test_suites", lambda: [d / "dyad" / "tests"] + sorted((d / "crafts").glob("*/tests")))
        p.start(); self.addCleanup(p.stop)
        return d, base, git

    def gate(self, base, pre_push=True, evidence=False):
        """`cmd_guards` (or `cmd_evidence`) with the registry emptied and `cmd_tests` recorded as its `roots`
        (repo-relative, or None for every root). Returns (calls, output)."""
        pkg, calls, buf = self.pkg, [], io.StringIO()
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=pkg.REPO, capture_output=True, text=True, env=dyadlib.git_env()).stdout.strip()
        rel = lambda roots: None if roots is None else [Path(os.path.relpath(r, pkg.REPO)).as_posix() for r in roots]
        def rule_12():
            pkg._SUITE_RAN = True; calls.append("check"); return []
        with unittest.mock.patch.object(pkg, "registry", lambda: []), \
             unittest.mock.patch.object(pkg, "cmd_invariants", lambda: 0), \
             unittest.mock.patch.object(pkg, "cmd_tests", lambda target=None, roots=None: calls.append(rel(roots)) or 0), \
             unittest.mock.patch.object(pkg, "CHECKS", {"Rule-12": rule_12}), \
             unittest.mock.patch.object(sys, "stdin", io.StringIO(f"refs/heads/main {head} refs/heads/main {'0' * 40}\n")), \
             contextlib.redirect_stdout(buf):
            pkg._SUITE_RAN = False
            pkg.cmd_evidence() if evidence else pkg.cmd_guards(base=base, pre_push=pre_push)
        return calls, buf.getvalue()

    def skip_line(self, rel, name):
        row = self.craft.registry_rows(self.pkg.REPO)[name]
        return f"skip [guards] Rule-12 suite: {rel} — {name} {row['version']} installed unmodified (crafts/REGISTRY.md)"

    def test_install_writes_the_core_row_idempotently(self):
        d, base, git = self.repo()
        row = self.craft.registry_rows(d)[self.craft.CORE_NAME]
        self.assertEqual((row["version"], row["sha256"]), (self.pkg.version(), self.craft.tree_sha(d, self.craft.CORE_NAME)))
        self.assertEqual(row["sha256"], self.pkg.distribute.archive_sha256(d, ["dyad"], tracked=False))   # the computation craft install uses
        reg = (d / "crafts" / "REGISTRY.md").read_bytes()
        r = PackageTests.run_py(self, "install", str(d))
        self.assertIn(f"installed into {Path(d).resolve()}: 0 changes", r.stdout, r.stdout + r.stderr)
        self.assertEqual((d / "crafts" / "REGISTRY.md").read_bytes(), reg)                                 # the same row, untouched
        (d / "crafts" / "REGISTRY.md").unlink()
        r = PackageTests.run_py(self, "install", str(d))
        self.assertIn(f"installed into {Path(d).resolve()}: 1 changes", r.stdout, r.stdout + r.stderr)    # the row alone
        self.assertEqual((d / "crafts" / "REGISTRY.md").read_bytes(), reg)

    def test_unmodified_installed_root_skips_under_pre_push_only(self):
        d, base, git = self.repo()
        calls, out = self.gate(base)
        self.assertIn(self.skip_line("dyad/tests", self.craft.CORE_NAME), out)
        self.assertEqual(calls, [[f"crafts/{c}/tests" for c in self.bundled if (d / "crafts" / c / "tests").is_dir()]], out)   # a bundled craft has no row (#201): it runs
        calls, out = self.gate(base, pre_push=False)                         # check --guards without --pre-push
        self.assertEqual(calls, [None], out); self.assertNotIn("installed unmodified", out)
        calls, out = self.gate(base, evidence=True)                          # check --evidence runs every root
        self.assertEqual(calls, ["check"], out); self.assertNotIn("installed unmodified", out)

    def test_a_craft_root_skips_with_its_own_row_and_an_unmodified_core(self):
        d, base, git = self.repo(craft_row=True)
        calls, out = self.gate(base)
        self.assertEqual(calls, [], out)                                     # every root skipped: no child at all
        for c in self.bundled:
            if (d / "crafts" / c / "tests").is_dir():
                self.assertIn(self.skip_line(f"crafts/{c}/tests", c), out)
        with (d / "dyad" / "VERSION").open("a") as f:                        # the core modified: a craft's tests import it
            f.write("\n")
        git("commit", "-qam", "core edit")
        calls, out = self.gate(base)
        self.assertEqual(calls, [None], out); self.assertNotIn("installed unmodified", out)

    def test_a_modified_file_runs_the_root(self):
        d, base, git = self.repo()
        (d / "dyad" / "tests" / "test_local_addition.py").write_text("import unittest\n")
        git("add", "-A"); git("commit", "-qm", "a local test")
        calls, out = self.gate(base)
        self.assertEqual(calls, [None], out); self.assertNotIn("installed unmodified", out)

    def test_no_row_runs_the_root(self):
        d, base, git = self.repo()
        git("rm", "-q", "crafts/REGISTRY.md"); git("commit", "-qm", "no registry")
        calls, out = self.gate(git("rev-parse", "HEAD~1"))                   # the range: the registry's removal
        self.assertEqual(calls, [None], out)
        calls, out = self.gate(git("rev-parse", "HEAD"))                     # nothing pushed: empty, skipped by #164
        self.assertEqual(calls, [], out)
        (d / "more.txt").write_text("x\n"); git("add", "-A"); git("commit", "-qm", "more")
        calls, out = self.gate(git("rev-parse", "HEAD~1"))                   # no row, registry untouched by the range
        self.assertEqual(calls, [None], out); self.assertNotIn("installed unmodified", out)

    def test_a_range_that_changes_the_registry_runs_every_root(self):
        """A hand-edited row is judged once, in this system, before the gate trusts it."""
        d, base, git = self.repo()
        rows =self.craft.registry_rows(d); rows[self.craft.CORE_NAME]["d-work"] = "#1"
        self.craft.write_registry(d, rows); git("commit", "-qam", "hand edit")
        calls, out = self.gate(base)
        self.assertEqual(calls, [None], out); self.assertNotIn("installed unmodified", out)

    def test_a_partial_pre_push_run_writes_no_memo(self):
        d, base, git = self.repo()
        memo = lambda: sorted(p.name for p in (d / ".git" / self.pkg.SUITE_MEMO_DIR).glob("*")) if (d / ".git" / self.pkg.SUITE_MEMO_DIR).is_dir() else []
        ran = []
        ok = lambda suite, target=None: ran.append(Path(os.path.relpath(suite, d)).as_posix()) or (0, ["Ran 1 test", "OK"], "")
        head = git("rev-parse", "HEAD")
        with unittest.mock.patch.object(self.pkg, "registry", lambda: []), \
             unittest.mock.patch.object(self.pkg, "cmd_invariants", lambda: 0), \
             unittest.mock.patch.object(self.pkg, "run_suite", ok), \
             unittest.mock.patch.object(sys, "stdin", io.StringIO(f"refs/heads/main {head} refs/heads/main {'0' * 40}\n")), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.pkg.cmd_guards(base=base, pre_push=True), 0)
            self.assertNotIn("dyad/tests", ran); self.assertEqual(memo(), [])          # partial: the core root skipped, nothing memoized
            self.pkg._SUITE_RAN = False; ran.clear()
            self.assertEqual(self.pkg.cmd_tests(), 0)                                  # the control: a full run writes one
        self.assertIn("dyad/tests", ran)
        self.assertEqual(memo(), [self.pkg.suite_memo_key(self.pkg.suite_memo_parts())])

if __name__ == "__main__":
    unittest.main()
