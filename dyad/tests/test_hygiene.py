"""Backlog hygiene (scripts/hygiene.py, d-work #565), over a scratch repo whose ledger holds a handful of rows:
- I1 untouched: a backlog row no commit touched in HYGIENE_STALE_DAYS is a finding; a fresh one is not;
- I2 malformed title: an empty title, or one starting with `-`;
- I4 orphaned: a backlog child whose parent row is terminal;
- I12 worked: a commit on an `origin/*` branch citing `d-work #N` for a backlog row;
- the ranking lists similar rows as candidates, skips siblings under one parent and drops boilerplate tokens;
- placement: no runner path (`check`, `--evidence`, `--corroborate`, the gate) and no guard reaches it;
- every line is information, never a disposition shape (the module's TREE_INVARIANTS)."""
import os, shutil, subprocess, sys, tempfile, time, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
hy = dyadlib.load_module(PKG / "scripts" / "hygiene.py", "hygiene")
INST = "agent-corpus"
ROW = "id: {id}\ntitle: {title}\nopened: 2026-09-01\nstate: {state}\ndisposed: {disposed}\nrefs: {refs}\n"
OLD = "2026-09-01T00:00:00Z"


def git(d, *a, date=None):
    env = {**dyadlib.git_env(), **({"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date} if date else {})}
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=env)
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class HygieneTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        git(self.d, "init", "-q", "-b", "main")
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            git(self.d, "config", k, v)

    def row(self, id, title, state="backlog", refs="", plan=None, date=None):
        rows = self.d / INST / "d-work" / "rows"; rows.mkdir(parents=True, exist_ok=True)
        (rows / f"{id}.md").write_text(ROW.format(id=id, title=title, state=state, refs=refs,
                                                  disposed="2026-09-01 Y backlog" if state == "backlog" else "2026-09-01 Y plan"))
        if plan:
            plans = self.d / INST / "d-work" / "plans"; plans.mkdir(parents=True, exist_ok=True)
            (plans / f"{id}.md").write_text(plan)
        git(self.d, "add", "-A"); git(self.d, "commit", "-qm", f"ledger: #{id}", date=date)

    def run_it(self):
        return hy.hygiene(self.d, "HEAD", time.time())

    def test_structural_findings(self):
        self.row(1, "a parent long done", state="done")
        self.row(2, "an old backlog row about widgets", date=OLD)
        self.row(3, "a fresh backlog row about gadgets")
        self.row(4, "--backlog")
        self.row(5, "a child of a done parent", refs="parent #1")
        git(self.d, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(self.d, "switch", "-qc", "feature"); (self.d / "x.txt").write_text("x\n"); git(self.d, "add", "-A")
        git(self.d, "commit", "-qm", "work on it (d-work #3)"); git(self.d, "update-ref", "refs/remotes/origin/feature", "HEAD")
        git(self.d, "switch", "-q", "main")
        findings, _ = self.run_it()
        self.assertTrue(any(f.startswith("hygiene I1 untouched: backlog row #2 ") for f in findings), findings)
        self.assertFalse(any("I1 untouched: backlog row #3 " in f for f in findings))
        self.assertIn("hygiene I2 malformed title: backlog row #4 has the title '--backlog'", findings)
        self.assertIn("hygiene I4 orphaned: backlog row #5's parent #1 is done", findings)
        self.assertTrue(any(f.startswith("hygiene I12 worked: backlog row #3 is cited by ") and f.endswith("on origin/feature")
                            for f in findings), findings)
        inbox = dyadlib.load_guard("agent", "inbox")
        self.assertFalse(any(inbox.DISPOSITION.search(f) for f in findings))      # information only

    def test_ranking_lists_near_duplicates_and_skips_siblings(self):
        self.row(10, "the parent", state="planned")
        for i, t in enumerate(["sweep the archive tags against their release entries",
                               "reconcile release tags against the archive entries", "an unrelated row about fonts",
                               "a second unrelated row about colours", "a third unrelated row about spacing",
                               "a fourth unrelated row about margins", "a fifth unrelated row about borders"], 11):
            self.row(i, t)
        self.row(20, "mode W fence: sibling one under the parent", refs="parent #10")
        self.row(21, "mode W fence: sibling two under the parent", refs="parent #10")
        _, candidates = self.run_it()
        self.assertTrue(any(c.startswith("candidate: #11 and #12 similar") for c in candidates), candidates)
        self.assertFalse(any("#20 and #21" in c for c in candidates))            # siblings share boilerplate (A5)

    def test_placement_no_runner_path_or_guard_reaches_it(self):
        runner = (PKG / "scripts" / "package.py").read_text()
        self.assertNotIn("hygiene", runner)
        self.assertFalse(any("hygiene" in str(p) for p in dyadlib.guard_files(PKG)))
        self.assertIn("hygiene_mod.hygiene(", (PKG / "scripts" / "automaton.py").read_text())

    def test_invariants(self):
        self.assertEqual(dyadlib.check_invariants(hy), len(hy.INVARIANTS) + len(hy.TREE_INVARIANTS))


if __name__ == "__main__":
    unittest.main()
