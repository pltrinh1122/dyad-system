"""merges.py (the merge guard, entity `merge`; d-work #541, R2 and R5): each first-parent merge's tree is `git
merge-tree` of its parents (a), and its second parent is named by an operative `Y done` in the ledger at its first
parent (b). Every case builds a scratch repo whose ledger holds row 9 and merges a PR branch into `main`: a true merge
named by a `Y done` passes; a doctored merge (a file added in the merge commit itself) warns, listing the path; a
conflict resolved warns, listing the conflicted path; a merge no `Y done` names warns; a `Y done` revoked by a later
`N` warns; a `Y release` written after the merge does not void its `Y`; a ledger-only merge and `main` merged into a
branch name no `Y`; package mode reads only merges since `SINCE` and skips a clone without it; everything is a
warning; and the contract holds."""
import os, subprocess, sys, tempfile, shutil, unittest, unittest.mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
mg = dyadlib.load_guard("agent", "merges")
INST = "agent-corpus"
ROW = "id: 9\ntitle: nine\nopened: 2026-10-31\nstate: planned\ndisposed: {disposed}\nrefs: \n"


def sh(d, *a):
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=dyadlib.git_env())
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class World(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        sh(self.d, "init", "-q", "-b", "main")
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            sh(self.d, "config", k, v)
        self.write({"dyad/a.txt": "a\n", f"{INST}/d-work/rows/9.md": ROW.format(disposed="2026-10-31 Y plan")}, "seed")
        self.base = sh(self.d, "rev-parse", "HEAD")

    def write(self, files, msg):
        for rel, text in files.items():
            p = self.d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
        sh(self.d, "add", "-A"); sh(self.d, "commit", "-qm", msg)
        return sh(self.d, "rev-parse", "HEAD")

    def pr(self, files, name="pr"):
        """A PR branch off `main`'s tip with `files`; its head. `main` is checked out again after."""
        sh(self.d, "checkout", "-q", "-b", name)
        head = self.write(files, f"{name} work")
        sh(self.d, "checkout", "-q", "main")
        return head

    def record(self, disposed):
        return self.write({f"{INST}/d-work/rows/9.md": ROW.format(disposed=disposed)}, "ledger: #9")

    def done(self, head, pr=7):
        return f"2026-10-31 Y plan; 2026-10-31 Y done (merges PR #{pr} at {head})"

    def merge(self, head, extra=None):
        """`git merge --no-ff head` onto main; with `extra`, files added in the merge commit itself (doctored)."""
        if extra is None:
            sh(self.d, "merge", "-q", "--no-ff", "-m", "merge", head)
        else:
            sh(self.d, "merge", "-q", "--no-ff", "--no-commit", head)
            for rel, text in extra.items():
                (self.d / rel).parent.mkdir(parents=True, exist_ok=True); (self.d / rel).write_text(text)
            sh(self.d, "add", "-A"); sh(self.d, "commit", "-qm", "merge (doctored)")
        return sh(self.d, "rev-parse", "HEAD")

    def judged(self, base=None):
        return mg.check_transaction(self.d, base or self.base, "HEAD")


class MergeGuardTests(World):
    def test_a_true_merge_named_by_a_y_done_passes(self):
        head = self.pr({"dyad/b.txt": "b\n"})
        self.record(self.done(head))
        self.merge(head)
        self.assertEqual(self.judged(), [])

    def test_a_short_recorded_head_names_it_too(self):
        head = self.pr({"dyad/b.txt": "b\n"})
        self.record(self.done(head[:12]))
        self.merge(head)
        self.assertEqual(self.judged(), [])

    def test_a_doctored_merge_warns_listing_the_path(self):
        head = self.pr({"dyad/b.txt": "b\n"})
        self.record(self.done(head))
        sha = self.merge(head, extra={"dyad/evil.txt": "not in either parent\n"})
        msgs = self.judged()
        self.assertEqual(len(msgs), 1, msgs)
        self.assertTrue(msgs[0].startswith(f"warning: merge {sha[:12]}'s tree is not the merge of its parents (a clean merge)"), msgs)
        self.assertIn("1 path(s): dyad/evil.txt", msgs[0])

    def test_a_resolved_conflict_warns_listing_the_conflicted_path(self):
        head = self.pr({"dyad/a.txt": "pr's a\n"})
        self.write({"dyad/a.txt": "main's a\n"}, "main a")
        self.record(self.done(head))
        r = subprocess.run(["git", "merge", "-q", "--no-ff", head], cwd=self.d, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        (self.d / "dyad" / "a.txt").write_text("resolved\n"); sh(self.d, "add", "-A"); sh(self.d, "commit", "-qm", "merge")
        msgs = self.judged()
        self.assertEqual(len(msgs), 1, msgs)
        self.assertIn("(a conflicted merge, resolved)", msgs[0]); self.assertIn("dyad/a.txt", msgs[0])

    def test_a_merge_no_y_done_names_warns(self):
        head = self.pr({"dyad/b.txt": "b\n"})
        sha = self.merge(head)
        msgs = self.judged()
        self.assertEqual(msgs, [f"warning: merge {sha[:12]} brings in {head[:12]}, which no operative Y done names "
                                f"(no row's last disposition is a `Y done` naming it; Rule-2 Binding, #541 A5)"])

    def test_a_revoked_y_done_warns(self):
        head = self.pr({"dyad/b.txt": "b\n"})
        self.record(self.done(head) + "; 2026-10-31 N hold")
        self.merge(head)
        self.assertEqual(len(self.judged()), 1)

    def test_a_y_release_written_after_the_merge_does_not_void_its_y(self):
        head = self.pr({"dyad/b.txt": "b\n"})
        self.record(self.done(head))
        self.merge(head)
        self.record(self.done(head) + "; 2026-10-31 Y release v9.9.9")
        self.assertEqual(self.judged(), [])

    def test_a_ledger_only_merge_and_main_into_a_branch_name_no_y(self):
        head = self.pr({f"{INST}/d-work/rows/10.md": ROW.format(disposed="").replace("id: 9", "id: 10")})
        self.merge(head)                                           # ledger-only: clerical, no Y
        self.assertEqual(self.judged(), [])
        tip = sh(self.d, "rev-parse", "HEAD")
        side = self.pr({"dyad/c.txt": "c\n"}, name="side")
        self.write({"dyad/d.txt": "d\n"}, "main moves")
        main = sh(self.d, "rev-parse", "HEAD")
        sh(self.d, "checkout", "-q", "side"); sh(self.d, "merge", "-q", "--no-ff", "-m", "bring main", "main")
        self.assertEqual(mg.check_transaction(self.d, main, "HEAD"), [])   # a branch push: main brought in
        self.assertNotEqual(tip, side)

    def test_package_mode_reads_merges_since_SINCE_and_skips_without_it(self):
        head = self.pr({"dyad/b.txt": "b\n"})
        self.merge(head)                                           # unnamed: package mode warns once SINCE is here
        self.assertEqual(mg.check_package(self.d), [])            # the real SINCE is not in this repo: nothing judged
        self.assertIn("is not in this clone", mg.summary(self.d))
        with unittest.mock.patch.object(mg, "SINCE", self.base):
            msgs = mg.check_package(self.d)
            self.assertEqual(len(msgs), 1, msgs); self.assertIn("no operative Y done names", msgs[0])
            self.assertEqual(mg.summary(self.d), f"1 merge(s) on HEAD since {self.base[:12]}")

    def test_everything_is_a_warning(self):
        head = self.pr({"dyad/b.txt": "b\n"})
        self.merge(head, extra={"dyad/evil.txt": "x\n"})
        msgs = self.judged()
        self.assertEqual(len(msgs), 2)
        self.assertTrue(all(m.startswith("warning:") for m in msgs), msgs)

    def test_contract(self):
        self.assertEqual((mg.ENTITY, mg.CORPUS, mg.TRANSACTION), ("merge", "agent", True))
        self.assertIsNone(dyadlib.contract_problem(mg, "core", "agent"))
        self.assertEqual(dyadlib.check_invariants(mg), len(mg.INVARIANTS))
        self.assertEqual([f[0] for f in mg.describe(self.d)["fields"]], list(mg.FIELDS))


if __name__ == "__main__":
    unittest.main()
