"""decision_log.py (the decision log, entity `decision`; d-work #644): `<instance>/d-work/decisions/<row>.md`, one
`## <case id>` block of `key: value` lines per ruling (plan revision 2: the d-work store pattern, never a `*.jsonl`).

The form and the check:
- a well-formed candidate and precedent block pass and read back as written; the latest block of a (record, case) is its
  state; a `--decisions` file of JSON lines parses to the same dicts;
- each defect fails, named: a missing key, an unknown key, a record that is no DMC record, an outcome that is not the
  record's, a bad case id, a row that is no row, an unknown status or source, a bad date, a precedent line whose `y` is
  not a `Y precedent (…)` entry of its file's row, a candidate carrying `y`, a done candidate in a row with no `Y done`,
  a field name with a space, a file not named `<row>.md` or naming no row, a line outside a block or no `key: value`, a
  heading whose ` precedent` disagrees with the status;
- `lines_for` writes candidates under a `Y done` and precedents under a `Y precedent (…)` (from the logged candidate),
  and refuses any other entry, an empty list, a line that would fail and a case named twice, before any write;
- the transaction check fails a commit that edits a logged line or deletes a file, and passes one that appends."""
import json, os, shutil, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
dl = dyadlib.load_guard("agent", "decision_log")

INST = "agent-corpus"
ROW = "id: {id}\ntitle: row {id}\nopened: 2026-11-01\nstate: planned\ndisposed: {disposed}\nrefs: \n"
PY = "2026-11-08 Y precedent (1 cases: replan×1)"
CAND = {"record": "replan", "case": "r1", "fields": {"accreted": "false"}, "inputs": "main moved past plans.py",
        "outcome": "replan", "row": 5, "status": "candidate", "source": "done", "date": "2026-11-08"}


def git(d, *a):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=d, capture_output=True, text=True,
                       env=dyadlib.git_env())
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class FormTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, True)
        self.rows = self.root / INST / "d-work" / "rows"; self.rows.mkdir(parents=True)
        self.row(5, "2026-11-01 Y plan; 2026-11-08 Y done")
        self.row(6, f"2026-11-01 Y plan; {PY}")
        self.row(7, "2026-11-01 Y plan")
        self.store = dl.store(self.root); self.store.mkdir(parents=True)

    def row(self, i, disposed):
        (self.rows / f"{i}.md").write_text(ROW.format(id=i, disposed=disposed))

    def put(self, name, *blocks):
        (self.store / name).write_text("\n".join(b if isinstance(b, str) else dl.render(b) for b in blocks))

    def test_well_formed_lines_pass_and_the_latest_is_the_state(self):
        prec = {**CAND, "status": "precedent", "y": PY}
        self.put("5.md", CAND); self.put("6.md", prec)
        self.assertEqual(dl.check_package(self.root), [])
        self.assertEqual(dl.read(self.root)[5], [CAND])                                          # read back as written
        self.assertTrue((self.store / "6.md").read_text().startswith("## r1 precedent\nrecord: replan\n"))
        self.assertIn(f"precedent-entry: {PY}\nfield.accreted: false\ninputs: main moved past plans.py\n", (self.store / "6.md").read_text())
        self.assertEqual(dl.parse(json.dumps(CAND) + "\n"), [CAND])                              # a --decisions file
        self.assertEqual(dl.latest([CAND, {**CAND, "status": "precedent"}])[("replan", "r1")]["status"], "precedent")
        self.assertEqual(dl.read(self.root)[6], [prec])
        self.assertIn("1 case(s) precedent", dl.summary(self.root))
        self.assertEqual([f[0] for f in dl.describe(self.root)["fields"]], list(dl.FIELDS))

    def test_each_defect_fails_named(self):
        cases = [({k: v for k, v in CAND.items() if k != "source"}, "lacks source"),
                 ({**CAND, "extra": "1"}, "unknown key(s) extra"),
                 ({**CAND, "record": "no-such-record"}, "names no DMC record"),
                 ({**CAND, "outcome": "maybe"}, "is no outcome of dmc:replan"),
                 ({**CAND, "row": 99}, "row 99 is no row"),
                 ({**CAND, "row": "five"}, "row 'five' is no row"),
                 ({**CAND, "status": "final"}, "status 'final'"),
                 ({**CAND, "source": "guess"}, "source 'guess'"),
                 ({**CAND, "date": "today"}, "is not YYYY-MM-DD"),
                 ({**CAND, "precedent": "abc"}, "not a set's sha256"),
                 ({**CAND, "y": PY}, "a candidate line carries `y`"),
                 ({**CAND, "fields": {"bad name": "x"}}, "field(s) bad name")]
        for block, says in cases:
            with self.subTest(says=says):
                self.put("5.md", block)
                got = dl.check_package(self.root)
                self.assertTrue(any(says in m for m in got), got)
        for text, says in (("record: replan\n", "line 1 is no `key: value` line of a block"),
                           ("## r1\nnot a pair\n", "line 2 is no `key: value` line of a block"),
                           ("## r1 precedent\nstatus: candidate\n", "the heading says precedent"),
                           ("## two words here\n", "a block opens")):
            with self.subTest(says=says):
                self.put("5.md", text)
                self.assertTrue(any(says in m for m in dl.check_package(self.root)), dl.check_package(self.root))
        with self.assertRaises(ValueError):
            dl.parse("[1, 2]\n{}")

    def test_precedent_and_done_lines_need_their_entries(self):
        self.put("7.md", {**CAND, "status": "precedent", "y": PY})
        self.assertTrue(any("is not on row #7" in m for m in dl.check_package(self.root)))
        self.put("7.md", {**CAND, "status": "precedent", "y": "2026-11-08 Y plan"})
        self.assertTrue(any("names no `Y precedent" in m for m in dl.check_package(self.root)))
        self.put("7.md", CAND)
        self.assertTrue(any("which holds no `Y done`" in m for m in dl.check_package(self.root)))
        self.put("7.md", {**CAND, "source": "structured"})                       # a backfilled candidate needs no Done
        self.assertEqual(dl.check_package(self.root), [])

    def test_files_are_named_by_an_existing_row(self):
        (self.store / "notes.txt").write_text("x")
        self.put("42.md", CAND); self.put("7.jsonl", CAND)
        got = dl.check_package(self.root)
        self.assertIn("notes.txt: not `<row>.md`; the decision log holds one file per row (#644)", got)
        self.assertIn("7.jsonl: not `<row>.md`; the decision log holds one file per row (#644)", got)
        self.assertIn("42.md: names no row", got)

    def test_lines_for_writes_candidates_then_precedents_and_refuses_first(self):
        given = [{**{k: CAND[k] for k in ("record", "case", "inputs", "outcome", "row")}, "fields": {"accreted": False}}]
        got = dl.lines_for(self.root, 5, "Y done", given, "2026-11-08")
        self.assertEqual(got, [CAND])                                                    # a field value stored as a string
        dl.append(self.root, 7, [{**CAND, "source": "structured"}])
        self.row(7, "2026-11-01 Y plan")
        got = dl.lines_for(self.root, 7, "Y precedent (1 cases: replan×1)", [{"record": "replan", "case": "r1"}], "2026-11-08")
        self.assertEqual(got, [{**CAND, "source": "structured", "status": "precedent", "y": PY}])   # from the logged line
        for entry, lines, says in (("Y plan", given, "rides a `Y done`"), ("Y done", [], "names no line"),
                                   ("Y done", [{**given[0], "outcome": "maybe"}], "is no outcome"),
                                   ("Y done", given * 2, "names replan/r1 twice"),
                                   ("Y precedent (1 cases: replan×1)", [{"record": "replan", "case": "unlogged"}], "lacks")):
            with self.subTest(says=says), self.assertRaises(ValueError) as e:
                dl.lines_for(self.root, 5, entry, lines, "2026-11-08")
            self.assertIn(says, str(e.exception))
        with self.assertRaises(ValueError):
            dl.lines_for(self.root, 99, "Y done", given, "2026-11-08")


