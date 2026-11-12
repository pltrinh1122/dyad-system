"""The monitor unit's registration (d-work #689): play-book step M6 and the Operating Guide's §3 item 3 say a monitor
desk opens no row of its own and registers by a touch with no row, its other acts riding an existing row (a post the
row holding its posting Y, a set-up host action the row that spawned or configures it); a unit that executes rows
keeps its registration row and touches with `-r`; and the stale reason, that a bare touch claims every open row, is
kept only as history, with #567's touch_owned as the reason now."""
import unittest
from pathlib import Path
CRAFT = Path(__file__).resolve().parents[1]
PLAYBOOK = CRAFT / "playbooks" / "monitor-unit.md"
GUIDE = CRAFT / "docs" / "operating-guide.md"

def m6() -> str:
    return next(l for l in PLAYBOOK.read_text().splitlines() if l.startswith("| M6 Register |"))

def item3() -> str:
    text = GUIDE.read_text()
    start = text.index("3. **The unit's first act is its registration.**")
    return " ".join(text[start:text.index("\n4. ", start)].split())

class MonitorRegistrationTests(unittest.TestCase):
    def test_m6_opens_no_row_and_names_where_the_other_acts_ride(self):
        line = m6()
        self.assertIn("opens no row of its own", line)
        self.assertIn("`dyad session touch` with no row", line)
        self.assertIn("Rule-3 Ledger", line)
        self.assertIn("posting `Y`", line)                     # a post rides the row holding its posting Y
        self.assertIn("Rule-8", line)                          # a set-up host action rides the spawning row
        self.assertNotIn("dyad dwork new", line)
        self.assertNotIn("never needs a row", line)

    def test_the_guide_splits_by_the_units_work(self):
        text = item3()
        self.assertIn("A unit that executes rows takes its registration row", text)
        self.assertIn("session touch -r <row>", text)
        self.assertIn("A monitor desk opens no row of its own", text)
        self.assertIn("monitor-unit.md` M6", text)

    def test_the_stale_reason_is_history_and_the_current_one_is_stated(self):
        text = item3()
        self.assertNotIn("always `-r`: a bare touch claims every open row", text)
        self.assertIn("Since #567 a bare touch claims only the rows the unit already owns", text)
        self.assertIn("sessions.touch_owned", text)
        self.assertIn("before it, a bare touch claimed every open row", text)

if __name__ == "__main__":
    unittest.main()
