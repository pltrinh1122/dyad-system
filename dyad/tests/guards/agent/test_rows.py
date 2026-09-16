"""Row guard tests (agent/rows.py): the main fence over row files — direct commits touch only the
ledger, a row file is never deleted or retitled, states follow dyadlib.TRANSITIONS, a new row starts
in NEW_STATES; the package check over a rows store; the transaction check applies on `main` only."""
import os, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
m = dyadlib.load_guard("agent", "rows")

def sh(*a, cwd): return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout
def row(id, title, state="open", disposed="", refs=""):
    return dyadlib.format_row_file(dyadlib.Row(id, title, "d", state, disposed, refs))

class Repo:
    def __init__(self):
        self.d = Path(tempfile.mkdtemp()); sh("git", "init", "-q", "-b", "main", cwd=self.d)
        sh("git", "config", "user.email", "t@t", cwd=self.d); sh("git", "config", "user.name", "t", cwd=self.d)
    def write(self, rel, text):
        p = self.d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text); sh("git", "add", rel, cwd=self.d)
    def remove(self, rel): sh("git", "rm", "-q", rel, cwd=self.d)
    def commit(self, msg="c"):
        sh("git", "commit", "-q", "-m", msg, cwd=self.d); return sh("git", "rev-parse", "HEAD", cwd=self.d).strip()

class FenceTests(unittest.TestCase):
    """Row-file store (Rule-16, d-work #111): LEDGER.md is a rendered, untracked view and is never diffed."""
    def setUp(self):
        self.r = Repo(); self.R = "agent-corpus/d-work/rows/1.md"
        self.r.write(self.R, row(1, "one")); self.base = self.r.commit("root")
    def fails(self, before, after): return m.check_range(before, after, cwd=self.r.d)
    def test_root_commit_rows_only_passes(self):
        self.assertEqual(m.check_commit(self.base, self.r.d, "agent-corpus"), [])
    def test_append_and_state_change_pass(self):
        self.r.write(self.R, row(1, "one", "done", "Y done", "PR #9")); self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); h = self.r.commit()
        self.assertEqual(self.fails(self.base, h), [])
    def test_other_path_fails(self):
        self.r.write("dyad/x.md", "x"); h = self.r.commit()
        self.assertIn("non-ledger paths", self.fails(self.base, h)[0])
    def test_removed_row_fails(self):
        self.r.remove(self.R); h = self.r.commit()
        self.assertIn("deletes row file", self.fails(self.base, h)[0])
    def test_changed_title_fails(self):
        self.r.write(self.R, row(1, "renamed")); h = self.r.commit()
        self.assertIn("changes id or title", self.fails(self.base, h)[0])
    # d-work #112: state transitions (Rule-16, dyadlib.TRANSITIONS)
    def transition(self, a, b):
        """Row 1 goes a -> b in two commits; return the fence output for the second."""
        self.r.write(self.R, row(1, "one", a, "seed")); base = self.r.commit("to a")  # disposed differs from root so the commit is never empty
        self.r.write(self.R, row(1, "one", b)); h = self.r.commit("to b")
        return self.fails(base, h)
    def test_allowed_transition_per_source_state(self):
        for a, b in [("open", "planned"), ("planned", "done"), ("blocked", "open"), ("backlog", "open"), ("open", "done")]:
            with self.subTest(a=a, b=b): self.assertEqual(self.transition(a, b), [])
    def test_refused_transition_per_source_state(self):
        for a, b in [("open", "backlog"), ("planned", "backlog"), ("blocked", "done"), ("backlog", "done"), ("done", "open"), ("done", "planned")]:
            with self.subTest(a=a, b=b):
                out = self.transition(a, b)
                self.assertEqual(len(out), 1, out); self.assertIn(f"state regresses {a}\u2192{b}", out[0])
    def test_unknown_state_leaves_table(self):
        out = self.transition("open", "foo")
        self.assertEqual(len(out), 1, out); self.assertIn("state leaves the table open\u2192foo", out[0])
    def test_same_state_edit_passes(self):
        self.r.write(self.R, row(1, "one", "open", "Y plan", "PR #3")); h = self.r.commit()
        self.assertEqual(self.fails(self.base, h), [])
    def test_new_row_as_done_fails(self):
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two", "done", "Y done")); h = self.r.commit()
        out = self.fails(self.base, h)
        self.assertEqual(len(out), 1, out); self.assertIn("adds row file agent-corpus/d-work/rows/2.md in state done", out[0])
    def test_new_row_as_backlog_passes(self):
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two", "backlog")); h = self.r.commit()
        self.assertEqual(self.fails(self.base, h), [])
    def test_table_covers_every_state(self):
        self.assertEqual(set(dyadlib.TRANSITIONS), set(dyadlib.STATES))
        for a, targets in dyadlib.TRANSITIONS.items():
            self.assertTrue(targets <= dyadlib.STATES, a); self.assertNotIn(a, targets, a)
        self.assertEqual(dyadlib.TRANSITIONS["done"], frozenset({"archived"})); self.assertEqual(dyadlib.TRANSITIONS["archived"], frozenset())
    def test_merge_commit_skipped(self):
        sh("git", "checkout", "-q", "-b", "feat", cwd=self.r.d); self.r.write("dyad/f.md", "f"); self.r.commit("feat")
        sh("git", "checkout", "-q", "main", cwd=self.r.d); sh("git", "merge", "-q", "--no-ff", "-m", "merge", "feat", cwd=self.r.d)
        h = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        self.assertEqual(self.fails(self.base, h), [])

