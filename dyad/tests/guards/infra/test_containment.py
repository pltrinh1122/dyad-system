import os, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
c = dyadlib.load_guard("infra", "containment")

def sh(*a, cwd): return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout

class Repo:
    def __init__(self):
        self.d = Path(tempfile.mkdtemp())
        sh("git", "init", "-q", cwd=self.d)
        sh("git", "config", "user.email", "t@t", cwd=self.d); sh("git", "config", "user.name", "t", cwd=self.d)
    def commit(self, files: dict[str, str | None], msg="c") -> str:
        for rel, content in files.items():
            p = self.d / rel
            if content is None:
                sh("git", "rm", "-q", rel, cwd=self.d)
            else:
                p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content); sh("git", "add", rel, cwd=self.d)
        sh("git", "commit", "-q", "--allow-empty", "-m", msg, cwd=self.d)
        return sh("git", "rev-parse", "HEAD", cwd=self.d).strip()

class ClassifyTests(unittest.TestCase):
    def test_globs(self):
        self.assertEqual(c.classify("dyad/rules/RULE-1.md"), "agent")
        self.assertEqual(c.classify("agent-corpus/d-work/LEDGER.md"), "agent")
        self.assertEqual(c.classify("CLAUDE.md"), "infra")
        self.assertEqual(c.classify("docs/x.md"), "unclassified")
        self.assertEqual(c.classify("dyadx/y"), "unclassified")
        self.assertEqual(c.classify("crafts/sysadmin/rules/host-mutation.md"), "craft")
        self.assertEqual(c.classify("craftsx/y"), "unclassified")
        # #152: committed harness adapters (slash commands, skills) are infra, beside the host frame
        self.assertEqual(c.classify(".claude/commands/falsify.md"), "infra")
        self.assertEqual(c.classify(".claude/skills/pb-craft/SKILL.md"), "infra")
        self.assertEqual(c.classify(".claudex/y"), "unclassified")
        # #501 (C3 of #498): the GitHub Pages site joins the front door's zone
        self.assertEqual(c.classify("site/index.md"), "infra")
        self.assertEqual(c.classify("site/episodes/000-announcement.md"), "infra")
        self.assertEqual(c.classify("sitex/y"), "unclassified")

