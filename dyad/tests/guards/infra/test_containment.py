import subprocess, sys, tempfile, unittest
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

class TransactionTests(unittest.TestCase):
    def setUp(self): self.r = Repo()
    def test_one_zone_commit_passes(self):
        sha = self.r.commit({"dyad/a.md": "x"})
        self.assertEqual(c.check_commit(sha, cwd=self.r.d), [])
    def test_cross_zone_commit_fails(self):
        sha = self.r.commit({"dyad/a.md": "x", "CLAUDE.md": "y"})
        self.assertTrue(any("multiple zones" in f for f in c.check_commit(sha, cwd=self.r.d)))
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


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(c, "core", c.CORPUS)
        self.assertEqual(dyadlib.check_invariants(c, extra), len(c.INVARIANTS) + 4)
        names = [n for n, _ in c.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
