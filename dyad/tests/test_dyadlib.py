import os, sys, unittest, unittest.mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dyadlib, livetest

LEDGER = """# d-work ledger

| id | title | opened | state | disposed | refs |
|----|-------|--------|-------|----------|------|
| 1 | first | 2026-09-12 | done | 2026-09-12 Y done | PR #2 |
| 12 | twelve | 2026-09-12 | open | 2026-09-12 Y plan |  |
| 13 | blocked one | 2026-09-12 | blocked | 2026-09-12 N | blocked by #24 |
"""

class LedgerTests(unittest.TestCase):
    def test_rows_parse_and_skip_header(self):
        rows = dyadlib.ledger_rows(LEDGER)
        self.assertEqual([r.id for r in rows], [1, 12, 13])
        self.assertEqual(rows[1].state, "open")
        self.assertEqual(rows[1].disposed, "2026-09-12 Y plan")
        self.assertEqual(rows[1].refs, "")

    def test_row_lookup_and_missing(self):
        self.assertEqual(dyadlib.ledger_row(LEDGER, 13).state, "blocked")
        self.assertIsNone(dyadlib.ledger_row(LEDGER, 99))

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            dyadlib.ledger_rows(LEDGER + "| 12 | again | 2026-09-13 | open | | |\n")

    def test_short_row_rejected(self):
        with self.assertRaises(ValueError):
            dyadlib.ledger_rows("| 5 | too | short |\n")

class SemverTests(unittest.TestCase):
    """D2 (#100): one grammar, shared by the core and every Tended craft's VERSION check — strict
    MAJOR.MINOR.PATCH, with an optional `+build` suffix a diverged, unreleased tree may carry."""
    def test_plain_semver_matches(self):
        self.assertTrue(dyadlib.SEMVER.fullmatch("1.2.3"))
        self.assertTrue(dyadlib.SEMVER.fullmatch("0.0.1"))
    def test_build_metadata_matches(self):
        self.assertTrue(dyadlib.SEMVER.fullmatch("1.2.3+local.1"))
        self.assertTrue(dyadlib.SEMVER.fullmatch("1.2.3+asg-1"))
    def test_malformed_does_not_match(self):
        for bad in ("1.2", "1.2.3.4", "v1.2.3", "1.2.3-rc1", ""):
            self.assertFalse(dyadlib.SEMVER.fullmatch(bad), bad)
    def test_semver_tuple_strips_build_suffix(self):
        self.assertEqual(dyadlib.semver_tuple("1.2.3"), (1, 2, 3))
        self.assertEqual(dyadlib.semver_tuple("1.2.3+local.1"), (1, 2, 3))
        self.assertTrue(dyadlib.semver_tuple("1.2.3+z") == dyadlib.semver_tuple("1.2.3") < dyadlib.semver_tuple("1.3.0"))

class PathTests(unittest.TestCase):
    def test_instance_default_and_override(self):
        root = Path("/r")
        os.environ.pop("DYAD_INSTANCE", None)
        self.assertEqual(dyadlib.instance(root), root / "agent-corpus")
        os.environ["DYAD_INSTANCE"] = "inst"
        self.assertEqual(dyadlib.ledger_path(root), root / "inst" / "d-work" / "LEDGER.md")
        os.environ.pop("DYAD_INSTANCE", None)

    def test_rule_files_numbered(self):
        files = dyadlib.rule_files()
        self.assertIn(1, files); self.assertIn(7, files); self.assertIn(11, files)
        self.assertTrue(all(isinstance(n, int) and p.name.startswith(f"RULE-{n}-") for n, p in files.items()))

    def test_plain_strips_emphasis(self):
        self.assertEqual(dyadlib.plain("plan-`Y` *coherent*"), "plan-Y coherent")

class TableHeaderTests(unittest.TestCase):
    def test_header_is_the_line_before_the_separator(self):
        self.assertEqual(dyadlib.table_header(LEDGER), ["id", "title", "opened", "state", "disposed", "refs"])
        self.assertEqual(dyadlib.table_header("prose\n| a | b |\nno separator\n"), [])
        self.assertEqual(dyadlib.table_header(""), [])
    def test_plan_parts_are_rule_15s(self):
        self.assertEqual(len(dyadlib.PLAN_PARTS), 5); self.assertIn("base commit", dyadlib.PLAN_PARTS)

if __name__ == "__main__":
    unittest.main()

