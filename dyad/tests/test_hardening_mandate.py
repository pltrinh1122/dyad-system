"""The standing hardening mandate (d-work #692): its two records, `dmc:hardening-work` (W1 source, W2 restore, W3 inside
the mandate, all three or ordinary) and `dmc:hardening-due` (H1 recurred, H2 re-tested open, H3 batch, not-due, the
capacity bounding every due outcome); the play-book that homes both cites both and restates neither; the tunable
`hardening-ceiling` defaults to 1; and the template ships `hardening-mandate: off`."""
import json, re, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dyadlib
PKG = dyadlib.PKG
WORK, DUE = PKG / "dmc" / "hardening-work.jsonld", PKG / "dmc" / "hardening-due.jsonld"
PLAYBOOK = PKG / "playbooks" / "incident-hardening.md"
TEMPLATE = PKG / "templates" / "PREFERENCES.md"

def terms(path):
    return {t["termCode"]: t for t in json.loads(path.read_text())["hasDefinedTerm"]}

class HardeningRecordTests(unittest.TestCase):
    def test_work_is_all_three_conditions_or_ordinary(self):
        d, t = json.loads(WORK.read_text()), terms(WORK)
        self.assertEqual(list(t), ["W1", "W2", "W3", "hardening", "ordinary"])
        self.assertIn("W1, W2 and W3 all hold", t["hardening"]["dyad:when"])
        self.assertIn("any of W1, W2 or W3 fails", t["ordinary"]["dyad:when"])
        self.assertEqual(d["dyad:default"], "ordinary")                       # what guesses nothing asks
        self.assertIn("Done is always asked", t["hardening"]["dyad:then"])
        self.assertEqual(d["dyad:judgedBy"]["dyad:implementation"], "scripts/package.py")   # W1's mechanical half

    def test_due_outcomes_and_their_capacity(self):
        d, t = json.loads(DUE.read_text()), terms(DUE)
        self.assertEqual(list(t), ["H1", "H2", "H3", "not-due"])
        self.assertEqual(re.findall(r"\b(H1|H2|H3)\b", d["dyad:precedence"]), ["H1", "H2", "H3"])
        self.assertIn("Capacity bounds every due outcome", d["dyad:precedence"])
        for code in ("H1", "H2", "H3"):
            self.assertIn("within capacity", t[code]["dyad:then"], code)
        self.assertEqual(t["not-due"]["dyad:effect"], "settles")
        self.assertTrue(all(t[c]["dyad:effect"] == "skips" for c in ("H1", "H2", "H3")))   # never settled by precedent
        self.assertEqual(d["dyad:default"], "not-due")

    def test_the_ceiling_defaults_to_one(self):
        self.assertEqual(dyadlib.tunable_default("hardening-ceiling"), 1)

    def test_the_play_book_homes_both_and_restates_neither(self):
        text = PLAYBOOK.read_text()
        for path, ident in ((WORK, "hardening-work"), (DUE, "hardening-due")):
            self.assertEqual(json.loads(path.read_text())["dyad:home"], "playbooks/incident-hardening.md")
            self.assertIn(f"dmc:{ident}", text)
        self.assertFalse(any(re.search(rf"\b{c}\b", text) for c in ("W1", "W2", "W3", "H1", "H2", "H3")))

    def test_the_template_ships_the_mandate_off(self):
        rows = {r[0].strip(): r for r in dyadlib.table_rows(TEMPLATE.read_text()) if r}
        self.assertEqual(rows["hardening-mandate"][1].strip(), "off")
        self.assertEqual(rows["hardening-ceiling"][1].strip(), "1")
        self.assertIn("granted: d-work #<id> entry <n>", TEMPLATE.read_text())

if __name__ == "__main__":
    unittest.main()
