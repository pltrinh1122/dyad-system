"""dmc/takeover.jsonld (the cabinet craft's take-over criterion; dyad-system #698): the record loads through the core's
DMC store reader; its four outcomes in the stated precedence; the default `hand-on`; the outage case is `wait-retry`;
the claiming unit's kind is an input; and only a solo is ever taken over (plan revision 2, the operator's amend)."""
import json, sys, unittest
from pathlib import Path
CRAFT = Path(__file__).resolve().parents[1]
REPO = CRAFT.parents[1]
sys.path.insert(0, str(REPO / "dyad" / "scripts"))
import dyadlib
dmc = dyadlib.load_module(REPO / "dyad" / "guards" / "agent" / "dmc.py", "cabinet_test_dmc")
RECORD = CRAFT / "dmc" / "takeover.jsonld"


class TakeoverRecordTests(unittest.TestCase):
    def setUp(self):
        self.rec = json.loads(RECORD.read_text())
        self.out = {t["termCode"]: t for t in self.rec["hasDefinedTerm"]}

    def test_the_record_is_found_by_the_dmc_store_reader(self):
        paths = [p.resolve() for _, p, _ in dmc.records(REPO)]
        self.assertIn(RECORD.resolve(), paths)
        self.assertEqual(self.rec["@id"], "urn:dyad:dmc:cabinet/takeover")

    def test_four_outcomes_in_the_stated_precedence_and_the_default(self):
        self.assertEqual(list(self.out), ["wait-retry", "nudge", "take-over", "hand-on"])
        prec = self.rec["dyad:precedence"]
        self.assertLess(prec.index("wait-retry"), prec.index("nudge"))
        self.assertLess(prec.index("nudge"), prec.index("take-over"))
        self.assertLess(prec.index("take-over"), prec.index("hand-on"))
        self.assertEqual(self.rec["dyad:default"], "hand-on")

    def test_an_outside_service_outage_is_wait_retry_and_the_home_never_hands_its_own_act_off(self):
        w = self.out["wait-retry"]
        self.assertIn("outside service", w["dyad:when"])
        self.assertIn("never handed off", w["dyad:then"])
        self.assertNotIn("outside service", self.out["take-over"]["dyad:when"])

    def test_only_a_solo_is_taken_over_and_a_dyad_unit_never(self):
        self.assertTrue(any("dyad unit or solo" in i for i in self.rec["dyad:inputs"]))
        self.assertTrue(self.out["take-over"]["dyad:when"].startswith("the claiming unit is a solo"))
        self.assertIn("never taken over", self.rec["dyad:precedence"])
        self.assertIn("dyad unit", self.out["nudge"]["dyad:when"])
        self.assertIn("never the home's to resume", self.out["nudge"]["dyad:then"])

    def test_a_take_over_is_announced_first(self):
        then = self.out["take-over"]["dyad:then"]
        self.assertIn("announces it first", then)
        self.assertIn("incident", then)


if __name__ == "__main__":
    unittest.main()
