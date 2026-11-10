import contextlib, importlib.util, inspect, io, os, shutil, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); import dyadlib, livetest
CORE = ["agent/board", "agent/decision_log", "agent/dmc", "agent/frame", "agent/inbox", "agent/merges", "agent/plans", "agent/provenance", "agent/prs", "agent/records", "agent/references", "agent/rows", "agent/rules", "agent/sessions", "agent/traces", "agent/vocabulary",
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

def hermetic_clone() -> Path:
    """A local clone of this repo's HEAD whose tags the test controls (#529): the core release tag its `BUNDLE.md`
    row names is created when missing, so `check --evidence` never depends on whether the live repo's tag has been
    cut or fetched yet (`main` read red from a release cut until its tag, #526). #505's refusal of a clone that
    lacks the tag stays covered by test_bootstrap's own worlds."""
    d = SCRATCH.mkdtemp() / "clone"
    subprocess.run(["git", "clone", "-q", "--local", str(PKG.parent), str(d)], check=True, capture_output=True, env=dyadlib.git_env())
    bs = dyadlib.load_module(PKG / "scripts" / "bootstrap.py", "bootstrap")
    v = bs.expected_core_release(d)
    if v and not bs.has_tag(d, bs.core_tag(v)):
        subprocess.run(["git", "tag", bs.core_tag(v), "HEAD"], cwd=d, check=True, capture_output=True, env=dyadlib.git_env())
    return d

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

_EVIDENCE = None
def evidence_in_a_hermetic_clone():
    """One `check --evidence` in a hermetic clone of HEAD per test process, read by the tests that only read its
    output (d-work #563 C3): (clone, completed run). Its `check` lines are the ones `check` prints, since
    `cmd_evidence` runs `cmd_check` then `cmd_guards`."""
    global _EVIDENCE
    if _EVIDENCE is None:
        clone = hermetic_clone()                      # #529: tags under the test's control, not the live repo's
        _EVIDENCE = clone, subprocess.run([sys.executable, str(clone / "dyad" / "scripts" / "package.py"), "check", "--evidence"],
                                          cwd=clone, capture_output=True, text=True, env={**env(), **dyadlib.git_env()})
    return _EVIDENCE

class PackageTests(livetest.LiveCase):
    def run_py(self, *a):
        return subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), *a], capture_output=True, text=True)
    def test_check_runs_and_reports_rules_and_guards(self):
        _, r = evidence_in_a_hermetic_clone()          # the check lines of the shared run (#563 C3)
        self.assertIn("[Rule-11]", r.stdout); self.assertIn("[Rule-12]", r.stdout)
        pkg = load_package()
        self.assertEqual(list(pkg.CHECKS)[:2], ["Rule-11", "Rule-12"])
        # crafts/sysarch/rules/guards.md p4: CHECKS is derived from the registry (dyad/guards/<corpus>/<entity>.py, then crafts/<craft>/guards/<entity>.py; #155), never hand-listed
        expected = [f"{dyadlib.guard_key(py)[1]}/{py.stem}" for py in dyadlib.guard_files()]
        self.assertEqual(list(pkg.CHECKS)[2:], expected)
        self.assertEqual(expected, CORE + CRAFT)
        for g in expected:   # every registered guard reports a line, whichever crafts this install carries (#171)
            self.assertIn(f"[{g}]", r.stdout, g)
    def test_the_check_table_is_built_on_first_use_not_at_import(self):
        """#563 C2: importing the runner loads no guard; the table is built when a check needs it, then kept."""
        pkg = load_package()
        self.assertFalse(pkg.CHECKS.built())                                 # importing loaded no guard
        self.assertEqual(list(pkg.CHECKS)[:2], ["Rule-11", "Rule-12"])
        self.assertTrue(pkg.CHECKS.built()); self.assertEqual(len(pkg.CHECKS), len(pkg.registry()) + 2)
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
        self.assertEqual({e[1] for e in reg if e[3]}, {"containment", "rows", "prs", "provenance", "merges", "inbox", "decision_log"} | ({"events"} if "sysadmin" in CRAFTS else set()))   # events: the sysadmin craft's (#171); provenance: #191; merges: #541; inbox: #536; decision_log: #644
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
    def test_suite_env_points_the_child_at_a_given_temp_root(self):
        """#326: the sweep's half in the environment — all three names, and none of them without a root."""
        pkg = load_package()
        names = ("TMPDIR", "TMP", "TEMP")
        # given a root, all three names point at it, whatever the ambient environment said — and given
        # none, the function adds nothing of its own (it inherits, as it does inside a suite child).
        self.assertEqual({k: pkg.suite_env("/x/y").get(k) for k in names}, {k: "/x/y" for k in names})
        self.assertEqual({k: pkg.suite_env().get(k) for k in names}, {k: os.environ.get(k) for k in names})
        self.assertEqual(pkg.suite_env("/x/y")["DYAD_NO_NESTED_TESTS"], "1")   # the root is added, nothing else changes
    def test_run_suite_sweeps_its_temp_root_and_keeps_a_failing_one(self):
        """#326: the fixtures leak ~13,300 inodes a run and clean up nothing, so the one child every
        sanctioned run goes through makes a temp root and removes it — unless the run failed, which is
        the tree worth reading. Before this, 24,876 orphaned fixture directories took /tmp to 100% of
        its inodes and no push could leave any clone."""
        import glob, shutil as sh
        pkg = load_package()
        before = set(glob.glob("/tmp/dyad-suite-*") + glob.glob(str(Path(tempfile.gettempdir()) / "dyad-suite-*")))
        code, summary, _ = pkg.run_suite(None, "dyad.tests.test_incidents")
        self.assertEqual(code, 0, summary)
        self.assertEqual(set(glob.glob(str(Path(tempfile.gettempdir()) / "dyad-suite-*"))) - before, set(),
                         "a passing run leaves no temp root")
        code, _, _ = pkg.run_suite(None, "dyad.tests.no_such_module_326")
        self.assertNotEqual(code, 0)
        kept = set(glob.glob(str(Path(tempfile.gettempdir()) / "dyad-suite-*"))) - before
        self.assertEqual(len(kept), 1, "a failing run keeps exactly its own root")
        for d in kept:
            sh.rmtree(d, ignore_errors=True)
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
        self.assertIn("[Rule-12] dyad.tests.test_playbooks: Ran 36 tests OK", r.stdout)   # 4 + the d-work trace play-book's 4 (#213) + the audit play-book's 4 (#223; #619 moved the survey test to test_audits) + the d-work play-book's 6 (#309) + the port play-book's 3 (#353) + the release play-book's 4 (#493) + the backlog-groom play-book's 5 (#625) + the play-book-optimize play-book's 3 (#642) + the precedent-bootstrap play-book's 3 (#645)
        # the target only, never the whole root: `cmd_tests` prints one `[Rule-12] … Ran` line for one
        # dotted target, where a rootful run prints one per test root (six as this repo stands). #186
        # replaced `assertNotIn("Ran 479", …)`: 479 was a whole-root total from an older tree, and the
        # root has held several hundred methods more for many d-works, so the literal could not appear
        # in any run and the assertion could not fail. A count does not rot the same way — it fails
        # both if the roots are run and if the line stops being printed at all — and it pins no total.
        ran = [l for l in r.stdout.splitlines() if "[Rule-12]" in l and "Ran" in l]
        self.assertEqual(len(ran), 1, r.stdout)
        pkg = load_package()
        self.assertIn("DYAD_NO_NESTED_TESTS", inspect.getsource(pkg.suite_child))   # the flag is the point (120 s -> 39 s); #475: the one child

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

    def test_suite_gate_skips_an_events_only_range(self):
        """#438: a two-dot range wholly under `<host>/runbooks/events/` skips the suite as a ledger-only one does;
        a range carrying both stores is neither and runs."""
        pkg = load_package(); d, seed, git = self.gate_repo()
        ledger = git("rev-parse", "HEAD")
        ev = d / "workstation-corpus" / "runbooks" / "events"; ev.mkdir(parents=True)
        (ev / "sessions.jsonl").write_text('{"a": 1}\n'); git("add", "-A"); git("commit", "-qm", "events")
        old = pkg.REPO; pkg.REPO = d
        try:
            with unittest.mock.patch.dict(os.environ, {}, clear=False):
                for k in ("DYAD_NO_NESTED_TESTS", "DYAD_HOST", "DYAD_RUNBOOKS"):
                    os.environ.pop(k, None)
                pkg._SUITE_RAN = False
                self.assertEqual(pkg.suite_gate(ledger, "HEAD"), (False, f"skip [guards] Rule-12 suite: {ledger}..HEAD is events-only (d-work #438)"))
                self.assertEqual(pkg.suite_gate(seed, "HEAD"), (True, None))                       # ledger and events together -> run
                os.environ["DYAD_HOST"] = "infrastructure"
                self.assertEqual(pkg.suite_gate(ledger, "HEAD"), (True, None))                     # not this host's store -> run
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
        # #522: under the parallel suite this second install once saw 2 changes, which did not reproduce in three full
        # runs; the message names what the install wrote (the destination's own diff), so the next occurrence says why
        changed = lambda: subprocess.run(["git", "-C", str(d), "status", "--porcelain", "--untracked-files=all"],
                                         capture_output=True, text=True).stdout
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"installed into {Path(d).resolve()}: 0 changes", r.stdout, f"{r.stdout}\nwhat the install changed:\n{changed()}")
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
        rid = subprocess.run(py + ["dwork", "new", "t", "-d", "Y plan", "--said", "Y", "--slug", "t-row"], capture_output=True, text=True, env=env(), cwd=d).stdout.strip()
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
        craft_rbs = sorted((d / "crafts").glob("*/runbooks/*.md"))                            # each installed craft's too (#640)
        self.assertIn(f"ok   [rule-19] {len(core_rbs) + len(craft_rbs)} run-book(s), ", r.stdout)   # every core run-book ships with the package (#165, #137); the count is derived, never pinned (backlog #10)
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
        r = subprocess.run(py + ["dwork", "new", "t", "-d", "Y plan", "--said", "Y", "--slug", "t-row"], capture_output=True, text=True, env=env(), cwd=d)
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
    # the shape assertions exercise a real `check --evidence` traversal (integration-flavored: head/tree/dirty
    # and the guard lines are real), run as a child of a local clone whose release tags the test controls
    # (`hermetic_clone`, #529), so a release cut on `main` before its tag is pushed cannot turn it red (#526).
    # DYAD_NO_NESTED_TESTS is set in the child's env (`env()`), so Rule-12's nested-suite recursion guard applies.
    # The hash property itself is unit-tested separately, on fixed fake lines, in
    # test_evidence_sha256_is_pure_and_deterministic below.
    def test_evidence_block_shape_and_hash(self):
        clone, r = evidence_in_a_hermetic_clone()     # shared with the check-report test (#563 C3)
        lines = r.stdout.splitlines()
        self.assertNotIn("FAIL [evidence]", r.stdout, r.stdout + r.stderr)
        self.assertRegex(lines[0], r"^head=[0-9a-f]{40}$"); self.assertRegex(lines[1], r"^tree=[0-9a-f]{40}$")
        self.assertEqual(lines[0], "head=" + subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=clone, text=True).strip())
        self.assertRegex(lines[2], r"^dirty=(yes|no)$")
        self.assertTrue(any("[Rule-11]" in l for l in lines) and any("[guards] infra/containment" in l for l in lines), r.stdout)
        self.assertRegex(lines[-1], r"^evidence-sha256=[0-9a-f]{64}$")
        self.assertEqual(lines[-1], "evidence-sha256=" + load_package().evidence_sha256(lines[:-1]))
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
    def trace(self, rows, *ids):
        """#465: under the real repo's `dwork-trace: always` (package.py reads REPO's preferences), a `Y done` is
        recorded only beside its trace; a case about something else writes the trace it needs first."""
        t = rows.parent / "traces"; t.mkdir(exist_ok=True)
        for rid in ids:
            t.joinpath(f"{rid}.md").write_text(f"# Trace #{rid}\n")
    def dwork_state(self, d, *a):
        import os
        env = dict(os.environ, DYAD_INSTANCE=str(d / "inst"))  # absolute: package.py resolves REPO from its own location
        return subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "dwork", "state", *a],
                              cwd=d, env=env, capture_output=True, text=True)
    _slugs = iter(range(1, 10**6))
    def dwork_new(self, d, *a, slug=True):
        """#622: every call carries a row slug of its own unless it names one (or `slug=False`), so a case reads the
        same under `dwork-slug: on` (this instance's value, read by the runner from this tree) and `off`."""
        import os
        if slug and "--slug" not in a:
            a = (*a, "--slug", f"t-{next(PackageTests._slugs)}")
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
    # d-work #464 (R1, mode O): `dwork state … --check` makes every refusal of the real call and writes nothing
    def snapshot(self, d):
        """Every file under the scratch instance with its bytes, and git's own status of the scratch repo."""
        files = {p.relative_to(d).as_posix(): p.read_bytes() for p in sorted((d / "inst").rglob("*")) if p.is_file()}
        return files, subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=d,
                                     capture_output=True, text=True).stdout
    def test_dwork_state_check_on_a_legal_transition_writes_nothing(self):
        d, rows = self.dwork_repo(); before = self.snapshot(d)
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y", "--check")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith("ok 1: open -> planned"), r.stdout); self.assertIn("nothing written", r.stdout)
        self.assertEqual(self.snapshot(d), before, "no row, no provenance record, nothing else")
        self.assertFalse((rows.parent / "provenance").exists())
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y")          # the real call it stood for
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("state: planned", rows.joinpath("1.md").read_text())
    def test_dwork_state_check_refuses_as_the_real_call_does(self):
        """Each refusal under --check is the real call's, word for word, exit for exit, and the tree is unchanged."""
        d, rows = self.dwork_repo(); rows.joinpath("5.md").write_text("id: 5\ntitle: five\nopened: d\nstate: backlog\ndisposed: \nrefs: \n")
        before = self.snapshot(d)
        cases = [("2", "open"),                                                              # transition outside the table
                 ("1", "bogus"),                                                             # no such state
                 ("1", "done"),                                                              # no `Y done` to execute
                 ("1", "done", "-d", "Y done (merges PR #9 at 0123abc)", "--said", "Y"),     # the Done order (#202)
                 ("1", "planned", "-d", "Y done (merges PR #9)", "--said", "Y"),             # a merge with no head
                 ("1", "open", "-d", "Y done", "--said", "Y"),                               # no trace under `always` (#465)
                 ("1", "planned", "-d", "Y plan"),                                           # a disposition without its words
                 ("5", "open"),                                                              # backlog opens only on a prompt
                 ("9", "open", "--prompt", "p")]                                             # no such row
        for args in cases:
            with self.subTest(args=args):
                real, check = self.dwork_state(d, *args), self.dwork_state(d, *args, "--check")
                self.assertNotEqual(real.returncode, 0, real.stdout)
                self.assertEqual((check.returncode, check.stderr, check.stdout), (real.returncode, real.stderr, real.stdout))
                self.assertEqual(self.snapshot(d), before, "nothing written")
    def test_dwork_new_does_not_take_check(self):
        d, _ = self.dwork_repo()
        r = self.dwork_new(d, "three", "--prompt", "p", "--check")
        self.assertNotEqual(r.returncode, 0); self.assertIn("does not take --check", r.stderr)
        self.assertFalse((d / "inst" / "d-work" / "rows" / "3.md").exists())
    def test_dwork_state_check_passes_the_trace_test_without_writing_the_trace(self):
        d, rows = self.dwork_repo(); self.trace(rows, 1); before = self.snapshot(d)
        r = self.dwork_state(d, "1", "open", "-d", "Y done", "--said", "Y", "--check")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("entries disposition", r.stdout)
        self.assertEqual(self.snapshot(d), before)
    def test_dwork_done_state_follows_the_merge(self):
        """#202: a `Y done` that ratifies a merge names the head it was given on, is recorded with the state
        unchanged, and the row reaches `done` by a second dispositionless call once that head is on `main`."""
        d, rows = self.dwork_repo(); self.trace(rows, 1)
        r = self.dwork_state(d, "1", "planned", "-d", "Y done (merges PR #9)", "--said", "Y")
        self.assertNotEqual(r.returncode, 0); self.assertIn("the head its `Y` was given on", r.stderr)
        r = self.dwork_state(d, "1", "done", "-d", "Y done (merges PR #9 at 0123abcdeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee)", "--said", "Y")
        self.assertNotEqual(r.returncode, 0); self.assertIn("the state follows the merge", r.stderr)
        self.assertIn("state: open", rows.joinpath("1.md").read_text(), "nothing written")
        # #439: package.py runs git in the checkout that holds it (REPO), not in the scratch repo, so the head
        # must be that checkout's own HEAD; a scratch sha is "unknown in this clone" and the landing test never ran
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PKG, capture_output=True, text=True).stdout.strip()
        r = self.dwork_state(d, "1", "open", "-d", f"Y done (merges PR #9 at {head})", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)                       # the record, state unchanged
        self.assertIn("state: open", rows.joinpath("1.md").read_text())
        self.assertIn("Y done (merges PR #9", rows.joinpath("1.md").read_text())
        r = self.dwork_state(d, "1", "done")                              # the close: the head is HEAD itself
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("state: done", rows.joinpath("1.md").read_text())
        self.assertNotIn("unknown in this clone", r.stderr)               # the landing test ran
        self.assertIn("refs: \n", rows.joinpath("1.md").read_text())    # #439: the landing test writes nothing to refs
    def test_dwork_done_keeps_the_rows_refs(self):
        """#439: the landing loop bound its branch list to `refs`, which the close then wrote into the row as
        `['origin/main', 'main', 'HEAD']` — 28 rows on `main`. A close on a resolvable head keeps the refs."""
        d, rows = self.dwork_repo()
        rows.joinpath("1.md").write_text("id: 1\ntitle: one\nopened: d\nstate: open\ndisposed: \nrefs: 7 parent #3\n"); self.trace(rows, 1)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PKG, capture_output=True, text=True).stdout.strip()   # resolvable in REPO
        r = self.dwork_state(d, "1", "open", "-d", f"Y done (merges PR #9 at {head})", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.dwork_state(d, "1", "done")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertNotIn("unknown in this clone", r.stderr)   # the landing test ran
        text = rows.joinpath("1.md").read_text()
        self.assertIn("state: done", text); self.assertIn("refs: 7 parent #3\n", text); self.assertNotIn("origin/main", text)
    def test_dwork_refuses_refs_shaped_as_a_list(self):
        """#439: refs is space-separated tokens; `-r` (and `new`'s positional refs) refuse `[ ] ' " ,` before any
        write — the fence's `rows.refs_shape_problems` clause said where it costs a line instead of a push."""
        d, rows = self.dwork_repo(); before = rows.joinpath("1.md").read_text()
        for args in [("1", "open", "-r", "['origin/main', 'main', 'HEAD']"), ("1", "open", "-r", "7, 8"),
                     ("1", "open", "-r", '"7"')]:
            with self.subTest(args=args):
                r = self.dwork_state(d, *args)
                self.assertNotEqual(r.returncode, 0); self.assertIn("space-separated tokens", r.stderr)
        r = self.dwork_new(d, "three", "7, 8", "--prompt", "p")
        self.assertNotEqual(r.returncode, 0); self.assertIn("space-separated tokens", r.stderr)
        self.assertEqual(rows.joinpath("1.md").read_text(), before, "nothing written"); self.assertFalse(rows.joinpath("3.md").exists())
        r = self.dwork_state(d, "1", "open", "-r", "202 321 parent #5 PR #9")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("refs: 202 321 parent #5 PR #9\n", rows.joinpath("1.md").read_text())
    def test_dwork_refuses_a_done_with_no_disposition_behind_it(self):
        """#202: the closing act writes no disposition, so the `Y` it executes must already be on the row —
        the coupling the 2026-10-08 chain-of-authority audit (C2) found missing. The landing test itself is
        the fence's (`dyad/tests/guards/agent/test_rows.py`), which owns a repository to judge."""
        d, rows = self.dwork_repo(); self.trace(rows, 1)
        r = self.dwork_state(d, "1", "done")
        self.assertNotEqual(r.returncode, 0); self.assertIn("carries no `Y done` entry", r.stderr)
        self.assertIn("state: open", rows.joinpath("1.md").read_text())
        ghost = "0" * 40
        r = self.dwork_state(d, "1", "open", "-d", f"Y done (merges PR #9 at {ghost})", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.dwork_state(d, "1", "done")                              # a sha no clone resolves is noted, not fatal
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("is unknown in this clone", r.stderr)
        self.assertIn("state: done", rows.joinpath("1.md").read_text())
    def test_dwork_requires_a_head_per_PR_the_done_names(self):
        d, rows = self.dwork_repo(); self.trace(rows, 1)
        r = self.dwork_state(d, "1", "open", "-d", "Y done (batch #1,#2, merges PR #9,#10 at 0123abcdeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee)", "--said", "Y")
        self.assertNotEqual(r.returncode, 0); self.assertIn("2 named, 1 head(s) given", r.stderr)
        before = rows.joinpath("1.md").read_text()
        for short in ("Y done (merges PR #9 at 0123abcd, PR #10 at 4567bcdeffffffffffffffffffffffffffffffff)", "Y done (merges PR #9 at 0123abcdeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, PR #10 at 4567bcd)"):
            with self.subTest(short=short):                                       # #661: every head in full, before any write
                r = self.dwork_state(d, "1", "open", "-d", short, "--said", "Y")
                self.assertNotEqual(r.returncode, 0); self.assertIn("names each head in full, 40 hex", r.stderr)
                self.assertIn("git ls-remote origin refs/pull/<n>/head", r.stderr)
                self.assertEqual(rows.joinpath("1.md").read_text(), before, "nothing written")
        r = self.dwork_state(d, "1", "open", "-d", "Y done (merges PR #9 at 0123abcdeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, PR #10 at 4567bcdeffffffffffffffffffffffffffffffff)", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
    def test_dwork_refuses_a_done_record_without_its_trace(self):
        """#465: under `dwork-trace: always` (the real repo's value, which package.py reads), a `Y done` entry is
        refused before any write until `<instance>/d-work/traces/<id>.md` exists — the fence's `rows.trace_problems`
        said where it costs a line instead of a push; with the trace beside it the same call records it."""
        self.assertEqual(dyadlib.preference("dwork-trace", PKG.parent), "always", "the case reads the live preference")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"; before = rows.joinpath("1.md").read_text()
        for args in (("1", "open", "-d", "Y done", "--said", "Y"), ("1", "done", "-d", "Y done", "--said", "Y"),
                     ("1", "open", "-d", "Y done (batch #1,#2, merges PR #9 at 0123abcdeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee)", "--said", "Y")):
            with self.subTest(args=args):
                r = self.dwork_state(d, *args)
                self.assertNotEqual(r.returncode, 0); self.assertIn("refused: a `Y done` entry is recorded with its trace", r.stderr)
                self.assertIn("write it first: dyad dwork trace 1 --out --said-file", r.stderr); self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(rows.joinpath("1.md").read_text(), before, "nothing written"); self.assertFalse(rec.exists())
        r = self.dwork_state(d, "1", "open", "-d", "Y plan", "--said", "Y")               # a disposition other than `Y done`
        self.assertEqual(r.returncode, 0, r.stderr)
        self.trace(rows, 1)
        r = self.dwork_state(d, "1", "done", "-d", "Y done", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("state: done", rows.joinpath("1.md").read_text())
    def test_dwork_refuses_a_done_record_beside_a_preview_trace(self):
        """#592 R-b: the fence fails a `Y done` commit whose trace is a preview; `dwork state` says so before any write,
        naming the rewrite, and records the same entry once the trace runs through the Done."""
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"; before = rows.joinpath("1.md").read_text()
        t = rows.parent / "traces"; t.mkdir(exist_ok=True)
        t.joinpath("1.md").write_text("# Trace #1\n\n## Limits\n\n- preview: no Done disposition yet\n")
        r = self.dwork_state(d, "1", "open", "-d", "Y done", "--said", "Y")
        self.assertNotEqual(r.returncode, 0); self.assertIn("is a preview", r.stderr)
        self.assertIn("dyad dwork trace 1 --out --said-file", r.stderr); self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(rows.joinpath("1.md").read_text(), before, "nothing written"); self.assertFalse(rec.exists())
        self.trace(rows, 1)                                               # rewritten through the Done
        r = self.dwork_state(d, "1", "open", "-d", "Y done", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
    def test_dwork_state_mandate_close_needs_no_trace(self):
        """#465: a `--mandate` close writes `Y done (mandate #<id>, …)`; the accreted row's Done rides the mandate's,
        whose own trace covers the set, so no trace of its own is asked for."""
        d, rows = self.mandate_repo()
        self.assertFalse((rows.parent / "traces" / "3.md").exists())
        r = self.dwork_state(d, "3", "done", "--mandate", "1")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("state: done", rows.joinpath("3.md").read_text())
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
                 (self.dwork_new, ("three", "#1", "extra", "--prompt", "p"), "does not take extra"),   # the gate's bound (#592 R-a)
                 (self.dwork_new, ("three", "#1", "-r", "#2", "--prompt", "p"), "refs given twice"),
                 (self.dwork_new, ("three", "--relayed-via", "peer"), "give them with --prompt[-file] or --said[-file]"),
                 (self.dwork_state, ("1", "planned", "--relayed-via", "peer"), "give them with --prompt[-file] or --said[-file]"),
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
                rc = pkg.cmd_dwork(["new", "three", "#1", "--prompt", "open three", "--slug", "three-row"])
        self.assertEqual(rc, 0)
        self.assertIn("warning: could not read origin/main's rows", stderr.getvalue())
        self.assertIn("local ids only", stderr.getvalue())
        self.assertIn("d-work #32", stderr.getvalue())
        text = rows.joinpath("3.md").read_text()   # allocation still proceeds, from what it has locally
        self.assertIn("id: 3\n", text); self.assertIn("state: open\n", text)
    # d-work #290: implicit mode — the accreted row an authorized plan already describes, at no Operator cost
    def test_dwork_new_mandate_writes_an_implicit_row(self):
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv, prs = dyadlib.load_guard("agent", "provenance"), dyadlib.load_guard("agent", "prs")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y, go ahead")      # the mandate
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.dwork_new(d, "the accreted row", "--mandate", "1")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "3")
        born = dyadlib.parse_row_file(rows.joinpath("3.md").read_text())
        self.assertEqual((born.state, born.mode, born.refs), ("open", "implicit", "parent #1"))
        self.assertRegex(born.disposed, r"^\d{4}-\d{2}-\d{2} Y plan \(mandate #1\)$")         # one entry, no disposition of its own
        self.assertEqual(rows.joinpath("3.md").read_text().splitlines()[-2:][0], "mode: implicit")   # #622: then the slug line
        e = pv.parse(rec.joinpath("3.md").read_text())
        self.assertEqual([(x["kind"], x["text"]) for x in e], [("disposition", "Y, go ahead")])   # the mandate's own words, copied verbatim
        self.assertRegex(e[0]["note"], r"^mandate #1, \d{4}-\d{2}-\d{2}$")                    # the date they were given, which predates the row
        self.assertEqual(e[0]["date"], born.opened)                                           # the heading is today: the copy is made today
        self.assertEqual(pv.check_record(rec / "3.md", row=born), [])                          # Rule-7 property 5 by construction
        self.assertEqual(prs.check("d-work #3", rows=[born]), [])                              # and the plan gate passes it at once
        self.trace(rows, 3)                                                                    # #465: not a `--mandate` close
        r = self.dwork_state(d, "3", "done", "-d", "Y done, with #1", "--said", "Y")           # its Done rides the mandate's
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(dyadlib.parse_row_file(rows.joinpath("3.md").read_text()).mode, "implicit")   # carried, never rewritten
    def test_dwork_new_mandate_refuses_past_the_plans_stated_ceiling(self):
        """#592 R-c (mode 31): with 12 of the plan's stated 12 children, `dwork new --mandate` refuses before any write;
        with 11 it writes the 12th. The ceiling is the plan's `Mandate scope:` line (`plans.mandate_ceiling`)."""
        d, rows = self.dwork_repo()
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y, go")
        self.assertEqual(r.returncode, 0, r.stderr)
        plans = rows.parent / "plans"; plans.mkdir(exist_ok=True)
        plans.joinpath("1.md").write_text("# Plan #1 — m\n\nBase commit: abc\n\nMandate scope: one child per item; ceiling 12\n")
        for rid in range(3, 14):
            rows.joinpath(f"{rid}.md").write_text(f"id: {rid}\ntitle: c{rid}\nopened: d\nstate: open\ndisposed: d Y plan (mandate #1)\nrefs: parent #1\nmode: implicit\n")
        r = self.dwork_new(d, "the twelfth", "--mandate", "1")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "14")
        before = sorted(p.name for p in rows.iterdir())
        r = self.dwork_new(d, "the thirteenth", "--mandate", "1")
        self.assertNotEqual(r.returncode, 0); self.assertIn("already has 12 children, its plan's stated ceiling 12", r.stderr)
        self.assertEqual(sorted(p.name for p in rows.iterdir()), before)                      # nothing written
        self.assertFalse((rows.parent / "provenance" / "15.md").exists())
    def test_dwork_state_planned_runs_the_plan_check_first(self):
        """#592 R-c: `dwork state <id> planned` prints the plan check's lines before its write, and never refuses on them."""
        d, rows = self.dwork_repo()
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y", "--check")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("warn [plan] no plan file", r.stderr)
        plans = rows.parent / "plans"; plans.mkdir(exist_ok=True)
        plans.joinpath("1.md").write_text("# Plan #1 — p\n\nBase commit: abc\n\n## Intent as read\nx\norder: required\n")
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("warn [plan] 1.md: says `order: required`", r.stderr)
        self.assertIn("state: planned", rows.joinpath("1.md").read_text())
        (rows.parent / "traces").mkdir(exist_ok=True); rows.parent.joinpath("traces", "1.md").write_text("# Trace #1\n")
        r = self.dwork_state(d, "1", "planned", "-d", "Y done", "--said", "Y")                # already planned: a Done record
        self.assertEqual(r.returncode, 0, r.stderr); self.assertNotIn("warn [plan]", r.stderr)
        r = self.dwork_state(d, "1", "open")                                                  # no other transition runs it
        self.assertNotIn("warn [plan]", r.stderr)
    def test_open_is_archived_only_by_the_bare_intent_n(self):
        """#615: `dwork state <id> archived` from open needs `-d 'N intent'` with its words, on a row holding no `Y plan`;
        `Y intent` and an amend `N intent` keep the state."""
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv = dyadlib.load_guard("agent", "provenance")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"
        r = self.dwork_state(d, "1", "archived", "-d", "N intent"); self.assertNotEqual(r.returncode, 0)   # no words
        for args in ((), ("-d", "Y archive", "--said", "Y"), ("-d", "N plan", "--said", "N")):
            r = self.dwork_state(d, "1", "archived", *args)
            self.assertNotEqual(r.returncode, 0, args); self.assertIn("bare N to the intent question", r.stderr + r.stdout, args)
        r = self.dwork_state(d, "1", "open", "-d", "N intent", "--said", "N, read it as the guard alone")   # amend: stays open
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.dwork_state(d, "1", "open", "-d", "Y intent", "--said", "Y"); self.assertEqual(r.returncode, 0, r.stderr)
        r = self.dwork_state(d, "1", "archived", "-d", "N intent", "--said", "N"); self.assertEqual(r.returncode, 0, r.stderr)
        row = dyadlib.parse_row_file(rows.joinpath("1.md").read_text())
        self.assertEqual(row.state, "archived"); self.assertRegex(row.disposed, r"\d{4}-\d{2}-\d{2} N intent$")
        self.assertEqual(pv.parse(rec.joinpath("1.md").read_text())[-1]["text"], "N")
        self.assertEqual(pv.check_record(rec / "1.md", row=row), [])                           # Rule-7 property 5
        rows.joinpath("3.md").write_text("id: 3\ntitle: three\nopened: d\nstate: open\ndisposed: 2026-11-05 Y plan\nrefs: \n")
        r = self.dwork_state(d, "3", "archived", "-d", "N intent", "--said", "N")              # a plan-Y stands: no edge
        self.assertNotEqual(r.returncode, 0); self.assertIn("holding no `Y plan`", r.stderr)
    def test_plan_check_cli(self):
        """#592 R-c: `dyad plan check <id>` is a noun of the dispatch; 589 exits 0 on the live store, which a fresh install
        does not have (#608: the test skips there)."""
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        if not (dyadlib.load_guard("agent", "plans").plans_dir(PKG.parent) / "589.md").is_file():
            self.skipTest("this instance keeps no plan #589 (a fresh install)")
        run = lambda *a: subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "plan", *a], capture_output=True, text=True)
        r = run("check", "589"); self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("ok   [plan] #589", r.stdout)
        r = run("--help"); self.assertEqual(r.returncode, 0); self.assertIn("usage: dyad plan check <id>", r.stdout)
        r = run("check", "589", "--bogus"); self.assertEqual(r.returncode, 1); self.assertIn("does not take --bogus", r.stderr)
    def test_dwork_new_backlog_mandate_carries_a_prescribed_row(self):
        """#574 revision 2: a row a play-book the mandate's plan runs prescribes is carried under that plan-`Y`: born
        backlog, explicit (no `mode` line, its Done never rides the parent's), its entry `Y backlog (mandate #<id>)`,
        its record's entry 1 the mandate's words noted `mandate #<id>, <date>`."""
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv = dyadlib.load_guard("agent", "provenance")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y, run the exercise")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.dwork_new(d, "fence: the mode found", "--backlog", "--mandate", "1")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "3")
        born = dyadlib.parse_row_file(rows.joinpath("3.md").read_text())
        self.assertEqual((born.state, born.mode, born.refs), ("backlog", dyadlib.DEFAULT_MODE, "parent #1"))
        self.assertRegex(born.disposed, r"^\d{4}-\d{2}-\d{2} Y backlog \(mandate #1\)$")
        self.assertNotIn("mode:", rows.joinpath("3.md").read_text())
        e = pv.parse(rec.joinpath("3.md").read_text())
        self.assertEqual([(x["kind"], x["text"]) for x in e], [("disposition", "Y, run the exercise")])
        self.assertRegex(e[0]["note"], r"^mandate #1, \d{4}-\d{2}-\d{2}$")
        self.assertEqual(pv.check_record(rec / "3.md", row=born), [])                          # Rule-7 property 5
    def test_decisions_ride_the_done_and_the_precedent_y(self):
        """#644: `--decisions <file>` logs a `Y done`'s rulings as candidates and a `Y precedent (…)`'s as precedents
        naming that entry, in the decision log beside the row; a bad line, a missing -d or another entry writes nothing."""
        import json
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        d, rows = self.dwork_repo(); log = rows.parent / "decisions" / "1.md"
        dl = dyadlib.load_guard("agent", "decision_log")
        f = d / "dec.jsonl"
        f.write_text(json.dumps({"record": "replan", "case": "r1", "fields": {"accreted": False}, "inputs": "main moved",
                                 "outcome": "replan", "row": 2}) + "\n")
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y", "--decisions", str(f))
        self.assertNotEqual(r.returncode, 0); self.assertIn("rides a `Y done`", r.stderr)
        self.assertFalse(log.exists()); self.assertNotIn("Y plan", rows.joinpath("1.md").read_text())   # nothing written
        r = self.dwork_state(d, "1", "planned", "--decisions", str(f))
        self.assertNotEqual(r.returncode, 0); self.assertIn("give the entry with -d", r.stderr)
        self.trace(rows, 1)
        bad = d / "bad.jsonl"; bad.write_text(json.dumps({"record": "replan", "case": "r1", "outcome": "maybe"}) + "\n")
        r = self.dwork_state(d, "1", "open", "-d", "Y done", "--said", "Y", "--decisions", str(bad))
        self.assertNotEqual(r.returncode, 0); self.assertIn("is no outcome of dmc:replan", r.stderr); self.assertFalse(log.exists())
        r = self.dwork_state(d, "1", "open", "-d", "Y done", "--said", "Y, done", "--decisions", str(f))
        self.assertEqual(r.returncode, 0, r.stderr)
        (cand,) = dl.parse(log.read_text())
        self.assertEqual((cand["status"], cand["source"], cand["row"], cand["fields"]), ("candidate", "done", 2, {"accreted": "false"}))
        first = log.read_text()
        f.write_text(json.dumps({"record": "replan", "case": "r1"}) + "\n")
        r = self.dwork_state(d, "1", "open", "-d", "Y precedent (1 cases: replan×1)", "--said", "Y, admit", "--decisions", str(f))
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = dl.parse(log.read_text()); self.assertTrue(log.read_text().startswith(first))
        self.assertEqual(lines[0], cand)                                                       # append-only
        self.assertEqual({k: v for k, v in lines[1].items() if k not in ("status", "y")}, {k: v for k, v in cand.items() if k != "status"})
        self.assertEqual(lines[1]["status"], "precedent"); self.assertRegex(lines[1]["y"], r"^\d{4}-\d{2}-\d{2} Y precedent \(1 cases: replan×1\)$")
        self.assertIn(lines[1]["y"], rows.joinpath("1.md").read_text())
        import os
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": str(d / "inst")}):
            self.assertEqual(dl.check_package(d), [])
    def test_a_done_with_candidates_needs_its_decisions(self):
        """#648: a `Y done` on a row whose sources hold candidate rulings is refused without `--decisions`, before any
        write, naming the file to write; with the file it records them; a row with none needs no file."""
        import json, os
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        d, rows = self.dwork_repo()
        plans = rows.parent / "plans"; plans.mkdir()
        (plans / "1.md").write_text("# Plan #1\n\n## Falsification\n| id | claim | attack | result | survivor |\n"
                                    "|---|---|---|---|---|\n| F1 | a claim | an attack | refuted | s |\n")
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y"); self.assertEqual(r.returncode, 0, r.stderr)
        self.trace(rows, 1)
        before = rows.joinpath("1.md").read_text()
        r = self.dwork_state(d, "1", "done", "-d", "Y done", "--said", "Y, done")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("#1's Done names 1 candidate ruling(s) (attack-result-1-1)", r.stderr)
        self.assertIn("dyad board draft 1 --decisions-out <file>", r.stderr)
        self.assertEqual(rows.joinpath("1.md").read_text(), before)                      # nothing written
        bf = dyadlib.load_module(PKG / "scripts" / "backfill.py", "pkg_test_backfill")
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": str(d / "inst")}):
            cands = bf.capture(PKG.parent, 1)
        f = d / "dec.jsonl"; f.write_text("".join(json.dumps(c) + "\n" for c in cands))
        r = self.dwork_state(d, "1", "done", "-d", "Y done", "--said", "Y, done", "--decisions", str(f))
        self.assertEqual(r.returncode, 0, r.stderr)
        (block,) = dyadlib.load_guard("agent", "decision_log").parse((rows.parent / "decisions" / "1.md").read_text())
        self.assertEqual((block["case"], block["outcome"], block["status"], block["source"]), ("attack-result-1-1", "refuted", "candidate", "done"))
        rows.joinpath("3.md").write_text("id: 3\ntitle: three\nopened: d\nstate: planned\ndisposed: 2026-11-01 Y plan\nrefs: \n")
        self.trace(rows, 3)
        r = self.dwork_state(d, "3", "done", "-d", "Y done", "--said", "Y")             # no sources, no file needed
        self.assertEqual(r.returncode, 0, r.stderr)
    def test_a_done_retires_only_backlog_or_done_rows_and_archives_them_on_its_words(self):
        """#574 revision 3: G2, the record refuses a `retires` naming an open row or itself; G6, `state <r> archived
        --retired-by <id>` writes `Y archive (done #<id>)` and copies the done words noted `done #<id>, <date>`."""
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv, sv = dyadlib.load_guard("agent", "provenance"), dyadlib.load_guard("agent", "sessions")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"
        rows.joinpath("3.md").write_text("id: 3\ntitle: three\nopened: d\nstate: backlog\ndisposed: \nrefs: \n")
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y, go"); self.assertEqual(r.returncode, 0, r.stderr)
        self.trace(rows, 1)
        for bad, says in (("Y done (retires #3, #1)", "#1 (planned)"), ("Y done (retires #9)", "#9 (no row)")):
            r = self.dwork_state(d, "1", "done", "-d", bad, "--said", "Y")
            self.assertNotEqual(r.returncode, 0); self.assertIn("retires", r.stderr); self.assertIn(says, r.stderr)
        r = self.dwork_state(d, "3", "archived", "--retired-by", "1")                     # no Done retires it yet
        self.assertNotEqual(r.returncode, 0); self.assertIn("carries no 'Y done'", r.stderr)
        r = self.dwork_state(d, "1", "done", "-d", "Y done (retires #3, #2)", "--said", "Y, delivered")
        self.assertEqual(r.returncode, 0, r.stderr)
        for rid in (3, 2):
            r = self.dwork_state(d, str(rid), "archived", "--retired-by", "1")
            self.assertEqual(r.returncode, 0, r.stderr)
            row = dyadlib.parse_row_file(rows.joinpath(f"{rid}.md").read_text())
            self.assertEqual(row.state, "archived"); self.assertRegex(row.disposed, r"\d{4}-\d{2}-\d{2} Y archive \(done #1\)$")
        e = pv.parse(rec.joinpath("3.md").read_text())
        self.assertEqual([(x["kind"], x["text"]) for x in e], [("disposition", "Y, delivered")])
        self.assertRegex(e[0]["note"], r"^done #1, \d{4}-\d{2}-\d{2}$"); self.assertFalse(sv.own_disposition(e[0]["note"]))
        self.assertEqual(pv.check_record(rec / "3.md", row=dyadlib.parse_row_file(rows.joinpath("3.md").read_text())), [])
        r = self.dwork_state(d, "1", "archived", "--retired-by", "1")
        self.assertNotEqual(r.returncode, 0)
    def test_retired_by_waits_for_the_done_and_reads_past_a_release_ready_line(self):
        """Review of #574 r3: the archive needs the retiring row `done` (the state follows the merge), and its
        operative Done is read past a `release-ready` line written after it (#545)."""
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"
        rows.joinpath("3.md").write_text("id: 3\ntitle: three\nopened: d\nstate: backlog\ndisposed: \nrefs: \n")
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y, go"); self.assertEqual(r.returncode, 0, r.stderr)
        self.trace(rows, 1)
        r = self.dwork_state(d, "1", "planned", "-d", "Y done (retires #3, merges PR #5 at abc1234000000000000000000000000000000000)", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.dwork_state(d, "3", "archived", "--retired-by", "1")
        self.assertNotEqual(r.returncode, 0); self.assertIn("#1 is planned", r.stderr)
        one = rows.joinpath("1.md").read_text()
        rows.joinpath("1.md").write_text(one.replace("state: planned", "state: done").replace(
            "abc1234000000000000000000000000000000000)\n", "abc1234000000000000000000000000000000000); 2026-11-05 release-ready v0.9.0 at " + "b" * 40 + " (archive " + "a" * 64 + ")\n"))
        r = self.dwork_state(d, "3", "archived", "--retired-by", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(dyadlib.parse_row_file(rows.joinpath("3.md").read_text()).state, "archived")
    def test_dwork_new_mandate_refuses_before_it_writes(self):
        d, rows = self.dwork_repo(); before = rows.joinpath("1.md").read_text()
        rows.joinpath("5.md").write_text("id: 5\ntitle: five\nopened: d\nstate: planned\ndisposed: 2026-10-01 Y plan\nrefs: \n")
        cases = [(("three", "--mandate", "9"), "is no row"),
                 (("three", "--mandate", "x"), "is not a number"),
                 (("three", "--mandate", "1"), "carries no 'Y plan' disposition"),             # open, nothing disposed
                 (("three", "--mandate", "5"), "holds no `disposition` entry noted 'Y plan'"),  # a row whose record is absent
                 (("three", "--mandate", "5", "--backlog", "-d", "Y backlog", "--said", "Y"), "it takes no -d"),
                 (("three", "--mandate", "5", "-d", "Y open", "--said", "Y"), "it takes no -d"),
                 (("three", "--mandate", "5", "--prompt", "the words"), "it takes no -d")]
        for args, msg in cases:
            with self.subTest(args=args):
                r = self.dwork_new(d, *args)
                self.assertNotEqual(r.returncode, 0); self.assertIn(msg, r.stderr); self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(rows.joinpath("1.md").read_text(), before, "nothing written")
        self.assertFalse(rows.joinpath("3.md").exists()); self.assertFalse((rows.parent / "provenance").exists())
    # d-work #422: the accreted row's close form, and a relayed disposition — the two notes `own_disposition` reads
    def mandate_repo(self):
        """Row #1 the mandate, planned and then closed on its Done-`Y`; row #3 accreted under it."""
        d, rows = self.dwork_repo(); self.trace(rows, 1)
        for args in (("1", "planned", "-d", "Y plan", "--said", "Y, go ahead"),
                     ("1", "done", "-d", "Y done (accreted #3)", "--said", "Y, both delivered")):
            r = self.dwork_state(d, *args); self.assertEqual(r.returncode, 0, r.stderr)
        r = self.dwork_new(d, "the accreted row", "--mandate", "1"); self.assertEqual(r.returncode, 0, r.stderr)
        return d, rows
    def test_dwork_state_mandate_closes_an_accreted_row_on_the_mandates_words(self):
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv, sv = dyadlib.load_guard("agent", "provenance"), dyadlib.load_guard("agent", "sessions")
        d, rows = self.mandate_repo(); rec = rows.parent / "provenance"
        r = self.dwork_state(d, "3", "done", "--mandate", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        row = dyadlib.parse_row_file(rows.joinpath("3.md").read_text())
        self.assertEqual((row.state, row.mode), ("done", "implicit"))
        self.assertRegex(row.disposed, r"; (\d{4}-\d{2}-\d{2}) Y done \(mandate #1, \1\)$")   # the workaround's entry, composed
        e = pv.parse(rec.joinpath("3.md").read_text())
        self.assertEqual([(x["kind"], x["text"]) for x in e], [("disposition", "Y, go ahead"), ("disposition", "Y, both delivered")])
        self.assertRegex(e[1]["note"], r"^mandate #1, \d{4}-\d{2}-\d{2}$")                  # Rule-7 property 4's form
        self.assertEqual(e[1]["note"].split(", ")[1], pv.parse(rec.joinpath("1.md").read_text())[-1]["date"])   # the mandate's own date
        self.assertEqual(pv.check_record(rec / "3.md", row=row), [])                           # property 5: one entry per disposition
        self.assertFalse(any(sv.own_disposition(x["note"]) for x in e))                         # never an own disposition in this seat
    def test_dwork_state_mandate_refuses_before_it_writes(self):
        d, rows = self.mandate_repo()
        rows.joinpath("5.md").write_text("id: 5\ntitle: five\nopened: d\nstate: planned\ndisposed: 2026-10-01 Y plan; 2026-10-02 Y done\nrefs: \n")
        rows.joinpath("6.md").write_text("id: 6\ntitle: six\nopened: d\nstate: open\ndisposed: 2026-10-01 Y plan (mandate #5)\nrefs: \nmode: implicit\n")
        rows.joinpath("7.md").write_text("id: 7\ntitle: seven\nopened: d\nstate: open\ndisposed: 2026-10-01 Y plan (mandate #4)\nrefs: parent #4\nmode: implicit\n")
        rows.joinpath("4.md").write_text("id: 4\ntitle: four\nopened: d\nstate: planned\ndisposed: 2026-10-01 Y plan\nrefs: \n")
        before = {p.name: p.read_text() for p in rows.parent.rglob("*.md")}
        cases = [(("3", "planned", "--mandate", "1"), "the state is `done`"),
                 (("3", "done", "--mandate", "1", "-d", "Y done", "--said", "Y"), "it takes no -d"),
                 (("3", "done", "--mandate", "1", "--prompt", "p"), "it takes no -d"),
                 (("3", "done", "--mandate", "9"), "is no row"),
                 (("3", "done", "--mandate", "x"), "is not a number"),
                 (("7", "done", "--mandate", "4"), "carries no 'Y done' disposition"),         # the mandate is not done
                 (("6", "done", "--mandate", "5"), "holds no `disposition` entry noted 'Y done'"),   # its record is absent
                 (("3", "done", "--mandate", "3"), "carries no 'Y done' disposition"),         # #3 holds no Done of its own
                 (("6", "done", "--mandate", "1"), "is not accreted under #1")]
        for args, msg in cases:
            with self.subTest(args=args):
                r = self.dwork_state(d, *args)
                self.assertNotEqual(r.returncode, 0); self.assertIn(msg, r.stderr); self.assertNotIn("Traceback", r.stderr)
        self.assertEqual({p.name: p.read_text() for p in rows.parent.rglob("*.md")}, before, "nothing written")
    def test_dwork_state_notes_a_relayed_disposition(self):
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv, sv = dyadlib.load_guard("agent", "provenance"), dyadlib.load_guard("agent", "sessions")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y", "--relayed-via", "program-59cec502")
        self.assertEqual(r.returncode, 0, r.stderr)
        row = dyadlib.parse_row_file(rows.joinpath("1.md").read_text())
        self.assertRegex(row.disposed, r"^\d{4}-\d{2}-\d{2} Y plan$")                         # the row's entry is unchanged
        e = pv.parse(rec.joinpath("1.md").read_text())
        self.assertEqual([(x["kind"], x["note"], x["text"]) for x in e], [("disposition", "Y plan, relayed via program-59cec502", "Y")])
        self.assertEqual(pv.check_record(rec / "1.md", row=row), [])
        self.assertFalse(sv.own_disposition(e[0]["note"]))
    def test_dwork_state_records_a_hosting_approval_by_reference(self):
        """#545: `--said-ref` records the approved run in place of the Operator's chat words, its note `by reference`."""
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv = dyadlib.load_guard("agent", "provenance")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"
        ref = "run 41331223332 approved by pltrinh1122 at 2026-11-01T17:02:09Z"
        for args, msg in ((("-d", "Y plan", "--said-ref", "Y"), "--said-ref is `run <id> approved by"),
                          (("-d", "Y plan", "--said", "Y", "--said-ref", ref), "not both")):
            r = self.dwork_state(d, "1", "planned", *args)
            self.assertNotEqual(r.returncode, 0); self.assertIn(msg, r.stderr)
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said-ref", ref)
        self.assertEqual(r.returncode, 0, r.stderr)
        e = pv.parse(rec.joinpath("1.md").read_text())
        self.assertEqual([(x["kind"], x["note"], x["text"]) for x in e], [("disposition", "Y plan, by reference", ref)])
        self.assertEqual(pv.check_record(rec / "1.md", row=dyadlib.parse_row_file(rows.joinpath("1.md").read_text())), [])
    # d-work #290: the retirement form — backlog or done → archived over k rows on one Operator question
    def dwork_retire(self, d, *a):
        env = dict(os.environ, DYAD_INSTANCE=str(d / "inst"))
        return subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "dwork", "retire", *a],
                              cwd=d, env=env, capture_output=True, text=True)
    def test_dwork_retire_archives_a_batch_on_one_disposition(self):
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        pv = dyadlib.load_guard("agent", "provenance")
        d, rows = self.dwork_repo(); rec = rows.parent / "provenance"; self.trace(rows, 1)
        for args in (("state", "1", "planned", "-d", "Y plan", "--said", "Y"), ("state", "1", "done", "-d", "Y done", "--said", "Y")):
            self.assertEqual(self.dwork_state(d, *args[1:]).returncode, 0)
        self.assertEqual(self.dwork_new(d, "a surfaced mode", "--backlog", "-d", "Y backlog", "--said", "Y").returncode, 0)
        r = self.dwork_retire(d, "1", "3", "-d", "Y archive", "--said", "Y, archive them")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "archived #1 #3")
        for rid in ("1", "3"):
            with self.subTest(row=rid):
                got = dyadlib.parse_row_file(rows.joinpath(f"{rid}.md").read_text())
                self.assertEqual(got.state, "archived")
                self.assertRegex(got.disposed.split("; ")[-1], r"^\d{4}-\d{2}-\d{2} Y archive \(batch #1,#3\)$")   # the set it was batched with
                e = pv.parse(rec.joinpath(f"{rid}.md").read_text())[-1]
                self.assertEqual((e["kind"], e["text"]), ("disposition", "Y, archive them"))    # the same words in every named row's record
                self.assertIn("(batch #1,#3)", e["note"])
                self.assertEqual(pv.check_record(rec / f"{rid}.md", row=got), [])               # property 5 holds for each
        self.assertNotEqual(self.dwork_retire(d, "1", "-d", "Y archive", "--said", "Y").returncode, 0)   # archived is terminal
    def test_dwork_retire_one_row_takes_no_batch_note(self):
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        d, rows = self.dwork_repo()
        self.assertEqual(self.dwork_new(d, "a surfaced mode", "--backlog", "-d", "Y backlog", "--said", "Y").returncode, 0)
        r = self.dwork_retire(d, "3", "-d", "Y archive, superseded by #290", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr)
        got = dyadlib.parse_row_file(rows.joinpath("3.md").read_text())
        self.assertEqual(got.state, "archived"); self.assertNotIn("(batch", got.disposed)       # one row is no batch
    def test_dwork_retire_refuses_before_it_writes(self):
        d, rows = self.dwork_repo(); before = {p.name: p.read_text() for p in rows.glob("*.md")}
        rows.joinpath("5.md").write_text("id: 5\ntitle: five\nopened: d\nstate: backlog\ndisposed: 2026-10-01 Y backlog\nrefs: \n")
        before["5.md"] = rows.joinpath("5.md").read_text()
        cases = [((), "usage: dwork retire"),
                 (("5",), "give -d and --said"),
                 (("5", "-d", "Y archive"), "--said"),
                 (("5", "-d", "Y archive (batch #5)", "--said", "Y"), "composes `(batch #a,#b,#c)`"),
                 (("5", "x", "-d", "Y archive", "--said", "Y"), "is not a number"),
                 (("5", "9", "-d", "Y archive", "--said", "Y"), "no row 9"),
                 (("5", "5", "-d", "Y archive", "--said", "Y"), "named twice"),
                 (("1", "-d", "Y archive", "--said", "Y"), "#1 is open; dwork retire archives a row from backlog or done"),
                 (("5", "1", "-d", "Y archive", "--said", "Y"), "#1 is open"),                  # the whole set is judged first
                 (("5", "-d", "Y archive; and more", "--said", "Y"), "contains ';'"),
                 (("5", "--prompt", "the words"), "does not take --prompt")]
        for args, msg in cases:
            with self.subTest(args=args):
                r = self.dwork_retire(d, *args)
                self.assertNotEqual(r.returncode, 0); self.assertIn(msg, r.stderr); self.assertNotIn("Traceback", r.stderr)
        self.assertEqual({p.name: p.read_text() for p in rows.glob("*.md")}, before, "nothing written")
        self.assertFalse((rows.parent / "provenance").exists())
    def test_dwork_state_accepts_open_to_planned(self):
        d, rows = self.dwork_repo()
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("1: planned", r.stdout)
        text = rows.joinpath("1.md").read_text()
        self.assertIn("state: planned", text); self.assertIn("Y plan", text)
    # projector registry (crafts/sysarch/rules/projection.md p4; #160): discovered over the core's dyad/scripts/project_*.py
    # (keyed dyad-operator/<surface>, #378) and crafts/*/projectors/, the generated projections/ pattern
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
        on_disk |= {f"{dyadlib.CORE_CRAFT}/{p.stem.removeprefix('project_')}" for p in (PKG / "scripts").glob("project_*.py")}   # the core's own (#378)
        self.assertIn(f"{dyadlib.CORE_CRAFT}/countersign", on_disk)
        self.assertRegex(r.stdout, rf"(?m)^{dyadlib.CORE_CRAFT}/countersign\s+dyad/scripts/project_countersign\.py$")
        self.assertEqual(set(reg), on_disk)
        self.assertLessEqual({f"{c}/{s}" for c, s in (("sysarch", "entities"), ("sysarch", "erd"), ("sysadmin", "events"), ("sysarch", "schema"), ("sysarch", "kanban"), ("sysarch", "instances"))}, set(reg))
        import re
        listed = {m.group(1) for m in re.finditer(r"(?m)^(\S+/\S+)\s+(?:crafts/\S+/projectors|dyad/scripts)/project_\S+\.py$", r.stdout)}
        self.assertEqual(listed, on_disk, "--list prints exactly the discovered registry")
        self.assertEqual(pkg.PROJECTORS, {k: rel for k, (c, rel) in reg.items()})
        for key, (craft, rel) in reg.items():
            self.assertTrue((pkg.REPO / rel).exists(), rel); self.assertEqual(dyadlib.projector_craft(pkg.REPO / rel), craft)
            self.assertEqual(rel.split("/")[1] if rel.startswith("crafts/") else dyadlib.CORE_CRAFT, craft); self.assertEqual(key, f"{craft}/{key.split('/', 1)[1]}")
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
        reg = sorted(k for k, (craft, _rel) in pkg.projectors().items() if craft in bundled or craft == dyadlib.CORE_CRAFT)   # the core's own ship with every install (#378)
        self.assertIn(f"{dyadlib.CORE_CRAFT}/countersign", reg)
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


# d-work #563 C5: the runner runs each test class as its own child, so PackageTests' 146 tests (203.5 s in one child at
# #561) were the whole suite's critical path. Its tests are dealt round-robin, in definition order, into
# PACKAGE_SPLIT classes that subclass it and so keep its helpers; PackageTests itself keeps none. The tests that read
# one shared run (`evidence_in_a_hermetic_clone`) stay in one class, since a child shares a run only with itself.
# Same file, same root: the Rule-12 test mapping is unchanged.
PACKAGE_SPLIT = 6
PACKAGE_TOGETHER = ("test_check_runs_and_reports_rules_and_guards", "test_evidence_block_shape_and_hash")
def _split(cls, n, together):
    names = [k for k in vars(cls) if k.startswith("test")]
    groups = [[] for _ in range(n)]
    rest = [k for k in names if k not in together]
    groups[0] += [k for k in names if k in together]
    for i, k in enumerate(rest):
        groups[(i % (n - 1)) + 1 if n > 1 else 0].append(k)
    made = {}
    for i, group in enumerate(groups, 1):
        name = f"{cls.__name__}{i}"
        made[name] = type(name, (cls,), {"__module__": cls.__module__, "__qualname__": name,
                                         **{k: vars(cls)[k] for k in group}})
    for k in names:
        delattr(cls, k)
    return made
globals().update(_split(PackageTests, PACKAGE_SPLIT, PACKAGE_TOGETHER))

class FailingLinesTests(unittest.TestCase):
    def test_a_failed_steps_line_leads_with_its_failing_lines(self):
        """#607: corroborate's FAIL line printed a child's last three lines, so a suite's FAIL scrolled out behind its
        summary (#603's cut-off notice); the failing lines come first now, then the last line."""
        pkg = load_package()
        out = ("ok   [guards] agent/rules\n" + "\n".join(f"ok   [guards] g{i}" for i in range(20)) +
               "\nFAIL [guards] agent/traces 584.md: a stored preview\n     [Rule-12] dyad/tests: Ran 9 tests FAILED\n"
               "FAIL: test_x (t.T.test_x)\nFAILED (failures=1)\npackage: 292 files")
        got = pkg.failing_lines(out)
        self.assertEqual(got[:2], ["FAIL [guards] agent/traces 584.md: a stored preview", "FAIL: test_x (t.T.test_x)"])
        self.assertEqual(got[-1], "package: 292 files")
        # replays 2 and 3 (#607 DoD): #603's 20:42Z and the 05:19Z corroboration notices ended `warn … | ok … |
        # package: N files`, the child's last three lines, with its FAIL above them; now the FAIL leads
        child = ("ok   [guards] agent/rules (19 Rules)\n"
                 "     [Rule-12] dyad/tests: Ran 1421 tests FAILED (failures=3, skipped=9)\n"
                 "FAIL [Rule-12] tests failed (dyad/tests):\n"
                 "FAIL: test_dyad_plan_check_589_exits_0 (test_plans.PlanCheckTests) — FileNotFoundError: plans/589.md\n"
                 "FAILED (failures=3, skipped=9)\n"
                 "warn [syseng/naming] dyad/templates/rows-README.md: 'rows-README.md' is not lowercase\n"
                 "ok   [syseng/tests]\npackage: 295 files")
        line = " | ".join(pkg.failing_lines(child))
        self.assertTrue(line.startswith("FAIL [Rule-12] tests failed (dyad/tests): | FAIL: test_dyad_plan_check_589_exits_0"), line)
        self.assertNotIn("ok   [syseng/tests]", line)
        self.assertEqual(pkg.failing_lines("a\nb\nc\nd"), ["b", "c", "d"])
        self.assertEqual(pkg.failing_lines(""), [])
        self.assertLessEqual(len(pkg.failing_lines("\n".join(f"FAIL {i}" for i in range(20)))), 6)

class UtcDateTests(PackageTests):
    """#592 R-b: every date `dwork new` and `dwork state` write is UTC's, whatever the host's local day (the row and
    provenance helpers are PackageTests', whose own tests `_split` has moved to its numbered classes)."""
    def test_dwork_new_and_state_write_the_utc_date(self):
        d, rows = self.dwork_repo()
        with livetest.off_utc() as (utc, local):
            self.assertNotEqual(utc, local)
            r = self.dwork_new(d, "three", "#1", "--prompt", "open three")
            self.assertEqual(r.returncode, 0, r.stderr)
            s = self.dwork_state(d, "1", "planned", "-d", "Y plan", "--said", "Y")
            self.assertEqual(s.returncode, 0, s.stderr)
        self.assertIn(f"opened: {utc}\n", rows.joinpath("3.md").read_text())
        self.assertIn(f"\n## 1 prompt {utc}\n", (rows.parent / "provenance" / "3.md").read_text())
        self.assertIn(f"disposed: {utc} Y plan\n", rows.joinpath("1.md").read_text())
        self.assertIn(f"disposition {utc} Y plan\n", (rows.parent / "provenance" / "1.md").read_text())
        for f in ("3.md", "1.md"):
            self.assertNotIn(local, rows.joinpath(f).read_text())
    def test_no_writer_reads_the_local_date(self):
        """#592 R-b: `dyadlib.utc_date` is the one date a store is written with; a grep of the core's scripts and guards
        for the host's local day finds none, so a seventh writer cannot reintroduce it unseen."""
        hits = [f"{p.relative_to(PKG)}:{n}" for root in ("scripts", "guards") for p in sorted((PKG / root).rglob("*.py"))
                for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1) if "date.today(" in line]
        self.assertEqual(hits, [])
        self.assertIs(load_package().dyadlib.utc_date, dyadlib.utc_date)

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