class GuardRootsTests(livetest.LiveCase):
    """#155: the registry has two roots — dyad/guards/<corpus>/ and crafts/<craft>/guards/ — and loading is
    absent-safe. Absent craft (a core-only install): the core half is asserted and the craft half skips (#171)."""
    def test_guard_files_core_then_craft(self):
        files = dyadlib.guard_files()
        keys = [dyadlib.guard_key(p) for p in files]
        self.assertEqual([k for k in keys if k[0] == "core"] + [k for k in keys if k[0] == "craft"], keys, "core root first, then craft roots")
        self.assertIn(("core", "agent", "rows"), keys)
        self.assertNotIn(("core", "workstation", "runbooks"), keys)
        self.assertTrue(all(not p.name.startswith("_") for p in files))
        if not livetest.crafts_installed():
            self.assertEqual([k for k in keys if k[0] == "craft"], [], "a core-only install has no craft guard")
        self.require_craft("sysadmin")
        self.assertIn(("craft", "sysadmin", "runbooks"), keys)
    def test_load_guard_falls_back_to_a_craft_by_corpus(self):
        self.require_craft("sysadmin")
        g = dyadlib.load_guard("workstation", "runbooks")
        self.assertEqual(g.CORPUS, "workstation"); self.assertTrue(str(Path(g.__file__)).endswith("crafts/sysadmin/guards/runbooks.py"))
        self.assertIs(sys.modules["dyad_guards_workstation_runbooks"], g)                 # importers keep one cache name
        self.assertIs(dyadlib.load_guard_file(dyadlib.crafts_dir() / "sysadmin" / "guards" / "runbooks.py"), g)
        with self.assertRaises(FileNotFoundError): dyadlib.load_guard("nowhere", "runbooks")   # a craft guard of another corpus is not it
    def test_find_guard_none_when_absent(self):
        self.assertIsNone(dyadlib.find_guard("workstation", "nope"))
        self.assertIsNone(dyadlib.find_guard("workstation", "runbooks", pkg=Path("/nonexistent/dyad")))
        self.assertIsNotNone(dyadlib.find_guard("agent", "rows"))
    def test_craft_glob(self):
        names = [p.parent.name for p in dyadlib.craft_glob("VERSION")]
        self.assertEqual(names, sorted(names)); self.assertEqual(names, [d.name for d in dyadlib.craft_dirs()])   # sorted by craft (#160; syseng joins in #162)
        self.assertEqual(dyadlib.craft_glob("VERSION", Path("/nonexistent/dyad")), [])                            # a core-only install: no crafts/ tree
        self.assertEqual(dyadlib.crafts_dir(), dyadlib.PKG.parent / "crafts")
        self.require_craft("sysadmin", "sysarch")
        # not names[:2] == [...]: a positional claim, true only by accident of these two names'
        # alphabetical order — false the moment any craft sorts earlier (lan-git does, #181).
        # Membership is the actual invariant this line is protecting.
        self.assertIn("sysadmin", names); self.assertIn("sysarch", names)

class PackageRulesTests(unittest.TestCase):
    """dyadlib.package_rules (#192): the package file is generic; a host's own strings come from
    <instance>/package_rules.local.txt and are never in the shipped file."""
    HOST = "pt-MS-" + "7D75"; LAN = "192." + "168."   # assembled: this test file ships in the package and must not carry a marker
    def test_package_file_carries_no_host_string(self):
        r = dyadlib.package_rules(dyadlib.PKG, None)
        self.assertNotIn(self.HOST, r["string"]); self.assertIn(self.LAN, r["string"])
        self.assertTrue(all(s.startswith("/ho") and s.endswith("me/") or s == self.LAN or ".claude" in s for s in r["string"]), r["string"])
    def test_local_file_merges_when_present(self):
        import tempfile
        root = Path(tempfile.mkdtemp()); inst = root / "agent-corpus"; inst.mkdir()
        (inst / dyadlib.RULES_LOCAL).write_text(f"# local\nstring: {self.HOST}\nname: SECRET.md\n")
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus"}):
            r = dyadlib.package_rules(dyadlib.PKG, root)
        self.assertIn(self.HOST, r["string"]); self.assertIn("SECRET.md", r["name"]); self.assertIn(self.LAN, r["string"])
    def test_local_file_absent_is_fine(self):
        import tempfile
        root = Path(tempfile.mkdtemp()); (root / "agent-corpus").mkdir()
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus"}):
            self.assertEqual(dyadlib.package_rules(dyadlib.PKG, root), dyadlib.package_rules(dyadlib.PKG, None))
    def test_this_instance_refuses_its_host_when_it_declares_one(self):
        root = dyadlib.repo_root(); local = dyadlib.instance(root) / dyadlib.RULES_LOCAL
        if not local.is_file():
            self.skipTest("this instance has no package_rules.local.txt (a host with nothing to refuse; dyad-system #1)")
        r = dyadlib.package_rules(dyadlib.PKG, root)
        self.assertTrue(any(s not in dyadlib.package_rules(dyadlib.PKG, None)["string"] for s in r["string"]), "the local file adds at least one row")

