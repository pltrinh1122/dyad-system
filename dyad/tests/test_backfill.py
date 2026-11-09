"""backfill.py (d-work #644 step 5(a)), over a scratch tree: the change log's class and actor cells, the `Y archive`,
`Y open (promotion …)` and `Y release` entries and the verdict tables of a plan file and a falsification record become
candidate lines of source `structured`, each naming the record's own outcome and its covering row; a cell naming no
outcome, an actor that is none of `party-kind`'s names and a table with no covering row are counted, never guessed;
`--record` keeps one record; every line passes the decision log's line check; nothing is written."""
import contextlib, io, json, os, shutil, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
bf = dyadlib.load_module(PKG / "scripts" / "backfill.py", "backfill_under_test")

ROW = "id: {id}\ntitle: t\nopened: 2026-11-01\nstate: done\ndisposed: {disposed}\nrefs: \n"
CHANGELOG = ("# Host change log\n\n| date | d-work | class | action | undo | outcome | actor |\n|---|---|---|---|---|---|---|\n"
             "| 2026-11-01 | #3 | reversible | append a line \\| to bashrc | remove it | ok | agent |\n"
             "| 2026-11-02 | #3 | weird | something | none | ok | operator |\n")
PLAN = ("# Plan #4\n\n## Falsification\n| id | claim | attack | result | survivor |\n|---|---|---|---|---|\n"
        "| F1 | a claim | an attack | **refuted** for practice | x |\n| F2 | b | c | survives, scoped | y |\n"
        "| F3 | d | e | unclear | z |\n")
RECORD = ("# Falsification — a thing\n\n| # | attack | result |\n|---|---|---|\n| 1 | before any heading | confirmed |\n\n"
          "## Amendment — d-work #5\n| # | attack | result |\n|---|---|---|\n| 1 | an attack | confirmed |\n")


class BackfillTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, True)
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "inst", "DYAD_HOST": "host"}); e.start(); self.addCleanup(e.stop)
        inst = self.root / "inst"
        (inst / "d-work" / "rows").mkdir(parents=True); (inst / "d-work" / "plans").mkdir(); (inst / "falsification").mkdir()
        disposed = {3: "2026-11-01 Y plan", 4: "2026-11-01 Y plan",
                    5: "2026-11-01 Y archive (retirement batch: #5, carried by #4); 2026-11-02 Y archive (done #4)",
                    6: "2026-11-01 Y open (promotion P2, a promise); 2026-11-02 Y open; 2026-11-03 Y release v1.0.0"}
        for i, d in disposed.items():
            (inst / "d-work" / "rows" / f"{i}.md").write_text(ROW.format(id=i, disposed=d))
        (self.root / "host").mkdir(); (self.root / "host" / "CHANGELOG.md").write_text(CHANGELOG)
        (inst / "d-work" / "plans" / "4.md").write_text(PLAN)
        (inst / "falsification" / "thing.md").write_text(RECORD)

    def mine(self, out):
        return [g for g in out if not g["case"].startswith("verdict:") or "plan-4" in g["case"] or "thing" in g["case"]]

    def test_each_source_yields_its_record_s_own_outcomes(self):
        before = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        out, skipped = bf.backfill(self.root)
        got = {(g["record"], g["case"], g["outcome"], g["row"]) for g in self.mine(out)}
        self.assertEqual(got, {("host-action-class", "changelog:5:class", "reversible", 3),
                               ("party-kind", "changelog:5:actor", "agent", 3),
                               ("retirement-candidate", "entry:5:0", "carried", 5),
                               ("promotion", "entry:6:0", "P2", 6),
                               ("attack-result", "verdict:plan-4:1:F1", "refuted", 4),
                               ("attack-result", "verdict:plan-4:1:F2", "survives", 4),
                               ("attack-result", "verdict:thing:2:1", "confirmed", 5)})
        g = next(g for g in out if g["case"] == "changelog:5:class")
        self.assertEqual((g["inputs"], g["fields"], g["source"]), ("append a line | to bashrc", {}, "structured"))
        self.assertEqual(next(g for g in out if g["case"] == "verdict:plan-4:1:F1")["inputs"], "a claim — an attack")
        for why in ("changelog class: weird", "changelog actor: operator", "entries Y archive: no outcome named",
                    "entries Y release: no outcome named", "verdicts: result names no outcome", "verdicts: no covering row"):
            self.assertGreaterEqual(skipped[why], 1, why)
        self.assertEqual(sorted(p.relative_to(self.root) for p in self.root.rglob("*")), before)   # read-only

    def test_every_line_passes_the_decision_log_and_record_filters(self):
        out, _ = bf.backfill(self.root)
        dl = dyadlib.load_guard("agent", "decision_log")
        codes, rows = dl.outcomes_by_record(self.root), {3, 4, 5, 6}
        for g in self.mine(out):
            self.assertEqual(dl.line_problems({**g, "status": "candidate", "date": "2026-11-08"}, 4, "", rows, codes), [], g)
        self.assertEqual({g["record"] for g in bf.backfill(self.root, "promotion")[0]}, {"promotion"})

    def test_main_prints_lines_and_counts(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(bf.main(["--record", "party-kind", str(self.root)]), 0)
        self.assertEqual([json.loads(l)["case"] for l in out.getvalue().splitlines()], ["changelog:5:actor"])
        self.assertIn("candidates: dmc:party-kind 1", err.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(bf.main(["--record"]), 1)


class ForRowTests(BackfillTests):
    def test_for_row_scopes_each_source_and_names_one_id_per_ruling(self):
        """#648: a row's own plan table, entries and change-log rows, renamed `<record>-<row>-<n>`, source done."""
        got = {(g["record"], g["case"], g["outcome"]) for g in bf.for_row(self.root, 4)}
        self.assertEqual(got, {("attack-result", "attack-result-4-1", "refuted"), ("attack-result", "attack-result-4-2", "survives")})
        self.assertEqual({(g["record"], g["case"]) for g in bf.for_row(self.root, 3)},
                         {("host-action-class", "host-action-class-3-1"), ("party-kind", "party-kind-3-1")})
        six = bf.for_row(self.root, 6)
        self.assertEqual([(g["record"], g["case"], g["source"]) for g in six], [("promotion", "promotion-6-1", "done")])
        self.assertEqual(bf.for_row(self.root, 99), [])
        cap = {g["case"] for g in bf.capture(self.root, 3)}
        self.assertEqual(cap, {"party-kind-3-1"})                                    # host-action-class is operator-side


if __name__ == "__main__":
    unittest.main()