class BundleWarningTests(unittest.TestCase):
    """#241: `cmd_bundle` was the one caller that ignored the runner's `warning:` convention — it
    printed every bundle message as `FAIL`, exited 1 from `check` and refused `build` on any of
    them. #232's disposition (two crafts held out of the bundle, which Rule-11 p7's
    unreleased-craft clause permits) made that fire on every call, so the release path was closed
    by a warning. Both halves now split the messages as `package.py`'s own check paths do."""
    def crafts(self, d: Path) -> list[str]:
        return sorted(p.name for p in (d / "crafts").iterdir() if p.is_dir()) if (d / "crafts").is_dir() else []
    def bundle_md(self, d: Path, core_version: str | None = None) -> None:
        """A `BUNDLE.md` naming only the core craft, in a repo with no tags: every craft in the tree
        is then unreleased and rowless, which is the #232 shape — warnings and nothing else."""
        ver = core_version or (d / "dyad" / "VERSION").read_text().strip()
        (d / "BUNDLE.md").write_text(f"# Bundle\n\nversion: 9.9.9\n\n| component | version |\n|---|---|\n| dyad-operator | {ver} |\n")
    def run_bundle(self, d: Path, *a: str):
        return subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "bundle", *a],
                              capture_output=True, text=True, env=env(), cwd=str(d))
    def test_a_warning_neither_fails_check_nor_refuses_build(self):
        d = scratch_install(with_craft=True)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        crafts = self.crafts(d)
        if not crafts:
            self.skipTest("no craft in this tree: nothing can be rowless and unreleased")
        self.bundle_md(d)
        r = self.run_bundle(d, "check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ok   [bundle] 1 components, v9.9.9", r.stdout)
        self.assertNotIn("FAIL", r.stdout + r.stderr)
        for c in crafts:
            self.assertIn(f"warn [bundle] '{c}' is in the tree but unreleased", r.stdout)
        out = SCRATCH.mkdtemp()
        r = self.run_bundle(d, "build", str(out))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("refused", r.stdout + r.stderr)
        ver = (d / "dyad" / "VERSION").read_text().strip()
        self.assertTrue((out / f"dyad-{ver}.tar.gz").is_file(), sorted(p.name for p in out.iterdir()))
        self.assertIn(f"dyad-{ver}.tar.gz", (out / "BUNDLE.sha256").read_text())
    def test_a_hard_message_still_fails_and_still_refuses(self):
        d = scratch_install(with_craft=True)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.bundle_md(d, core_version="0.0.1")   # a row that names a version the tree does not have
        r = self.run_bundle(d, "check")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("FAIL [bundle] 'dyad-operator': bundle names 0.0.1", r.stderr)
        out = SCRATCH.mkdtemp()
        r = self.run_bundle(d, "build", str(out))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("refused: bundle fails its check; not built", r.stderr)
        self.assertEqual(sorted(p.name for p in out.iterdir()), [])
    def test_messages_split_where_the_runner_splits_them(self):
        pkg = load_package()
        warn = "warning: 'disclosure' is in the tree but unreleased (no disclosure-v* tag): not yet bundled"   # a craft that stays unreleased (#369 C5 retires countersign)
        hard = "'sysarch': bundle names 0.1.0, the tree has 0.2.0"
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            left = pkg.bundle_messages([warn, hard])
        self.assertEqual(left, [hard])                                    # only the hard one travels
        self.assertEqual(buf.getvalue(), f"warn [bundle] {warn.removeprefix('warning:').strip()}\n")
        self.assertEqual(err.getvalue(), f"FAIL [bundle] {hard}\n")
        self.assertEqual(pkg.bundle_messages([]), [])

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
        self.assertEqual(labels, ["dyadlib", "package"] + guards + projectors + ["runbook", "craft", "distribute", "privatecite"])
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
                self.assertEqual(r.stderr.strip().splitlines(), ["InvariantError: dyadlib: invariant(s) failed: archived-is-terminal, inputs-cover-the-machine, terminal-states-stay-terminal"])   # one line, no traceback; the two #309 invariants over the same table fail with it
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
    def test_f_private_citation_to_a_public_remote_is_refused_by_the_hook(self):
        """#518: the hook threads git's `<remote> <url>` to the private-citation fence; fixture names only."""
        import hashlib
        self.ensure_main_pushed()
        self.git("checkout", "-q", "-B", "leak", "main")
        inst = self.d / "agent-corpus"
        (inst / "public_remotes.local.txt").write_text(f"{self.bare}\n")
        (inst / "private_repos.local.txt").write_text(hashlib.sha256(b"acme/secret").hexdigest() + "\n")
        self.git("add", "-A"); self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "lists")   # one zone per commit (Rule-1)
        f = self.d / "workstation-corpus" / "leak.md"; f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"[^1]: repo:acme/secret@{'c' * 40}:notes.md\n\n```\nprivate words\n```\n")
        self.git("add", "-A"); self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "leak")
        r = self.push("leak")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("FAIL [private-cite]", r.stdout + r.stderr)
        self.assertIn("workstation-corpus/leak.md:1 cites a private repo", r.stdout + r.stderr)
        self.assertNotIn("[guards]", r.stdout + r.stderr)             # refused before any guard runs
        f.write_text("[^1]: repo:acme/secret@" + "c" * 40 + ":notes.md\n")   # the citation alone, no quoted body
        self.git("add", "-A"); self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "no body")
        r = self.push("leak")                                           # the earlier commit still leaves with it: refused
        self.assertIn("FAIL [private-cite]", r.stdout + r.stderr)
        self.git("checkout", "-q", "main")
    def test_pushed_refs_skips_lines_it_cannot_read(self):
        pkg = load_package()
        z = "0" * 40
        self.assertEqual(pkg.pushed_refs(["", "garbage", f"(delete) {z} refs/heads/x {'1' * 40}"]), (None, []))

