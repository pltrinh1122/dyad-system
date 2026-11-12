"""The judgement trace (d-work #690): its play-book cites its master record `dmc:judgement-cause` at the classing step
and restates none of the record's definitions; every class of the record has an effect from `dmc:precedent-scope`'s
set, and `misapplied` acts while `intended` settles; the precedence names every class once, in the stated order; the
default is the class that guesses nothing; and the run-book holds the three read-only steps the play-book names."""
import json, re, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dyadlib
PKG = dyadlib.PKG
RECORD = PKG / "dmc" / "judgement-cause.jsonld"
PLAYBOOK = PKG / "playbooks" / "judgement-trace.md"
RUNBOOK = PKG / "runbooks" / "judgement-trace.md"
ORDER = ["misapplied", "conflict", "stale", "gap", "undetermined", "intended"]
EFFECTS = {"settles", "asks", "shapes", "skips", "acts"}   # dmc:precedent-scope's declared effects (#649)

class JudgementTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(RECORD.read_text())
        cls.terms = {t["termCode"]: t for t in cls.d["hasDefinedTerm"]}

    def test_the_play_book_cites_the_record_and_homes_it(self):
        text = PLAYBOOK.read_text()
        self.assertEqual(self.d["dyad:home"], "playbooks/judgement-trace.md")
        self.assertIn("dmc:judgement-cause", text)
        t4 = next(l for l in text.splitlines() if "**T4 Cause.**" in l)
        self.assertIn("dmc:judgement-cause", t4)                           # cited at the step that applies it
        self.assertFalse(all(c in text for c in ORDER), "the home restates every class")

    def test_every_class_has_an_effect(self):
        self.assertEqual(sorted(self.terms), sorted(ORDER))
        for code, t in self.terms.items():
            self.assertIn(t.get("dyad:effect"), EFFECTS, code)
        self.assertEqual(self.terms["misapplied"]["dyad:effect"], "acts")   # an incident: never settled by precedent
        self.assertEqual(self.terms["intended"]["dyad:effect"], "settles")

    def test_the_precedence_names_every_class_once_in_order(self):
        prec = self.d["dyad:precedence"]
        found = re.findall(r"\b(" + "|".join(ORDER) + r")\b", prec)
        self.assertEqual(found, ORDER)

    def test_the_default_guesses_nothing(self):
        self.assertTrue(self.d["dyad:default"].startswith("undetermined"))
        self.assertEqual(self.d["dyad:judgedBy"]["dyad:kind"], "inference")

    def test_the_run_book_holds_the_three_read_only_steps(self):
        rb = RUNBOOK.read_text()
        self.assertIn("# sections: Symptom, Trace, Cause", rb)
        for name in ("symptom", "trace", "cause"):
            self.assertRegex(rb, rf"name: {name}\nclass: read-only\n")
        for step in ("T1 Symptom", "T2 Trace back", "T3 Conflicts", "T4 Cause", "T5 Outcome", "T6 Report"):
            self.assertIn(f"**{step}.**", PLAYBOOK.read_text())

if __name__ == "__main__":
    unittest.main()
