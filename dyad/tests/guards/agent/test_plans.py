"""Plan guard tests (agent/plans.py): the `# Plan #<id>` title (id equals the file name), the base
commit line, an intent line; the PLAN_PARTS presence warnings; the live plan store fails nothing."""
import contextlib, io, os, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
pl = dyadlib.load_guard("agent", "plans")


def live_plan(test: unittest.TestCase, rid: int) -> None:
    """#608: a test that reads one of this instance's own plan files skips where the file is absent — a fresh install,
    as corroboration's scratch install builds it (core plus bundled crafts), holds no plans of this instance."""
    if not (pl.plans_dir(dyadlib.repo_root()) / f"{rid}.md").is_file():
        test.skipTest(f"this instance keeps no plan #{rid} (a fresh install)")

GOOD = "# Plan #7 — a title\n\nBase commit of `main`: abc1234. Falsification below.\n\n## Intent as read\nx\n## Mutation\ny\nfiles touched: f\n"

def fixture(plans: dict[str, str]):
    root = Path(tempfile.mkdtemp()); d = root / "agent-corpus" / "d-work" / "plans"; d.mkdir(parents=True)
    for name, text in plans.items(): (d / name).write_text(text)
    return root

class PlanTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_parse(self):
        self.assertEqual(pl.parse(GOOD), {"id": "7", "title": "a title", "base commit": "abc1234.", "intent": "## Intent as read"})
        self.assertEqual(pl.parse("# Plan #8\nbase commit: def (main)\n")["base commit"], "def")
        self.assertEqual(pl.parse("# nope\n"), {"id": "", "title": "", "base commit": "", "intent": ""})
    def test_good_plan_passes(self):
        self.assertEqual(pl.check_package(fixture({"7.md": GOOD})), [])
        self.assertEqual(pl.check_package(fixture({})), []); self.assertEqual(pl.check_package(Path(tempfile.mkdtemp())), [])
    def test_bad_title_and_id_mismatch_fail(self):
        msgs = pl.check_package(fixture({"7.md": GOOD.replace("# Plan #7", "# Plan 7")}))
        self.assertEqual(len([m for m in msgs if not m.startswith("warning:")]), 1); self.assertIn("first line is not `# Plan #<id>`", msgs[0])
        msgs = pl.check_package(fixture({"8.md": GOOD}))
        self.assertIn("title id #7 differs from the file name", msgs[0])
    def test_missing_base_commit_fails(self):
        msgs = pl.check_package(fixture({"7.md": GOOD.replace("Base commit of `main`: abc1234.", "at abc1234.")}))
        self.assertTrue(any("no base commit line" in m and not m.startswith("warning:") for m in msgs), msgs)
    def test_missing_intent_and_parts_warn_only(self):
        msgs = pl.check_package(fixture({"7.md": "# Plan #7\nbase commit: abc\n"}))
        self.assertTrue(all(m.startswith("warning: ") for m in msgs), msgs)
        self.assertTrue(any("names no intent" in m for m in msgs)); self.assertTrue(any("never mentions `mutation`" in m for m in msgs))
        self.assertEqual(len(msgs), 1 + len([p for p in dyadlib.PLAN_PARTS[:-1] if p != "base commit"]))   # no row: five parts
    def test_definition_of_done_is_asked_only_from_DOD_SINCE(self):
        """#574: a plan whose row opened on or after DOD_SINCE is asked for its definition of done; an older one is not."""
        root = fixture({"7.md": GOOD, "8.md": GOOD.replace("#7", "#8"), "9.md": GOOD.replace("#7", "#9") + "## Definition of done\nz\n"})
        rows = root / "agent-corpus" / "d-work" / "rows"; rows.mkdir(parents=True)
        for rid, opened in ((7, "2026-11-04"), (8, dyadlib.DOD_SINCE), (9, "2026-12-01")):
            (rows / f"{rid}.md").write_text(f"id: {rid}\ntitle: t\nopened: {opened}\nstate: open\ndisposed: \nrefs: \n")
        self.assertEqual(pl.check_package(root), ["warning: 8.md: never mentions `definition of done` (dyadlib.PLAN_PARTS)"])
        self.assertEqual(pl.parts_for(None), dyadlib.PLAN_PARTS[:5])

    def test_non_numeric_files_ignored(self):
        self.assertEqual(pl.check_package(fixture({"README.md": "# no plan\n"})), [])
    def test_describe_fields_start_with_FIELDS_and_add_parts(self):
        d = pl.describe(fixture({"7.md": GOOD}))
        names = [f[0] for f in d["fields"]]
        self.assertEqual(names[:4], list(pl.FIELDS)); self.assertEqual(len(names), len(set(names)))
        self.assertIn("intent as read", names); self.assertNotIn("base commit", names[4:])
        self.assertEqual(d["observed"], 1)

