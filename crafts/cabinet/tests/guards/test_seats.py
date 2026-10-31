"""seats.py (the cabinet craft's guard, entity `seat`; #383): the seat-name form and its reading rule, the advisory
lines over a fixture store, the mandates table against the template, and the live repo (never a failure)."""
import datetime, shutil, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
seats = dyadlib.load_guard_file(Path(__file__).resolve().parents[2] / "guards" / "seats.py")
TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "mandates.md"

def fixture(names: list[str], mandates: str | None = None) -> Path:
    root = Path(tempfile.mkdtemp())
    d = root / "agent-corpus" / "d-work" / "sessions"; d.mkdir(parents=True)
    for n in names:
        (d / f"{n}.md").write_text(f"session: {n}\nseen: 2026-10-22T00:00:00+00:00\nroot: /r\nrows: \nfiles: \n")
    if mandates is not None:
        (root / "preferences-corpus").mkdir(); (root / "preferences-corpus" / "MANDATES.md").write_text(mandates)
    return root

class SeatForm(unittest.TestCase):
    def setUp(self):
        self.form, self.functions = seats.rules()
    def test_rules_file_declares_the_seven_functions(self):
        self.assertEqual(self.functions, ["program", "counsel", "audit", "engineer", "distribute", "operate", "communicate"])
    def test_reading_rule(self):
        k = lambda n: seats.kind(seats.parse_seat(n, self.form), self.functions)
        self.assertEqual(k("program-59cec502"), "leader")
        self.assertEqual(k("counsel-0032b4c0"), "secretary")
        self.assertEqual(k("engineer-ledgerd-1537d8fb"), "desk")
        self.assertEqual(k("program-alice-59cec502"), "leader")   # a member pair's leader in a multi-Operator tree: the leader keeps no desk (naming.md §1)
        self.assertEqual(k("foo-0032b4c0"), "unknown-function")
        self.assertEqual(seats.parse_seat("counsel-0032b4c0", self.form), {"seat": "counsel-0032b4c0", "function": "counsel", "topic": "", "hp": "0032b4c0"})
    def test_history_is_outside_the_form(self):
        for n in ("cab-2", "cos-1", "cos", "unnamed-b3ee7a0eaf8d", "ds-cabinet-term-1", "Counsel-0032b4c0", "counsel-0032B4C0", "counsel-0032b4c"):
            self.assertIsNone(seats.parse_seat(n, self.form), n)

class Advisory(unittest.TestCase):
    def test_names_are_counted_never_failed(self):
        msgs = seats.check_names(["cab-2", "counsel-0032b4c0", "unnamed-x", "zed-0032b4c0"], *seats.rules())
        self.assertEqual(len(msgs), 2)
        self.assertTrue(msgs[0].startswith("warning: 2 of 4 presence file(s) are outside the seat form"), msgs[0]); self.assertIn("cab-2, unnamed-x", msgs[0])
        self.assertTrue(msgs[1].startswith("warning: 1 presence file(s) name a function outside"), msgs[1]); self.assertIn("first: zed-0032b4c0", msgs[1])
        self.assertEqual(seats.check_names(["counsel-0032b4c0"], *seats.rules()), [])
    def test_two_live_leaders_of_one_operator_warn(self):
        form, functions = seats.rules()
        never, always = (lambda seen: False), (lambda seen: True)
        rec = lambda n: {"_path": f"{n}.md", "seen": "x"}
        two = [rec("program-59cec502"), rec("program-0032b4c0"), rec("counsel-0032b4c0")]
        msgs = seats.check_leaders(two, form, functions, never)
        self.assertEqual(len(msgs), 1); self.assertIn("2 live program seats for one Operator", msgs[0])
        self.assertIn("program-0032b4c0, program-59cec502", msgs[0])
        self.assertEqual(seats.check_leaders(two, form, functions, always), [])          # a stale seat is off the board (d-work #531)
        operators = [rec("program-alice-59cec502"), rec("program-bob-0032b4c0"), rec("program-1537d8fb")]
        self.assertEqual(seats.check_leaders(operators, form, functions, never), [])     # one leader per Operator: no warning
        same = operators + [rec("program-alice-1537d8fb")]
        msgs = seats.check_leaders(same, form, functions, never)
        self.assertEqual(len(msgs), 1); self.assertIn("Operator 'alice'", msgs[0])
        self.assertEqual(seats.check_leaders([rec("cos-1"), rec("cos-59cec502"), rec("program-59cec502")], form, functions, never), [])   # history is not a leader
    def test_check_package_reads_live_leaders(self):
        root = fixture(["program-59cec502", "program-0032b4c0"], TEMPLATE.read_text()); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self.assertEqual(seats.check_package(root), [])                                  # the fixture's `seen` is past the stale window
        d = root / "agent-corpus" / "d-work" / "sessions"
        now = datetime.datetime.now(datetime.UTC).isoformat()
        for n in ("program-59cec502", "program-0032b4c0"):
            (d / f"{n}.md").write_text(f"session: {n}\nseen: {now}\nroot: /r\nrows: \nfiles: \n")
        msgs = seats.check_package(root)
        self.assertEqual(len(msgs), 1); self.assertTrue(msgs[0].startswith("warning: 2 live program seats"), msgs)
    def test_mandates_table_against_the_template(self):
        _, functions = seats.rules()
        self.assertEqual(seats.check_mandates(TEMPLATE.read_text(), functions, "templates/mandates.md"), [])   # the template seeds a passing table
        bad = "| seat | function | domain |\n|---|---|---|\n| x | counsel | d |\n"
        self.assertEqual(len(seats.check_mandates(bad, functions)), 1); self.assertIn("columns", seats.check_mandates(bad, functions)[0])
        hdr = "| " + " | ".join(seats.MANDATE_COLUMNS) + " |\n|" + "---|" * len(seats.MANDATE_COLUMNS) + "\n"
        msgs = seats.check_mandates(hdr + "| x-1 | nobody | d | f | 1 | e | r |\n| y-1 | audit | d |\n", functions)
        self.assertEqual(len(msgs), 2); self.assertIn("'nobody'", msgs[0]); self.assertIn("3 cells", msgs[1])
    def test_check_package_over_a_fixture(self):
        root = fixture(["cab-2", "counsel-0032b4c0"]); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        msgs = seats.check_package(root)
        self.assertEqual(len(msgs), 2); self.assertTrue(msgs[0].startswith("warning: 1 of 2")); self.assertTrue(msgs[1].startswith("warning: skip mandates: no preferences-corpus/MANDATES.md"))
        root2 = fixture(["counsel-0032b4c0"], TEMPLATE.read_text()); self.addCleanup(shutil.rmtree, root2, ignore_errors=True)
        self.assertEqual(seats.check_package(root2), [])
        self.assertIn("1 seat(s) in the form of 1 presence file(s)", seats.summary(root2))
    def test_live_repo_never_fails(self):
        root = dyadlib.repo_root()
        msgs = seats.check_package(root)
        self.assertTrue(all(m.startswith("warning:") for m in msgs), msgs)   # advisory by construction (Rule-16 Presence): the runner fails any other line
        d = seats.describe(root); self.assertEqual([f[0] for f in d["fields"]], list(seats.FIELDS))

if __name__ == "__main__":
    unittest.main()
