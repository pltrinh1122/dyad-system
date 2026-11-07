"""`dyad dwork intent` tests (scripts/intent.py, d-work #615): the candidates a reading reads — rows of any state and
surface items, ranked by cosine against the row's prompts, ten of each, no threshold — and the parsers they read."""
import contextlib, io, os, sys, tempfile, unittest, unittest.mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dyadlib
it = dyadlib.load_module(dyadlib.PKG / "scripts" / "intent.py", "intent")


def R(i, title, state="done", opened="2026-11-01"):
    return dyadlib.Row(i, title, opened, state, "", "", "explicit")


class CandidateTests(unittest.TestCase):
    def test_ranks_rows_of_any_state_and_surface_items_with_no_threshold(self):
        rows = [R(1, "the guard for backlog hygiene", "backlog"), R(2, "a release gate for tags", "done"),
                R(3, "unrelated weather"), R(4, "the guard reads the backlog twice", "archived"),
                *[R(10 + k, f"filler row {k} alpha") for k in range(20)]]
        near, items = it.candidates("a guard for the backlog", rows, {}, {"S1 `dyad sweep`": "| `dyad sweep` | backlog guard |"})
        self.assertEqual([i for _, i in near][:2], [1, 4])                  # backlog and archived rows both ranked
        self.assertNotIn(3, [i for _, i in near])                            # zero cosine: no shared token, dropped
        self.assertEqual([k for _, k in items], ["S1 `dyad sweep`"])
        self.assertTrue(all(0 < c <= 1.0 + 1e-9 for c, _ in near + items))
    def test_the_row_itself_is_never_a_candidate_and_top_bounds_each_list(self):
        rows = [R(i, f"the guard topic {i}") for i in range(1, 6)] + [R(100 + k, f"pad{k} filler{k}") for k in range(30)]
        near, _ = it.candidates("guard topic", rows, {}, {}, rid=1, top=3)
        self.assertEqual(len(near), 3); self.assertNotIn(1, [i for _, i in near])
    def test_texts_override_titles(self):
        rows = [R(1, "one"), R(2, "two"), *[R(10 + k, f"pad {k}") for k in range(10)]]
        near, _ = it.candidates("zebra", rows, {2: "two zebra"}, {})
        self.assertEqual([i for _, i in near], [2])


class ParserTests(unittest.TestCase):
    def test_plan_sections_keeps_intent_and_definition_of_done(self):
        text = "# Plan #1\n## Intent as read\nkeep a\n## Mutation\ndrop b\n## Definition of done (proposed)\nkeep c\n"
        self.assertEqual(it.plan_sections(text), "keep a\nkeep c")
    def test_surface_items_skip_headers_and_other_sections(self):
        text = ("# t\n## Not surface\n| x | y |\n|---|---|\n| no | 1 |\n## S2 Stores\n| entity | path |\n|---|---|\n"
                "| row | `rows/` |\n| row | again |\n")
        self.assertEqual(it.surface_items(text), {"S2 row": "| row | `rows/` |"})
    def test_age_reads_a_date_or_says_so(self):
        import datetime
        self.assertEqual(it.age("2026-11-01", datetime.date(2026, 11, 6)), "5d")
        self.assertEqual(it.age("d", datetime.date(2026, 11, 6)), "?")


class MainTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        d = self.root / "agent-corpus" / "d-work"
        for sub in ("rows", "provenance", "plans"):
            (d / sub).mkdir(parents=True)
        for i, title, state in ((1, "intent reading before the plan", "open"), (2, "a reading of the operator prompt", "done"),
                                (3, "zebra crossing", "backlog"), *[(10 + k, f"pad row {k}", "done") for k in range(10)]):
            (d / "rows" / f"{i}.md").write_text(dyadlib.format_row_file(R(i, title, state)))
        (d / "provenance" / "1.md").write_text("# Provenance #1\n\n## 1 prompt 2026-11-06\n```\nread the operator prompt first\n```\n")
        (d / "plans" / "2.md").write_text("# Plan #2\n## Intent as read\nthe operator prompt is read\n## Mutation\nzebra\n")
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus"}); e.start(); self.addCleanup(e.stop)
    def run_(self, *a):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = it.main(list(a), self.root)
        return rc, out.getvalue(), err.getvalue()
    def test_prints_rows_with_state_and_age_against_the_prompts(self):
        rc, out, _ = self.run_("1")
        self.assertEqual(rc, 0)
        self.assertIn("intent candidates for #1 intent reading before the plan (against its prompts;", out)
        self.assertRegex(out, r"\n  \d\.\d\d  #2 \[done, \d+d\] a reading of the operator prompt\n")
        self.assertNotIn("#3 ", out); self.assertNotIn("#1 [", out)
        self.assertIn("surface:", out)                                            # the live surface, read as data
    def test_labels_under_dwork_slug_on(self):
        """#622 Decision 4: the head line and each candidate row read `#<id>-<slug>` under `on`."""
        d = self.root / "agent-corpus" / "d-work" / "rows"
        for i, slug in ((1, "intent-reading"), (2, "operator-prompt")):
            (d / f"{i}.md").write_text((d / f"{i}.md").read_text() + f"slug: {slug}\n")
        with unittest.mock.patch.object(dyadlib, "slugs_on", lambda root=None: True):
            rc, out, _ = self.run_("1")
        self.assertEqual(rc, 0)
        self.assertIn("intent candidates for #1-intent-reading intent reading before the plan", out)
        self.assertRegex(out, r"\n  \d\.\d\d  #2-operator-prompt \[done, \d+d\] a reading of the operator prompt\n")
    def test_refuses_a_bad_form_or_an_unknown_row(self):
        self.assertEqual(self.run_()[0], 1); self.assertEqual(self.run_("x")[0], 1); self.assertEqual(self.run_("1", "2")[0], 1)
        rc, _, err = self.run_("77"); self.assertEqual(rc, 1); self.assertIn("no row 77", err)
    def test_invariants(self):
        self.assertEqual(dyadlib.check_invariants(it), len(it.INVARIANTS))



if __name__ == "__main__":
    unittest.main()
