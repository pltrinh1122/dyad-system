"""Row guard tests (agent/rows.py): the main fence over row files — direct commits touch only the
ledger, a row file is never deleted or retitled, states follow dyadlib.TRANSITIONS, a new row starts
in NEW_STATES; the package check over a rows store; the transaction check applies on `main` only."""
import os, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
m = dyadlib.load_guard("agent", "rows")

def sh(*a, cwd): return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout
def row(id, title, state="open", disposed="", refs="", mode="explicit"):
    return dyadlib.format_row_file(dyadlib.Row(id, title, "d", state, disposed, refs, mode))

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
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y done", "PR #9")); self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); h = self.r.commit()
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
        seed = f"2026-01-01 Y seed {a} to {b}"   # unique per case, so neither commit is ever empty
        self.r.write(self.R, row(1, "one", a, seed)); base = self.r.commit("to a")
        # #202: a row reaches `done` only with a `Y done` entry already on it, so the fixture carries one
        # wherever `done` is the target; the transition under test is still the only thing that changes.
        d = f"{seed}; 2026-01-02 Y done" if b == "done" else seed
        self.r.write(self.R, row(1, "one", b, d)); h = self.r.commit("to b")
        return self.fails(base, h)
    def test_allowed_transition_per_source_state(self):
        for a, b in [("open", "planned"), ("planned", "done"), ("blocked", "open"), ("backlog", "open"), ("open", "done"),
                     ("backlog", "archived"), ("done", "archived")]:   # #290: the board's drain
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
        self.r.write(self.R, row(1, "one", "open", "2026-01-01 Y plan", "PR #3")); h = self.r.commit()
        self.assertEqual(self.fails(self.base, h), [])
    def test_new_row_as_done_fails(self):
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two", "done", "2026-01-01 Y done")); h = self.r.commit()
        out = self.fails(self.base, h)
        self.assertEqual(len(out), 1, out); self.assertIn("adds row file agent-corpus/d-work/rows/2.md in state done", out[0])
    def test_new_row_as_backlog_passes(self):
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two", "backlog")); h = self.r.commit()
        self.assertEqual(self.fails(self.base, h), [])
    def test_merge_commit_skipped(self):
        sh("git", "checkout", "-q", "-b", "feat", cwd=self.r.d); self.r.write("dyad/f.md", "f"); self.r.commit("feat")
        sh("git", "checkout", "-q", "main", cwd=self.r.d); sh("git", "merge", "-q", "--no-ff", "-m", "merge", "feat", cwd=self.r.d)
        h = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        self.assertEqual(self.fails(self.base, h), [])

