"""Test-level script tests (dyad/scripts/levels.py, the core's since #378; the audit play-book's self-diagnostic section): a
complete classification passes, comments and blank lines carry nothing; an unclassified module, a stale entry, a
malformed line, an unknown level, a misshapen path (a backslash spelling among them) and a path listed twice each fail
once; the test roots are `dyad/tests/` and every `crafts/<craft>/tests/`, `__pycache__` below a root and non-`test_*`
files never count, a repo inside a `__pycache__` directory loses nothing, and `test_.py` counts and may be listed; a
UTF-8 BOM is dropped and a file that is not UTF-8 is one failure; the host path comes from the preference and
`DYAD_HOST`; an absent file skips; the seed is checked for form only; `list` prints one level sorted, refuses a failing
file and exits 2 on no file or a malformed call; `self_check` names each false invariant. Every tree the script
judges here is a scratch directory — no git, no child process, never a system's inventory; the one live read is this
craft's own `tests/` and seed, to hold the seed's lines for this craft to its own modules. A script is no guard, so
nothing else runs its checks on a push: here, wherever this suite runs (every push of the authoring repo; L2's
evidence run, which runs every root, where a push gate skips an unmodified installed root), its pure invariants and
the seed invariant hold, and the craft's own seed is well-formed and classifies exactly this craft's test modules
(its other lines are other trees' and judged nowhere here). Beside them, the run-book template, which no instance
check reads in a repo that only authors it: parsed by
the core runner's parser and never run, its steps, sections, classes and gates agree with each other, with the
`record` step's level table and with the run-book check when the sysadmin craft is present."""
import ast, contextlib, io, os, re, shutil, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
PKG = Path(__file__).resolve().parents[1]                                    # dyad/
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib, runbook as rb
import levels as lv

CORE_A, CORE_B = "dyad/tests/test_alpha.py", "dyad/tests/guards/agent/test_beta.py"
CRAFT_A, CRAFT_B = "crafts/kit/tests/test_project_kit.py", "crafts/kit/tests/guards/test_gamma.py"
MODULES = (CORE_A, CORE_B, CRAFT_A, CRAFT_B)
COMPLETE = (f"# levels\n\nunit        {CORE_A}\nintegration {CORE_B}   # builds a scratch repo\n\n"
            f"unit {CRAFT_B}\nintegration {CRAFT_A}\n")
PREFS = ("# Operator preferences\n\n| key | value | allowed | read by |\n|-----|-------|---------|---------|\n"
         "| host-path | infrastructure | a repo-relative directory | Rule-1 |\n")

def tree(case, modules=MODULES, levels=None, host="workstation-corpus", prefs=None, extra=()) -> Path:
    """A scratch root, removed after `case`: empty files at `modules` and `extra`, the levels file at
    `<host>/self-diagnostic-levels.txt` when `levels` is given, a preferences table when `prefs` is."""
    root = Path(tempfile.mkdtemp()); case.addCleanup(shutil.rmtree, root, ignore_errors=True)
    for m in (*modules, *extra):
        p = root / m; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("")
    if prefs is not None:
        (root / "preferences-corpus").mkdir(); (root / "preferences-corpus" / "PREFERENCES.md").write_text(prefs)
    if levels is not None:
        (root / host).mkdir(parents=True, exist_ok=True); (root / host / lv.FILE).write_text(levels)
    return root

def craft(case, template=None) -> Path:
    """A scratch craft root: `templates/self-diagnostic-levels.txt` holding `template`, or no templates/ at all."""
    d = Path(tempfile.mkdtemp()); case.addCleanup(shutil.rmtree, d, ignore_errors=True)
    if template is not None:
        (d / "templates").mkdir(); (d / "templates" / lv.FILE).write_text(template)
    return d

def run(argv) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = lv.main([str(a) for a in argv])
    return rc, out.getvalue(), err.getvalue()