class PrePushStdinTests(unittest.TestCase):
    """d-work #592 (mode 28, F13): `check --guards --pre-push` with no ref line on stdin judged nothing and printed the
    deletion line, passing; on a hand run (no argv) it now prints its own line and fails, while git's own call (argv
    `<remote> <url>`, an up-to-date or git-rejected push) passes. A terminal on stdin is refused before `read()`, which
    would block. Under `--pre-push` a clone missing the core tag `BUNDLE.md` names fails, a shallow one only warns.
    A deletion-only push carries a ref line and still passes. Each case runs `cmd_guards` in process over a scratch repo."""
    class Reached(Exception):
        pass
    def setUp(self):
        self.pkg = load_package()
        self.d = scratch_repo(["a.txt"])
        self.pkg.REPO = self.d
    def git(self, *a):
        return subprocess.run(["git", "-C", str(self.d), *a], check=True, capture_output=True, text=True, env=dyadlib.git_env()).stdout.strip()
    def run_guards(self, stdin, argv=None, **patches):
        """(rc, output, reached): `reached` is True when the run got past the pre-push gate to the guards; `argv` is
        git's hook argv `(remote, url)`, absent on a hand run."""
        buf = io.StringIO()
        def reach():
            raise self.Reached()
        with contextlib.ExitStack() as st:
            st.enter_context(unittest.mock.patch.object(sys, "stdin", stdin))
            st.enter_context(unittest.mock.patch.object(self.pkg, "cmd_invariants", reach))
            for k, v in patches.items():
                st.enter_context(unittest.mock.patch.object(self.pkg, k, v))
            st.enter_context(contextlib.redirect_stdout(buf))
            try:
                rc = self.pkg.cmd_guards(pre_push=True, **dict(zip(("remote", "url"), argv or ())))
            except self.Reached:
                return None, buf.getvalue(), True
        return rc, buf.getvalue(), False
    def head_line(self):
        head = self.git("rev-parse", "HEAD")
        return f"refs/heads/main {head} refs/heads/main {'0' * 40}\n"
    def test_no_ref_line_fails_with_its_own_line(self):
        for text in ("", "\n", "garbage\n"):
            with self.subTest(stdin=text):
                rc, out, reached = self.run_guards(io.StringIO(text))
                self.assertEqual((rc, out, reached), (1, self.pkg.PRE_PUSH_EMPTY + "\n", False))
                self.assertEqual(out, "warn [pre-push] no ref line on stdin: nothing judged\n")
    def test_git_s_empty_stdin_passes(self):
        """git runs the hook with `<remote> <url>` and an empty stdin for an up-to-date push and for one it rejects
        itself (non-fast-forward): nothing to judge, so it passes and git reports its own outcome."""
        for text in ("", "\n"):
            with self.subTest(stdin=text):
                rc, out, reached = self.run_guards(io.StringIO(text), argv=("origin", "/x"))
                self.assertEqual((rc, out, reached), (0, self.pkg.PRE_PUSH_NOTHING + "\n", False))
                self.assertNotIn(self.pkg.PRE_PUSH_EMPTY, out)
    def test_an_up_to_date_git_push_exits_0_through_the_hook(self):
        """End to end: a clone whose pre-push hook execs this package's gate as `dyad/hooks/pre-push` does; an
        up-to-date `git push` runs it with argv and an empty stdin, and git prints `Everything up-to-date`, exit 0."""
        up = SCRATCH.mkdtemp() / "up.git"
        subprocess.run(["git", "init", "-q", "--bare", str(up)], check=True, env=dyadlib.git_env())
        self.git("remote", "add", "origin", str(up)); self.git("push", "-q", "origin", "HEAD:main")
        hooks = SCRATCH.mkdtemp()
        hook = hooks / "pre-push"
        hook.write_text(f'#!/usr/bin/env bash\nexec "{PKG / "bin" / "dyad-python"}" "{PKG / "scripts" / "package.py"}" '
                        f'check --guards --pre-push "$@"\n')
        hook.chmod(0o755)
        self.git("config", "core.hooksPath", str(hooks))
        r = subprocess.run(["git", "-C", str(self.d), "push", "origin", "HEAD:main"], capture_output=True, text=True,
                           env=dyadlib.git_env(), stdin=subprocess.DEVNULL, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Everything up-to-date", r.stdout + r.stderr)
        self.assertIn(self.pkg.PRE_PUSH_NOTHING, r.stdout + r.stderr)
    def test_a_terminal_is_refused_before_reading(self):
        test = self
        class Tty(io.StringIO):
            def isatty(self):
                return True
            def read(self, *a):
                test.fail("read() on a terminal")
        rc, out, reached = self.run_guards(Tty())
        self.assertEqual((rc, reached), (1, False))
        self.assertEqual(out, "refused: --pre-push reads git's ref lines on stdin; run it from the hook\n")
    def test_a_deletion_only_push_still_passes(self):
        called = []
        line = f"(delete) {'0' * 40} refs/heads/gone {'a' * 40}\n"
        rc, out, reached = self.run_guards(io.StringIO(line), clone_lines=lambda repo, clerical=None: called.append(repo) or ["FAIL [pre-push] x"])
        self.assertEqual((rc, reached, called), (0, False, []), out)
        self.assertIn("ok   [pre-push] nothing new to judge", out)
        self.assertNotIn(self.pkg.PRE_PUSH_EMPTY, out)
    def test_a_clone_missing_the_core_tag_fails_before_any_guard(self):
        (self.d / "BUNDLE.md").write_text("# Bundle\n\nversion: 0.2.0\n\n| component | version |\n|-----------|---------|\n| dyad-operator | 0.1.0 |\n")
        self.git("add", "BUNDLE.md"); self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "bundle")
        rc, out, reached = self.run_guards(io.StringIO(self.head_line()))
        self.assertEqual((rc, reached), (1, False), out)
        self.assertIn("FAIL [pre-push] no dyad-operator-v0.1.0 tag while BUNDLE.md names dyad-operator 0.1.0", out)
        self.git("tag", "dyad-operator-v0.1.0")                                 # the tag present: on to the guards
        rc, out, reached = self.run_guards(io.StringIO(self.head_line()))
        self.assertTrue(reached, out); self.assertNotIn("[pre-push]", out)
    def test_a_shallow_clone_only_warns(self):
        rc, out, reached = self.run_guards(io.StringIO(self.head_line()),
                                           clone_lines=lambda repo, clerical=None: ["warn [pre-push] shallow clone: fetch it"])
        self.assertTrue(reached, out); self.assertIn("warn [pre-push] shallow clone: fetch it\n", out)
    def test_clone_lines_classes_bootstrap_s_problems(self):
        bs = dyadlib.load_module(PKG / "scripts" / "bootstrap.py", "bootstrap")
        probs = ["shallow clone: run bootstrap (git fetch --unshallow --tags)", "no dyad-operator-v1.0.0 tag while BUNDLE.md names dyad-operator 1.0.0: x"]
        with unittest.mock.patch.object(bs, "clone_problems", lambda repo: probs):
            self.assertEqual(self.pkg.clone_lines(self.d), ["warn [pre-push] " + probs[0], "FAIL [pre-push] " + probs[1]])
        with unittest.mock.patch.object(bs, "clone_problems", lambda repo: []):
            self.assertEqual(self.pkg.clone_lines(self.d), [])
        with unittest.mock.patch.object(bs, "is_shallow", lambda repo: True):   # the prefix is bootstrap's own shallow line
            (line,) = self.pkg.clone_lines(self.d)
        self.assertTrue(line.startswith("warn [pre-push] " + self.pkg.SHALLOW_PREFIX), line)

    def test_no_guard_that_reads_tags_runs_on_a_clerical_push(self):
        """#621 Decision 1: the clerical skip of a missing core tag is true only while every guard that reads tags is
        left to the sweep on a ledger-only or an events-only push; a new tag-reading guard that runs there fails here."""
        import re
        reads_tags = re.compile(r"""["']tag["']|refs/tags""")
        self.pkg.REPO = PKG.parent                                              # the registry of this tree
        rel = dyadlib.instance_rel(self.pkg.REPO) or "agent-corpus"
        ledger, events = [f"{rel}/d-work/rows/1.md"], [f"{dyadlib.events_rel(self.pkg.REPO) or 'x'}/x.jsonl"]
        found = []
        for corpus, entity, path, tx, mod, problem in self.pkg.registry():
            if mod is None or not reads_tags.search(Path(mod.__file__).read_text()):
                continue
            found.append(f"{corpus}/{entity}")
            for clerical in (ledger, events):
                self.assertTrue(self.pkg.swept(mod, clerical), (f"{corpus}/{entity}", clerical))
        self.assertTrue({"infra/bundle", "craft/crafts"} <= set(found), found)

