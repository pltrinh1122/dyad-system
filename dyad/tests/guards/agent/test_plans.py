"""Plan guard tests (agent/plans.py): the `# Plan #<id>` title (id equals the file name), the base
commit line, an intent line; the PLAN_PARTS presence warnings; the live plan store fails nothing."""
import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
pl = dyadlib.load_guard("agent", "plans")

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

if __name__ == "__main__":
    unittest.main()