class RepoRootHookEnv(unittest.TestCase):
    """#142: repo_root ignores GIT_DIR set by hooks and returns the work tree, not the package dir."""
    def test_repo_root_under_git_dir(self):
        import os, subprocess
        root = dyadlib.repo_root()
        gd = subprocess.check_output(["git", "rev-parse", "--absolute-git-dir"], cwd=root, text=True).strip()
        old = os.environ.get("GIT_DIR")
        os.environ["GIT_DIR"] = gd
        try:
            self.assertEqual(dyadlib.repo_root(), root)
        finally:
            if old is None: del os.environ["GIT_DIR"]
            else: os.environ["GIT_DIR"] = old

class TrackedModeTests(unittest.TestCase):
    """#141: the mode a guard judges is git's, not the disk's — `core.fileMode=false` (NTFS) shows 755 for a
    file tracked 100644, which passed three ops scripts and shipped an entrypoint that could not exec (#135)."""
    def repo(self, fileMode=None) -> Path:
        import shutil, subprocess, tempfile
        d = Path(tempfile.mkdtemp(prefix="dyad-mode-")); self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        if fileMode is not None:
            subprocess.run(["git", "-C", str(d), "config", "core.fileMode", fileMode], check=True)
        return d
    def add(self, root: Path, rel: str, disk=0o755, chmod: str | None = None):
        import subprocess
        p = root / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("#!/usr/bin/env bash\n"); p.chmod(disk)
        subprocess.run(["git", "-C", str(root), "add", "--", rel], check=True)
        if chmod:
            subprocess.run(["git", "-C", str(root), "update-index", f"--chmod={chmod}", "--", rel], check=True)
        return p
    def test_index_mode_wins_over_the_disk_bit(self):
        r = self.repo(fileMode="false")
        self.add(r, "a.sh", disk=0o755, chmod="-x")          # the #135 shape: 755 on disk, 100644 in the index
        self.assertEqual(dyadlib.tracked_mode(r, "a.sh"), dyadlib.MODE_FILE)
        self.assertTrue(os.access(r / "a.sh", os.X_OK))
        self.add(r, "b.sh", disk=0o644, chmod="+x")
        self.assertEqual(dyadlib.tracked_mode(r, "b.sh"), dyadlib.MODE_EXEC)
    def test_untracked_and_outside_and_non_repo_are_none(self):
        import tempfile
        r = self.repo()
        (r / "new.sh").write_text("x\n")
        self.assertIsNone(dyadlib.tracked_mode(r, "new.sh"))
        self.assertIsNone(dyadlib.tracked_mode(r, "absent.sh"))
        self.assertIsNone(dyadlib.tracked_mode(r, Path(tempfile.gettempdir()) / "elsewhere.sh"))   # absolute, outside root
        self.assertIsNone(dyadlib.tracked_mode(r / "gone", "a.sh"))                                # no such directory
    def test_a_glob_in_the_name_and_a_directory(self):
        r = self.repo(); self.add(r, "sub/a[1].sh", chmod="+x"); self.add(r, "sub/a1.sh", chmod="-x")
        self.assertEqual(dyadlib.tracked_mode(r, "sub/a[1].sh"), dyadlib.MODE_EXEC)   # a name, not a pattern
        self.assertEqual(dyadlib.tracked_mode(r, "sub/a1.sh"), dyadlib.MODE_FILE)
        self.assertIsNone(dyadlib.tracked_mode(r, "sub"))                             # a directory has no one mode
    def test_absolute_path_inside_root_resolves(self):
        r = self.repo(); p = self.add(r, "sub/c.sh", chmod="+x")
        self.assertEqual(dyadlib.tracked_mode(r, p), dyadlib.MODE_EXEC)
        self.assertEqual(dyadlib.tracked_mode(r, "sub/c.sh"), dyadlib.MODE_EXEC)
    def test_git_dir_in_the_environment_is_ignored(self):
        """#142's shape for the index: a hook exports GIT_DIR/GIT_INDEX_FILE; the answer stays this tree's."""
        r = self.repo(); self.add(r, "d.sh", chmod="+x")
        other = self.repo()
        old = {k: os.environ.get(k) for k in dyadlib.GIT_VARS}
        os.environ["GIT_DIR"] = str(other / ".git"); os.environ["GIT_INDEX_FILE"] = str(other / ".git" / "index")
        try:
            self.assertEqual(dyadlib.tracked_mode(r, "d.sh"), dyadlib.MODE_EXEC)
            self.assertEqual(dyadlib.git_env().keys() & set(dyadlib.GIT_VARS), set())
        finally:
            for k, v in old.items():
                os.environ.pop(k, None)
                if v is not None: os.environ[k] = v
    def test_live_package_entrypoint_and_hooks_are_tracked_executable(self):
        root = dyadlib.repo_root()
        for rel in ("dyad/bin/dyad", "dyad/hooks/pre-commit", "dyad/hooks/pre-push"):
            self.assertEqual(dyadlib.tracked_mode(root, rel), dyadlib.MODE_EXEC, rel)