class ReleaseWindowTests(unittest.TestCase):
    """#621 Decision 1: after a cut lands on `main` and before its tag exists, a ledger-only or events-only push passes
    the pre-push gate with one skip line, a code push and `check --evidence` still refuse, and the tag ends the window.
    A scratch origin, the cut and each push replayed in order, `cmd_guards` judging each in process."""
    Reached, git, run_guards = PrePushStdinTests.Reached, PrePushStdinTests.git, PrePushStdinTests.run_guards
    def setUp(self):
        self.pkg = load_package()
        self.addCleanup(setattr, self.pkg, "REPO", self.pkg.REPO)
        self.d = scratch_repo(["a.txt"])
        self.pkg.REPO = self.d
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus"}); e.start(); self.addCleanup(e.stop)
        for k in ("DYAD_RUNBOOKS", "DYAD_HOST"):
            os.environ.pop(k, None)
        for k, v in (("user.email", "t@t"), ("user.name", "t"), ("commit.gpgsign", "false")):
            self.git("config", k, v)
        self.git("branch", "-M", "main")
        self.origin = SCRATCH.mkdtemp() / "o.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True, env=dyadlib.git_env())
        self.git("remote", "add", "origin", str(self.origin))
        self.release("0.1.0", "base"); self.git("tag", "dyad-operator-v0.1.0"); self.land()
    BUNDLE = "# Bundle\n\nversion: {v}\n\n| component | version |\n|-----------|---------|\n| dyad-operator | {v} |\n"
    def commit(self, files, msg):
        for rel, text in files.items():
            (self.d / rel).parent.mkdir(parents=True, exist_ok=True); (self.d / rel).write_text(text)
        self.git("add", "-A"); self.git("commit", "-qm", msg)
    def release(self, v, msg):
        self.commit({"dyad/VERSION": f"{v}\n", "BUNDLE.md": self.BUNDLE.format(v=v)}, msg)
    def land(self):
        self.git("push", "-q", "origin", "HEAD:main"); self.git("fetch", "-q", "origin")
    def judge(self):
        return self.run_guards(io.StringIO(f"refs/heads/main {self.git('rev-parse', 'HEAD')} refs/heads/main "
                                           f"{self.git('rev-parse', 'origin/main')}\n"))
    def test_after_a_cut_clerical_pushes_pass_before_the_tag(self):
        self.release("0.2.0", "the cut"); self.land()                            # on main, no dyad-operator-v0.2.0
        skip = ("skip [pre-push] no dyad-operator-v0.2.0 tag while BUNDLE.md names dyad-operator 0.2.0: "
                "a ledger-only or events-only push runs no check that reads tags (d-work #621)")
        for step, files in (("the close", {"agent-corpus/d-work/rows/9.md": "id: 9\nstate: done\n"}),
                            ("an inbox post", {"agent-corpus/d-work/inbox/program/m.md": "from: automaton\n"}),
                            ("an events-only commit", {"workstation-corpus/runbooks/events/released.jsonl": "{}\n"}),
                            ("the release-ready line", {"agent-corpus/d-work/rows/9.md": "id: 9\nstate: done\nready\n"})):
            with self.subTest(step):
                self.commit(files, step)
                rc, out, reached = self.judge()
                self.assertTrue(reached, out); self.assertIn(skip, out); self.assertNotIn("FAIL", out)
                self.land()
        self.commit({"code.py": "x = 1\n"}, "a code commit")
        rc, out, reached = self.judge()
        self.assertEqual((rc, reached), (1, False), out)
        self.assertIn("FAIL [pre-push] no dyad-operator-v0.2.0 tag while BUNDLE.md names dyad-operator 0.2.0", out)
        code = self.git("rev-parse", "HEAD")
        self.git("checkout", "-q", "HEAD~1")                                  # the ledger head: the evidence still refuses
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(self.pkg.cmd_evidence(), 2)
        self.assertIn("FAIL [evidence] no dyad-operator-v0.2.0 tag", buf.getvalue())
        self.git("checkout", "-q", "main"); self.assertEqual(self.git("rev-parse", "HEAD"), code)
        self.git("tag", "dyad-operator-v0.2.0", "origin/main")                  # the tag ends the window
        rc, out, reached = self.judge()
        self.assertTrue(reached, out); self.assertNotIn("[pre-push]", out)