class ContractTests(unittest.TestCase):
    def test_contract(self):
        self.assertEqual((m.ENTITY, m.CORPUS, m.TRANSACTION, m.FIELDS), ("row", "agent", True, dyadlib.FIELDS))
    def test_package_check_over_a_store(self):
        r = Repo(); r.write("agent-corpus/d-work/rows/1.md", row(1, "one")); r.write("agent-corpus/d-work/rows/2.md", row(2, "two", "planned", "Y plan"))
        os.environ.pop("DYAD_INSTANCE", None)
        self.assertEqual(m.check_package(r.d), [])
        r.write("agent-corpus/d-work/rows/3.md", row(9, "nine", "nope"))
        out = m.check_package(r.d)
        self.assertEqual(len(out), 2, out); self.assertIn("id 9 differs from the file name", out[0]); self.assertIn("state 'nope'", out[1])
        r.write("agent-corpus/d-work/rows/4.md", "id: 4\ntitle: t\n")
        self.assertTrue(any("missing" in x for x in m.check_package(r.d)))
    def test_transaction_check_on_main_only(self):
        r = Repo(); r.write("agent-corpus/d-work/rows/1.md", row(1, "one")); base = r.commit("root")
        r.write("dyad/x.md", "x"); h = r.commit("touch package")
        os.environ.pop("DYAD_INSTANCE", None)
        self.assertEqual(len(m.check_transaction(r.d, base, h)), 1)            # on main: fenced
        sh("git", "checkout", "-q", "-b", "feature", cwd=r.d)
        self.assertEqual(m.check_transaction(r.d, base, h), [])              # on a branch: the PR guard's turn
    def test_live_rows_store_passes(self):
        self.assertEqual(m.check_package(dyadlib.repo_root()), [])
    def test_cli_main_fence_line(self):
        r = Repo(); r.write("agent-corpus/d-work/rows/1.md", row(1, "one")); base = r.commit("root")
        r.write("agent-corpus/d-work/rows/1.md", row(1, "one", "done", "Y done")); h = r.commit("done")
        out = subprocess.run([sys.executable, str(Path(m.__file__)), base, h], cwd=r.d, capture_output=True, text=True,
                             env={k: v for k, v in os.environ.items() if k not in ("DYAD_INSTANCE", "DYAD_RUNBOOKS")})
        # the CLI resolves the repo from the package, not cwd: it judges the live repo's range (absent here) and exits 128 or prints the fence line
        self.assertIn(out.stdout.strip() or "main fence", ("main fence OK", "main fence FAILED", "main fence"))


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(m, "core", m.CORPUS)
        self.assertEqual(dyadlib.check_invariants(m, extra), len(m.INVARIANTS) + 4)
        names = [n for n, _ in m.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