class ModeFenceTests(unittest.TestCase):
    """d-work #290: `mode` is append-only like id and title. A row is born in its mode or not at all —
    `implicit`→`explicit` would revoke a mandate by an edit and `explicit`→`implicit` would grant one after
    the Operator read the plan that bounds it. A row born `implicit` is born `open` carrying exactly one
    entry `<date> Y plan (mandate #<id>)`, since implicit mode takes no disposition of its own."""
    R = "agent-corpus/d-work/rows/1.md"
    MANDATE = "2026-10-14 Y plan (mandate #290)"
    def setUp(self):
        self.r = Repo(); os.environ.pop("DYAD_INSTANCE", None)
        self.r.write(self.R, row(1, "one")); self.base = self.r.commit("root")
    def fails(self, before, after): return m.check_range(before, after, cwd=self.r.d)
    def add(self, state="open", disposed=MANDATE, mode="implicit"):
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two", state, disposed, "parent #290", mode))
        return self.fails(self.base, self.r.commit("accrete"))
    def test_a_row_born_implicit_open_under_its_mandate_passes(self):
        self.assertEqual(self.add(), [])
    def test_a_row_born_implicit_as_backlog_fails(self):
        out = self.add(state="backlog")
        self.assertEqual(len(out), 1, out)
        self.assertIn("adds implicit-mode row file agent-corpus/d-work/rows/2.md in state backlog", out[0])
        self.assertIn("born open", out[0])
    def test_a_row_born_implicit_without_its_mandate_entry_fails(self):
        for disposed in ("", "2026-10-14 Y plan", "2026-10-14 Y plan (mandate #290); 2026-10-14 Y done",
                         "2026-10-14 Y backlog (mandate #290)", "2026-10-14 Y plan (mandate #290) and more"):
            with self.subTest(disposed=disposed):
                sh("git", "reset", "-q", "--hard", self.base, cwd=self.r.d)
                out = self.add(disposed=disposed)
                self.assertTrue(any("not one entry `<date> Y plan (mandate #<id>)`" in o for o in out), out)
                self.assertTrue(all("agent-corpus/d-work/rows/2.md" in o for o in out), out)
    def test_a_row_born_explicit_is_judged_as_before(self):
        self.assertEqual(self.add(disposed="", mode="explicit"), [])       # #290 adds nothing to the explicit path
    def test_mode_never_changes_after_the_commit_that_adds_the_row(self):
        for a, b, why in (("implicit", "explicit", "never revoked by an edit"),
                          ("explicit", "implicit", "never made implicit later")):
            with self.subTest(a=a, b=b):
                sh("git", "reset", "-q", "--hard", self.base, cwd=self.r.d)
                self.r.write(self.R, row(1, "one", "open", self.MANDATE, "", a)); base = self.r.commit("born " + a)
                self.r.write(self.R, row(1, "one", "open", self.MANDATE, "", b)); h = self.r.commit("rewrite mode")
                out = self.fails(base, h)
                self.assertEqual(len(out), 1, out)
                self.assertIn(f"changes mode of row file {self.R} {a}→{b}", out[0]); self.assertIn(why, out[0])
    def test_an_implicit_rows_own_state_change_passes(self):
        self.r.write(self.R, row(1, "one", "open", self.MANDATE, "", "implicit")); base = self.r.commit("born implicit")
        self.r.write(self.R, row(1, "one", "done", self.MANDATE + "; 2026-10-15 Y done", "PR #9", "implicit")); h = self.r.commit("done")
        self.assertEqual(self.fails(base, h), [])
    def test_a_mode_rewritten_resolving_a_merge_fails(self):
        """The per-commit walk skips merges, so the merge is judged against both parents (#191's hole, #290's field)."""
        self.r.write(self.R, row(1, "one", "open", self.MANDATE, "", "implicit")); born = self.r.commit("born implicit")
        sh("git", "checkout", "-q", "-b", "ledger", cwd=self.r.d)
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); self.r.commit("branch row")
        sh("git", "checkout", "-q", "main", cwd=self.r.d)
        self.r.write(self.R, row(1, "one", "planned", self.MANDATE, "", "implicit")); main_h = self.r.commit("planned on main")
        sh("git", "checkout", "-q", "ledger", cwd=self.r.d)
        sh("git", "merge", "-q", "--no-commit", "-s", "ours", "main", cwd=self.r.d)
        self.r.write(self.R, row(1, "one", "planned", self.MANDATE, "", "explicit"))   # the rewrite, hidden in the merge
        sh("git", "commit", "-qm", "merge main", cwd=self.r.d); h = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        out = m.check_transaction(self.r.d, main_h, h)
        self.assertTrue(any("merge" in o and "changes mode" in o and "implicit→explicit" in o for o in out), out)
        self.assertNotEqual(born, h)
    def test_an_unparseable_mode_is_the_package_checks_report(self):
        p = self.r.d / "agent-corpus" / "d-work" / "rows" / "2.md"
        p.write_text(row(2, "two") + "mode: automatic\n")
        self.assertTrue(any("not one of explicit implicit" in x for x in m.check_package(self.r.d)))

class ContractTests(unittest.TestCase):
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
    def test_cli_main_fence_line(self):
        r = Repo(); r.write("agent-corpus/d-work/rows/1.md", row(1, "one")); base = r.commit("root")
        r.write("agent-corpus/d-work/rows/1.md", row(1, "one", "done", "Y done")); h = r.commit("done")
        out = subprocess.run([sys.executable, str(Path(m.__file__)), base, h], cwd=r.d, capture_output=True, text=True,
                             env={k: v for k, v in os.environ.items() if k not in ("DYAD_INSTANCE", "DYAD_RUNBOOKS")})
        # the CLI resolves the repo from the package, not cwd: it judges the live repo's range (absent here) and exits 128 or prints the fence line
        self.assertIn(out.stdout.strip() or "main fence", ("main fence OK", "main fence FAILED", "main fence"))


class BranchIdCollisionTests(unittest.TestCase):
    """F2 (d-work #32): on a branch, `check_transaction` now runs `check_id_collisions` — nothing
    else caught two sessions racing the allocator to the same id before it reached a PR or merge."""
    def setUp(self):
        self.r = Repo()
        self.r.write("agent-corpus/d-work/rows/1.md", row(1, "one"))
        self.base = self.r.commit("root")
        sh("git", "checkout", "-q", "-b", "feature", cwd=self.r.d)
        os.environ.pop("DYAD_INSTANCE", None)
    def test_same_id_different_title_fails(self):
        self.r.write("agent-corpus/d-work/rows/1.md", row(1, "one but renamed on this branch"))
        h = self.r.commit("collide")
        out = m.check_id_collisions(self.r.d, self.base, h)
        self.assertEqual(len(out), 1, out)
        self.assertIn("id 1 already names", out[0]); self.assertIn("'one'", out[0])
    def test_same_id_same_title_passes(self):
        self.r.write("agent-corpus/d-work/rows/1.md", row(1, "one", "planned", "2026-01-01 Y plan"))
        h = self.r.commit("state change only")
        self.assertEqual(m.check_id_collisions(self.r.d, self.base, h), [])
    def test_new_id_passes(self):
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two"))
        h = self.r.commit("new row")
        self.assertEqual(m.check_id_collisions(self.r.d, self.base, h), [])
    def test_unrelated_change_passes(self):
        self.r.write("dyad/x.md", "x")
        h = self.r.commit("touch package")
        self.assertEqual(m.check_id_collisions(self.r.d, self.base, h), [])
    def test_malformed_head_row_is_skipped_not_crashed(self):
        self.r.write("agent-corpus/d-work/rows/1.md", "not: a valid row file at all\n")
        h = self.r.commit("garbage")
        self.assertEqual(m.check_id_collisions(self.r.d, self.base, h), [])
    def test_check_transaction_runs_it_on_a_branch(self):
        self.r.write("agent-corpus/d-work/rows/1.md", row(1, "one but renamed on this branch"))
        h = self.r.commit("collide")
        out = m.check_transaction(self.r.d, self.base, h)
        self.assertIn("id 1 already names", out[0])
        self.assertIn("changes id or title", out[1])   # #191: a ledger-only branch is fenced as `main` would fence it