def sh(*a, cwd): return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout

def row(rid, state="open", refs="", opened="2026-11-01"):
    return f"id: {rid}\ntitle: t{rid}\nopened: {opened}\nstate: {state}\ndisposed: \nrefs: {refs}\n"

def plan(rid, body=""):
    return f"# Plan #{rid} — t\n\nBase commit of main: abc1234.\n\n## Intent as read\nx\n{body}"

class PlanCheckTests(unittest.TestCase):
    """#592 R-c: `dyad plan check <id>` warns on a second zone in Files touched, a touched module whose test is not
    listed, a touched craft whose VERSION is already its tag (mode 18), the callers of each `module.function` the
    Mutation names (mode 37), a refs dependency not done, and `order: required` with no `step:` line (mode 17)."""
    def setUp(self):
        os.environ.pop("DYAD_INSTANCE", None)
        self.root = Path(tempfile.mkdtemp())
        sh("git", "init", "-q", "-b", "main", cwd=self.root)
        sh("git", "config", "user.email", "t@t", cwd=self.root); sh("git", "config", "user.name", "t", cwd=self.root)
        for rel, text in (("dyad/VERSION", "1.0.0\n"), ("dyad/scripts/foo.py", "def bar():\n    return 1\n"),
                          ("dyad/scripts/baz.py", "import foo\nfoo.bar()\n"), ("dyad/tests/test_foo.py", "\n")):
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True); (self.root / rel).write_text(text)
        self.rows = self.root / "agent-corpus" / "d-work" / "rows"; self.rows.mkdir(parents=True)
        self.plans = self.root / "agent-corpus" / "d-work" / "plans"; self.plans.mkdir(parents=True)
        sh("git", "add", "-A", cwd=self.root); sh("git", "commit", "-qm", "root", cwd=self.root)
    def check(self, body, refs="", rows=()):
        self.rows.joinpath("7.md").write_text(row(7, refs=refs))
        for rid, st in rows: self.rows.joinpath(f"{rid}.md").write_text(row(rid, st))
        self.plans.joinpath("7.md").write_text(plan(7, body))
        return [m for m in pl.check_dwork(7, self.root) if "never mentions" not in m]
    def test_files_touched_parses_inline_and_heading_forms(self):
        self.assertEqual(pl.files_touched("Files touched: a/b.py, `c/d.md`,\ne/f.txt.\n\nx/y.py\n"), ["a/b.py", "c/d.md", "e/f.txt"])
        self.assertEqual(pl.files_touched("## Files touched\ndyad/x.py (or the existing one), dyad/tests/test_x.py\n## Next\nz/z.py\n"),
                         ["dyad/x.py", "dyad/tests/test_x.py"])
        self.assertEqual(pl.files_touched("no such part\n"), [])
    def test_a_clean_plan_warns_nothing(self):
        self.assertEqual(self.check("Files touched: dyad/scripts/foo.py, dyad/tests/test_foo.py, dyad/VERSION\n"), [])
    def test_a_second_zone_warns(self):
        out = self.check("Files touched: dyad/tests/test_foo.py, preferences-corpus/PREFERENCES.md\n")
        self.assertEqual(len(out), 1, out); self.assertIn("span zones agent, preferences", out[0])
    def test_a_touched_module_without_its_test_warns(self):
        out = self.check("Files touched: dyad/scripts/foo.py, dyad/VERSION\n")
        self.assertEqual(out, ["warning: 7.md: touches dyad/scripts/foo.py but not its test dyad/tests/test_foo.py "
                               "(crafts/syseng/rules/verifiable-code.md p4)"])
    def test_a_touched_craft_whose_version_is_its_tag_warns(self):
        body = "Files touched: dyad/scripts/foo.py, dyad/tests/test_foo.py\n"
        self.assertEqual(self.check(body), [])                                          # no tag yet: nothing to drift from
        sh("git", "tag", "dyad-operator-v1.0.0", cwd=self.root)
        out = self.check(body); self.assertEqual(len(out), 1, out)
        self.assertIn("release tag dyad-operator-v1.0.0", out[0]); self.assertIn("mode 18", out[0])
        self.assertEqual(self.check(body.replace("\n", ", dyad/VERSION\n")), [])        # the plan bumps it
    def test_callers_of_a_named_function_warn(self):
        out = self.check("## Mutation\n- `foo.bar` changes; `foo.nothing` and `zzz.bar` are not functions here.\n")
        self.assertEqual(out, ["warning: 7.md: the Mutation names foo.bar, called from 1 other file(s): dyad/scripts/baz.py (mode 37)"])
        out = self.check("## Mutation\n- `dyad/scripts/foo.py` `bar` changes.\n")
        self.assertEqual(len(out), 1, out); self.assertIn("foo.bar", out[0])
    def test_a_same_named_function_of_another_module_is_no_caller(self):
        (self.root / "dyad/scripts/other.py").write_text("def bar():\n    return 2\n\nbar()\n")   # its own `bar`, defined and called
        (self.root / "dyad/scripts/third.py").write_text("x = bar(1)\n")                         # a `bar` from nowhere named
        (self.root / "dyad/scripts/alias.py").write_text("import dyadlib\nF = dyadlib.load_guard(\"x\", \"foo\")\nF.bar()\n")
        (self.root / "dyad/scripts/frm.py").write_text("from foo import bar as _b, bar\n\nbar()\n")
        out = self.check("## Mutation\n- `foo.bar` changes.\n")
        self.assertEqual(len(out), 1, out)
        self.assertIn("called from 3 other file(s): dyad/scripts/alias.py, dyad/scripts/baz.py, dyad/scripts/frm.py", out[0])
        self.assertNotIn("other.py", out[0]); self.assertNotIn("third.py", out[0])
    def test_a_refs_dependency_not_done_warns(self):
        out = self.check("", refs="parent #3 4 #5 PR #6", rows=((3, "open"), (4, "open"), (5, "done"), (6, "open")))
        self.assertEqual(out, ["warning: 7.md: refs dependency #4 is open, not done"])   # the parent and a PR are no dependency
    def test_mode_numbers_and_a_second_pr_or_child_are_no_dependency(self):
        rows = tuple((i, "open") for i in (3, 4, 5, 6, 8, 9, 10, 11))
        out = self.check("", refs="parent #3 4 modes 05 06 PR #8 #9 children #10 #11", rows=rows)
        self.assertEqual(out, ["warning: 7.md: refs dependency #4 is open, not done"])
    def test_order_required_needs_a_step_line(self):
        out = self.check("order: required\n")
        self.assertEqual(len(out), 1, out); self.assertIn("names no `step:` line", out[0])
        self.assertEqual(self.check("order: required\n- step 1: the guard\n- step 2: the CLI\n"), [])
    def test_backticked_order_and_step_mentions_are_prose(self):
        self.assertEqual(self.check("Not needed: `order: required` for that one file only.\n"), [])   # no declaration
        out = self.check("order: required\n  `step:` lines under `order: required` are counsel's.\n")   # a mention declares no step
        self.assertEqual(len(out), 1, out); self.assertIn("names no `step:` line", out[0])
    def test_no_plan_file_is_the_one_failure(self):
        out = pl.check_dwork(99, self.root)
        self.assertEqual(len(out), 1); self.assertFalse(out[0].startswith("warning:")); self.assertIn("no plan file", out[0])
    def test_cli(self):
        self.check("order: required\n")
        with contextlib.redirect_stdout(io.StringIO()) as so:
            self.assertEqual(pl.cli(["check", "7"], self.root), 0)
        self.assertIn("warn [plan] 7.md: says `order: required`", so.getvalue()); self.assertIn("ok   [plan] #7", so.getvalue())
        with contextlib.redirect_stdout(io.StringIO()) as so:
            self.assertEqual(pl.cli(["--help"], self.root), 0); self.assertEqual(pl.cli(["check", "--help"], self.root), 0)
        self.assertIn("usage: dyad plan check <id>", so.getvalue())
        with contextlib.redirect_stderr(io.StringIO()) as se:
            self.assertEqual(pl.cli(["check", "7", "--bogus"], self.root), 1)
            self.assertEqual(pl.cli(["nope"], self.root), 1); self.assertEqual(pl.cli(["check", "x"], self.root), 1)
            self.assertEqual(pl.cli(["check", "99"], self.root), 1)
        self.assertIn("does not take --bogus", se.getvalue()); self.assertIn("FAIL [plan] no plan file", se.getvalue())