class SlugVerbTests(unittest.TestCase):
    """d-work #622 Decision 2: `dwork new --slug` and `dwork state --slug`, in process over a scratch instance, with the
    preference `dwork-slug` read through `dyadlib.slugs_on` (patched to `on` or `off`)."""
    def setUp(self):
        self.pkg = load_package()
        self.d = scratch_repo(["README.md"])
        self.rows = self.d / "inst" / "d-work" / "rows"; self.rows.mkdir(parents=True)
        self.rows.joinpath("1.md").write_text("id: 1\ntitle: one\nopened: d\nstate: open\ndisposed: \nrefs: \n")
        self.rows.joinpath("2.md").write_text("id: 2\ntitle: two\nopened: d\nstate: done\ndisposed: Y done\nrefs: \n")
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": str(self.d / "inst")}); e.start(); self.addCleanup(e.stop)
    def run_(self, *a, on=False):
        err = io.StringIO()
        with unittest.mock.patch.object(dyadlib, "slugs_on", lambda root=None: on), contextlib.redirect_stderr(err), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            try:
                rc = self.pkg.cmd_dwork(list(a))
            except SystemExit as x:
                return 1, out.getvalue(), str(x.code)
        return rc, out.getvalue(), err.getvalue()
    def row(self, rid):
        return dyadlib.parse_row_file(self.rows.joinpath(f"{rid}.md").read_text())
    def test_new_takes_a_slug_and_refuses_a_bad_or_held_one(self):
        self.assertEqual(self.run_("new", "three", "--prompt", "p", "--slug", "row-slugs")[0], 0)
        self.assertEqual(self.row(3).slug, "row-slugs")
        rc, _, err = self.run_("new", "four", "--prompt", "p", "--slug", "release")
        self.assertEqual(rc, 1); self.assertIn("not 2 to 4 pieces", err)
        rc, _, err = self.run_("new", "four", "--prompt", "p", "--slug", "row-slugs")
        self.assertEqual(rc, 1); self.assertIn("held by #3", err)
        self.assertFalse(self.rows.joinpath("4.md").exists())
    def test_under_on_a_row_opens_only_with_its_slug(self):
        for args in (("new", "x", "--prompt", "p"), ("new", "x", "--backlog", "-d", "Y backlog", "--said", "Y"),
                     ("new", "x", "--mandate", "1")):
            with self.subTest(args=args):
                rc, _, err = self.run_(*args, on=True)
                self.assertEqual(rc, 1, err); self.assertIn("needs --slug <slug> under the preference dwork-slug: on", err)
        self.assertFalse(self.rows.joinpath("3.md").exists())
        self.assertEqual(self.run_("new", "x", "--prompt", "p")[0], 0)                  # off: as before
        self.assertEqual(self.row(3).slug, "")
    def test_state_writes_a_slug_once_never_on_a_terminal_row(self):
        self.assertEqual(self.run_("state", "1", "open", "--slug", "one-row")[0], 0)
        self.assertEqual(self.row(1).slug, "one-row")
        self.assertEqual(self.run_("state", "1", "open", "--slug", "one-row")[0], 0)      # the same slug: no change
        rc, _, err = self.run_("state", "1", "open", "--slug", "other-row")
        self.assertEqual(rc, 1); self.assertIn("never changed", err)
        rc, _, err = self.run_("state", "2", "done", "--slug", "two-row")
        self.assertEqual(rc, 1); self.assertIn("a terminal row never gains a row slug", err)
        self.run_("new", "three", "--prompt", "p")
        rc, _, err = self.run_("state", "3", "open", "--slug", "one-row")
        self.assertEqual(rc, 1); self.assertIn("held by #1", err)
    def test_state_and_retire_keep_the_slug(self):
        self.run_("state", "1", "open", "--slug", "one-row")
        self.assertEqual(self.run_("state", "1", "planned", "-d", "Y plan", "--said", "Y")[0], 0)
        self.assertEqual((self.row(1).state, self.row(1).slug), ("planned", "one-row"))
        self.run_("new", "four", "--backlog", "-d", "Y backlog", "--said", "Y", "--slug", "four-row")
        self.assertEqual(self.run_("retire", "3", "-d", "Y archive", "--said", "Y")[0], 0)
        self.assertEqual((self.row(3).state, self.row(3).slug), ("archived", "four-row"))
    def test_list_prints_labels_under_on(self):
        self.run_("state", "1", "open", "--slug", "one-row")
        self.assertIn("#1-one-row [open] one", self.run_("list", on=True)[1])
        out = self.run_("list")[1]
        self.assertIn("#1 [open] one", out); self.assertIn("#2 [done] two", out)

class DoneHeadPrePushTests(unittest.TestCase):
    """d-work #495 (F1 of #487): the pre-push gate refuses a push that moves a head the operative `Y done` of a row
    not yet terminal names (`Y done (merges PR #9 at <head>)`), since the push would void that `Y` (Rule-2, Binding;
    #476). A scratch repo, `pkg.REPO` pointed at it: `origin/main` (a remote-tracking ref written by hand) holds the
    rows, the branch `feat` is at X, and each case feeds `done_head_refusals` git's pre-push lines."""
    def setUp(self):
        self.pkg = load_package()
        self.addCleanup(setattr, self.pkg, "REPO", self.pkg.REPO)
        e = unittest.mock.patch.dict(os.environ, {}, clear=False); e.start(); self.addCleanup(e.stop)
        os.environ.pop("DYAD_INSTANCE", None)
        d = self.d = SCRATCH.mkdtemp()
        self.git = lambda *a: subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True,
                                             env=dyadlib.git_env()).stdout.strip()
        self.git("init", "-q", "-b", "main")
        for k, v in (("user.email", "t@example.com"), ("user.name", "t"), ("commit.gpgsign", "false")):
            self.git("config", k, v)
        (d / "seed.txt").write_text("seed\n"); self.git("add", "-A"); self.git("commit", "-qm", "seed")
        self.git("checkout", "-q", "-b", "feat")
        (d / "feat.txt").write_text("x\n"); self.git("add", "-A"); self.git("commit", "-qm", "x")
        self.x = self.git("rev-parse", "HEAD")
        (d / "feat.txt").write_text("y\n"); self.git("add", "-A"); self.git("commit", "-qm", "y")
        self.y = self.git("rev-parse", "HEAD")
        self.git("checkout", "-q", "main")
        self.pkg.REPO = d
    def ledger(self, state, disposed, publish=True):
        """Row 1 on `main` in `state` with `disposed`; `origin/main` moved to it unless `publish` is False."""
        rows = self.d / "agent-corpus" / "d-work" / "rows"; rows.mkdir(parents=True, exist_ok=True)
        (rows / "1.md").write_text(dyadlib.format_row_file(dyadlib.Row(1, "one", "d", state, disposed, "")))
        self.git("add", "-A"); self.git("commit", "-qm", f"row {state}")
        if publish:
            self.git("update-ref", "refs/remotes/origin/main", "HEAD")
    def done_on(self, head):
        return f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {head})"
    def judge(self, *lines):
        return self.pkg.done_head_refusals(list(lines))
    def move(self, old=None, new=None, ref="refs/heads/feat"):
        return f"refs/heads/feat {new or self.y} {ref} {old or self.x}"
    def test_moving_a_named_head_is_refused(self):
        self.ledger("planned", self.done_on(self.x[:7]))       # a short sha, as entries may hold
        refusals, notes = self.judge(self.move())
        self.assertEqual(len(refusals), 1, refusals); self.assertEqual(notes, [])
        self.assertIn("row #1", refusals[0]); self.assertIn("PR #9", refusals[0]); self.assertIn(self.x[:9], refusals[0])
        self.assertIn("void", refusals[0])
        self.ledger("planned", self.done_on(self.x))           # the full sha too
        self.assertEqual(len(self.judge(self.move())[0]), 1)
    def test_a_deletion_of_a_named_head_is_refused(self):
        self.ledger("open", self.done_on(self.x))
        refusals, _ = self.judge(f"(delete) {'0' * 40} refs/heads/feat {self.x}")
        self.assertEqual(len(refusals), 1, refusals); self.assertIn("deletes it", refusals[0])
    def test_an_unrelated_branch_passes(self):
        self.ledger("planned", self.done_on(self.x))
        self.assertEqual(self.judge(f"refs/heads/other {self.x} refs/heads/other {self.y}"), ([], []))
        self.assertEqual(self.judge(f"refs/heads/new {self.y} refs/heads/new {'0' * 40}"), ([], []))   # replaces nothing
        self.assertEqual(self.judge(f"refs/tags/t {self.y} refs/tags/t {self.x}"), ([], []))           # not a branch
        self.assertEqual(self.judge(self.move(ref="refs/heads/main")), ([], []))                         # the ledger's branch
        self.assertEqual(self.judge(self.move(new=self.x)), ([], []))                                    # moves nothing
    def test_a_done_or_archived_row_passes(self):
        for state in ("done", "archived"):
            self.ledger(state, self.done_on(self.x))
            self.assertEqual(self.judge(self.move()), ([], []), state)
    def test_a_later_done_on_the_new_head_passes(self):
        self.ledger("planned", self.done_on(self.x) + f"; 2026-01-03 Y done (merges PR #9 at {self.y[:7]})")
        self.assertEqual(self.judge(self.move()), ([], []))      # X is history: the operative entry names Y
        self.assertEqual(len(self.judge(self.move(old=self.y, new=self.x))[0]), 1)   # and Y is now held
    def test_a_landed_head_passes(self):
        self.ledger("planned", self.done_on(self.x))
        self.git("merge", "-q", "--no-ff", "-m", "merge PR #9", self.x)
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.assertEqual(self.judge(f"(delete) {'0' * 40} refs/heads/feat {self.x}"), ([], []))
    def test_a_record_on_local_main_not_yet_pushed_counts(self):
        self.ledger("planned", "2026-01-01 Y plan")
        self.ledger("planned", self.done_on(self.x), publish=False)
        self.assertEqual(len(self.judge(self.move())[0]), 1)
    def test_no_ledger_skips_with_one_line(self):
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        refusals, notes = self.judge(self.move())
        self.assertEqual(refusals, []); self.assertEqual(len(notes), 1); self.assertIn("skip [pre-push]", notes[0])
    def test_cmd_guards_refuses_before_any_guard(self):
        self.ledger("planned", self.done_on(self.x))
        buf = io.StringIO()
        with unittest.mock.patch.object(sys, "stdin", io.StringIO(self.move() + "\n")), contextlib.redirect_stdout(buf):
            rc = self.pkg.cmd_guards(pre_push=True)
        self.assertEqual(rc, 1, buf.getvalue())
        self.assertIn("FAIL [pre-push] refs/heads/feat is at", buf.getvalue())
        self.assertNotIn("[guards]", buf.getvalue())

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
                         ("4", "core.autocrlf", "commit.gpgsign", "false"))
        self.assertEqual([(env[f"GIT_CONFIG_KEY_{i}"], env[f"GIT_CONFIG_VALUE_{i}"]) for i in (2, 3)],
                         [("gc.auto", "0"), ("maintenance.auto", "false")])   # #475: no background repack under a copy
        with tempfile.TemporaryDirectory() as d:
            git = lambda *a: subprocess.run(["git", *a], cwd=d, env=env, check=True, capture_output=True, text=True).stdout
            git("init", "-q"); git("config", "commit.gpgsign", "true")   # the local config asks; the env entry wins
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "c")
            self.assertNotIn("gpgsig", git("cat-file", "-p", "HEAD"))
            self.assertEqual((git("config", "--get", "gc.auto").strip(), git("config", "--get", "maintenance.auto").strip()),
                             ("0", "false"))
    def test_caller_git_c_never_reaches_a_fixture_repo(self):
        """#456 (row 153): a caller's `git -c` arrives as `GIT_CONFIG_PARAMETERS`; under `suite_env()` it is
        gone, while the caller's `GIT_CONFIG_COUNT` entries (#206) still survive. A scratch repo whose
        `dyad/hooks/pre-commit` fails commits under `suite_env()` and fails under the raw environment."""
        pkg = load_package()
        with unittest.mock.patch.dict(os.environ, {"GIT_CONFIG_PARAMETERS": "'core.hookspath=dyad/hooks'",
                                                   "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.autocrlf",
                                                   "GIT_CONFIG_VALUE_0": "false"}):
            env, raw = pkg.suite_env(), {**dyadlib.git_env()}
        self.assertNotIn("GIT_CONFIG_PARAMETERS", env)
        self.assertEqual((env["GIT_CONFIG_KEY_0"], env["GIT_CONFIG_KEY_1"]), ("core.autocrlf", "commit.gpgsign"))
        with tempfile.TemporaryDirectory() as d:
            run = lambda e, *a: subprocess.run(["git", *a], cwd=d, env=e, capture_output=True, text=True)
            run(env, "init", "-q")
            hook = Path(d) / "dyad" / "hooks" / "pre-commit"
            hook.parent.mkdir(parents=True); hook.write_text("#!/bin/sh\nexit 1\n"); hook.chmod(0o755)
            who = ("-c", "user.name=t", "-c", "user.email=t@t")
            self.assertNotEqual(run(raw, *who, "commit", "-q", "--allow-empty", "-m", "raw").returncode, 0)
            self.assertEqual(run(env, *who, "commit", "-q", "--allow-empty", "-m", "suite").returncode, 0)

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
    root, a target) runs with `env=suite_env()`, unless PY_ALLOWED names the env it runs in and why (the `--at`
    evidence child, #448); every other site is a git call the runner makes for itself,
    listed here with why it may inherit `os.environ` — so a new spawn site fails until it is judged."""
    SPAWN = {"run", "Popen", "check_output", "check_call", "call", "system", "popen", "execv", "execve", "execvp",
             "execvpe", "execl", "execle", "execlp", "execlpe", "spawnv", "spawnve", "spawnl", "spawnle", "posix_spawn"}
    GIT_ALLOWED = {   # enclosing function -> why its git call(s) run with the parent's environment (core_extra left it in #353: it reads through distribute.files)
        "<module>": "REPO discovery; strips the hook's GIT_DIR itself (#142) so --show-toplevel finds the true root",
        "tracked_files": "ls-files of the repo the runner judges; a hook's GIT_DIR names that same repo",
        "pushed_refs": "reads the refs the hook is pushing, in the repo the hook runs for (#194)",
        "done_head_refusals": "rev-parse, cat-file and merge-base of the ledger's refs and the heads a pushed ref "
                              "replaces, in the repo the hook runs for (#495); no write",
        "cmd_guards": "rev-parse of base and HEAD in the repo being pushed; no write",
        "cmd_pr": "rev-parse of the PR's refs in the repo judged; no write",
        "cmd_evidence": "head sha, tree hash and status of the head being evidenced; no write",
        "code_digest": "ls-tree of another repository's tree, when a caller names one (#619 P1, the audit watermark); no write",
        "cmd_dwork": "fetches origin/main into the operator's own repo before allocating an id (Rule-16)",
        "landing_refusal": "cat-file, rev-parse and merge-base of the head a `Y done` names in the operator's own "
                           "repo: the close's landing test (#202), moved out of cmd_dwork by #439; no write",
        "_git": "the suite memo's reads (status, trees, tags, common dir, merge-base) of the repo judged, and the "
                "evidence store's common dir (#476), under dyadlib.git_env() so a hook's GIT_VARS never redirect "
                "them; no write (#162)",
        "cmd_evidence_at": "rev-parse of the head asked for, under dyadlib.git_env(); no write (#448)",
        "corroborate_git": "init, add and commit of `check --corroborate`'s own scratch repo under a temp dir, under "
                           "corroborate_env(); never the repo judged (#564)",
        "checkout_snapshot": "status of the live checkout before and after the suite, under dyadlib.git_env(); no write "
                             "(the cleanliness fence, #552)",
        "evidence_in_worktree": "rev-parse of the common dir, then `worktree add --detach` and `worktree remove`/`prune` "
                                "of its own dyad-evidence-* worktree, under dyadlib.git_env(); the caller's checkout, "
                                "HEAD and index are never written (#448, shared with the baseline by #476)",
    }
    # enclosing function -> the env a python child that is not a test child runs in, and why: the `--at` child is
    # `check --evidence` itself, so it must run the suite whenever the caller would, which suite_env() forbids
    PY_ALLOWED = {
        "cmd_evidence_at": ("evidence_env", "the evidence block of another head, run by that tree's own runner; "
                                            "GIT_VARS dropped, DYAD_NO_NESTED_TESTS the caller's (#448)"),
        "corroborate_py": ("corroborate_env", "`check --corroborate`'s steps, what hosted CI on main ran; the suite runs "
                                              "unless an evidenced head's code equals the landed code (#564)"),
        "evidence_baseline_compute": ("baseline_env", "origin/main's `check` for its warn kinds, run by that tree's own "
                                                      "runner; GIT_VARS dropped and DYAD_NO_NESTED_TESTS set: never the suite (#476)"),
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
                want = self.PY_ALLOWED.get(fn, ("suite_env",))[0]
                if not (isinstance(env, ast.Call) and ast.unparse(env.func).endswith(want)):
                    problems.append(f"l.{line} {fn}: python child without env={want}()")
            elif head == "'git'":
                git_fns.add(fn)
                if fn not in self.GIT_ALLOWED:
                    problems.append(f"l.{line} {fn}: git call not listed in GIT_ALLOWED")
            else:
                problems.append(f"l.{line} {fn}: unclassified spawn {ast.unparse(call)[:80]}")
        self.assertEqual(problems, [])
        # #326: one spawn site, not two — `check_rule_12` now goes through `run_suite`, which is what
        # lets the temp-root sweep cover the push gate and the evidence run as well as `--tests`.
        self.assertGreaterEqual(len(python), 1, "run_suite spawns the suite")
        self.assertEqual(set(self.GIT_ALLOWED) - git_fns, set(), "stale GIT_ALLOWED entry")

class EvidenceAtTests(unittest.TestCase):
    """d-work #448 (child C2 of #443): `check --evidence --at <rev>` prints the evidence block of `<rev>`, computed
    by that tree's own runner in a detached worktree under the git common dir, removed afterwards; the caller's
    checkout, HEAD and index are untouched. The child runs under the caller's DYAD_NO_NESTED_TESTS (`env()` sets
    it), so these cases run the guards and skip the suite, as `test_evidence_block_shape_and_hash` does in-process."""
    def git(self, d, *a):
        return subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True,
                              env=dyadlib.git_env()).stdout
    def at(self, d, rev, *extra):
        return subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--evidence", "--at", rev, *extra],
                              cwd=d, capture_output=True, text=True, env=env())
    def snapshot(self, d):
        """What a run must leave as it was: HEAD, the index's entries, the status, the files and the worktrees."""
        return (self.git(d, "rev-parse", "HEAD"), self.git(d, "ls-files", "-s"), self.git(d, "diff", "--cached"),
                self.git(d, "status", "--porcelain=v1", "-uall"), (d / "note.md").read_text(), (d / "stray.txt").read_text(),
                self.git(d, "worktree", "list", "--porcelain"))
    def leftovers(self, d):
        common = Path(self.git(d, "rev-parse", "--path-format=absolute", "--git-common-dir").strip())
        return sorted(p.name for p in common.glob("dyad-evidence-*")) + sorted(p.name for p in (common / "worktrees").glob("*"))
    def fixture(self):
        """A scratch install with a second commit, so HEAD~1 is a head other than HEAD, and a caller's checkout
        carrying a staged change and an untracked file."""
        d = scratch_install(with_craft=False)
        (d / "note.md").write_text("one\n"); self.git(d, "add", "note.md")
        self.git(d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-qm", "two")
        (d / "note.md").write_text("staged\n"); self.git(d, "add", "note.md")
        (d / "stray.txt").write_text("untracked\n")
        return d
    _full = None
    def full_at_head_1(self):
        """One full `--at HEAD~1` run over one fixture, shared by the tests that only read it (d-work #563 C3): (repo,
        target, tree, the run, the snapshot before, the snapshot after, the leftovers after), all taken at the run."""
        cls = type(self)
        if cls._full is None:
            d = self.fixture()
            target = self.git(d, "rev-parse", "HEAD~1").strip(); tree = self.git(d, "rev-parse", "HEAD~1^{tree}").strip()
            before = self.snapshot(d)
            r = self.at(d, "HEAD~1")
            cls._full = (d, target, tree, r, before, self.snapshot(d), self.leftovers(d))
        return cls._full
    def test_a_head_other_than_HEAD_is_evidenced_and_the_checkout_untouched(self):
        d, target, tree, r, before, after, leftovers = self.full_at_head_1()
        lines = r.stdout.splitlines()
        self.assertEqual(lines[:3], [f"head={target}", f"tree={tree}", "dirty=no"], r.stdout + r.stderr)
        self.assertTrue(any("[guards] infra/containment" in l for l in lines), r.stdout)
        self.assertEqual(lines[-1], "evidence-sha256=" + load_package().evidence_sha256(lines[:-1]))   # the block's own form
        self.assertEqual(after, before)                     # files, HEAD, index, status and worktrees as they were
        self.assertEqual(leftovers, [])                     # the worktree and git's record of it are gone
        self.assertNotIn("warn [evidence]", r.stderr)
    def test_b_the_worktree_is_removed_when_the_child_fails(self):
        d = self.fixture()
        empty = self.git(d, "hash-object", "-t", "tree", "/dev/null").strip()
        orphan = self.git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit-tree", empty, "-m", "no runner").strip()
        before = self.snapshot(d)
        r = self.at(d, orphan)                               # a tree with no dyad/scripts/package.py: the child fails
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.snapshot(d), before)
        self.assertEqual(self.leftovers(d), [])
    def test_c_a_rev_that_names_no_commit_is_refused_with_one_line(self):
        pkg = load_package()
        for rev in ("no-such-rev-448", None, "--help", "HEAD^{tree}"):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = pkg.cmd_evidence_at(rev)
            self.assertEqual(rc, 2, rev)
            self.assertEqual(len(buf.getvalue().splitlines()), 1, buf.getvalue())
            self.assertRegex(buf.getvalue(), r"^FAIL \[evidence\] --at .*: not a commit in this repository$")
    def test_d_the_child_env_drops_git_vars_and_keeps_the_callers_nesting(self):
        pkg = load_package()
        hook = {"GIT_DIR": "/elsewhere/.git", "GIT_WORK_TREE": "/elsewhere", "GIT_INDEX_FILE": "/x", "GIT_COMMON_DIR": "/y"}
        with unittest.mock.patch.dict(os.environ, {**hook, "DYAD_NO_NESTED_TESTS": "1"}):
            e = pkg.evidence_env()
        self.assertFalse(set(dyadlib.GIT_VARS) & set(e)); self.assertEqual(e["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertEqual(e["DYAD_NO_NESTED_TESTS"], "1")
        with unittest.mock.patch.dict(os.environ, {}):
            os.environ.pop("DYAD_NO_NESTED_TESTS", None)
            self.assertNotIn("DYAD_NO_NESTED_TESTS", pkg.evidence_env())   # a real run: the child runs the suite

    def test_e_brief_composes_with_at_and_stores_the_childs_block(self):
        """#476: `--brief --at <rev>` reads the child's full block short in the parent, with the full form's hash,
        and stores the full block, which `--show` prints back by a 12-hex prefix."""
        d, target, _, full, _, _, _ = self.full_at_head_1()   # the full form's run, shared (#563 C3)
        brief = self.at(d, "HEAD~1", "--brief")
        self.assertEqual(brief.returncode, full.returncode, brief.stdout + brief.stderr)
        b = brief.stdout.splitlines()
        self.assertEqual(b[0], f"head={target}"); self.assertRegex(b[3], r"^code=[0-9a-f]{64}$")
        self.assertRegex(b[4], r"^counts: ok=\d+ warn=\d+ skip=\d+ fail=\d+")
        self.assertEqual(b[-1], full.stdout.splitlines()[-1])        # the same evidence-sha256 as the full form
        self.assertTrue(b[-2].startswith("stored: ") and b[-2].endswith(b[-1].split("=")[1] + ".txt"), b[-2])
        show = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--evidence", "--show",
                               b[-1].split("=")[1][:12]], cwd=d, capture_output=True, text=True, env=env())
        self.assertEqual((show.returncode, show.stdout), (0, full.stdout))
        self.assertEqual(self.leftovers(d), [])

