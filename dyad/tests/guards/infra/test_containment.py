import os, subprocess, sys, tempfile, unittest
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
    def test_modes_are_declared(self):
        self.assertEqual((c.TRANSACTION_MODE, c.PR_MODE), ("commits", "range"))
        self.assertLessEqual({c.TRANSACTION_MODE, c.PR_MODE}, set(c.MODES))
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


class VerbTableTests(unittest.TestCase):
    """#25: the CLI verb table is a declared constant, and the lift out of `main` is behaviour-preserving."""
    def setUp(self): self.r = Repo()
    def run_cli(self, *a, cwd=None):
        return subprocess.run([sys.executable, str(Path(c.__file__)), *a], cwd=cwd or self.r.d, capture_output=True, text=True)

    def test_every_verb_of_the_usage_block_is_in_the_table(self):
        """The docstring is the user-facing contract; the table is the code's. They agree."""
        usage = [l.split()[1] for l in (c.__doc__ or "").splitlines()
                 if l.strip().startswith("containment.py ")]
        self.assertEqual(sorted(usage), sorted(c.VERBS))
        self.assertEqual(sorted(c.VERBS), ["commit", "commits", "range", "staged", "tree", "zones"])

    def test_hook_verb_and_modes_are_verbs(self):
        self.assertEqual(c.HOOK_VERB, "staged")
        self.assertIn(c.HOOK_VERB, c.VERBS)
        self.assertLessEqual(set(c.MODES), set(c.VERBS))

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
    ("infra", ".gitignore"), ("infra", "BUNDLE.md"), ("infra", ".claude/*"),
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
        out = subprocess.run([sys.executable, str(Path(c.__file__)), "zones"], cwd=Repo().d, capture_output=True, text=True).stdout
        self.assertEqual(out, "zone         pattern\n" + "".join(f"{z:<12} {p}\n" for z, p in DEFAULT_TABLE))


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(c, "core", c.CORPUS)
        self.assertEqual(dyadlib.check_invariants(c, extra), len(c.INVARIANTS) + 4)
        names = [n for n, _ in c.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