class DisposedShapeTests(unittest.TestCase):
    """d-work #133: every `disposed` entry a range adds is `<date> <Y|N>[ text]` with balanced parentheses,
    on `main` (the fence, per commit) and on a branch (the whole diff); existing entries are never re-judged."""
    R = "agent-corpus/d-work/rows/1.md"
    def setUp(self):
        self.r = Repo(); self.r.write(self.R, row(1, "one", "open", "2026-01-01 Y plan")); self.base = self.r.commit("root")
        os.environ.pop("DYAD_INSTANCE", None)
    def test_semicolon_split_fails_on_main(self):   # the #100 shape
        self.r.write(self.R, row(1, "one", "open", "2026-01-01 Y plan; 2026-01-02 N plan (patching; falsify first)")); h = self.r.commit()
        out = m.check_range(self.base, h, cwd=self.r.d)
        self.assertEqual(len(out), 2, out); self.assertTrue(all("[disposed]" in o for o in out), out)
    def test_entry_without_disposition_fails_on_a_new_row(self):   # the #94 shape
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two", "backlog", "2026-01-01 opened by #1's prompt")); h = self.r.commit()
        out = m.check_range(self.base, h, cwd=self.r.d)
        self.assertEqual(len(out), 1, out); self.assertIn("opened by", out[0])
    def test_well_formed_append_passes(self):
        # #202: a Done that names a merge may not be the commit that sets `done` (DoneOrderTests), so this
        # shape test uses a Done that names none — the entry shape is what it is about.
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-02 Y done")); h = self.r.commit()
        self.assertEqual(m.check_range(self.base, h, cwd=self.r.d), [])
    def test_existing_malformed_entry_not_rejudged(self):
        self.r.write(self.R, row(1, "one", "open", "legacy")); legacy = self.r.commit("legacy")
        self.r.write(self.R, row(1, "one", "planned", "legacy; 2026-01-03 Y plan")); h = self.r.commit()
        self.assertEqual(m.check_range(legacy, h, cwd=self.r.d), [])
    def test_branch_whole_diff_checked(self):
        sh("git", "checkout", "-q", "-b", "feature", cwd=self.r.d)
        self.r.write(self.R, row(1, "one", "planned", "2026-01-01 Y plan; 2026-01-02 Y (a; b)")); h = self.r.commit()
        out = m.check_transaction(self.r.d, self.base, h)
        self.assertEqual(len(out), 2, out); self.assertTrue(all("[disposed]" in o for o in out), out)