class EvidenceBriefTests(unittest.TestCase):
    """d-work #476 (child C3 of #473): `check --evidence --brief`, the store and `--show`, on fixed blocks — no
    suite and no guard runs; the store is pointed at a scratch directory."""
    BODY = ["head=" + "a" * 40, "tree=" + "b" * 40, "dirty=no",
            "ok   [invariant] dyadlib (3)", "ok   [Rule-11]", "FAIL [Rule-12] core suite: 1 failure",
            "     [Rule-12] test_x (dyad.tests.test_y) ... FAIL", "ok   [Rule-12] crafts/sysadmin",
            "     [Rule-12] a detail of an ok line", "warn [agent/provenance] row 12 unrecorded",
            "skip [guards] sysadmin/events: no store", "ok   [guards] infra/containment commits"]
    def setUp(self):
        self.pkg = load_package()
        self.dir = Path(tempfile.mkdtemp()) / self.pkg.EVIDENCE_STORE
        self.addCleanup(shutil.rmtree, self.dir.parent, True)
        patcher = unittest.mock.patch.object(self.pkg, "evidence_dir", return_value=self.dir)
        patcher.start(); self.addCleanup(patcher.stop)
    def block(self, body=None):
        body = list(self.BODY if body is None else body)
        return body + ["evidence-sha256=" + self.pkg.evidence_sha256(body)]
    def run_out(self, fn, *a):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = fn(*a)
        return rc, out.getvalue(), err.getvalue()
    def test_counts_classify_by_leading_token_and_skip_continuations(self):
        self.assertEqual(self.pkg.evidence_counts(self.block()), {"ok": 4, "warn": 1, "skip": 1, "fail": 1, "other": 0})
        self.assertEqual(self.pkg.evidence_counts(["huh?"])["other"], 1)   # an unknown line is counted, never dropped
    def test_brief_keeps_header_non_ok_lines_in_order_and_the_full_hash(self):
        block = self.block()
        self.assertEqual(self.pkg.evidence_brief(block, "/s/x.txt"), [
            "head=" + "a" * 40, "tree=" + "b" * 40, "dirty=no",
            "counts: ok=4 warn=1 skip=1 fail=1",
            "warn [evidence] no baseline for origin/main: warnings not folded (not looked up)",
            "FAIL [Rule-12] core suite: 1 failure", "     [Rule-12] test_x (dyad.tests.test_y) ... FAIL",
            "warn [agent/provenance] row 12 unrecorded", "skip [guards] sysadmin/events: no store",
            "stored: /s/x.txt", block[-1]])
        self.assertEqual(self.pkg.evidence_brief(block)[-2], "stored: none")
        self.assertEqual(self.pkg.evidence_brief(block[:-1])[-1], block[-1])   # computed over the full block, either way
        self.assertIn("counts: ok=0 warn=0 skip=0 fail=0 other=1", self.pkg.evidence_brief(self.block(["head=x", "huh?"])))
    def test_store_then_show_by_full_sha_and_by_a_12_hex_prefix(self):
        block = self.block(); sha = block[-1].split("=")[1]
        path = self.pkg.evidence_store(block)
        self.assertEqual(path, self.dir / f"{sha}.txt")
        for key in (sha, sha[:12], sha[:12].upper()):
            rc, out, _ = self.run_out(self.pkg.cmd_evidence_show, key)
            self.assertEqual((rc, out.splitlines()), (0, block), key)
    def test_show_refuses_short_ambiguous_missing_and_non_hex(self):
        self.pkg.evidence_store(self.block())
        twin = self.block(self.BODY + ["ok   [x]"]); sha = twin[-1].split("=")[1]
        (self.dir / f"{sha[:12]}{'0' * 52}.txt").write_text("x\n")   # a second block sharing twin's 12-hex prefix
        self.pkg.evidence_store(twin)
        for key, why in ((sha[:11], "at least 12 hex"), (None, "at least 12 hex"), ("z" * 12, "at least 12 hex"),
                         (sha[:12], "ambiguous (2 stored blocks)"), ("f" * 64, "no stored evidence block")):
            rc, out, _ = self.run_out(self.pkg.cmd_evidence_show, key)
            self.assertEqual(rc, 2, key); self.assertEqual(len(out.splitlines()), 1, out)
            self.assertRegex(out, r"^FAIL \[evidence\] --show "); self.assertIn(why, out)
    def test_a_failed_store_warns_and_never_raises(self):
        self.dir.parent.joinpath(self.pkg.EVIDENCE_STORE).write_text("a file where the store's directory goes")
        rc = self.run_out(lambda: self.pkg.evidence_store(self.block()))
        self.assertIsNone(rc[0]); self.assertRegex(rc[2], r"^warn \[evidence\] block not stored: ")
        self.assertIsNone(self.run_out(lambda: self.pkg.evidence_store(self.BODY))[0])   # no sha line: not a block
    def test_cmd_evidence_brief_prints_brief_stores_full_and_keeps_the_exit_code(self):
        """In-process, with `cmd_check`/`cmd_guards` replaced by fixed lines: the brief and the full form share the
        hash and the exit code, and both store the full block."""
        lines = self.BODY[3:]
        old = self.pkg.REPO; self.addCleanup(setattr, self.pkg, "REPO", old)
        self.pkg.REPO = hermetic_clone()              # #529: tags under the test's control, not the live repo's
        def check(): print(*lines[:5], sep="\n"); return 1
        def guards(): print(*lines[5:], sep="\n"); return 0
        with unittest.mock.patch.object(self.pkg, "cmd_check", check), unittest.mock.patch.object(self.pkg, "cmd_guards", guards), \
             unittest.mock.patch.object(self.pkg, "evidence_baseline", lambda block: (set(), "origin/main x (test)")):
            rc_full, full, _ = self.run_out(self.pkg.cmd_evidence)
            rc_brief, brief, _ = self.run_out(self.pkg.cmd_evidence, True)
        full, brief = full.splitlines(), brief.splitlines()
        self.assertEqual((rc_full, rc_brief), (1, 1))
        self.assertEqual(full[4:-1], lines); self.assertEqual(brief[-1], full[-1])
        self.assertTrue(full[3].startswith("code=")); self.assertEqual(brief[3], full[3])   # #562: the code digest
        self.assertEqual(brief[4], "counts: ok=4 warn=1 skip=1 fail=1")
        stored = self.dir / (full[-1].split("=")[1] + ".txt")
        self.assertEqual(stored.read_text().splitlines(), full); self.assertEqual(brief[-2], f"stored: {stored}")
        self.assertEqual(brief[5], "baseline: origin/main x (test)")
        self.assertIn("warn [agent/provenance] row 12 unrecorded", brief)    # a kind main lacks: verbatim

    # ---- folding against origin/main's warn kinds (#476, the extension the Operator approved)
    PLANS = ["warn [agent/plans] 43.md: never mentions `intent as read` (dyadlib.PLAN_PARTS)",
             "warn [agent/plans] 454.md: never mentions `mutation` (dyadlib.PLAN_PARTS)"]
    def test_warn_kind_normalizes_ids_quotes_paths_and_numbers_and_keeps_the_guard(self):
        k = self.pkg.warn_kind
        self.assertEqual(k(self.PLANS[0]), "warn [agent/plans] <path>: never mentions <q> (dyadlib.PLAN_PARTS)")
        self.assertEqual(k(self.PLANS[0]), k(self.PLANS[1]))
        self.assertEqual(k("warn [agent/provenance] 451.md: entry 3 carries a 40-hex string (commit sha or token)"),
                         "warn [agent/provenance] <path>: entry <n> carries a <n>-hex string (commit sha or token)")
        self.assertEqual(k(f"warn [x/y] head {'ab12' * 10} and {'cd34' * 16} at cab-10-cbc041dd"),
                         "warn [x/y] head <sha> and <sha> at cab-<n>-<sha>")
        self.assertEqual(k("warn [x/y] mentions 'the Agent', 'counter-prompt' — the Agent's process"),
                         "warn [x/y] mentions <q> — the Agent's process")          # a run of one placeholder is one
        self.assertEqual(k("warn [s/i] crafts/a: 2 module(s): a/b.py, c/d.py"), k("warn [s/i] crafts/b: 5 module(s): e.py"))
        self.assertEqual(k("warn [c/c] floor dyad-operator>=0.10.0"), "warn [c/c] floor dyad-operator>=<n>")
        self.assertNotEqual(k("warn [agent/plans] 3.md: x"), k("warn [agent/rows] 3.md: x"))   # another guard, another kind
        self.assertNotEqual(k("warn [x/y] names no intent"), k("warn [x/y] names no mutation"))   # words are kept
        self.assertIsNone(k("ok   [agent/plans]")); self.assertIsNone(k("FAIL [agent/plans] 3.md: x"))
    def test_the_guards_prefix_maps_to_the_guard_label(self):
        g = "warn [guards] agent/plans 43.md: never mentions `intent as read` (dyadlib.PLAN_PARTS)"
        self.assertEqual(self.pkg.warn_unprefix(g), self.PLANS[0])
        self.assertEqual(self.pkg.warn_kind(g), self.pkg.warn_kind(self.PLANS[0]))
        self.assertEqual(self.pkg.warn_guard(g), "agent/plans")
        self.assertEqual(self.pkg.warn_unprefix("warn [guards] agent/plans"), "warn [agent/plans]")
        self.assertEqual(self.pkg.warn_unprefix("ok   [guards] agent/plans"), "ok   [guards] agent/plans")
    def fold_body(self):
        return ["head=" + "a" * 40, "tree=" + "b" * 40, "dirty=no", "ok   [Rule-11]", *self.PLANS,
                "warn [agent/plans] 7.md: names no intent (Rule-15 phase 1)", "     a continuation of a new warning",
                "FAIL [x/y] broken", "ok   [guards] x/y",
                *(l.replace("warn [agent/plans]", "warn [guards] agent/plans") for l in self.PLANS),
                "warn [guards] agent/plans 7.md: names no intent (Rule-15 phase 1)", "     a continuation of a new warning",
                "skip [guards] z: none"]
    def test_brief_folds_standing_warnings_per_guard_and_prints_a_new_kind_once(self):
        block = self.block(self.fold_body())
        kinds = {self.pkg.warn_kind(self.PLANS[0])}
        out = self.pkg.evidence_brief(block, "/s/x.txt", (kinds, "origin/main 0123456789ab (stored)"))
        self.assertEqual(out, [*block[:3], "counts: ok=2 warn=6 skip=1 fail=1", "baseline: origin/main 0123456789ab (stored)",
                               "warn [agent/plans] 2 standing (4 lines)",                    # deduped: 2 warnings, 4 lines
                               "warn [agent/plans] 7.md: names no intent (Rule-15 phase 1)",  # a new kind: verbatim, once
                               "     a continuation of a new warning", "FAIL [x/y] broken", "skip [guards] z: none",
                               "stored: /s/x.txt", block[-1]])
        self.assertEqual(out[-1], "evidence-sha256=" + self.pkg.evidence_sha256(block[:-1]))   # still the full block's
    def test_no_baseline_prints_every_warning_and_one_line_saying_why(self):
        block = self.block(self.fold_body())
        out = self.pkg.evidence_brief(block, None, (None, "origin/main does not resolve"))
        self.assertEqual(out[4], "warn [evidence] no baseline for origin/main: warnings not folded (origin/main does not resolve)")
        self.assertEqual([l for l in out if l.startswith("warn [") and "evidence" not in l],
                         [l for l in block if l.startswith("warn [")])                         # every warning, verbatim
        self.assertEqual(out[-1], block[-1])
    def baseline_repo(self):
        """A scratch repo with one commit and `origin/main` pointing at it (an update-ref, no remote needed); REPO and
        the store pointed there. Returns the main sha."""
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        git = lambda *a: subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True,
                                        env=dyadlib.git_env()).stdout.strip()
        git("init", "-q"); (d / "f").write_text("x\n"); git("add", "f")
        git("-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-qm", "one")
        sha = git("rev-parse", "HEAD"); git("update-ref", "refs/remotes/origin/main", sha)
        p = unittest.mock.patch.object(self.pkg, "REPO", d); p.start(); self.addCleanup(p.stop)
        return sha
    def test_baseline_from_a_stored_block_then_from_the_cache_never_computed(self):
        sha = self.baseline_repo()
        mine = self.block(["head=" + "c" * 40, "tree=t", "dirty=no", *self.PLANS])
        def compute(_): raise AssertionError("computed although a stored block or the cache had the kinds")
        with unittest.mock.patch.object(self.pkg, "evidence_baseline_compute", compute):
            self.assertEqual(self.pkg.evidence_baseline(mine), (None, "AssertionError: computed although a stored block "
                                                                      "or the cache had the kinds"))   # nothing stored yet
            main = self.block([f"head={sha}", "tree=t", "dirty=no", self.PLANS[0]])
            self.pkg.evidence_store(self.block([f"head={sha}", "tree=t", "dirty=yes", "warn [q/r] dirty only"]))  # not used
            self.pkg.evidence_store(main)
            kinds, src = self.pkg.evidence_baseline(mine)
            self.assertEqual((kinds, src), ({self.pkg.warn_kind(self.PLANS[0])}, f"origin/main {sha[:12]} (stored)"))
            cache = self.dir / f"baseline-{sha}.kinds"
            self.assertTrue(cache.is_file())
            (self.dir / (main[-1].split("=")[1] + ".txt")).unlink()                # the stored block gone: the cache serves
            self.assertEqual(self.pkg.evidence_baseline(mine), (kinds, f"origin/main {sha[:12]} (cached)"))
            self.assertEqual(self.pkg.evidence_baseline(main)[1], f"origin/main {sha[:12]} (self)")   # main itself
    def test_a_cached_kinds_file_is_used_without_recomputation_and_a_computed_set_is_cached(self):
        sha = self.baseline_repo()
        mine = self.block(["head=" + "c" * 40, "tree=t", "dirty=no", *self.PLANS])
        calls = []
        def compute(s): calls.append(s); return {"warn [a/b] <n>"}
        with unittest.mock.patch.object(self.pkg, "evidence_baseline_compute", compute):
            self.assertEqual(self.pkg.evidence_baseline(mine), ({"warn [a/b] <n>"}, f"origin/main {sha[:12]} (computed)"))
            self.assertEqual(self.pkg.evidence_baseline(mine), ({"warn [a/b] <n>"}, f"origin/main {sha[:12]} (cached)"))
        self.assertEqual(calls, [sha])                                                  # once, then the cache
        cache = self.dir / f"baseline-{sha}.kinds"
        cache.write_text(f"# warn_kind v0 {sha}\nwarn [old] x\n")                       # another rule's cache: a miss
        with unittest.mock.patch.object(self.pkg, "evidence_baseline_compute", lambda s: calls.append(s) or set()):
            self.assertEqual(self.pkg.evidence_baseline(mine), (set(), f"origin/main {sha[:12]} (computed)"))
        self.assertEqual(len(calls), 2)
    def test_a_baseline_that_cannot_be_had_never_raises(self):
        self.baseline_repo()
        mine = self.block(["head=" + "c" * 40])
        with unittest.mock.patch.object(self.pkg, "evidence_baseline_compute", lambda s: (_ for _ in ()).throw(RuntimeError("offline"))):
            self.assertEqual(self.pkg.evidence_baseline(mine), (None, "RuntimeError: offline"))
        with unittest.mock.patch.object(self.pkg, "_git", lambda *a: None):
            self.assertEqual(self.pkg.evidence_baseline(mine), (None, "origin/main does not resolve"))