class TransactionTests(unittest.TestCase):
    def setUp(self): self.r = Repo()
    def test_one_zone_commit_passes(self):
        sha = self.r.commit({"dyad/a.md": "x"})
        self.assertEqual(c.check_commit(sha, cwd=self.r.d), [])
    def test_cross_zone_commit_fails(self):
        sha = self.r.commit({"dyad/a.md": "x", "CLAUDE.md": "y"})
        self.assertTrue(any("multiple zones" in f for f in c.check_commit(sha, cwd=self.r.d)))
    def test_claude_adapter_rides_with_host_frame(self):
        """#152: a slash command and CLAUDE.md are one zone (infra)."""
        sha = self.r.commit({".claude/commands/x.md": "x", "CLAUDE.md": "y"})
        self.assertEqual(c.check_commit(sha, cwd=self.r.d), [])
    def test_claude_adapter_never_mixes_with_package(self):
        """#152: an adapter and the procedure it invokes (dyad/...) are separate transactions."""
        sha = self.r.commit({".claude/commands/x.md": "x", "dyad/playbooks/x.md": "y"})
        fails = c.check_commit(sha, cwd=self.r.d)
        self.assertTrue(any("multiple zones: agent infra" in f for f in fails), fails)
    def test_craft_zone_never_mixes_with_instance(self):
        sha = self.r.commit({"crafts/a/VERSION": "0.1.0", "workstation-corpus/x.md": "y"})
        self.assertTrue(any("multiple zones" in f for f in c.check_commit(sha, cwd=self.r.d)))
    def test_unclassified_add_fails_and_delete_passes(self):
        sha = self.r.commit({"stray.txt": "x"})
        self.assertTrue(any("unclassified" in f for f in c.check_commit(sha, cwd=self.r.d)))
        sha2 = self.r.commit({"stray.txt": None})
        self.assertEqual(c.check_commit(sha2, cwd=self.r.d), [])
    def test_range_catches_mixed_whole_diff(self):
        base = self.r.commit({"README.md": "r"})
        self.r.commit({"dyad/a.md": "x"}); head = self.r.commit({"CLAUDE.md": "y"})
        fails = c.check_range(base, head, cwd=self.r.d)
        self.assertTrue(any("range" in f and "multiple zones" in f for f in fails))

    # #528: a criss-cross range (several merge bases) is judged by its merge's net diff
    def criss_cross(self, extra=None):
        """#569's shape: main lands a prerequisite `u` (agent) by merging it after its own commit `v`; the PR was
        stacked on `u`, adds an infra file, then merges `v`. Both `u` and `v` are merge bases of main and the PR."""
        r0 = self.r.commit({"README.md": "r"})
        sh("git", "branch", "-M", "main", cwd=self.r.d)
        sh("git", "checkout", "-q", "-b", "prereq", cwd=self.r.d); self.r.commit({"dyad/u.md": "u"})
        sh("git", "checkout", "-q", "main", cwd=self.r.d); v = self.r.commit({"dyad/v.md": "v"})
        sh("git", "checkout", "-q", "-b", "pr", "prereq", cwd=self.r.d)
        self.r.commit({".github/x.yml": "x"})
        if extra:
            self.r.commit(extra)   # its own single-zone commit: only the range sees the PR span two zones
        sh("git", "merge", "-q", "--no-ff", "-m", "merge main", v, cwd=self.r.d)
        head = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        sh("git", "checkout", "-q", "main", cwd=self.r.d)
        sh("git", "merge", "-q", "--no-ff", "-m", "land prereq", "prereq", cwd=self.r.d)
        base = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        self.assertEqual(len(c.merge_bases(base, head, cwd=self.r.d)), 2)
        return base, head
    def test_a_criss_cross_pr_is_judged_by_its_net_merge_diff(self):
        base, head = self.criss_cross()
        three_dot = c.check_paths("x", c.name_status(f"{base}...{head}", cwd=self.r.d), self.r.d)
        self.assertTrue(any("multiple zones" in f for f in three_dot), three_dot)   # the false FAIL #528 removes
        how, entries = c.range_diff(base, head, cwd=self.r.d)
        self.assertEqual((how, entries), ("net merge diff, 2 merge bases", [("A", ".github/x.yml")]))
        self.assertEqual(c.check_range(base, head, cwd=self.r.d), [])
        self.assertEqual(c.check_pr(self.r.d, base, head), [])
    def test_a_truly_mixed_criss_cross_pr_still_fails(self):
        base, head = self.criss_cross(extra={"dyad/x.md": "agent too"})
        self.assertEqual(c.check_commits(base, head, cwd=self.r.d), [])
        fails = c.check_range(base, head, cwd=self.r.d)
        self.assertEqual(len(fails), 1, fails)
        self.assertIn("(net merge diff, 2 merge bases)]: touches multiple zones: agent infra", fails[0])
    def test_one_merge_base_keeps_the_three_dot_diff(self):
        base = self.r.commit({"README.md": "r"}); head = self.r.commit({"dyad/a.md": "x"})
        self.assertEqual(c.range_diff(base, head, cwd=self.r.d), ("", [("A", "dyad/a.md")]))

    # #166: Rule-1 binds a commit and a PR; a push range is neither.
    def test_commits_mode_passes_a_stacked_push_the_range_mode_refuses(self):
        """Two single-zone commits in different zones: a correct push (commits), a refused PR (range)."""
        base = self.r.commit({"README.md": "r"})
        self.r.commit({"dyad/a.md": "x"}); head = self.r.commit({"CLAUDE.md": "y"})
        self.assertEqual(c.check_commits(base, head, cwd=self.r.d), [])
        self.assertEqual(c.check_transaction(self.r.d, base, head), [])        # the pre-push path
        fails = c.check_pr(self.r.d, base, head)                               # the PR path
        self.assertTrue(any("range" in f and "multiple zones" in f for f in fails), fails)
    def test_mixed_commit_fails_in_both_modes(self):
        base = self.r.commit({"README.md": "r"})
        head = self.r.commit({"dyad/a.md": "x", "CLAUDE.md": "y"})
        for fails in (c.check_commits(base, head, cwd=self.r.d), c.check_range(base, head, cwd=self.r.d),
                      c.check_transaction(self.r.d, base, head), c.check_pr(self.r.d, base, head)):
            self.assertTrue(any("commit" in f and "multiple zones" in f for f in fails), fails)
    def test_cli_names_the_mode_it_ran(self):
        base = self.r.commit({"README.md": "r"})
        self.r.commit({"dyad/a.md": "x"}); head = self.r.commit({"CLAUDE.md": "y"})
        run = lambda *a: subprocess.run([sys.executable, str(Path(c.__file__)), *a], cwd=self.r.d, capture_output=True, text=True)
        ok = run("commits", base, head)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr); self.assertIn("containment OK [commits]", ok.stdout)
        bad = run("range", base, head)
        self.assertEqual(bad.returncode, 1); self.assertIn("containment FAILED [range]", bad.stdout)
    def test_tree_flags_stray(self):
        self.r.commit({"dyad/a.md": "x", "stray/z.txt": "s"})
        self.assertEqual(len(c.check_tree(cwd=self.r.d)), 1)
    def test_contract_package_and_transaction(self):
        self.assertEqual((c.ENTITY, c.CORPUS, c.TRANSACTION, c.FIELDS), ("zone", "infra", True, ("zone", "pattern")))
        base = self.r.commit({"README.md": "r"}); self.r.commit({"dyad/a.md": "x"}); head = self.r.commit({"CLAUDE.md": "y"})
        self.assertEqual(c.check_package(self.r.d), [])
        self.assertEqual(c.check_transaction(self.r.d, base, head), [])   # #166: a push range is not a transaction
        self.assertTrue(any("multiple zones" in f for f in c.check_pr(self.r.d, base, head)))
        self.r.commit({"stray/z.txt": "s"}); self.assertEqual(len(c.check_package(self.r.d)), 1)
    def test_staged(self):
        self.r.commit({"dyad/a.md": "x"})
        (self.r.d / "dyad" / "b.md").write_text("b"); sh("git", "add", "dyad/b.md", cwd=self.r.d)
        self.assertEqual(c.check_staged(cwd=self.r.d), [])
    def conflicted_merge(self):
        """A merge of two branches touching different zones, stopped on a conflict: the index spans both zones."""
        self.r.commit({"README.md": "r"})
        sh("git", "checkout", "-q", "-b", "side", cwd=self.r.d)
        self.r.commit({"dyad/a.md": "side", "README.md": "side"})
        sh("git", "checkout", "-q", "-", cwd=self.r.d)
        self.r.commit({"CLAUDE.md": "main", "README.md": "main"})
        m = subprocess.run(["git", "merge", "-q", "--no-ff", "side"], cwd=self.r.d, capture_output=True, text=True)
        self.assertNotEqual(m.returncode, 0, "expected a conflict")
        (self.r.d / "README.md").write_text("resolved"); sh("git", "add", "README.md", cwd=self.r.d)
        self.assertTrue(c.merge_in_progress(self.r.d))
    def test_staged_skips_a_merge_commit(self):
        """#38: a merge commit is not a Rule-1 transaction (#166); the hook skips it, says so, and exits 0."""
        self.conflicted_merge()
        self.assertTrue(any("multiple zones" in f for f in c.check_paths("staged", c.name_status("--cached", cwd=self.r.d), self.r.d)))
        self.assertEqual(c.check_staged(cwd=self.r.d), [])
        r = subprocess.run([sys.executable, str(Path(c.__file__)), "staged"], cwd=self.r.d, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("containment SKIP [staged]: a merge commit is not a Rule-1 transaction", r.stdout)
        sh("git", "commit", "-q", "--no-edit", cwd=self.r.d)
        self.assertFalse(c.merge_in_progress(self.r.d))
    def test_staged_still_refuses_a_mixed_ordinary_commit(self):
        self.r.commit({"README.md": "r"})
        for rel in ("dyad/a.md", "CLAUDE.md"):
            (self.r.d / rel).parent.mkdir(parents=True, exist_ok=True); (self.r.d / rel).write_text("x")
            sh("git", "add", rel, cwd=self.r.d)
        self.assertFalse(c.merge_in_progress(self.r.d))
        self.assertTrue(any("multiple zones" in f for f in c.check_staged(cwd=self.r.d)))


class VerbTableTests(unittest.TestCase):
    """#25: the CLI verb table is a declared constant, and the lift out of `main` is behaviour-preserving."""
    def setUp(self): self.r = Repo()
    def run_cli(self, *a, cwd=None):
        return subprocess.run([sys.executable, str(Path(c.__file__)), *a], cwd=cwd or self.r.d, capture_output=True, text=True)

    def test_hook_verb_is_what_the_shipped_hook_passes(self):
        """The one surface this module cannot see: the bash hook. Read here so the constant is not a fiction."""
        hook = Path(c.__file__).resolve().parents[2] / "hooks" / "pre-commit"
        self.assertIn(f"containment.py\" {c.HOOK_VERB}", hook.read_text())

    def test_each_verb_dispatches_as_before(self):
        """The handlers take no cwd — as in `main`, they run against the process's own repo — so the
        equivalence is checked from inside the temp repo, where a cross-zone head gives them something
        to disagree about."""
        base = self.r.commit({"README.md": "r"})
        self.r.commit({"dyad/a.md": "x"}); head = self.r.commit({"CLAUDE.md": "y"})
        cwd = os.getcwd()
        try:
            os.chdir(self.r.d)
            self.assertEqual(c.VERBS["staged"]([]), c.check_staged())
            self.assertEqual(c.VERBS["commit"]([head]), c.check_commit(head))
            self.assertEqual(c.VERBS["commits"]([base, head]), c.check_commits(base, head))
            self.assertEqual(c.VERBS["range"]([base, head]), c.check_range(base, head))
            self.assertEqual(c.VERBS["tree"]([]), c.check_tree())
            self.assertTrue(any("multiple zones" in f for f in c.VERBS["range"]([base, head])))
        finally:
            os.chdir(cwd)

    def test_zones_prints_the_table_and_no_result_line(self):
        out = self.run_cli("zones")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("zone         pattern", out.stdout)
        for z in c.ZONE_NAMES:
            self.assertIn(z, out.stdout)
        self.assertNotIn("containment OK", out.stdout)      # `zones` reports no verdict, as before the lift
        self.assertIsNone(c.VERBS["zones"]([]))

    def test_unknown_verb_and_no_argv_both_exit_the_usage(self):
        for argv in (["bogus"], []):
            out = self.run_cli(*argv)
            self.assertEqual(out.returncode, 1, out.stdout)
            self.assertIn("containment.py staged", out.stderr)


DEFAULT_TABLE = [
    ("agent", "agent-corpus/*"), ("agent", "dyad/*"), ("workstation", "workstation-corpus/*"),
    ("preferences", "preferences-corpus/*"), ("craft", "crafts/*"), ("infra", ".github/*"),
    ("infra", ".githooks/*"), ("infra", "CLAUDE.md"), ("infra", "README.md"), ("infra", "LICENSE"),
    ("infra", ".gitignore"), ("infra", "BUNDLE.md"), ("infra", ".claude/*"), ("infra", "site/*"),
]
PREFS = """| key | value | allowed | read by |
|-----|-------|---------|---------|
| host-path | {path} | a repo-relative directory | Rule-1 |
| host-zone | {zone} | `workstation` \\| `infra` | Rule-1 |
"""

class HostRowTests(unittest.TestCase):
    """#175: the host row of the zone table is read from the preferences `host-path` / `host-zone`
    (env `DYAD_HOST` / `DYAD_HOST_ZONE` for tests); the defaults reproduce the five-zone table."""
    def setUp(self):
        self.prev = {k: os.environ.pop(k, None) for k in ("DYAD_HOST", "DYAD_HOST_ZONE")}
    def tearDown(self):
        for k, v in self.prev.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    def test_default_table_byte_identical(self):
        self.assertEqual(c.zones_for(), DEFAULT_TABLE)
        self.assertEqual(c.zone_names_for(), ("agent", "workstation", "preferences", "infra", "craft"))
        r = Repo()   # no preferences: the defaults
        self.assertEqual(c.table(r.d), DEFAULT_TABLE)
    def test_env_infra_host_gives_four_zones(self):
        os.environ["DYAD_HOST"], os.environ["DYAD_HOST_ZONE"] = "infrastructure", "infra"
        r = Repo(); t = c.table(r.d)
        self.assertEqual(t[c.HOST_ROW], ("infra", "infrastructure/*"))
        self.assertEqual({z for z, _ in t}, {"agent", "preferences", "infra", "craft"})
        self.assertEqual(c.zone_names_for("infra"), ("agent", "preferences", "infra", "craft"))
        self.assertEqual(c.classify("infrastructure/x.md", r.d), "infra")
        self.assertEqual(c.classify("workstation-corpus/x.md", r.d), "unclassified")
        self.assertEqual(c.classify("dyad/infrastructure/INFRASTRUCTURE.md", r.d), "agent")
    def test_preferences_drive_the_table_and_transactions(self):
        r = Repo()
        r.commit({"preferences-corpus/PREFERENCES.md": PREFS.format(path="infrastructure", zone="infra")})
        self.assertEqual(c.table(r.d)[c.HOST_ROW], ("infra", "infrastructure/*"))
        r.commit({"infrastructure/HOST.md": "h", "README.md": "r"})          # one zone: infra
        self.assertEqual(c.check_tree(cwd=r.d), [])
        base = sh("git", "rev-parse", "HEAD", cwd=r.d).strip()
        head = r.commit({"infrastructure/INFRASTRUCTURE.md": "i", "dyad/a.md": "x"})
        self.assertTrue(any("multiple zones: agent infra" in f for f in c.check_commits(base, head, cwd=r.d)))
    def test_bad_host_zone_raises(self):
        os.environ["DYAD_HOST_ZONE"] = "host"
        with self.assertRaises(ValueError):
            c.table(Repo().d)
    def test_infra_host_keeps_logical_corpus(self):
        os.environ["DYAD_HOST"], os.environ["DYAD_HOST_ZONE"] = "infrastructure", "infra"
        r = Repo()
        self.assertIn(dyadlib.HOST_CORPUS, c.corpora(r.d)); self.assertNotIn("workstation", {z for z, _ in c.table(r.d)})
        self.assertEqual(c.corpus_zone("workstation", r.d), "infra"); self.assertEqual(c.corpus_zone("agent", r.d), "agent")
        os.environ.pop("DYAD_HOST"); os.environ.pop("DYAD_HOST_ZONE")
        self.assertEqual(c.corpus_zone("workstation", r.d), "workstation")
    def test_zones_cli_unchanged_for_defaults(self):
        # the CLI prints the table of the repo it ships in (`ZONES`), so the defaults are pinned by env,
        # never assumed from the live preferences (#179: a four-zone system is a legal instance)
        env = dict(os.environ, DYAD_HOST=dyadlib.DEFAULT_HOST, DYAD_HOST_ZONE=dyadlib.DEFAULT_HOST_ZONE)
        out = subprocess.run([sys.executable, str(Path(c.__file__)), "zones"], cwd=Repo().d, env=env, capture_output=True, text=True).stdout
        self.assertEqual(out, "zone         pattern\n" + "".join(f"{z:<12} {p}\n" for z, p in DEFAULT_TABLE))
        env = {k: v for k, v in os.environ.items() if k not in ("DYAD_HOST", "DYAD_HOST_ZONE")}   # unpinned: the live repo's own table
        live = subprocess.run([sys.executable, str(Path(c.__file__)), "zones"], cwd=Repo().d, env=env, capture_output=True, text=True).stdout
        self.assertEqual(live, "zone         pattern\n" + "".join(f"{z:<12} {p}\n" for z, p in c.table(dyadlib.repo_root())))


FOUR_ZONE_INFRA = """| component | partition | version | purpose | license | replacement | profile |
|-----------|-----------|---------|---------|---------|-------------|---------|
| venv + pip (PyPI) | library | stdlib | builds the kernel's Python slice | PSF-2.0 / MIT | a system-wide install | operating |
"""

class FourZoneSystemTests(unittest.TestCase):
    """#179: end to end on a scratch system whose own preferences set `host-path: infrastructure`,
    `host-zone: infra` — the live package copied in, its guards run from that copy by path with no
    `DYAD_HOST*` in the environment, so they read the scratch tree's preferences exactly as that
    system's hooks would. #175 shipped tests that held only on dyad-system's defaults; this is the
    check that would have caught it."""
    @classmethod
    def setUpClass(cls):
        cls.env = {k: v for k, v in os.environ.items() if k not in ("DYAD_HOST", "DYAD_HOST_ZONE")}
        r = cls.r = Repo(); live = dyadlib.PKG.parent
        files = {rel: (live / rel).read_text() for rel in sh("git", "ls-files", "dyad", cwd=live).split()}
        files.update({
            "preferences-corpus/PREFERENCES.md": PREFS.format(path="infrastructure", zone="infra"),
            "infrastructure/INFRASTRUCTURE.md": FOUR_ZONE_INFRA, "infrastructure/HOST.md": "# Host\n",
            "CLAUDE.md": "@dyad/CLAUDE.md\n"})
        for rel, text in files.items():
            p = r.d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
            if (live / rel).is_file() and os.access(live / rel, os.X_OK): p.chmod(0o755)
        sh("git", "add", "-A", cwd=r.d); sh("git", "commit", "-qm", "four-zone system", cwd=r.d)
    def guard(self, name, *args):
        return subprocess.run([sys.executable, str(self.r.d / "dyad" / "guards" / "infra" / f"{name}.py"), *args],
                              cwd=self.r.d, env=self.env, capture_output=True, text=True)
    def test_zone_guard_sees_four_zones(self):
        out = self.guard("containment", "zones")
        self.assertEqual(out.returncode, 0, out.stderr)
        rows = [l.split() for l in out.stdout.splitlines()[1:]]
        self.assertIn(["infra", "infrastructure/*"], rows)
        self.assertEqual({z for z, _ in rows}, {"agent", "preferences", "infra", "craft"})
        self.assertEqual(c.classify("infrastructure/x", self.r.d), "infra")
        tree = self.guard("containment", "tree")
        self.assertEqual(tree.returncode, 0, tree.stdout + tree.stderr)
    def test_zone_guard_one_infra_commit_passes(self):
        base = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        head = self.r.commit({"infrastructure/HOST.md": "# Host\nkernel\n", "CLAUDE.md": "@dyad/CLAUDE.md\n\n"})
        out = self.guard("containment", "commits", base, head)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
    def test_manifest_guard_loads_the_instance_row(self):
        out = self.guard("manifest")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertNotIn("FAIL", out.stdout + out.stderr)
        inf = dyadlib.load_guard("infra", "manifest")
        with unittest.mock.patch.dict(os.environ, {}, clear=False):   # restored after, whatever the caller set
            for k in ("DYAD_HOST", "DYAD_HOST_ZONE"): os.environ.pop(k, None)
            rows, msgs = inf.manifest_rows(self.r.d / "dyad", self.r.d)
        self.assertEqual(msgs, [])
        self.assertEqual([s for s, _ in rows if s != "the manifest"], ["infrastructure/INFRASTRUCTURE.md"])

if __name__ == "__main__":
    unittest.main()
