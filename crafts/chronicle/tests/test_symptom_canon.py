"""Tests of crafts/chronicle/scripts/symptom_canon.py (record collateral-symptom-canon)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import symptom_canon as sc

TREE = "judged: ready (source x)\nA0 [symptom; H] It does a thing.\n  A0.1 [cause; H] Because.\nA1 [symptom; H] Another.\nA2 [symptom; H] A third.\n"
REF = "B0 [symptom; H] A reference symptom.\n"
GOOD = """# Symptoms
## S1 It does a thing.
class: O1
proficiency: cursory
served: partly
cite: cited.md
sources: observed:696#5, seg:A0, ref:B0
## candidates
- seg:A2 unobserved: no one has reported it yet
## excluded
- seg:A1 restated: it rewords A0.1
"""


class Check(unittest.TestCase):
    def run_check(self, canon):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            (d / "seg").mkdir()
            (d / "seg" / "why-tree.md").write_text(TREE)
            (d / "reference").mkdir()
            (d / "reference" / "ref.md").write_text(REF)
            (d / "cited.md").write_text("x")
            (d / "symptoms.md").write_text(canon)
            return sc.check(d, d)

    def has(self, problems, text):
        self.assertTrue(any(text in p for p in problems), problems)

    def test_good_canon_passes(self):
        self.assertEqual(self.run_check(GOOD), [])

    def test_uncovered_symptom_fails(self):
        self.has(self.run_check(GOOD.replace("- seg:A2 unobserved: no one has reported it yet\n", "")), "seg:A2 is a tree symptom")

    def test_an_entry_needs_an_observation(self):
        self.has(self.run_check(GOOD.replace("observed:696#5, ", "")), "no observation")
        self.has(self.run_check(GOOD.replace("observed:696#5", "observed:somewhere")), "reads `observed:")
        self.assertEqual(self.run_check(GOOD.replace("observed:696#5", "channel:post-12")), [])

    def test_served_needs_an_existing_cite(self):
        self.has(self.run_check(GOOD.replace("cite: cited.md\n", "")), "cites nothing")
        self.has(self.run_check(GOOD.replace("cited.md", "gone.md")), "does not exist")
        self.assertEqual(self.run_check(GOOD.replace("served: partly\ncite: cited.md\n", "served: not yet\n")), [])

    def test_bad_nodes_and_outcomes_fail(self):
        self.has(self.run_check(GOOD.replace("ref:B0", "ref:B9")), "ref:B9 names no tree node")
        self.has(self.run_check(GOOD.replace("A2 unobserved", "A2 restated")), "candidates outcome")
        self.has(self.run_check(GOOD.replace("A1 restated", "A1 unobserved")), "excluded outcome")
        self.has(self.run_check(GOOD.replace("served: partly", "served: maybe")), "served 'maybe'")

    def test_a_superseded_entry_covers_nothing(self):
        canon = GOOD.replace("## candidates\n- seg:A2 unobserved: no one has reported it yet\n",
                             "## S2 Old.\nclass: O1\nproficiency: cursory\nserved: not yet\nsources: observed:696#10, seg:A2\n"
                             "## S3 New.\nclass: O1\nproficiency: cursory\nserved: not yet\nsources: observed:696#10\nsupersedes: S2\n")
        self.has(self.run_check(canon), "seg:A2 is a tree symptom")


if __name__ == "__main__":
    unittest.main()
