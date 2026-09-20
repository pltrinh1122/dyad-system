import importlib.util, os, shutil, subprocess, sys, tempfile, unittest
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

def scratch_install(with_craft: bool) -> Path:
    """A scratch git repo with the core craft installed (package.py install) and, optionally, every crafts/<craft>/ copied in (whatever this repo currently has, discovered dynamically)."""
    d = Path(tempfile.mkdtemp()); subprocess.run(["git", "init", "-q", str(d)], check=True)
    r = subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "install", str(d)], capture_output=True, text=True); assert r.returncode == 0, r.stderr
    if with_craft:
        for c in dyadlib.craft_dirs(PKG):
            shutil.copytree(c, d / "crafts" / c.name, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(dyadlib.crafts_dir(PKG) / "REGISTRY.md", d / "crafts" / "REGISTRY.md")   # the craft zone's instance state (#156); Rule-11 names it
    subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "scratch"], check=True)
    return d

def load_package():
    spec = importlib.util.spec_from_file_location("package", PKG / "scripts" / "package.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def scratch_repo(paths, tracked=True):
    """A temp git repo holding `paths` (added and committed when tracked, else left untracked)."""
    d = Path(tempfile.mkdtemp())
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
        self.assertEqual({e[1] for e in reg if e[3]}, {"containment", "rows", "prs"} | ({"events"} if "sysadmin" in CRAFTS else set()))   # events: the sysadmin craft's (#171)
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
        d = Path(tempfile.mkdtemp()); shutil.copytree(PKG, d / "dyad", ignore=shutil.ignore_patterns("__pycache__"))
        (d / "dyad" / "guards" / "agent" / "zzz.py").write_text("ENTITY = 'zzz'\n")
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--list"], capture_output=True, text=True, env={**os.environ, "DYAD_NO_NESTED_TESTS": "1"})
        self.assertNotEqual(r.returncode, 0); self.assertIn("agent/zzz.py", r.stdout); self.assertIn("lacks CORPUS, FIELDS, TRANSACTION, check_package", r.stdout)
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--guards"], capture_output=True, text=True, env={**os.environ, "DYAD_NO_NESTED_TESTS": "1"})
        self.assertIn("FAIL [guards] agent/zzz:", r.stdout)
    def test_guards_entry_point(self):
        r = self.run_py("check", "--guards")
        for g in ("infra/containment", "agent/rules", "agent/vocabulary", "agent/references", *CRAFT):   # every craft guard this install carries (#171)
            self.assertTrue(any(l.startswith(("ok   [guards] " + g, "FAIL [guards] " + g)) for l in r.stdout.splitlines()), g)
        self.assertRegex(r.stdout, r"\[guards\] agent/rules \(\d+ Rules\)")
    def test_rule_12_runs_the_suites_and_maps_nothing(self):
        """#162: the mapping is the syseng craft's guard (`syseng/tests`); the runner keeps the suites."""
        pkg = load_package(); crafts = dyadlib.crafts_dir(PKG)
        self.assertFalse(hasattr(pkg, "test_for"))
        self.assertEqual(pkg.test_suites(), [PKG / "tests"] + [c / "tests" for c in dyadlib.craft_dirs()])
        self.assertEqual(crafts / "sysarch" / "tests" in pkg.test_suites(), "sysarch" in CRAFTS)   # a core-only install runs the core suite alone (#171)
        self.assertEqual(pkg.check_rule_12(), [])   # under DYAD_NO_NESTED_TESTS: no mapping, no failure
        self.assertNotIn("CHANGELOG.md", pkg.TEMPLATES)   # the change log's seed is the craft's (#155, attack 13)
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
        d = Path(tempfile.mkdtemp()); (d / "x.md").write_text("# x\n")   # `new` refuses to overwrite an existing run-book (#155, attack 7)
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
        d = Path(tempfile.mkdtemp())
        a, b = self.run_py("build", str(d / "a.tar.gz")), self.run_py("build", str(d / "b.tar.gz"))
        self.assertEqual(a.returncode, 0, a.stderr); self.assertIn(f"built {d}/a.tar.gz (version {load_package().version()})", a.stdout)
        self.assertEqual(hashlib.sha256((d / "a.tar.gz").read_bytes()).hexdigest(), hashlib.sha256((d / "b.tar.gz").read_bytes()).hexdigest())
        import tarfile
        with tarfile.open(d / "a.tar.gz") as tar:
            names = tar.getnames()
        self.assertEqual(names, load_package().package_files()); self.assertTrue(all(n.startswith("dyad/") or n.startswith(".github/workflows/dyad-") for n in names))
        shutil.rmtree(d, ignore_errors=True)
    def test_install_twice_is_zero_changes(self):
        d = scratch_install(with_craft=False)
        r = self.run_py("install", str(d))
        # cmd_install prints the resolved destination (hostadapter.resolve; d-work #179, G5) — d itself
        # may be a symlink (e.g. macOS /var -> /private/var) even though it never is on this kernel,
        # which is exactly how this assertion passed here by coincidence before the fix (#179 plan, attack 3)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn(f"installed into {Path(d).resolve()}: 0 changes", r.stdout)
        self.assertEqual((d / "CLAUDE.md").read_text().count("@dyad/CLAUDE.md"), 1)
        for t, rel in load_package().TEMPLATES.items(): self.assertTrue((d / rel).exists(), rel)
        pkg = load_package(); self.assertEqual(pkg.CORE_ROOTS, ["dyad"]); self.assertEqual(pkg.CORE_HOOKS.templates, pkg.TEMPLATES); self.assertEqual(pkg.CORE_HOOKS.import_line, pkg.IMPORT_LINE)
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
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn(f"installed into {Path(d).resolve()}: 0 changes", r.stdout)
        self.assertEqual((d / ".gitignore").read_text(), ignore_text)
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
        rid = subprocess.run(py + ["dwork", "new", "t", "-d", "Y plan"], capture_output=True, text=True, env=env(), cwd=d).stdout.strip()
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
        d = scratch_install(with_craft=False)
        py = [sys.executable, str(d / "dyad" / "scripts" / "package.py")]
        r = subprocess.run(py + ["check", "--list"], capture_output=True, text=True, env=env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        labels = [l.split()[0] + "/" + l.split()[1] for l in r.stdout.splitlines()[1:]]
        self.assertEqual(labels, CORE)
        r = subprocess.run(py + ["check", "--guards"], capture_output=True, text=True, env=env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # Rule-11 property 2's contribution mechanism (#101) retired these four core rows in favor
        # of the sysadmin craft's own `REFERENCES_CONTRIB`: absent here, they print nothing at all,
        # never a skip line — there is no core row left to skip.
        for kind in ("changelog.action->ops", "ops.dwork->row", "ops.changelog->changelog", "changelog.event->event"):
            self.assertNotIn(kind, r.stdout, kind)
        self.assertNotIn("skip event.command->command", r.stdout)   # no craft needed: the core run-book (dyad/runbooks/craft.md) resolves alone; nothing prints with no events store to check against it (#213 d-work #46)
        self.assertIn("skip rule.text->path: `crafts/…` tokens; no crafts/ tree is installed", r.stdout)   # Rules 1, 11 name crafts/ paths
        self.assertFalse((d / "workstation-corpus" / "CHANGELOG.md").exists())   # no core seed since #155; the craft's install seeds it (#156)
        r = subprocess.run(py + ["runbook", "check"], capture_output=True, text=True, env=env())
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
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("ok   [rule-19] 1 run-book(s), 8 commands", r.stdout)   # the core run-book dyad/runbooks/craft.md ships with the package (#165)
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
        r = subprocess.run(py + ["dwork", "new", "t", "-d", "Y plan"], capture_output=True, text=True, env=env(), cwd=d)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rid = r.stdout.strip()
        self.assertTrue((d / "agent-corpus" / "d-work" / "rows" / f"{rid}.md").exists())
        git("add", "-A"); git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", f"ledger: open #{rid}")
        g = subprocess.run(py + ["check", "--guards"], capture_output=True, text=True, env=env(), cwd=d)
        self.assertEqual(g.returncode, 0, g.stdout + g.stderr)
        self.assertNotIn("FAIL", g.stdout)
        self.assertIn("ok   [guards] agent/references", g.stdout)
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
    # Rule-14 property 3 (d-work #138): the evidence block
    def test_evidence_block_shape_and_hash(self):
        import hashlib, re
        r = self.run_py("check", "--evidence")
        lines = r.stdout.splitlines()
        self.assertRegex(lines[0], r"^head=[0-9a-f]{40}$"); self.assertRegex(lines[1], r"^tree=[0-9a-f]{40}$")
        self.assertRegex(lines[2], r"^dirty=(yes|no)$")
        self.assertTrue(any("[Rule-11]" in l for l in lines) and any("[guards] infra/containment" in l for l in lines), r.stdout)
        self.assertRegex(lines[-1], r"^evidence-sha256=[0-9a-f]{64}$")
        self.assertEqual(lines[-1], "evidence-sha256=" + hashlib.sha256("\n".join(lines[:-1]).encode()).hexdigest())
    def test_evidence_block_deterministic(self):
        a, b = self.run_py("check", "--evidence"), self.run_py("check", "--evidence")
        self.assertEqual(a.stdout, b.stdout); self.assertEqual(a.returncode, b.returncode)

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
        r = self.dwork_new(d, "three", "#1")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "3")
        text = rows.joinpath("3.md").read_text()
        self.assertIn("state: open\n", text); self.assertIn("refs: #1\n", text)
    def test_dwork_new_backlog_flag(self):
        sys.path.insert(0, str(PKG / "scripts")); import dyadlib
        d, rows = self.dwork_repo()
        r = self.dwork_new(d, "four", "--backlog", "-d", "opened as backlog on #2 Done", "#2")
        self.assertEqual(r.returncode, 0, r.stderr)
        text = rows.joinpath("3.md").read_text()
        self.assertIn("state: backlog\n", text); self.assertIn("refs: #2\n", text)
        self.assertIn("opened as backlog on #2 Done", text)
        self.assertIn("backlog", dyadlib.NEW_STATES)
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
                rc = pkg.cmd_dwork(["new", "three", "#1"])
        self.assertEqual(rc, 0)
        self.assertIn("warning: could not read origin/main's rows", stderr.getvalue())
        self.assertIn("local ids only", stderr.getvalue())
        self.assertIn("d-work #32", stderr.getvalue())
        text = rows.joinpath("3.md").read_text()   # allocation still proceeds, from what it has locally
        self.assertIn("id: 3\n", text); self.assertIn("state: open\n", text)
    def test_dwork_state_refuses_done_to_open(self):
        d, rows = self.dwork_repo(); before = rows.joinpath("2.md").read_text()
        r = self.dwork_state(d, "2", "open")
        self.assertNotEqual(r.returncode, 0); self.assertIn("done\u2192open", r.stderr)
        self.assertEqual(rows.joinpath("2.md").read_text(), before, "nothing written")
    def test_dwork_state_refuses_unknown_state(self):
        d, rows = self.dwork_repo(); before = rows.joinpath("1.md").read_text()
        r = self.dwork_state(d, "1", "foo")
        self.assertNotEqual(r.returncode, 0); self.assertIn("no such state 'foo'", r.stderr)
        self.assertEqual(rows.joinpath("1.md").read_text(), before, "nothing written")
    def test_dwork_state_accepts_open_to_planned(self):
        d, rows = self.dwork_repo()
        r = self.dwork_state(d, "1", "planned", "-d", "Y plan")
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
        self.assertEqual(set(reg), {f"{c}/{s}" for c, s in (("sysarch", "entities"), ("sysarch", "erd"), ("sysadmin", "events"), ("sysarch", "schema"), ("sysarch", "kanban"), ("sysarch", "instances"))})
        self.assertEqual(pkg.PROJECTORS, {k: rel for k, (c, rel) in reg.items()})
        for key, (craft, rel) in reg.items():
            self.assertTrue((pkg.REPO / rel).exists(), rel); self.assertEqual(rel.split("/")[1], craft); self.assertEqual(key, f"{craft}/{key.split('/', 1)[1]}")
    def test_project_unknown_surface_fails(self):
        self.require_craft("sysarch")   # with no projector the line names the install instead (test below)
        r = self.run_py("project", "nope")
        self.assertEqual(r.returncode, 2); self.assertIn("no projector for 'nope': registered:", r.stderr)
    def test_project_without_a_craft_prints_the_install_line(self):
        """A core-only install (no crafts/ tree): `dyad project <s>` exits 2 naming the install; `--list` prints an empty registry with the same line."""
        d = scratch_install(with_craft=False)
        self.addCleanup(shutil.rmtree, d)
        run = lambda *a: subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "project", *a], capture_output=True, text=True, env=env(), cwd=d)
        r = run("erd")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn("no projector for 'erd': no installed craft provides projectors (dyad craft install crafts/sysarch)", r.stderr)
        r = run("--list")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "no projector: no installed craft provides projectors (dyad craft install crafts/sysarch)")
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
    def test_live_repo_tracks_no_generated_file(self):
        pkg = load_package()
        self.assertEqual(pkg.check_generated(pkg.REPO, pkg.rules()["generated"]), [])


class InvariantPassTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md p1, p4: the pass runs before any check in `check` and `check --guards`, prints one
    line per model module in a fixed order, never runs at import or under --list/--help, and a false invariant is a red
    check that does not stop the other checks."""
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
        for cmd in (("check", "--guards"), ("check",)):
            r = self.run_py(*cmd)
            lines = [l for l in r.stdout.splitlines() if "[invariant]" in l]
            self.assertEqual(lines[: len(labels)], [f"ok   [invariant] {l} ({dyadlib.check_invariants(m, e)})" for l, m, e in pkg.invariant_modules()], cmd)
            self.assertTrue(r.stdout.splitlines()[0].startswith("ok   [invariant] dyadlib ("), cmd)   # before any check
        self.assertNotIn("invariants", pkg.CHECKS)   # the pass is not a check entry; it precedes them
    def test_list_and_help_do_not_run_the_pass(self):
        self.assertNotIn("[invariant]", self.run_py("check", "--list").stdout)
        r = self.run_py(); self.assertNotRegex(r.stdout + r.stderr, r"(?m)^(ok  |FAIL) \[invariant\]")   # usage text only
    def test_false_invariant_is_red_but_checks_still_run(self):
        d = scratch_install(with_craft=False)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        g = d / "dyad" / "guards" / "agent" / "zzz.py"
        g.write_text('ENTITY, CORPUS, TRANSACTION = "zzz", "agent", False\nFIELDS = ("a",)\nINVARIANTS = [("never-holds", lambda: False), ("holds", lambda: True)]\n'
                     'def check_package(root=None, pkg=None): return []\ndef describe(root, pkg): return {"store": "", "parser": "", "fields": [("a", "text", "", True, "", "zzz.FIELDS")]}\n')
        (d / "dyad" / "tests" / "guards" / "agent" / "test_zzz.py").write_text("import unittest\n")
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check"], capture_output=True, text=True, env=env())
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("FAIL [invariant] agent/zzz: never-holds", r.stdout); self.assertNotIn("ok   [invariant] agent/zzz", r.stdout)
        self.assertIn("ok   [Rule-11]", r.stdout); self.assertIn("ok   [agent/zzz]", r.stdout)   # the checks still run: evidence stays complete
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "check", "--guards"], capture_output=True, text=True, env=env())
        self.assertNotEqual(r.returncode, 0); self.assertIn("FAIL [invariant] agent/zzz: never-holds", r.stdout); self.assertIn("ok   [guards] agent/zzz", r.stdout)
    def test_dwork_refuses_when_dyadlib_invariants_break(self):
        d = scratch_install(with_craft=False)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        lib = d / "dyad" / "scripts" / "dyadlib.py"
        lib.write_text(lib.read_text().replace('"archived": frozenset(),', '"archived": frozenset({"open"}),'))   # archived is no longer terminal
        r = subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "dwork", "new", "t"], capture_output=True, text=True, env=env(), cwd=d)
        self.assertNotEqual(r.returncode, 0); self.assertIn("refused: dyadlib: invariant(s) failed: archived-is-terminal", r.stderr)
        self.assertEqual(list((d / "agent-corpus" / "d-work" / "rows").glob("[0-9]*.md")), [])

if __name__ == "__main__":
    unittest.main()