class SuiteMemoTests(unittest.TestCase):
    """#162 (d-work #199 N2): the suite memo. Written after a full, all-roots pass on a clean tree, under the
    git common dir; read by `suite_gate` only under `pre_push`; never by `check --evidence` nor by
    `check --guards` without `--pre-push`. Every case runs over a scratch repo with `pkg.REPO` pointed at it
    and `test_suites` pinned to one root inside it, so the key's `roots` part is the scratch repo's."""
    PARTS = {"tree", "code", "executable", "python", "git", "roots", "env", "tags", "local", "date"}

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
        miss = lambda *k: (f"     [Rule-12] suite memo miss: {', '.join(k)} differ{'s' if len(k) == 1 else ''} "
                           "from the nearest pass on this checkout")   # d-work #474: the part that missed is named
        self.assertEqual(gate(), (True, "     [Rule-12] suite memo miss: no pass recorded on this checkout"))
        write(); self.assertFalse(gate()[0])                                        # the control: a hit
        git("tag", "v9.9.9"); self.assertEqual(gate(), (True, miss("tags")))                # tags (check_drift reads them)
        write(); self.assertFalse(gate()[0])
        os.environ["DYAD_HOST_ZONE"] = "infra"; self.assertEqual(gate(), (True, miss("env:DYAD_HOST_ZONE")))   # an env knob
        write(); self.assertFalse(gate()[0])
        with unittest.mock.patch.object(self.pkg, "utc_date", lambda: "2999-01-01"):
            self.assertEqual(gate(), (True, miss("date")))                                  # the UTC day
        with unittest.mock.patch.object(self.pkg, "test_suites", lambda: [d / "dyad" / "tests", d / "crafts" / "x" / "tests"]):
            self.assertEqual(gate(), (True, miss("roots")))                                  # the roots
        with unittest.mock.patch.object(sys, "executable", sys.executable + "x"):
            self.assertEqual(gate(), (True, miss("executable")))                                  # the interpreter
        with unittest.mock.patch.object(sys, "version", sys.version + "x"):
            self.assertEqual(gate(), (True, miss("python")))
        real = self.pkg._git
        with unittest.mock.patch.object(self.pkg, "_git", lambda *a: "git version 0.0.0" if a == ("--version",) else real(*a)):
            self.assertEqual(gate(), (True, miss("git")))                                  # git
        inst = os.environ.get("DYAD_INSTANCE", "agent-corpus")
        (d / inst / "provenance_legacy.local.txt").write_text("1 0 predates\n")
        self.assertEqual(self.pkg.suite_memo_parts()["tree"], git("rev-parse", "HEAD^{tree}"))   # ignored: still clean
        self.assertEqual(gate(), (True, miss("local")))                             # instance-local data git ignores
        write(); self.assertFalse(gate()[0])
        (d / "code.txt").write_text("changed\n"); git("commit", "-qam", "tree")
        self.assertEqual(gate(), (True, miss("tree", "code")))                              # the tree and its code (#562)

    def test_dirty_tree_partial_run_or_failure_never_writes(self):
        d, seed, git = self.repo()
        ok = lambda *a, **k: (0, ["Ran 1 test", "OK"], "")
        with unittest.mock.patch.object(self.pkg, "run_suite", ok), contextlib.redirect_stdout(io.StringIO()):
            (d / "stray.txt").write_text("untracked\n")                  # dirty: an untracked file counts
            self.assertIsNone(self.pkg.suite_memo_parts())
            self.assertEqual(self.pkg.cmd_tests(), 0)
            self.assertEqual(self.memos(d), [])
            (d / "stray.txt").unlink()
            (d / "dyad" / "tests").mkdir(parents=True, exist_ok=True)   # #592 R-a: a dotted target's first part must import
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
        self.assertEqual(gate(), (True, "     [Rule-12] suite memo miss: no pass recorded on this checkout"))   # two-dot main..HEAD carries main's code
        self.assertEqual(self.pkg.suite_gate("main", "HEAD", pre_push=False), (True, None))
        self.pkg.suite_memo_write(self.pkg.suite_memo_parts(fork))      # the merge-base's tree passed
        tree = git("rev-parse", f"{fork}^{{tree}}")
        self.assertEqual(gate(), (False, f"skip [guards] Rule-12 suite: main...HEAD is ledger-only and its merge-base tree "
                                         f"{tree[:9]} already passed on this checkout (d-work #162)"))
        self.assertEqual(self.pkg.suite_gate("main", "HEAD", pre_push=False), (True, None))   # never without --pre-push
        (d / "code.txt").write_text("branch code\n"); git("commit", "-qam", "not ledger")
        self.assertEqual(gate(), (True, "     [Rule-12] suite memo miss: tree, code differ from the nearest pass on this checkout"))                          # one non-ledger commit: the clause is off

    def test_events_branch_behind_main_skips_only_on_a_memoized_merge_base(self):
        """#438: the memo's second clause holds for an events-only branch as for a ledger-only one, each class
        read whole."""
        d, seed, git = self.repo()
        for k in ("DYAD_HOST", "DYAD_RUNBOOKS"):
            os.environ.pop(k, None)
        fork = git("rev-parse", "HEAD")
        git("switch", "-qc", "events")
        ev = d / "workstation-corpus" / "runbooks" / "events"; ev.mkdir(parents=True)
        (ev / "sessions.jsonl").write_text('{"a": 1}\n'); git("add", "-A"); git("commit", "-qm", "events")
        git("switch", "-q", "main")
        (d / "code.txt").write_text("main moved\n"); git("commit", "-qam", "main moves")
        git("switch", "-q", "events")
        gate = lambda: self.pkg.suite_gate("main", "HEAD", pre_push=True)
        self.assertEqual(gate(), (True, "     [Rule-12] suite memo miss: no pass recorded on this checkout"))   # two-dot main..HEAD carries main's code
        self.pkg.suite_memo_write(self.pkg.suite_memo_parts(fork))      # the merge-base's tree passed
        tree = git("rev-parse", f"{fork}^{{tree}}")
        self.assertEqual(gate(), (False, f"skip [guards] Rule-12 suite: main...HEAD is events-only and its merge-base tree "
                                         f"{tree[:9]} already passed on this checkout (d-work #162)"))
        self.assertEqual(self.pkg.suite_gate("main", "HEAD", pre_push=False), (True, None))   # never without --pre-push
        inst = os.environ.get("DYAD_INSTANCE", "agent-corpus")
        (d / inst / "d-work" / "rows" / "2.md").write_text("id: 2\n"); git("add", "-A"); git("commit", "-qm", "a ledger commit")
        tree = git("rev-parse", "HEAD^{tree}")                  # events then ledger: neither class, so the range clause is
        self.assertEqual(gate(), (False, f"skip [guards] Rule-12 suite: tree {tree[:9]}'s code equals tree "   # off; the
                                         f"{git('rev-parse', f'{fork}^{{tree}}')[:9]}'s, which already passed on this "   # code
                                         "checkout; they differ only under the ledger or the events (d-work #562)"))   # clause (#562)
        (d / "code.txt").write_text("branch code\n"); git("commit", "-qam", "code")
        self.assertEqual(gate(), (True, "     [Rule-12] suite memo miss: tree, code differ from the nearest pass on this checkout"))

class CodeKeyedSkipTests(unittest.TestCase):
    """d-work #562 (b): the pre-push gate skips the suite when the pushed code was already judged — (b1) a recorded pass
    on this checkout with the same code digest beside another ledger, (b2) the code of a head an operative `Y done` on
    the base names, whose evidence passed (Rule-2 Binding). Code that differs runs, and `check --evidence` and
    `check --guards` without `--pre-push` never skip."""
    def setUp(self):
        SuiteMemoTests.setUp(self)

    def repo(self):
        d, seed, git = SuiteMemoTests.repo(self)
        self.inst = os.environ.get("DYAD_INSTANCE", "agent-corpus")
        return d, seed, git

    def row(self, d, git, disposed):
        (d / self.inst / "d-work" / "rows" / "1.md").write_text(
            f"id: 1\ntitle: one\nopened: 2026-11-03\nstate: planned\ndisposed: {disposed}\nrefs: \n")
        git("add", "-A"); git("commit", "-qm", "ledger: #1")

    def test_code_digest_ignores_the_ledger_and_the_events_only(self):
        d, seed, git = self.repo()
        before = self.pkg.code_digest()
        (d / self.inst / "d-work" / "rows" / "2.md").write_text("id: 2\n"); git("add", "-A"); git("commit", "-qm", "row")
        self.assertEqual(self.pkg.code_digest(), before)
        (d / "code.txt").write_text("other\n"); git("commit", "-qam", "code")
        self.assertNotEqual(self.pkg.code_digest(), before)

    def test_code_digest_prunes_more_and_reads_another_repo_when_asked(self):
        """#619 P1: an optional predicate prunes more paths, and `repo` names the repository read; callers pass neither."""
        d, seed, git = self.repo()
        before, pruned = self.pkg.code_digest(), self.pkg.code_digest(prune=lambda p: p.startswith("dated/"))
        self.assertEqual(before, pruned)                                             # nothing under dated/ yet
        (d / "dated").mkdir(); (d / "dated" / "r.md").write_text("x\n"); git("add", "-A"); git("commit", "-qm", "dated")
        self.assertNotEqual(self.pkg.code_digest(), before)
        self.assertEqual(self.pkg.code_digest(prune=lambda p: p.startswith("dated/")), before)
        self.assertEqual(self.pkg.code_digest(repo=d), self.pkg.code_digest())
        self.assertIsNone(self.pkg.code_digest("no-such-rev", repo=d))

    def test_b1_a_ledger_drift_after_a_pass_skips_and_a_code_drift_runs(self):
        d, seed, git = self.repo()
        passed = git("rev-parse", "HEAD^{tree}")
        self.pkg.suite_memo_write(self.pkg.suite_memo_parts())          # this code passed here
        (d / self.inst / "d-work" / "rows" / "2.md").write_text("id: 2\n"); git("add", "-A"); git("commit", "-qm", "row")
        gate = lambda: self.pkg.suite_gate(seed, "HEAD", pre_push=True)   # seed..HEAD carries code: no range clause
        tree = git("rev-parse", "HEAD^{tree}")
        self.assertEqual(gate(), (False, f"skip [guards] Rule-12 suite: tree {tree[:9]}'s code equals tree {passed[:9]}'s, "
                                         "which already passed on this checkout; they differ only under the ledger or the "
                                         "events (d-work #562)"))
        self.assertEqual(self.pkg.suite_gate(seed, "HEAD", pre_push=False), (True, None))   # never without --pre-push
        (d / "code.txt").write_text("other\n"); git("commit", "-qam", "code")
        self.assertEqual(gate(), (True, "     [Rule-12] suite memo miss: tree, code differ from the nearest pass on this checkout"))

    def test_b2_code_named_by_an_operative_done_y_skips(self):
        d, seed, git = self.repo()
        git("switch", "-qc", "pr")
        (d / "code.txt").write_text("the pr\n"); git("commit", "-qam", "pr")
        pr = git("rev-parse", "HEAD")
        git("switch", "-q", "main")
        self.row(d, git, f"2026-11-03 Y plan; 2026-11-03 Y done (merges PR #5 at {pr})")
        git("merge", "-q", "--no-ff", "-m", "Merge PR #5", pr)            # the cut: the PR's code beside the new ledger
        line = (f"skip [guards] Rule-12 suite: the pushed code equals PR #5's head {pr[:12]}, named by row #1's operative "
                "Y done, whose evidence passed every root (Rule-2 Binding; d-work #562)")
        self.assertEqual(self.pkg.suite_gate("main~1", "HEAD", pre_push=True), (False, line))
        self.assertEqual(self.pkg.suite_gate("main~1", "HEAD", pre_push=False), (True, None))   # never without --pre-push
        (d / "code.txt").write_text("changed after the Y\n"); git("commit", "-qam", "more code")
        self.assertTrue(self.pkg.suite_gate("main~2", "HEAD", pre_push=True)[0])      # other code: the suite runs

    def test_corroboration_skips_the_suite_only_for_an_evidenced_head(self):
        """#564 E2: `check --corroborate` skips the suite when the landed code equals a merged PR head a Y done names."""
        d, seed, git = self.repo()
        git("switch", "-qc", "pr")
        (d / "code.txt").write_text("the pr\n"); git("commit", "-qam", "pr")
        pr = git("rev-parse", "HEAD")
        git("switch", "-q", "main")
        self.row(d, git, f"2026-11-03 Y plan; 2026-11-03 Y done (merges PR #5 at {pr})")
        before = git("rev-parse", "HEAD")
        git("merge", "-q", "--no-ff", "-m", "Merge PR #5", pr)
        line = self.pkg.corroborate_suite_skip(before, "HEAD")
        self.assertIn(f"the landed code equals PR #5's head {pr[:12]}", line)
        self.assertIsNone(self.pkg.corroborate_suite_skip(None, "HEAD"))            # no range: the suite runs
        (d / "code.txt").write_text("changed after the Y\n"); git("commit", "-qam", "more code")
        self.assertIsNone(self.pkg.corroborate_suite_skip(before, "HEAD"))          # other code: the suite runs

    def test_b2_a_void_or_absent_done_y_runs(self):
        d, seed, git = self.repo()
        git("switch", "-qc", "pr")
        (d / "code.txt").write_text("the pr\n"); git("commit", "-qam", "pr")
        pr = git("rev-parse", "HEAD")
        git("switch", "-q", "main")
        self.row(d, git, f"2026-11-03 Y plan; 2026-11-03 Y done (merges PR #5 at {pr}); 2026-11-03 N")   # revoked (#541)
        git("merge", "-q", "--no-ff", "-m", "Merge PR #5", pr)
        self.assertTrue(self.pkg.suite_gate("main~1", "HEAD", pre_push=True)[0])

    def test_evidence_never_skips_and_prints_the_code_line(self):
        d, seed, git = self.repo()
        self.pkg.suite_memo_write(self.pkg.suite_memo_parts())
        calls, reads, out = SuiteMemoTests.guards(self, "main", False, evidence=True)
        self.assertIn(("check",), calls)                                   # the suite ran, memo or not
        self.assertEqual(reads, [])
        self.assertIn(f"code={self.pkg.code_digest()}", out.splitlines()[:4])