class DoneOrderTests(unittest.TestCase):
    """d-work #202: the Done state follows the merge. One commit may not both record a `Y done` that names
    a merge and set the row `done`; the commit that does set `done` must show every head those entries name
    as an ancestor of itself; and the package check reads the interval between them as one warning."""
    R = "agent-corpus/d-work/rows/1.md"
    def setUp(self):
        self.r = Repo(); self.r.write(self.R, row(1, "one", "planned", "2026-01-01 Y plan"))
        self.base = self.r.commit("root")
        os.environ.pop("DYAD_INSTANCE", None)
    def test_the_old_order_fails(self):
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9)"))
        h = self.r.commit()
        out = m.check_range(self.base, h, cwd=self.r.d)
        self.assertEqual(len(out), 1, out); self.assertIn("the state follows the merge", out[0])
    def test_the_two_commit_order_passes(self):
        self.r.write(self.R, row(1, "one", "planned", "2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9)"))
        rec = self.r.commit("record")                      # 1: the disposition, state unchanged
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9)"))
        h = self.r.commit("close")                         # 2: the state, no entry
        self.assertEqual(m.check_range(self.base, h, cwd=self.r.d), [], )
        self.assertEqual(m.check_commit(rec, self.r.d, "agent-corpus"), [])
    def test_a_done_naming_no_merge_still_closes_in_one_commit(self):
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-02 Y done")); h = self.r.commit()
        self.assertEqual(m.check_range(self.base, h, cwd=self.r.d), [])
    def test_a_head_that_has_not_landed_fails(self):
        side = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        sh("git", "checkout", "-q", "-b", "side", cwd=self.r.d)
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); unlanded = self.r.commit("not on main")
        sh("git", "checkout", "-q", "main", cwd=self.r.d)
        self.r.write(self.R, row(1, "one", "planned", f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {unlanded})"))
        self.r.commit("record")
        self.r.write(self.R, row(1, "one", "done", f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {unlanded})"))
        h = self.r.commit("close")
        out = m.check_range(self.base, h, cwd=self.r.d)
        self.assertEqual(len(out), 1, out); self.assertIn("the merge that `Y` ratified has not landed", out[0])
        self.assertEqual(side, side)
    def test_a_head_that_landed_passes(self):
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); landed = self.r.commit("landed")
        self.r.write(self.R, row(1, "one", "planned", f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {landed})"))
        self.r.commit("record")
        self.r.write(self.R, row(1, "one", "done", f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {landed})"))
        h = self.r.commit("close")
        self.assertEqual(m.check_range(self.base, h, cwd=self.r.d), [])
    def test_a_sha_unknown_to_this_clone_is_skipped_not_failed(self):
        ghost = "0" * 40
        self.r.write(self.R, row(1, "one", "planned", f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {ghost})"))
        self.r.commit("record")
        self.r.write(self.R, row(1, "one", "done", f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {ghost})"))
        h = self.r.commit("close")
        self.assertEqual(m.check_range(self.base, h, cwd=self.r.d), [])
    def test_every_head_the_operative_entry_names_is_checked(self):
        # a multi-PR Done is the normal case under `batch-disposition-mode: always`, so one head landing
        # must not excuse another that did not
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); landed = self.r.commit("landed")
        sh("git", "checkout", "-q", "-b", "side2", cwd=self.r.d)
        self.r.write("agent-corpus/d-work/rows/3.md", row(3, "three")); unlanded = self.r.commit("not on main")
        sh("git", "checkout", "-q", "main", cwd=self.r.d)
        e = f"2026-01-02 Y done (merges PR #9 at {landed}, PR #10 at {unlanded})"
        self.r.write(self.R, row(1, "one", "planned", f"2026-01-01 Y plan; {e}")); self.r.commit("record")
        self.r.write(self.R, row(1, "one", "done", f"2026-01-01 Y plan; {e}")); h = self.r.commit("close")
        out = m.check_range(self.base, h, cwd=self.r.d)
        self.assertEqual(len(out), 1, out); self.assertIn(unlanded, out[0])
    def test_an_N_done_after_the_operative_Y_does_not_cancel_the_check(self):
        sh("git", "checkout", "-q", "-b", "side3", cwd=self.r.d)
        self.r.write("agent-corpus/d-work/rows/4.md", row(4, "four")); unlanded = self.r.commit("not on main")
        sh("git", "checkout", "-q", "main", cwd=self.r.d)
        es = f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {unlanded}); 2026-01-03 N done (re-asked)"
        self.r.write(self.R, row(1, "one", "planned", es)); self.r.commit("record")
        self.r.write(self.R, row(1, "one", "done", es)); h = self.r.commit("close")
        out = m.check_range(self.base, h, cwd=self.r.d)
        self.assertEqual(len(out), 1, out); self.assertIn("has not landed", out[0])
    def test_an_N_done_on_a_live_row_warns_nothing(self):
        d = self.r.d / "agent-corpus/d-work/rows"
        (d / "1.md").write_text(row(1, "one", "open", "2026-01-01 Y plan; 2026-01-02 N done (the answer did not establish it)"))
        self.assertEqual([x for x in m.check_package(self.r.d) if x.startswith("warning:")], [])
    def test_done_with_no_Y_done_entry_fails(self):
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan")); h = self.r.commit("close")
        out = m.check_range(self.base, h, cwd=self.r.d)
        self.assertEqual(len(out), 1, out); self.assertIn("no `Y done` entry", out[0])
    def test_a_head_on_the_base_but_not_on_the_commit_passes(self):
        # the ledger-only-branch shape: the merge is on `main`, the record and close travel on a branch
        self.r.write("agent-corpus/d-work/rows/5.md", row(5, "five")); merged = self.r.commit("the merge, on main")
        sh("git", "checkout", "-q", "-b", "ledger", self.base, cwd=self.r.d)
        es = f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {merged})"
        self.r.write(self.R, row(1, "one", "planned", es)); self.r.commit("record")
        self.r.write(self.R, row(1, "one", "done", es)); h = self.r.commit("close")
        self.assertEqual(m.check_commit(h, self.r.d, "agent-corpus", merged), [])     # judged against the base
        out = m.check_commit(h, self.r.d, "agent-corpus", self.base)                  # a base without the merge
        self.assertEqual(len(out), 1, out); self.assertIn("has not landed", out[0])
    def test_a_superseded_entry_is_history_not_an_obligation(self):
        # Rule-2 Binding: a resolution that changes the head voids the `Y` given against it, so the Done is
        # asked again and the later entry is the operative one (#202, attack A5).
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); landed = self.r.commit("landed")
        ghost = "0" * 39 + "1"
        es = (f"2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9 at {ghost}); "
              f"2026-01-03 Y done (merges PR #9 at {landed})")
        self.r.write(self.R, row(1, "one", "planned", es)); self.r.commit("record again")
        self.r.write(self.R, row(1, "one", "done", es)); h = self.r.commit("close")
        self.assertEqual(m.check_range(self.base, h, cwd=self.r.d), [])
    def test_the_interval_is_one_warning_in_the_package_check(self):
        d = self.r.d / "agent-corpus/d-work/rows"
        (d / "1.md").write_text(row(1, "one", "planned", "2026-01-01 Y plan; 2026-01-02 Y done (merges PR #9)"))
        (d / "2.md").write_text(row(2, "two", "done", "2026-01-01 Y plan; 2026-01-02 Y done"))
        msgs = m.check_package(self.r.d)
        self.assertEqual([x for x in msgs if not x.startswith("warning:")], [], msgs)
        warns = [x for x in msgs if x.startswith("warning:")]
        self.assertEqual(len(warns), 1, warns); self.assertIn("row #1 is planned", warns[0])
        self.assertIn("merges are still owed", warns[0])

class RefsShapeTests(unittest.TestCase):
    """#439: the close path wrote `['origin/main', 'main', 'HEAD']` over 28 rows' refs and no guard read the
    value's shape. A commit that adds or changes a refs holding `[ ] ' " ,` fails; a legacy comma refs the
    commit leaves alone passes; the package check fails a bracket anywhere in the store."""
    R = "agent-corpus/d-work/rows/1.md"; LEGACY = "agent-corpus/d-work/rows/2.md"
    def setUp(self):
        self.r = Repo(); os.environ.pop("DYAD_INSTANCE", None)
        self.r.write(self.R, row(1, "one", "open", "2026-01-01 Y plan; 2026-01-02 Y done", "7 parent #3"))
        self.r.write(self.LEGACY, row(2, "two", "done", "2026-01-01 Y done", "109, 110"))   # a pre-fence row
        self.base = self.r.commit("root")
    def fails(self, before, after): return m.check_range(before, after, cwd=self.r.d)
    def test_a_close_writing_the_branch_list_fails(self):
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-02 Y done", "['origin/main', 'main', 'HEAD']")); h = self.r.commit()
        out = self.fails(self.base, h)
        self.assertEqual(len(out), 1, out); self.assertIn("writes refs", out[0]); self.assertIn("space-separated tokens", out[0])
    def test_a_new_row_with_a_comma_or_quote_fails(self):
        for i, refs in enumerate(["109, 110", "'#4'", '"#4"'], start=3):
            with self.subTest(refs=refs):
                self.r.write(f"agent-corpus/d-work/rows/{i}.md", row(i, f"r{i}", refs=refs)); h = self.r.commit(f"add {i}")
                out = m.check_commit(h, self.r.d, "agent-corpus")
                self.assertEqual(len(out), 1, out); self.assertIn("writes refs", out[0])
    def test_space_separated_tokens_pass(self):
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-02 Y done", "202 321 parent #5 PR #9")); h = self.r.commit()
        self.assertEqual(self.fails(self.base, h), [])
    def test_a_legacy_comma_refs_left_alone_passes(self):
        self.r.write(self.LEGACY, row(2, "two", "done", "2026-01-01 Y done; 2026-01-03 Y archive", "109, 110"))
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-02 Y done", "7 parent #3")); h = self.r.commit()
        self.assertEqual(self.fails(self.base, h), [])
    def test_a_refs_rewritten_resolving_a_merge_fails(self):
        sh("git", "checkout", "-q", "-b", "ledger", cwd=self.r.d)
        self.r.write("agent-corpus/d-work/rows/3.md", row(3, "three")); self.r.commit("branch row")
        sh("git", "checkout", "-q", "main", cwd=self.r.d)
        self.r.write(self.R, row(1, "one", "planned", "2026-01-01 Y plan; 2026-01-02 Y done", "7 parent #3")); main_h = self.r.commit("planned")
        sh("git", "checkout", "-q", "ledger", cwd=self.r.d)
        sh("git", "merge", "-q", "--no-commit", "-s", "ours", "main", cwd=self.r.d)
        self.r.write(self.R, row(1, "one", "planned", "2026-01-01 Y plan; 2026-01-02 Y done", "['main', 'HEAD']"))   # hidden in the merge
        sh("git", "commit", "-qm", "merge main", cwd=self.r.d); h = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        out = m.check_transaction(self.r.d, main_h, h)
        self.assertTrue(any("merge" in o and "writes refs" in o for o in out), out)
    def test_the_package_check_fails_a_bracket_not_a_legacy_comma(self):
        d = self.r.d / "agent-corpus/d-work/rows"
        fails = lambda: [x for x in m.check_package(self.r.d) if not x.startswith("warning:")]   # row 1's open interval warns
        self.assertEqual(fails(), [])                                          # `109, 110` is legacy, not judged here
        (d / "1.md").write_text(row(1, "one", "done", "2026-01-01 Y plan; 2026-01-02 Y done", "['origin/main', 'main', 'HEAD']"))
        out = fails()
        self.assertEqual(len(out), 1, out); self.assertIn("holds a bracket", out[0])

class LedgerBranchFenceTests(unittest.TestCase):
    """#191: a ledger-only branch skips the plan gate because `main` would admit its commits — so the fence
    judges each of them as `main` would. A PR merge (`--no-ff`) lands them where the first-parent walk of
    the main fence never looks."""
    R = "agent-corpus/d-work/rows/1.md"
    def setUp(self):
        self.r = Repo(); os.environ.pop("DYAD_INSTANCE", None)
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-01 Y done")); self.base = self.r.commit("root")
        sh("git", "checkout", "-q", "-b", "ledger", cwd=self.r.d)
    def test_regression_on_a_ledger_branch_fails(self):
        self.r.write(self.R, row(1, "one", "planned", "2026-01-01 Y plan")); h = self.r.commit()
        out = m.check_transaction(self.r.d, self.base, h)
        self.assertTrue(any("state regresses done\u2192planned" in o for o in out), out)
    def test_deletion_and_retitle_on_a_ledger_branch_fail(self):
        self.r.remove(self.R); h = self.r.commit()
        self.assertTrue(any("deletes row file" in o for o in m.check_transaction(self.r.d, self.base, h)))
        sh("git", "reset", "-q", "--hard", self.base, cwd=self.r.d)
        self.r.write(self.R, row(1, "renamed", "done", "2026-01-01 Y plan; 2026-01-01 Y done")); h = self.r.commit()
        out = m.check_transaction(self.r.d, self.base, h)
        self.assertTrue(any("changes id or title" in o for o in out), out)
    def test_a_legal_ledger_branch_passes(self):
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); h = self.r.commit()
        self.assertEqual(m.check_transaction(self.r.d, self.base, h), [])
    def test_a_code_branch_is_not_fenced_here(self):
        """Not ledger-only: the plan gate judges it (a planned d-work), not this per-commit fence."""
        self.r.write("dyad/x.md", "x"); h = self.r.commit()
        self.assertEqual(m.check_transaction(self.r.d, self.base, h), [])
    def test_a_regression_made_resolving_a_merge_fails(self):
        """The per-commit walk skips merges; the merge is judged against both parents."""
        sh("git", "checkout", "-q", "-B", "main", self.base, cwd=self.r.d)
        self.r.write(self.R, row(1, "one", "planned", "2026-01-01 Y plan")); self.r.commit("planned")   # a legal-looking base for the test
        sh("git", "checkout", "-q", "-B", "ledger", cwd=self.r.d); base = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); self.r.commit("branch row")
        sh("git", "checkout", "-q", "main", cwd=self.r.d)
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-02 Y done")); main_done = self.r.commit("done on main")
        sh("git", "checkout", "-q", "ledger", cwd=self.r.d)
        sh("git", "merge", "-q", "--no-commit", "-s", "ours", "main", cwd=self.r.d)   # keep the branch's `planned`: a regression against main
        sh("git", "commit", "-qm", "merge main", cwd=self.r.d); h = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        out = m.check_transaction(self.r.d, main_done, h)
        self.assertTrue(any("merge" in o and "regresses done\u2192planned" in o for o in out), out)
    def test_repairing_an_unparseable_row_on_a_ledger_branch_does_not_crash(self):
        sh("git", "checkout", "-q", "-B", "main", self.base, cwd=self.r.d)
        self.r.write(self.R, "id: 1\ntitle: one\nopened: d\nstate: done\n"); broken = self.r.commit("broken")
        sh("git", "checkout", "-q", "-B", "fix", cwd=self.r.d)
        self.r.write(self.R, row(1, "one", "done", "2026-01-01 Y plan; 2026-01-01 Y done")); h = self.r.commit("repair")
        self.assertEqual(m.check_transaction(self.r.d, broken, h), [])
    def test_a_branch_that_ever_touched_code_is_not_ledger_only(self):
        """A revert makes the net diff ledger-only; the gate and the fence still read it commit by commit."""
        self.r.write("dyad/x.md", "x"); self.r.commit("code"); self.r.remove("dyad/x.md"); self.r.commit("revert")
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two")); h = self.r.commit("ledger")
        self.assertFalse(dyadlib.ledger_only(self.r.d, self.base, h))
        self.assertEqual(m.check_transaction(self.r.d, self.base, h), [])   # the plan gate's, not this fence's
    def test_ledger_only_under_another_instance(self):
        os.environ["DYAD_INSTANCE"] = "other-corpus"; self.addCleanup(os.environ.pop, "DYAD_INSTANCE", None)
        self.r.write("other-corpus/d-work/rows/2.md", row(2, "two")); h = self.r.commit()
        self.assertTrue(dyadlib.ledger_only(self.r.d, self.base, h))
        self.r.write("agent-corpus/d-work/rows/3.md", row(3, "three")); h = self.r.commit()   # the default instance is no ledger here
        self.assertFalse(dyadlib.ledger_only(self.r.d, self.base, h))
    def test_a_non_canonical_row_file_name_fails_the_package_check(self):
        root = Path(tempfile.mkdtemp()); (root / "agent-corpus" / "d-work" / "rows").mkdir(parents=True)
        (root / "agent-corpus" / "d-work" / "rows" / "01.md").write_text(row(1, "one"))
        self.assertIn("differs from the file name", " ".join(m.check_package(root)))

