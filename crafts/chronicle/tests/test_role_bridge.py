"""Tests of crafts/chronicle/scripts/role_bridge.py (record collateral-role-bridge)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import role_bridge as rb


class Rules(unittest.TestCase):
    def test_shipped_data_is_clean(self):
        ways, objects, th, problems = rb.rules()
        self.assertEqual(problems, [])
        self.assertEqual(tuple(ways), rb.WAYS)

    def test_bad_lines_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.txt"
            p.write_text("way: evaluation\nthreshold: handed-over = x\nnonsense: 1\n")
            *_, problems = rb.rules(p)
            self.assertTrue(any("needs" in x for x in problems))
            self.assertTrue(any("not a number" in x for x in problems))
            self.assertTrue(any("unknown key" in x for x in problems))
            self.assertTrue(any("no object line" in x for x in problems))


class Judge(unittest.TestCase):
    V, O = rb._pattern(["review"]), rb._pattern(["report"])

    def j(self, tasks, e, c):
        return rb.judge(tasks, e, c, self.V, self.O, 0.1)

    def test_verb_needs_an_information_object(self):
        self.assertTrue(rb.stated("Review reports for accuracy.", self.V, self.O))
        self.assertFalse(rb.stated("Review equipment on site.", self.V, self.O))

    def test_outcomes_in_order(self):
        self.assertEqual(self.j([], 0.5, 1)[0], "unsourced")
        self.assertEqual(self.j([("Review reports.", 4.0), ("Lift boxes.", 4.0)], 0.5, 1), ("demanded", 0.25))
        self.assertEqual(self.j([("Lift boxes.", 3.0)], 0.3, 5)[0], "net-cost")
        self.assertEqual(self.j([("Lift boxes.", 3.0)], 0.5, 1), ("emerging", 0.5))
        self.assertEqual(self.j([("Lift boxes.", 3.0)], 0.05, 1)[0], "absent")
        self.assertEqual(self.j([("Lift boxes.", 3.0)], None, None)[0], "absent")


class Rank(unittest.TestCase):
    def test_ties_share_a_rank_and_best_way_is_named(self):
        titles = {"a": "A", "b": "B", "c": "C"}
        tasks = {"a": [("Review reports.", 5.0)], "b": [("Review reports.", 5.0)], "c": [("Lift boxes.", 3.0)]}
        rows = rb.rank(titles, tasks, {}, {"a": 0.5, "b": 0.5, "c": 0.0})
        by = {r["code"]: r for r in rows}
        self.assertEqual(by["a"]["rank"], by["b"]["rank"])
        self.assertEqual(by["a"]["best"], "evaluation")
        self.assertEqual(by["c"]["rank"], 3)
        self.assertIn("| `demanded` | 2 |", rb.markdown(rows, "31.0", "test"))

    def test_net_cost_ranks_below_emerging(self):
        rows = rb.rank({"n": "N", "e": "E"}, {"n": [("Lift boxes.", 3.0)], "e": [("Lift boxes.", 3.0)]},
                       {"n": 5.0, "e": 1.0}, {"n": 0.3, "e": 0.3})
        by = {r["code"]: r for r in rows}
        self.assertEqual((by["e"]["outcome"], by["n"]["outcome"]), ("emerging", "net-cost"))
        self.assertLess(by["e"]["rank"], by["n"]["rank"])


if __name__ == "__main__":
    unittest.main()