class BatchTests(FormTests):
    def test_a_batch_done_takes_only_its_rows_lines(self):
        """#648: one --decisions file may serve a batch Done; each row's state call takes the lines naming it."""
        lines = [{**{k: CAND[k] for k in ("record", "fields", "inputs", "outcome")}, "case": f"r{r}", "row": r} for r in (5, 6)]
        got = dl.lines_for(self.root, 5, "Y done (batch #5,#6)", lines, "2026-11-09")
        self.assertEqual([g["case"] for g in got], ["r5"])
        self.assertEqual(dl.lines_for(self.root, 7, "Y done (batch #5,#7)", lines[:1], "2026-11-09"), [])   # none of its own
        self.assertEqual(len(dl.lines_for(self.root, 5, "Y done", lines, "2026-11-09")), 2)               # a single Done: all


class TransactionTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        git(self.d, "init", "-q", "-b", "main")
        self.f = self.d / INST / "d-work" / "decisions" / "5.md"; self.f.parent.mkdir(parents=True)
        self.f.write_text(dl.render(CAND)); git(self.d, "add", "-A"); git(self.d, "commit", "-qm", "base")
        self.base = git(self.d, "rev-parse", "HEAD")

    def test_append_passes_an_edit_or_delete_fails(self):
        self.f.write_text(self.f.read_text() + "\n" + dl.render({**CAND, "status": "precedent", "y": PY}))
        git(self.d, "commit", "-qam", "append")
        self.assertEqual(dl.check_transaction(self.d, self.base, "HEAD"), [])
        self.f.write_text(dl.render({**CAND, "outcome": "as-written"})); git(self.d, "commit", "-qam", "edit")
        self.assertTrue(any("changes a line already logged" in m for m in dl.check_transaction(self.d, self.base, "HEAD")))
        mid = git(self.d, "rev-parse", "HEAD")
        self.f.unlink(); git(self.d, "commit", "-qam", "delete")
        self.assertTrue(any("is deleted" in m for m in dl.check_transaction(self.d, mid, "HEAD")))


if __name__ == "__main__":
    unittest.main()