PREFS = "# Operator preferences\n\n| key | value | allowed | read by |\n|-----|-------|---------|---------|\n| dwork-trace | {v} | `always` \\| `on-demand` | Rule-3 |\n"

class TraceFenceTests(unittest.TestCase):
    """#465: under `dwork-trace: always`, read at the commit's own tree, a commit that adds a `Y done` entry to row N —
    a mandate close excepted — holds `<instance>/d-work/traces/N.md` in that tree: carried by it, or on the base."""
    R, T = "agent-corpus/d-work/rows/1.md", "agent-corpus/d-work/traces/1.md"
    def setUp(self, pref="always"):
        self.r = Repo(); os.environ.pop("DYAD_INSTANCE", None)
        self.r.write("preferences-corpus/PREFERENCES.md", PREFS.format(v=pref))
        self.r.write(self.R, row(1, "one", "planned", "2026-01-01 Y plan"))
        self.r.write("agent-corpus/d-work/rows/2.md", row(2, "two", "planned", "2026-01-01 Y plan"))
        self.base = self.r.commit("root")
    def fails(self, h, base=None): return m.check_range(base or self.base, h, cwd=self.r.d)
    def done(self, rid=1, entry="2026-01-02 Y done", state="done"):
        self.r.write(f"agent-corpus/d-work/rows/{rid}.md", row(rid, {1: "one", 2: "two"}[rid], state, f"2026-01-01 Y plan; {entry}"))
    def test_a_done_record_without_its_trace_fails(self):
        self.done(); out = self.fails(self.r.commit())
        self.assertEqual(len(out), 1, out)
        self.assertIn(f"without its trace {self.T}", out[0]); self.assertIn("dyad dwork trace 1 --out", out[0])
        self.assertIn(f"`land {self.T}`", out[0]); self.assertIn("[main-fence]", out[0])
    def test_the_trace_in_the_same_commit_passes(self):
        self.done(); self.r.write(self.T, "# Trace #1\n")
        self.assertEqual(self.fails(self.r.commit()), [])
    def test_the_trace_already_on_the_base_passes(self):
        self.r.write(self.T, "# Trace #1\n"); base = self.r.commit("trace first")
        self.done(); self.assertEqual(self.fails(self.r.commit(), base), [])
    def test_a_record_with_the_state_left_as_it_is_is_judged_too(self):
        self.done(entry="2026-01-02 Y done (merges PR #9 at abc1234)", state="planned")
        out = self.fails(self.r.commit())
        self.assertEqual(len(out), 1, out); self.assertIn("without its trace", out[0])
    def test_the_close_commit_adds_no_entry_and_is_not_judged(self):
        self.r.write(self.T, "# Trace #1\n"); self.done(state="planned"); base = self.r.commit("record")
        self.r.remove(self.T); self.r.commit("trace removed, a state guard's concern")   # the close below adds no entry
        self.done(); h = self.r.commit("close")
        self.assertEqual(m.check_commit(h, self.r.d, "agent-corpus", base), [])
    def test_a_mandate_close_passes_without_a_trace(self):
        self.done(entry="2026-10-26 Y done (mandate #3, 2026-10-26)")
        self.assertEqual(self.fails(self.r.commit()), [])
    def test_a_batch_done_needs_every_rows_trace(self):
        e = "2026-01-02 Y done (batch #1,#2, merges PR #9 at abc1234)"
        self.done(1, e, "planned"); self.done(2, e, "planned"); self.r.write(self.T, "# Trace #1\n")
        out = self.fails(self.r.commit())
        self.assertEqual(len(out), 1, out); self.assertIn("agent-corpus/d-work/traces/2.md", out[0])
        self.r.write("agent-corpus/d-work/traces/2.md", "# Trace #2\n"); sh("git", "commit", "-q", "--amend", "--no-edit", cwd=self.r.d)
        self.assertEqual(self.fails(sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()), [])
    def test_a_new_row_born_with_a_done_entry_is_judged(self):
        self.r.write("agent-corpus/d-work/rows/3.md", row(3, "three", "open", "2026-01-02 Y done"))
        out = self.fails(self.r.commit())
        self.assertEqual(len(out), 1, out); self.assertIn("agent-corpus/d-work/traces/3.md", out[0])
    def test_on_demand_disables_the_clause(self):
        self.setUp("on-demand")
        self.done(); self.assertEqual(self.fails(self.r.commit()), [])
    def test_no_preference_file_disables_the_clause(self):
        self.r.remove("preferences-corpus/PREFERENCES.md"); base = self.r.commit("no prefs")
        self.done(); self.assertEqual(self.fails(self.r.commit(), base), [])
    def test_a_done_record_resolved_into_a_merge_without_its_trace_fails(self):
        sh("git", "checkout", "-q", "-b", "ledger", cwd=self.r.d)
        self.r.write("agent-corpus/d-work/rows/3.md", row(3, "three")); self.r.commit("branch row")
        sh("git", "checkout", "-q", "main", cwd=self.r.d)
        self.r.write("agent-corpus/d-work/rows/4.md", row(4, "four")); main_h = self.r.commit("main row")
        sh("git", "checkout", "-q", "ledger", cwd=self.r.d)
        sh("git", "merge", "-q", "--no-commit", "main", cwd=self.r.d)
        self.done()                                                                  # the record, hidden in the merge
        sh("git", "commit", "-qm", "merge main", cwd=self.r.d); h = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        out = m.check_transaction(self.r.d, main_h, h)
        self.assertTrue(any(o.startswith("FAIL [main-fence]: merge ") and "without its trace" in o for o in out), out)
        self.r.write(self.T, "# Trace #1\n"); sh("git", "commit", "-q", "--amend", "--no-edit", cwd=self.r.d)
        h = sh("git", "rev-parse", "HEAD", cwd=self.r.d).strip()
        self.assertFalse([o for o in m.check_transaction(self.r.d, main_h, h) if "trace" in o])