class LevelsTests(unittest.TestCase):
    def setUp(self):
        env = mock.patch.dict(os.environ); env.start(); self.addCleanup(env.stop)
        for k in ("DYAD_HOST", "DYAD_HOST_ZONE"):
            os.environ.pop(k, None)
        self.no_seed = craft(self)

    def check(self, root):
        return lv.check_package(root, craft=self.no_seed)

    def test_data_model_and_invariants(self):
        self.assertEqual((lv.FIELDS, lv.LEVELS, lv.PKG), (("level", "path"), ("unit", "integration"), PKG))
        self.assertEqual(dyadlib.check_invariants(list(lv.INVARIANTS)), len(lv.INVARIANTS))
        seed = [e for e in lv.TREE_INVARIANTS if e[0] == "seed-template-exists"]   # the runner's one starts git: `self_check`
        self.assertEqual(dyadlib.check_invariants(seed), 1)

    def test_self_check_names_each_false_invariant(self):
        with mock.patch.object(lv, "INVARIANTS", [("a-holds", lambda: True), ("b-false", lambda: False)]), \
             mock.patch.object(lv, "TREE_INVARIANTS", [("c-raises", lambda: 1 / 0), ("d-holds", lambda: True)]):
            self.assertEqual(lv.self_check(), ["b-false", "c-raises"])
        with mock.patch.object(lv, "INVARIANTS", [("a-holds", lambda: True)]), mock.patch.object(lv, "TREE_INVARIANTS", []):
            self.assertEqual(lv.self_check(), [])

    def test_the_cores_own_seed(self):
        """Form, and the core's own lines: the seed names exactly the test modules under `dyad/tests/`
        (a core module moved, added or removed moves its line in the same change)."""
        seed = PKG / "templates" / lv.FILE
        self.assertEqual(lv.check_file(seed, f"templates/{lv.FILE}"), [])
        repo = PKG.parent
        own = sorted(p.relative_to(repo).as_posix() for p in (PKG / "tests").rglob("test_*.py")
                     if lv.is_test_name(p.name) and "__pycache__" not in p.relative_to(PKG).parts)
        named = sorted(path for _, _, path in lv.parse(lv.read(seed))[0] if path.startswith(PKG.relative_to(repo).as_posix() + "/tests/"))
        self.assertEqual(named, own)

    def test_complete_classification_passes(self):
        root = tree(self, levels=COMPLETE)
        self.assertEqual(self.check(root), [])
        self.assertEqual(lv.summary(root), "4 modules: 2 unit, 2 integration")
        self.assertEqual(lv.test_modules(root), sorted(MODULES))

    def test_absent_file_skips(self):
        root = tree(self)
        self.assertEqual(self.check(root), [])
        self.assertEqual(lv.summary(root), "skip: no workstation-corpus/self-diagnostic-levels.txt")
        self.assertEqual(lv.listing(root, "unit"), [])

    def test_unclassified_module_fails(self):
        root = tree(self, levels=COMPLETE.replace(f"unit {CRAFT_B}\n", ""))
        msgs = self.check(root); self.assertEqual(len(msgs), 1, msgs)
        self.assertIn(f"{CRAFT_B} is a test module this file does not classify", msgs[0])

    def test_stale_entry_fails(self):
        root = tree(self, levels=COMPLETE + "unit dyad/tests/test_gone.py\n")
        msgs = self.check(root); self.assertEqual(len(msgs), 1, msgs)
        self.assertIn("line 8: dyad/tests/test_gone.py names no test module of this tree", msgs[0])

    def test_only_test_modules_under_the_test_roots_count(self):
        extra = ("docs/test_outside.py", "dyad/tests/helper.py", "dyad/tests/__pycache__/test_alpha.py",
                 "crafts/kit/scripts/test_not_a_root.py", "dyad/scripts/test_nor_this.py")
        root = tree(self, levels=COMPLETE, extra=extra)
        self.assertEqual(lv.test_modules(root), sorted(MODULES))
        self.assertEqual(self.check(root), [])
        root = tree(self, levels=COMPLETE + "unit docs/test_outside.py\n", extra=extra)
        msgs = self.check(root); self.assertEqual(len(msgs), 1, msgs); self.assertIn("docs/test_outside.py names no test module", msgs[0])

    def test_empty_stem_is_counted_and_may_be_listed(self):
        root = tree(self, levels=COMPLETE + "unit dyad/tests/test_.py\n", extra=("dyad/tests/test_.py",))
        self.assertIn("dyad/tests/test_.py", lv.test_modules(root))
        self.assertEqual(self.check(root), [])
        root = tree(self, levels=COMPLETE, extra=("dyad/tests/test_.py",))
        msgs = self.check(root); self.assertEqual(len(msgs), 1, msgs); self.assertIn("dyad/tests/test_.py is a test module", msgs[0])

    def test_a_repo_inside_a_pycache_directory_loses_nothing(self):
        outer = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, outer, ignore_errors=True)
        root = outer / "__pycache__" / "repo"
        for m in MODULES:
            (root / m).parent.mkdir(parents=True, exist_ok=True); (root / m).write_text("")
        (root / "workstation-corpus").mkdir(); (root / "workstation-corpus" / lv.FILE).write_text(COMPLETE)
        self.assertEqual(lv.test_modules(root), sorted(MODULES))
        self.assertEqual(self.check(root), [])

    def test_bom_is_dropped_and_undecodable_bytes_fail_once(self):
        root = tree(self, levels="")
        (root / "workstation-corpus" / lv.FILE).write_bytes(b"\xef\xbb\xbf" + COMPLETE.encode())
        self.assertEqual(self.check(root), []); self.assertEqual(lv.listing(root, "unit"), sorted((CORE_A, CRAFT_B)))
        (root / "workstation-corpus" / lv.FILE).write_bytes(COMPLETE.encode() + b"unit dyad/tests/caf\xe9.py\n")
        msgs = self.check(root); self.assertEqual(len(msgs), 1, msgs)
        self.assertIn("workstation-corpus/self-diagnostic-levels.txt: not UTF-8 (byte ", msgs[0])
        self.assertEqual(lv.listing(root, "unit"), [])
        rc, out, err = run(["list", "unit", root])
        self.assertEqual((rc, out), (1, "")); self.assertIn("not UTF-8", err)

    def test_malformed_lines_fail_once_each(self):
        bad = ("unit\n", f"unit {CORE_A} extra\n", f"smoke {CORE_A}\n", "unit /dyad/tests/test_alpha.py\n",
               "unit ../dyad/tests/test_alpha.py\n", "unit dyad/tests/helper.py\n", "unit dyad\\tests\\test_alpha.py\n")
        root = tree(self, levels=COMPLETE + "".join(bad))
        msgs = self.check(root)
        want = ("line 8: `unit` is not `<level> <path>`", "line 9: `unit dyad/tests/test_alpha.py extra` is not",
                "line 10: level `smoke` is not one of unit, integration", "line 11: path `/dyad/tests/test_alpha.py` is not",
                "line 12: path `../dyad/tests/test_alpha.py` is not", "line 13: path `dyad/tests/helper.py` is not",
                "line 14: path `dyad\\tests\\test_alpha.py` is not")
        for w in want:
            self.assertTrue(any(w in m for m in msgs), (w, msgs))
        # the `smoke` line names CORE_A a second time: the duplicate is reported beside its level
        self.assertTrue(any("line 10: dyad/tests/test_alpha.py already classified at line 3" in m for m in msgs), msgs)
        self.assertEqual(len(msgs), len(want) + 1, msgs)

    def test_duplicate_path_fails_whatever_its_level(self):
        for level in ("unit", "integration"):
            root = tree(self, levels=COMPLETE + f"{level} {CORE_A}\n")
            msgs = self.check(root); self.assertEqual(len(msgs), 1, msgs)
            self.assertIn(f"line 8: {CORE_A} already classified at line 3", msgs[0])

    def test_host_path_from_preference_and_environment(self):
        root = tree(self, levels=COMPLETE, host="infrastructure", prefs=PREFS)
        self.assertEqual(self.check(root), []); self.assertTrue(lv.summary(root).startswith("4 modules"))
        root = tree(self, levels=COMPLETE.replace(f"unit {CRAFT_B}\n", ""), host="infrastructure", prefs=PREFS)
        self.assertEqual(len(self.check(root)), 1)
        self.assertTrue(self.check(root)[0].startswith("infrastructure/self-diagnostic-levels.txt: "))
        root = tree(self, levels=COMPLETE, host="ops-host")
        self.assertEqual(lv.summary(root), "skip: no workstation-corpus/self-diagnostic-levels.txt")
        with mock.patch.dict(os.environ, {"DYAD_HOST": "ops-host"}):
            self.assertTrue(lv.summary(root).startswith("4 modules")); self.assertEqual(self.check(root), [])

    def test_seed_is_checked_for_form_only(self):
        root = tree(self)    # no instance file; the seed names modules this tree lacks, which is no fault of a seed
        self.assertEqual(lv.check_package(root, craft=craft(self, "unit dyad/tests/test_elsewhere.py\n")), [])
        msgs = lv.check_package(root, craft=craft(self, "unit dyad/tests/test_a.py\nunit\nfast dyad/tests/test_b.py\n"))
        self.assertEqual(len(msgs), 2, msgs)
        self.assertTrue(all(m.startswith(f"templates/{lv.FILE} line ") for m in msgs), msgs)

    def test_cli_check(self):
        root = tree(self, levels=COMPLETE)
        with mock.patch.object(lv, "PKG", self.no_seed):
            self.assertEqual(run([root]), (0, "ok   [levels] 4 modules: 2 unit, 2 integration\n", ""))
            self.assertEqual(run([tree(self)]), (0, "skip [levels] no workstation-corpus/self-diagnostic-levels.txt\n", ""))
            rc, out, err = run([tree(self, levels=COMPLETE + "unit dyad/tests/test_gone.py\n")])
            self.assertEqual((rc, out), (1, "")); self.assertIn("FAIL [levels] workstation-corpus/self-diagnostic-levels.txt line 8", err)

    def test_cli_list(self):
        root = tree(self, levels=COMPLETE)
        self.assertEqual(run(["list", "unit", root]), (0, f"{CRAFT_B}\n{CORE_A}\n", ""))          # sorted: crafts/ before dyad/
        self.assertEqual(run(["list", "integration", root]), (0, f"{CRAFT_A}\n{CORE_B}\n", ""))
        rc, out, err = run(["list", "unit", tree(self)])
        self.assertEqual((rc, out), (2, "")); self.assertIn("skip [levels] no workstation-corpus/self-diagnostic-levels.txt", err)
        rc, out, err = run(["list", "smoke", root])
        self.assertEqual((rc, out), (2, "")); self.assertIn("usage: levels.py list <unit|integration>", err)
        rc, out, err = run(["list", "unit", root, "x"])
        self.assertEqual((rc, out), (2, "")); self.assertIn("usage: levels.py list <unit|integration>", err)
        rc, out, err = run(["list", "unit", tree(self, levels=COMPLETE.replace(f"unit {CRAFT_B}\n", ""))])
        self.assertEqual((rc, out), (1, "")); self.assertIn(f"FAIL [levels] workstation-corpus/self-diagnostic-levels.txt: {CRAFT_B}", err)

