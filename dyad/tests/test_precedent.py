"""precedent.py (`dyad precedent prompt|score`, d-work #645): the blind two-reader labelling of precedent cases.
- `prompt` holds each record's question, inputs, outcomes with their when and then, precedence and default, and each
  case's id and facts, sorted by record then case; never a label; the same inputs give the same bytes;
- it refuses, naming each, a case that lacks a key, names no record, carries a label that is no outcome of its record,
  names a record not judged by inference, or one operator-side under `dmc:precedent-admission`; nothing is written;
- `score` reads `<case id>: <outcome>` lines and JSON lines, counts each reader per record, keeps the cases both match,
  and classes each mismatch `model-limit` (one missed) or `context-gap` (both missed); `--kept` writes the kept as
  `--decisions` input (source two-readers) that the decision log's line check passes;
- `gate` judges each kept line by `dmc:precedent-admission` before the question: admitted, superseded by a logged line
  naming the case, self-derived, operator-side, or no record; `--out` writes the admitted;
- `agreement` re-measures a record's admitted cases leave-one-out, and reports n 0 for a record with none."""
import contextlib, io, json, os, shutil, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
pr = dyadlib.load_module(PKG / "scripts" / "precedent.py", "precedent_under_test")

CASES = [{"case": "ar-2", "record": "attack-result", "row": 5, "facts": "The attack showed the claim false.", "label": "confirmed"},
         {"case": "ar-1", "record": "attack-result", "row": 5, "facts": "The attack\nfound nothing wrong.", "label": "survives"},
         {"case": "ca-1", "record": "changelog-actor", "row": 6, "facts": "The person at the keyboard ran the command by hand.", "label": "operator"},
         {"case": "pr-1", "record": "promotion", "row": 7, "facts": "A live defect blocks work.", "label": "P1"}]


class PrecedentTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        self.cases = self.d / "cases.jsonl"
        self.cases.write_text("".join(json.dumps(c) + "\n" for c in CASES))
        self.root = dyadlib.repo_root()

    def run_(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = pr.main(list(argv), self.root)
        return rc, out.getvalue(), err.getvalue()

    def test_the_prompt_holds_records_and_facts_never_a_label(self):
        text = pr.prompt(self.root, CASES)
        self.assertEqual(text, pr.prompt(self.root, list(reversed(CASES))))          # deterministic, order-free
        self.assertTrue(text.startswith("# Blind labelling: 4 case(s) of 3 record(s)\n"))
        for c in CASES:
            self.assertIn(f"### Case {c['case']}\n", text)
        self.assertIn("The attack found nothing wrong.", text)                          # one line of facts
        self.assertLess(text.index("## Record attack-result"), text.index("## Record changelog-actor"))
        self.assertLess(text.index("### Case ar-1"), text.index("### Case ar-2"))
        self.assertIn("- `confirmed` (", text); self.assertIn("Question: ", text); self.assertIn("Precedence: ", text)
        self.assertIn("Default: ", text)                                                # promotion states one
        body = text.split("## Record", 1)[1]
        for c in CASES:   # the case's own block holds its facts alone, never the label after them
            block = body.split(f"### Case {c['case']}\n", 1)[1].split("\n\n", 1)[0]
            self.assertNotIn(c["label"], block)
        rc, out, _ = self.run_("prompt", str(self.cases), "--out", str(self.d / "p.md"))
        self.assertEqual(rc, 0); self.assertEqual((self.d / "p.md").read_text(), text); self.assertIn("bytes", out)

    def test_the_prompt_refuses_what_cannot_be_labelled_blind(self):
        bad = [{"case": "x-1", "record": "attack-result", "row": 5, "facts": "f"},
               {"case": "x-2", "record": "no-such", "row": 5, "facts": "f", "label": "a"},
               {"case": "x-3", "record": "attack-result", "row": 5, "facts": "f", "label": "maybe"},
               {"case": "x-4", "record": "replan", "row": 5, "facts": "f", "label": "replan"},
               {"case": "x-5", "record": "plan-departure", "row": 5, "facts": "f", "label": "execution-detail"},
               {"case": "two words", "record": "attack-result", "row": 5, "facts": "f", "label": "confirmed"}]
        with self.assertRaises(ValueError) as e:
            pr.prompt(self.root, bad + CASES[:1] + CASES[:1])
        for says in ("x-1: lacks label", "x-2: names no DMC record", "x-3: label 'maybe' is no outcome",
                     "x-4: dmc:replan is judged mechanical", "x-5: dmc:plan-departure outcome 'execution-detail' is operator-side (skips",
                     "two words: the case id", "ar-2: named twice"):
            self.assertIn(says, str(e.exception))
        (self.d / "bad.jsonl").write_text(json.dumps(bad[4]) + "\n")
        rc, out, err = self.run_("prompt", str(self.d / "bad.jsonl"), "--out", str(self.d / "q.md"))
        self.assertEqual((rc, out), (1, "")); self.assertIn("refused: x-5", err); self.assertFalse((self.d / "q.md").exists())
        self.assertEqual(self.run_("prompt")[0], 1); self.assertEqual(self.run_("nothing")[0], 1)

    def test_score_counts_keeps_and_classes_mismatches(self):
        (self.d / "a.txt").write_text("Here are my answers:\n- `ar-1`: survives\nar-2: confirmed\nca-1: agent\npr-1: P1\n")
        (self.d / "b.txt").write_text('{"case": "ar-1", "label": "survives"}\n{"case": "ar-2", "label": "refuted"}\n'
                                      "ca-1: agent\npr-1: P1\npr-1: P2\n")                 # a second answer is ignored
        rc, out, err = self.run_("score", str(self.cases), str(self.d / "a.txt"), str(self.d / "b.txt"), "--kept", str(self.d / "k.jsonl"))
        self.assertEqual(rc, 0, err)
        self.assertIn("record attack-result: n 2; reader a 2/2; reader b 1/2; kept 1", out)
        self.assertIn("record changelog-actor: n 1; reader a 0/1; reader b 0/1; kept 0", out)
        self.assertIn("mismatch ar-2 (dmc:attack-result): label confirmed, a confirmed, b refuted: model-limit", out)
        self.assertIn("mismatch ca-1 (dmc:changelog-actor): label operator, a agent, b agent: context-gap", out)
        self.assertIn("total: n 4; reader a 3/4; reader b 2/4; kept 2; model-limit 1; context-gap 1", out)
        kept = [json.loads(l) for l in (self.d / "k.jsonl").read_text().splitlines()]
        self.assertEqual([(k["case"], k["outcome"], k["source"], k["inputs"]) for k in kept],
                         [("ar-1", "survives", "two-readers", "The attack found nothing wrong."), ("pr-1", "P1", "two-readers", "A live defect blocks work.")])
        dl = dyadlib.load_guard("agent", "decision_log")
        codes = dl.outcomes_by_record(self.root)
        for k in kept:
            self.assertEqual(dl.line_problems({**k, "status": "candidate", "date": "2026-11-08"}, 7, "", {5, 6, 7}, codes), [])
        self.assertEqual(self.run_("score", str(self.cases), str(self.d / "a.txt"))[0], 1)

    def test_answers_read_both_forms(self):
        self.assertEqual(pr.read_answers("* `a-1` = x\nnoise line\n{\"case\": \"b-1\", \"label\": \"y\"}\n{broken\n"),
                         {"a-1": "x", "b-1": "y"})


class GateTests(unittest.TestCase):
    PY = "2026-11-08 Y precedent (2 cases: promotion×2)"

    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "inst"}); e.start(); self.addCleanup(e.stop)
        rows = self.d / "inst" / "d-work" / "rows"; rows.mkdir(parents=True)
        (rows / "7.md").write_text(f"id: 7\ntitle: t\nopened: 2026-11-01\nstate: planned\ndisposed: 2026-11-01 Y plan; {self.PY}\nrefs: \n")
        self.dl = dyadlib.load_guard("agent", "decision_log")
        base = {"record": "promotion", "fields": {}, "row": 7, "status": "precedent", "source": "two-readers",
                "date": "2026-11-08", "y": self.PY}
        blocks = [{**base, "case": f"p-{i}", "outcome": o, "inputs": t} for i, (o, t) in enumerate(
            (("P1", "a live defect blocks work on the board"), ("P1", "a live defect corrupts a store"),
             ("P2", "a promise made while working the anchor"), ("P2", "a promise in the plan file"),
             ("P1", "a live defect misleads a reading")), 1)]
        log = self.d / "inst" / "d-work" / "decisions"; log.mkdir(parents=True)
        (log / "7.md").write_text("\n".join(self.dl.render(b) for b in blocks))

    def line(self, case, record="promotion", outcome="P1", **kw):
        return {"record": record, "case": case, "fields": {}, "inputs": "a live defect", "outcome": outcome, "row": 7,
                "source": "two-readers", **kw}

    def test_gate_judges_each_line_before_the_question(self):
        lines = [self.line("new-1"), self.line("p-1"), self.line("new-2", precedent="0" * 64),
                 self.line("pd-1", "plan-departure", "execution-detail"), self.line("x-1", "no-such"),
                 self.line("rc-1", "release-class", "capability")]                  # #649: shapes, so admitted
        admitted, refused = pr.gate(self.d, lines)
        self.assertEqual([l["case"] for l in admitted], ["new-1", "rc-1"])
        self.assertEqual(refused, [("promotion", "p-1", "superseded"), ("promotion", "new-2", "self-derived"),
                                   ("plan-departure", "pd-1", "operator-side"), ("no-such", "x-1", "no-record")])
        kept = self.d / "kept.jsonl"; kept.write_text("".join(json.dumps(l) + "\n" for l in lines))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(pr.main(["gate", str(kept), "--out", str(self.d / "adm.jsonl")], self.d), 0, err.getvalue())
        self.assertIn("refused p-1 (dmc:promotion): superseded", out.getvalue())
        self.assertIn("admitted: 2; refused: 4", out.getvalue())
        self.assertEqual([json.loads(l)["case"] for l in (self.d / "adm.jsonl").read_text().splitlines()], ["new-1", "rc-1"])

    def test_agreement_re_measures_the_admitted_set(self):
        m = pr.agreement(self.d, "promotion")
        self.assertEqual((m["n"], m["bar"], m["refused"], m["max_df"]), (5, None, [], pr.SMALL_MAX_DF))
        self.assertEqual(m["agreement"], m["reproduced"] / 5); self.assertGreaterEqual(m["reproduced"], 1)   # tokens kept
        self.assertEqual(pr.agreement(self.d, "attack-result")["n"], 0)
        with self.assertRaises(ValueError):
            pr.agreement(self.d, "no-such")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(pr.main(["agreement", "promotion"], self.d), 0)
        self.assertRegex(out.getvalue(), r"^agreement dmc:promotion: n 5; reproduced \d; abstained \d; agreement \d\.\d{3}; bar none; max_df 0.5")


if __name__ == "__main__":
    unittest.main()