class EventsOnlyFenceTests(unittest.TestCase):
    """#438: the main fence admits an events-only direct commit (`<host>/runbooks/events/` only) as it admits a
    ledger-only one — it carries no row for the fence to judge, and the store's append-only rule stays the
    sysadmin craft's `events` guard. A commit touching both stores is neither and fails, as any other path does."""
    R, EV = "agent-corpus/d-work/rows/1.md", "workstation-corpus/runbooks/events/sessions.jsonl"
    def setUp(self):
        self.prev = {k: os.environ.pop(k, None) for k in ("DYAD_HOST", "DYAD_RUNBOOKS", "DYAD_INSTANCE")}
        self.r = Repo(); self.r.write(self.R, row(1, "one")); self.base = self.r.commit("root")
    def tearDown(self):
        for k, v in self.prev.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    def test_an_events_only_direct_commit_passes(self):
        self.r.write(self.EV, '{"a": 1}\n'); h = self.r.commit("events")
        self.assertEqual(m.check_commit(h, self.r.d, "agent-corpus"), [])
        self.assertEqual(m.check_range(self.base, h, cwd=self.r.d), [])
        self.assertEqual(m.check_transaction(self.r.d, self.base, h), [])      # on main
    def test_a_commit_touching_both_stores_fails(self):
        self.r.write(self.EV, '{"a": 1}\n'); self.r.write(self.R, row(1, "one", "planned", "2026-01-01 Y plan")); h = self.r.commit("both")
        out = m.check_range(self.base, h, cwd=self.r.d)
        self.assertEqual(len(out), 1, out); self.assertIn("non-ledger paths: workstation-corpus/runbooks/events/sessions.jsonl", out[0])
    def test_a_run_book_beside_its_events_fails(self):
        self.r.write(self.EV, '{"a": 1}\n'); self.r.write("workstation-corpus/runbooks/sessions.md", "x"); h = self.r.commit("runbook")
        self.assertIn("non-ledger paths", m.check_range(self.base, h, cwd=self.r.d)[0])
    def test_the_store_follows_the_host_path(self):
        os.environ["DYAD_HOST"] = "infrastructure"
        self.r.write(self.EV, '{"a": 1}\n'); h = self.r.commit("events under another host")
        self.assertIn("non-ledger paths", m.check_range(self.base, h, cwd=self.r.d)[0])
        self.r.write("infrastructure/runbooks/events/sessions.jsonl", '{"a": 1}\n'); h2 = self.r.commit("this host's events")
        self.assertEqual(m.check_commit(h2, self.r.d, "agent-corpus"), [])
    def test_an_events_only_branch_gets_the_per_commit_fence(self):
        sh("git", "checkout", "-q", "-b", "events", cwd=self.r.d)
        self.r.write(self.EV, '{"a": 1}\n'); h = self.r.commit("events")
        self.assertTrue(dyadlib.events_only(self.r.d, self.base, h))
        self.assertEqual(m.check_transaction(self.r.d, self.base, h), [])

if __name__ == "__main__":
    unittest.main()