# The self-diagnostic run-book of record: the core's (`dyad/runbooks/`, where #369 C3 moves it) once it exists, until then
# the craft's template, which #369 C5 deletes — so the tests always read the one copy the tree holds, never a fixture.
_CORE_RUNBOOK = lv.PKG / "runbooks" / "self-diagnostic.md"
RUNBOOK = _CORE_RUNBOOK if _CORE_RUNBOOK.exists() else lv.PKG.parent / "crafts" / "countersign" / "templates" / "runbooks" / "self-diagnostic.md"
STEPS = ("health", "unit", "integration", "evidence", "invariants", "units", "acts", "pairs", "host", "record")
GATED = ("integration", "evidence", "invariants", "units", "acts", "pairs", "host")
_GATE = re.compile(r"sys\.exit\(3 if bad else 0\)' ([a-z ]+) \|\| exit$", re.M)
_LEVELS = re.compile(r"^LEVELS = (\{.*\})$", re.M)

class RunbookTemplateTests(unittest.TestCase):
    def setUp(self):
        self.text = RUNBOOK.read_text(); self.cmds = rb.parse_text(self.text)

    def test_steps_sections_and_classes(self):
        self.assertEqual([c.name for c in self.cmds], list(STEPS))
        self.assertEqual(rb.declared_sections(self.text), [f"Level {n}" for n in range(1, 5)])
        self.assertEqual(rb.prose_blocks(self.text), [])
        for c in self.cmds:
            self.assertEqual((c.cls, c.role, bool(c.cmd)), ("read-only", "any", True), c.name)   # every step read-only
        self.assertNotIn(self.cmds[0].postcondition, ("", rb.NONE))   # `health` states its pass criterion (Rule-19 p1)

    def test_each_gate_names_only_earlier_steps(self):
        order = {n: i for i, n in enumerate(STEPS)}
        gates = {c.name: m.group(1).split() for c in self.cmds for m in [_GATE.search(c.cmd)] if m}
        self.assertEqual(sorted(gates), sorted(GATED))
        for name, needs in gates.items():
            self.assertTrue(needs and all(order[n] < order[name] for n in needs), (name, needs))

    def test_record_step_levels_follow_the_sections(self):
        record = next(c for c in self.cmds if c.name == "record")
        levels = ast.literal_eval(_LEVELS.search(record.cmd).group(1))
        self.assertEqual(sorted(levels), [1, 2, 3, 4])
        self.assertEqual({n for steps in levels.values() for n in steps} | {"health", "record"}, set(STEPS))
        sec = {c.name: c.section for c in self.cmds}
        for lvl, steps in levels.items():
            for n in steps:
                self.assertTrue(rb.in_section(sec[n], f"Level {lvl}"), (n, sec[n]))

    def test_passes_the_run_book_check_when_present(self):
        guard = dyadlib.find_guard("workstation", "runbooks")
        if guard is None or not hasattr(guard, "declared_sections"):
            self.skipTest("no craft provides a run-book check that reads `# sections:`")
        self.assertEqual(guard.check_runbook(RUNBOOK, None), [])

if __name__ == "__main__":
    unittest.main()