class GateSplitTests(unittest.TestCase):
    """d-work #564: on a clerical push (every path under the ledger or the events store) the pre-push gate leaves a
    guard's state check to the sweep when the guard declares `CLERICAL_READS` and the push touches none of them; a
    push carrying code, and every run without `--pre-push`, runs them all."""
    def setUp(self):
        SuiteMemoTests.setUp(self)

    def test_clerical_paths_and_swept(self):
        d, seed, git = SuiteMemoTests.repo(self)
        inst = os.environ.get("DYAD_INSTANCE", "agent-corpus")
        base = git("rev-parse", "HEAD")
        (d / inst / "d-work" / "rows" / "2.md").write_text("id: 2\n"); git("add", "-A"); git("commit", "-qm", "row")
        ledger = git("rev-parse", "HEAD")
        self.assertEqual(self.pkg.clerical_paths(base, ledger), [f"{inst}/d-work/rows/2.md"])
        guard = type("G", (), {"CLERICAL_READS": ()}); reads_version = type("V", (), {"CLERICAL_READS": ("d-work/VERSION",)})
        self.assertTrue(self.pkg.swept(guard, self.pkg.clerical_paths(base, ledger)))
        self.assertFalse(self.pkg.swept(type("U", (), {}), self.pkg.clerical_paths(base, ledger)))   # undeclared: always runs
        self.assertFalse(self.pkg.swept(guard, None))                                                # no clerical range
        (d / inst / "d-work" / "VERSION").write_text("1\n"); git("add", "-A"); git("commit", "-qm", "version")
        self.assertFalse(self.pkg.swept(reads_version, self.pkg.clerical_paths(base, "HEAD")))       # it touches what it reads
        self.assertTrue(self.pkg.swept(reads_version, self.pkg.clerical_paths(base, ledger)))
        (d / "code.txt").write_text("more\n"); git("commit", "-qam", "code")
        self.assertIsNone(self.pkg.clerical_paths(base, "HEAD"))                                     # code: nothing swept
        self.assertIsNone(self.pkg.clerical_paths("HEAD", "HEAD"))                                   # empty range

    def test_the_declaring_guards_read_no_ledger(self):
        declared = {f"{c}/{e}" for c, e, _, _, mod, _ in self.pkg.registry() if mod is not None and hasattr(mod, "CLERICAL_READS")}
        self.assertTrue({"agent/merges", "infra/manifest", "craft/crafts", "agent/dmc", "infra/bundle"} <= declared)
        self.assertFalse(declared & {"agent/rows", "agent/provenance", "agent/plans", "agent/traces", "agent/board",
                                     "agent/inbox", "agent/references", "syseng/naming"})   # these read the ledger: never swept


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
        self.assertEqual(calls, [], out)                                     # every root skipped: the core install now records each bundled craft's row too (#201, d-work #228)
        for c in self.bundled:
            if (d / "crafts" / c / "tests").is_dir():
                self.assertIn(self.skip_line(f"crafts/{c}/tests", c), out)
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

class InstallFromTests(unittest.TestCase):
    """`dyad install <repo> --from <src>` (d-work #353, A3): the core craft from a release archive or a tree, VERSION, roots,
    hooks and bundled crafts read from the source, through the one install path; idempotent; the registry `source` names
    what was installed from (`distribute.source_name`); a source without `dyad/VERSION` is refused."""
    def run_py(self, *a):
        return subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), *a], capture_output=True, text=True)
    def test_from_archive_then_from_tree(self):
        pkg = load_package(); craft = dyadlib.load_module(PKG / "scripts" / "craft.py", "craft")
        d = SCRATCH.mkdtemp(); subprocess.run(["git", "init", "-q", str(d)], check=True)
        arch = SCRATCH.mkdtemp() / "dyad-x.tar.gz"; r = self.run_py("build", str(arch)); self.assertEqual(r.returncode, 0, r.stderr)
        r = self.run_py("install", str(d), "--from", str(arch)); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("; from dyad-x.tar.gz; run: git -C", r.stdout, r.stdout)
        row = craft.registry_rows(d)[craft.CORE_NAME]
        self.assertEqual((row["source"], row["version"], row["sha256"]), ("dyad-x.tar.gz", pkg.version(), craft.tree_sha(d, craft.CORE_NAME)))
        self.assertEqual((d / "dyad" / "VERSION").read_text(), (PKG / "VERSION").read_text())
        self.assertIn(pkg.IMPORT_LINE, (d / "CLAUDE.md").read_text().splitlines())                      # the core's hooks, from the archive's templates
        for c in pkg.bundled_crafts():
            self.assertTrue((d / "crafts" / c / "VERSION").exists(), c); self.assertIsNotNone(craft.unmodified(d, c), c)
        r = self.run_py("install", str(d), "--from", str(arch)); self.assertIn(": 0 changes;", r.stdout, r.stdout)   # idempotent
        r = self.run_py("install", str(d), "--from", str(PKG.parent)); self.assertEqual(r.returncode, 0, r.stderr)    # the same tree as a clone: only the row moves
        src = pkg.distribute.source_name(PKG.parent); self.assertRegex(src, r"^.+@.+$")
        self.assertEqual(craft.registry_rows(d)[craft.CORE_NAME]["source"], src); self.assertIn(f"; from {src}; run:", r.stdout)
        r = self.run_py("install", str(d), "--from", str(PKG.parent)); self.assertIn(": 0 changes;", r.stdout, r.stdout)
        r = self.run_py("install", str(d), "--from", str(SCRATCH.mkdtemp())); self.assertEqual(r.returncode, 2); self.assertIn("holds no dyad/VERSION", r.stderr)
        r = self.run_py("install", "--from"); self.assertNotEqual(r.returncode, 0)
        shutil.rmtree(d, ignore_errors=True)
    def test_core_extra_reads_any_tree(self):
        pkg = load_package()
        self.assertEqual(pkg.core_extra(), pkg.core_extra(pkg.REPO)); self.assertTrue(all(Path(p).name.startswith("dyad-") for p in pkg.core_extra()))
        arch = SCRATCH.mkdtemp() / "a.tar.gz"; self.run_py("build", str(arch)); root = pkg.distribute.extract(arch, SCRATCH.mkdtemp())
        self.assertEqual(pkg.core_extra(root), pkg.core_extra())                                          # an extracted release: the same hooks, by walk
        self.assertEqual(pkg.bundled_crafts(root / "dyad"), pkg.bundled_crafts())                        # read as text there, never executed

class SuiteParallelTests(unittest.TestCase):
    """d-work #475 (C2 of #473): a root's classes run as separate children, each in its own temp root, at most
    SUITE_JOBS at a time, and the root's summary is the sum of theirs in unittest's own words — so the evidence
    block's `[Rule-12]` lines are the serial run's whatever order the children finish in."""
    def root(self, files):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        r = Path(td.name) / "tests"; r.mkdir()
        for name, text in files.items():
            (r / name).write_text(text)
        return r
    # each class creates one fixed name under the temp dir, exclusively: two classes sharing a temp dir would collide
    FIXED = ("import os, tempfile, unittest\n"
             "class {c}(unittest.TestCase):\n"
             "    def test_fixed_name(self): open(os.path.join(tempfile.gettempdir(), 'fixed.tar.gz'), 'x').close()\n"
             "    def test_skip(self): self.skipTest('stated')\n")
    def discover(self, root):
        """The serial child's summary over the same root, as `run_suite` built it before #475."""
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(root), "-q"], capture_output=True,
                           text=True, env={**load_package().suite_env(tempfile.mkdtemp(dir=root.parent))})
        return [l.split(" in ")[0] for l in r.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]

    def test_summary_sums_in_unittests_words_and_order(self):
        pkg = load_package()
        self.assertEqual(pkg.suite_summary(["Ran 1 test in 0.1s\n\nOK\n"], False), ["Ran 1 test", "OK"])
        self.assertEqual(pkg.suite_summary(["Ran 3 tests in 1s\nOK (skipped=1)", "Ran 2 tests in 1s\nOK (skipped=2)"], False),
                         ["Ran 5 tests", "OK (skipped=3)"])
        self.assertEqual(pkg.suite_summary(["Ran 2 tests in 1s\nFAILED (errors=1, skipped=1)", "Ran 1 test in 0s\nFAILED (failures=1)"], True),
                         ["Ran 3 tests", "FAILED (failures=1, errors=1, skipped=1)"])
        self.assertEqual(pkg.suite_summary(["boom"], True), ["Ran 0 tests", "FAILED"])   # a child that printed no summary

    def test_classes_run_apart_and_sum_to_the_serial_summary(self):
        pkg = load_package()
        root = self.root({"test_a.py": self.FIXED.format(c="A") + self.FIXED.format(c="B").split("\n", 1)[1],
                          "test_b.py": self.FIXED.format(c="C")})
        self.assertEqual([len(u) for u in pkg.suite_units(root)], [2, 2, 2])      # one unit per class
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc, summary, err = pkg.run_suite(root)
        self.assertEqual((rc, summary), (0, ["Ran 6 tests", "OK (skipped=3)"]), err)   # three classes, one fixed name each
        self.assertEqual(out.getvalue(), "")                                       # nothing kept, nothing printed
        self.assertNotEqual(self.discover(root)[1:], ["OK (skipped=3)"])           # the control: one shared temp dir collides

    def test_failures_name_each_failing_test_and_its_exception(self):
        """A red run on a CI runner printed only `FAILED (errors=1)`: the kept root went with the runner, and no
        log named the test (main's `rule-11 package` from 76c1a92 on)."""
        pkg = load_package(); bar, dash = "=" * 70, "-" * 70
        err = (f".EF\n{bar}\nERROR: test_b (m.C.test_b)\n{dash}\nTraceback (most recent call last):\n  File \"x\", line 1\n"
               f"RuntimeError: git clone failed\n\n{bar}\nFAIL: test_c (m.C.test_c)\n{dash}\nTraceback (most recent call last):\n"
               f"AssertionError: 1 != 2\n\n{dash}\nRan 3 tests in 0.1s\n\nFAILED (failures=1, errors=1)\n")
        self.assertEqual(pkg.suite_failures(err), ["ERROR: test_b (m.C.test_b) — RuntimeError: git clone failed",
                                                   "FAIL: test_c (m.C.test_c) — AssertionError: 1 != 2"])
        self.assertEqual(pkg.suite_failures("Ran 1 test in 0s\n\nOK\n"), [])

    def test_a_failing_class_keeps_its_root_and_ends_the_stderr_with_the_sum(self):
        pkg = load_package()
        root = self.root({"test_a.py": "import unittest\nclass A(unittest.TestCase):\n    def test_no(self): self.fail('red')\n",
                          "test_b.py": "import unittest\nclass B(unittest.TestCase):\n    def test_ok(self): pass\n"})
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc, summary, err = pkg.run_suite(root)
        self.assertEqual((rc, summary), (1, ["Ran 2 tests", "FAILED (failures=1)"]))
        self.assertEqual(summary, self.discover(root))
        self.assertEqual(err.strip().splitlines()[-1], "FAILED (failures=1)"); self.assertIn("red", err)
        self.assertEqual(pkg.suite_failures(err), ["FAIL: test_no (test_a.A.test_no) — AssertionError: red"])
        kept = [l.split(": ", 1)[1] for l in out.getvalue().splitlines() if "temp root kept" in l]
        self.assertEqual(len(kept), 1, out.getvalue())                             # the failing child's, not the passing one's
        self.assertTrue(Path(kept[0]).is_dir()); shutil.rmtree(kept[0])

    def test_a_module_that_fails_to_import_runs_the_root_as_one_discover_child(self):
        pkg = load_package()
        root = self.root({"test_a.py": "import no_such_module_475\n",
                          "test_b.py": "import unittest\nclass B(unittest.TestCase):\n    def test_ok(self): pass\n"})
        self.assertIsNone(pkg.suite_units(root))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc, summary, err = pkg.run_suite(root)
        self.assertEqual((rc, summary), (1, self.discover(root)))
        self.assertIn("no_such_module_475", err)
        for l in out.getvalue().splitlines():
            shutil.rmtree(l.split(": ", 1)[1], ignore_errors=True)
        self.assertIsNone(pkg.suite_units(self.root({"README": "no tests\n"})))   # nothing found: discover reports it

    def test_roots_run_together_and_return_in_their_own_order(self):
        import threading, time
        pkg = load_package(); live, peak, lock = [0], [0], threading.Lock()
        def fake(suite, target=None):
            with lock:
                live[0] += 1; peak[0] = max(peak[0], live[0])
            time.sleep(0.2 if suite == "first" else 0.01)                       # the first root finishes last
            with lock:
                live[0] -= 1
            return 0, [f"Ran 1 test {suite}", "OK"], ""
        with unittest.mock.patch.object(pkg, "run_suite", fake):
            got = pkg.run_suites(["first", "second", "third"])
        self.assertEqual([s[0] for _, s, _ in got], ["Ran 1 test first", "Ran 1 test second", "Ran 1 test third"])
        self.assertGreater(peak[0], 1)

class TransactionWarningTests(unittest.TestCase):
    """#519: a transaction guard's `warning:` line is printed as `warn` and never fails the PR transaction, as
    `check_package`'s are; anything else still fails."""
    def run_pr(self, msgs):
        pkg = load_package()
        fake = type("G", (), {"check_transaction": staticmethod(lambda root, base, head: list(msgs))})
        with unittest.mock.patch.object(pkg, "registry", return_value=[("agent", "row", "x", True, fake, None)]), \
             unittest.mock.patch.object(pkg, "cmd_invariants", return_value=0), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rc = pkg.cmd_pr("HEAD", "HEAD")
        return rc, out.getvalue()
    def test_a_warning_is_printed_and_passes(self):
        rc, out = self.run_pr(["warning: a separate merge question"])
        self.assertEqual(rc, 0, out); self.assertIn("warn [pr] agent/row a separate merge question", out)
        self.assertIn("ok   [pr] agent/row", out)
    def test_a_failure_still_fails(self):
        rc, out = self.run_pr(["warning: w", "FAIL [main-fence]: x"])
        self.assertEqual(rc, 1, out); self.assertIn("FAIL [pr] agent/row [main-fence]: x", out); self.assertIn("warn [pr]", out)

class CleanlinessTests(unittest.TestCase):
    """The suite-cleanliness fence (d-work #552, mode W): a run whose tests change the live checkout fails, naming the
    paths. An edit made before the run is in both snapshots, so it is never the tests'; a second change to an
    already-dirty file still is. #536's deletion — a test removing a tracked presence file — is reproduced as a real
    failing `check --tests` run in a scratch install, beside a clean run of the same shape that passes."""
    def setUp(self):
        self.pkg = load_package()

    def test_changes_are_status_or_bytes(self):
        d = scratch_repo(["a.txt", "b.txt"])
        (d / "a.txt").write_text("edited before the run\n")
        before = self.pkg.checkout_snapshot(d)
        self.assertEqual(self.pkg.checkout_changes(before, self.pkg.checkout_snapshot(d)), [])   # the user's edit is no change
        (d / "a.txt").write_text("edited again by a test\n")                                     # dirty before, changed again
        (d / "b.txt").unlink()
        (d / "new.txt").write_text("x\n")
        changes = self.pkg.checkout_changes(before, self.pkg.checkout_snapshot(d))
        self.assertEqual(changes, ["a.txt", "b.txt", "new.txt"])
        self.assertIn("the suite changed the live checkout (3 path(s)): a.txt, b.txt, new.txt", self.pkg.cleanliness_problem(changes))
        self.assertIsNone(self.pkg.cleanliness_problem([]))
        self.assertEqual(self.pkg.checkout_changes(None, {}), [])

    def run_target(self, body):
        """`check --tests` of one scratch test module whose one test runs `body`, in a scratch install holding a
        tracked presence file; (returncode, stderr)."""
        d = scratch_install(False)
        presence = d / "agent-corpus" / "d-work" / "sessions" / "program-59cec502.md"
        presence.parent.mkdir(parents=True, exist_ok=True); presence.write_text("session: program-59cec502\n")
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(d), *livetest.IDENTITY, "commit", "-qm", "presence"], check=True, capture_output=True)
        t = d / "dyad" / "tests" / "test_zz_552.py"
        t.write_text("import pathlib, tempfile, unittest\n"
                     "ROOT = pathlib.Path(__file__).resolve().parents[2]\n"
                     "class T(unittest.TestCase):\n"
                     f"    def test_it(self):\n        {body}\n")
        env = {k: v for k, v in dyadlib.git_env().items() if k != "DYAD_NO_NESTED_TESTS"}
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--tests",
                            "dyad/tests/test_zz_552.py"], cwd=d, capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr

    def test_536s_deletion_fails_the_run_naming_the_path(self):
        rc, out = self.run_target("(ROOT / 'agent-corpus/d-work/sessions/program-59cec502.md').unlink()")
        self.assertEqual(rc, 1, out)
        self.assertIn("Ran 1 test", out)                                                          # the test itself passed
        self.assertIn("FAIL [Rule-12] the suite changed the live checkout (1 path(s)): "
                      "agent-corpus/d-work/sessions/program-59cec502.md", out)

    def test_a_test_writing_only_its_scratch_passes(self):
        rc, out = self.run_target("pathlib.Path(tempfile.mkdtemp(), 'x').write_text('x')")
        self.assertEqual(rc, 0, out); self.assertNotIn("changed the live checkout", out)

    def test_check_rule_12_reports_it_too(self):
        """The evidence run and the push gate's full run: `check_rule_12` adds the same line to its failures."""
        d = scratch_repo(["keep.md"])
        def fake(suites):
            (d / "keep.md").unlink()
            return [(0, ["Ran 1 test", "OK"], "")]
        with unittest.mock.patch.dict(os.environ), unittest.mock.patch.object(self.pkg, "REPO", d), \
             unittest.mock.patch.object(self.pkg, "test_suites", lambda: [d / "tests"]), \
             unittest.mock.patch.object(self.pkg, "run_suites", fake), contextlib.redirect_stdout(io.StringIO()):
            os.environ.pop("DYAD_NO_NESTED_TESTS", None)
            msgs = self.pkg.check_rule_12()
        self.assertEqual(len(msgs), 1, msgs)
        self.assertIn("the suite changed the live checkout (1 path(s)): keep.md", msgs[0])


if __name__ == "__main__":
    unittest.main()