class InvariantTests(livetest.LiveCase):
    """crafts/syseng/rules/invariants.md: the protocol — INVARIANTS is data, check_invariants runs it sorted, an
    InvariantError names every false one, nothing runs at import."""
    def test_dyadlib_invariants_hold_and_are_counted(self):
        self.assertEqual(dyadlib.check_invariants(dyadlib), len(dyadlib.INVARIANTS))
        names = [n for n, _ in dyadlib.INVARIANTS]
        self.assertEqual(len(set(names)), len(names)); self.assertTrue(all(callable(p) for _, p in dyadlib.INVARIANTS))
        self.assertEqual([n for n, _ in dyadlib.invariants_of(dyadlib)], sorted(names))
    def test_failed_invariants_raise_with_names_sorted(self):
        inv = [("z-false", lambda: False), ("a-true", lambda: True), ("m-raises", lambda: 1 / 0), ("b-false", lambda: 0)]
        with self.assertRaises(dyadlib.InvariantError) as cm:
            dyadlib.check_invariants(inv, label="fx")
        self.assertEqual(cm.exception.failed, ["b-false", "m-raises", "z-false"]); self.assertEqual(cm.exception.module, "fx")
        self.assertEqual(str(cm.exception), "fx: invariant(s) failed: b-false, m-raises, z-false")
    def test_module_without_invariants_counts_zero_and_extras_are_appended(self):
        import types
        m = types.ModuleType("bare")
        self.assertEqual(dyadlib.check_invariants(m), 0)
        self.assertEqual(dyadlib.check_invariants(m, extra=[("x", lambda: True)]), 1)
        with self.assertRaises(dyadlib.InvariantError): dyadlib.check_invariants(m, extra=[("x", lambda: False)])
    def test_contract_invariants_restate_the_contract(self):
        import types
        g = types.ModuleType("g"); g.ENTITY, g.CORPUS, g.FIELDS, g.TRANSACTION = "e", "agent", ("a", "b"), False
        names = [n for n, _ in dyadlib.contract_invariants(g, "core", "agent")]
        self.assertEqual(names, ["entity-non-empty", "corpus-matches-directory", "fields-unique-strings", "transaction-implies-check_transaction"])
        self.assertEqual(dyadlib.check_invariants(g, dyadlib.contract_invariants(g, "core", "agent")), 4)
        with self.assertRaises(dyadlib.InvariantError) as cm: dyadlib.check_invariants(g, dyadlib.contract_invariants(g, "core", "infra"))
        self.assertEqual(cm.exception.failed, ["corpus-matches-directory"])
        g.TRANSACTION = True
        with self.assertRaises(dyadlib.InvariantError) as cm: dyadlib.check_invariants(g, dyadlib.contract_invariants(g, "core", "agent"))
        self.assertEqual(cm.exception.failed, ["transaction-implies-check_transaction"])
        g.FIELDS = ("a", "a"); g.TRANSACTION = False
        with self.assertRaises(dyadlib.InvariantError) as cm: dyadlib.check_invariants(g, dyadlib.contract_invariants(g, "craft", "x", {"agent"}))
        self.assertEqual(cm.exception.failed, ["fields-unique-strings"])
    def test_runner_and_projector_discovery(self):
        r = dyadlib.runner_module()
        self.assertEqual(Path(r.__file__), dyadlib.PKG / "scripts" / "package.py"); self.assertIs(dyadlib.runner_module(), r)
        self.assertTrue(hasattr(r, "INVARIANTS") and hasattr(r, "invariant_modules"))
        stems = [p.stem for p in dyadlib.projector_files()]
        if not livetest.crafts_installed():
            self.assertEqual(stems, [], "a core-only install has no projector")            # the documented absent-craft behaviour
            return
        self.require_craft("sysadmin", "sysarch")
        # Expected set derived from the tree, not a literal list (#156 I1, the #46/#98 class): any craft
        # may ship a projector. Order: by craft, then surface.
        crafts = dyadlib.PKG.parent / "crafts"
        on_disk = [(p.parents[1].name, p.stem) for p in sorted(crafts.glob("*/projectors/project_*.py"))]
        self.assertEqual(stems, [s for _c, s in on_disk])
        known = {"sysadmin": ["project_events"], "sysarch": ["project_entities", "project_erd", "project_instances", "project_kanban", "project_schema"]}
        for craft, surfaces in known.items():   # a known craft silently dropping a projector still fails
            self.assertEqual([s for c, s in on_disk if c == craft], surfaces, craft)