class MandateCeilingTests(unittest.TestCase):
    """#592 R-c (mode 31): the plan's stated ceiling refuses one row past it at `dwork new --mandate`; the seat's
    charter ceiling (MANDATES.md) only warns (the home's answer to F11)."""
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_stated_ceiling(self):
        for text, want in (("Mandate scope: one child per item; ceiling 2\n", 2), ("- **Mandate scope:** a rule; ceiling **1**\n", 1),
                           ("3. **Mandate ceiling:** 12 children.\n", 12), ("Mandate scope — rule: x; ceiling: 7\n", 7),
                           ("Mandate scope: none of its own.\n", None), ("The mandate's ceiling drops from 12.\n", None),
                           ("Mandate scope: a; ceiling 2\nrevision 2 — Mandate scope: a; ceiling 5\n", 5),
                           ("- **Mandate scope:** one child each; ceiling 12; x\n\nThe ceiling stays 2 at a time.\n\n"
                            "**Ceiling.** This mandate has 12 children, at revision 1's ceiling of 12. These two\n"
                            "make 14, so the ceiling rises to 14 with this plan-`Y`.\n", 14),               # plan #570 revision 2's shape
                           ("Mandate scope: a; ceiling 12\nthe ceiling rises to 14.\nLater the ceiling rises to 16.\n", 16),
                           ("Mandate scope: a; ceiling 12\nThe mandate's ceiling drops from 12 to whatever H1 finds.\n", 12)):
            with self.subTest(text=text):
                self.assertEqual(pl.stated_ceiling(text), want)
    def test_the_live_plan_570_reads_its_last_statement(self):
        """Revision 2 of plan #570 raises the ceiling from 12 to 14 (`the ceiling rises to 14`); the live reading is that,
        or a later revision's, never revision 1's 12."""
        live_plan(self, 570)
        self.assertGreaterEqual(pl.mandate_ceiling(570), 14)
    def fixture(self, n, ceiling=12, seat=None, charter=None):
        root = fixture({"1.md": plan(1, f"Mandate scope: one child per criterion; ceiling {ceiling}\n")})
        rows = {i: dyadlib.Row(i, "t", "d", "open", "", f"parent #1" if i > 1 else "", "implicit") for i in range(1, n + 2)}
        if seat:
            pv = root / "agent-corpus" / "d-work" / "provenance"; pv.mkdir(parents=True)
            pv.joinpath("1.md").write_text(f"# Provenance #1\n\nsession: {seat}\n")
        if charter is not None:
            (root / "preferences-corpus").mkdir()
            (root / "preferences-corpus" / "MANDATES.md").write_text(
                "| seat | function | domain | fence | ceiling | escalations | revocation |\n|---|---|---|---|---|---|---|\n"
                f"| program-1234abcd | program | d | f | {charter} (none) | e | r |\n| engineer-<hp> | engineer | d | f | 8 | e | r |\n")
        return rows, root
    def test_twelve_of_twelve_refuses(self):
        rows, root = self.fixture(12)
        self.assertEqual(pl.children(rows, 1), list(range(2, 14)))
        refusal, warns = pl.ceiling_check(rows, 1, root)
        self.assertIn("already has 12 children, its plan's stated ceiling 12", refusal); self.assertEqual(warns, [])
        rows, root = self.fixture(11); self.assertEqual(pl.ceiling_check(rows, 1, root), (None, []))   # 11 of 12: the 12th is inside
    def test_the_charter_ceiling_only_warns(self):
        rows, root = self.fixture(3, seat="program-1234abcd", charter=0)
        refusal, warns = pl.ceiling_check(rows, 1, root)
        self.assertIsNone(refusal); self.assertEqual(len(warns), 1); self.assertIn("charter ceiling 0", warns[0])
        rows, root = self.fixture(3, seat="engineer-feedbeef", charter=0)   # the `<function>-<hp>` row: 8
        self.assertEqual(pl.charter_ceiling("engineer-feedbeef", root), 8); self.assertEqual(pl.ceiling_check(rows, 1, root), (None, []))
    def test_a_seat_re_held_under_a_new_hp_finds_its_function_row(self):
        rows, root = self.fixture(3, seat="program-deadbeef", charter=0)   # the row is program-1234abcd
        self.assertEqual(pl.charter_ceiling("program-deadbeef", root), 0)
        self.assertEqual(pl.charter_ceiling("program-topic-deadbeef", root), 0)   # a topic seat of the function
        self.assertEqual(pl.charter_ceiling("program-1234abcd", root), 0); self.assertIsNone(pl.charter_ceiling("nosuch-deadbeef", root))
        refusal, warns = pl.ceiling_check(rows, 1, root)
        self.assertIsNone(refusal); self.assertEqual(len(warns), 1); self.assertIn("charter ceiling 0", warns[0])
    def test_a_plan_stating_no_ceiling_warns(self):
        root = fixture({"1.md": plan(1, "Mandate scope: none.\n")})
        refusal, warns = pl.ceiling_check({}, 1, root)
        self.assertIsNone(refusal); self.assertIn("states no mandate ceiling", warns[0])

class LivePlanCheckTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_plan_589_has_no_failure(self):
        """#592 DoD: `dyad plan check 589` exits 0."""
        live_plan(self, 589)
        self.assertEqual([m for m in pl.check_dwork(589) if not m.startswith("warning: ")], [])

if __name__ == "__main__":
    unittest.main()
