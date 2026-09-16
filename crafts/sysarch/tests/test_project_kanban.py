"""kanban projector tests (crafts/sysarch/rules/projection.md; d-work #186): fixture rows across
every state land in the right column, a blocked card shows its refs, the archived column collapses,
the phase strip reads every life-cycle phase from the store and flags one out of order (#37),
determinism (render twice, byte-equal), self-contained output, and a live run over the real
instance."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projectors"))
import project_kanban as pk
import dyadlib

def fixture(rows: dict[str, dict]) -> Path:
    """rows: id -> {title, state, disposed, refs}."""
    root = Path(tempfile.mkdtemp())
    d = root / "agent-corpus" / "d-work" / "rows"; d.mkdir(parents=True)
    for rid, fields in rows.items():
        r = dyadlib.Row(id=int(rid), title=fields.get("title", "t"), opened="2026-09-14",
                         state=fields["state"], disposed=fields.get("disposed", ""), refs=fields.get("refs", ""))
        (d / f"{rid}.md").write_text(dyadlib.format_row_file(r))
    return root

class ContractTests(unittest.TestCase):
    def test_columns_match_states(self):
        self.assertEqual(set(pk.COLUMNS), dyadlib.STATES)
        self.assertEqual(len(pk.COLUMNS), 6); self.assertEqual(pk.COLUMNS[-1], "archived"); self.assertEqual(pk.COLLAPSED, "archived")

class CollectTests(unittest.TestCase):
    def test_groups_by_state_sorted_by_id(self):
        root = fixture({"3": {"title": "c", "state": "open"}, "1": {"title": "a", "state": "open"},
                         "2": {"title": "b", "state": "done"}})
        groups = pk.collect(root)
        self.assertEqual([r.id for r in groups["open"]], [1, 3])
        self.assertEqual([r.id for r in groups["done"]], [2])
        self.assertEqual(groups["planned"], []); self.assertEqual(groups["blocked"], []); self.assertEqual(groups["backlog"], []); self.assertEqual(groups["archived"], [])
    def test_every_column_present_even_when_empty(self):
        groups = pk.collect(fixture({}))
        self.assertEqual(set(groups.keys()), set(pk.COLUMNS))

class CraftFilterTests(unittest.TestCase):
    """`--craft` (d-work #22): the same `refs` routing tag `dyad dwork list --craft` reads."""
    def test_collect_keeps_only_tagged_rows(self):
        root = fixture({"1": {"title": "a", "state": "backlog", "refs": "workstation-149 sysarch"},
                         "2": {"title": "b", "state": "backlog", "refs": "workstation-184 1 syseng"},
                         "3": {"title": "c", "state": "open"}})
        groups = pk.collect(root, craft="sysarch")
        self.assertEqual([r.id for r in groups["backlog"]], [1])
        self.assertEqual(sum(len(v) for v in groups.values()), 1)
    def test_no_craft_keeps_every_row(self):
        root = fixture({"1": {"title": "a", "state": "backlog", "refs": "sysarch"},
                         "2": {"title": "b", "state": "open"}})
        self.assertEqual(sum(len(v) for v in pk.collect(root).values()), 2)
    def test_unmatched_craft_yields_empty_board(self):
        root = fixture({"1": {"title": "a", "state": "backlog", "refs": "sysarch"}})
        groups = pk.collect(root, craft="syseng")
        self.assertEqual(sum(len(v) for v in groups.values()), 0)
    def test_render_heading_and_subtitle_name_the_craft(self):
        root = fixture({"1": {"title": "a", "state": "backlog", "refs": "sysarch"}})
        out = pk.render(pk.collect(root, craft="sysarch"), craft="sysarch")
        self.assertIn("d-work kanban — sysarch", out)
        self.assertIn("1 row tagged `sysarch`", out)
    def test_render_unfiltered_keeps_original_heading(self):
        out = pk.render(pk.collect(fixture({})))
        self.assertIn("<h1>d-work kanban</h1>", out)
        self.assertNotIn("tagged", out)
    def test_deterministic_with_craft(self):
        root = fixture({"1": {"title": "a", "state": "backlog", "refs": "sysarch"},
                         "2": {"title": "b", "state": "open", "refs": "sysarch"}})
        groups = pk.collect(root, craft="sysarch")
        self.assertEqual(pk.render(groups, "sysarch"), pk.render(groups, "sysarch"))


class RenderTests(unittest.TestCase):
    def test_card_shows_id_title_and_refs(self):
        groups = pk.collect(fixture({"7": {"title": "fix the thing", "state": "open", "refs": "#3"}}))
        out = pk.render(groups)
        self.assertIn("#7", out); self.assertIn("fix the thing", out); self.assertIn("refs: #3", out)
    def test_blocked_card_shows_refs(self):
        groups = pk.collect(fixture({"9": {"title": "waiting", "state": "blocked", "refs": "#5"}}))
        out = pk.render(groups)
        self.assertIn('id="d-9"', out); self.assertIn("refs: #5", out); self.assertIn("blocked", out)
    def test_archived_column_collapsed_when_nonempty(self):
        groups = pk.collect(fixture({"1": {"title": "x", "state": "archived", "disposed": "2026-09-14 Y plan; 2026-09-15 Y done; 2026-09-16 Y archive"}}))
        out = pk.render(groups)
        self.assertIn("<details>", out); self.assertIn("show 1 archived row", out)
    def test_done_column_stays_open(self):
        groups = pk.collect(fixture({"1": {"title": "x", "state": "done", "disposed": "2026-09-14 Y plan; 2026-09-15 Y done"}}))
        out = pk.render(groups)
        self.assertNotIn("<details>", out); self.assertIn("Done", out)
    def test_disposition_badge_counts_semicolon_entries(self):
        groups = pk.collect(fixture({"1": {"title": "x", "state": "planned", "disposed": "2026-09-14 Y plan; 2026-09-14 Y done"}}))
        out = pk.render(groups)
        self.assertIn(">2<", out)
    def test_long_title_is_cut_but_full_title_in_tooltip(self):
        long = "x" * 200
        groups = pk.collect(fixture({"1": {"title": long, "state": "open"}}))
        out = pk.render(groups)
        self.assertIn("…", out)
        self.assertIn(f'title="{long}"', out)
    def test_html_escaped(self):
        groups = pk.collect(fixture({"1": {"title": "<script>alert(1)</script>", "state": "open"}}))
        out = pk.render(groups)
        self.assertNotIn("<script>alert", out)
        self.assertIn("&lt;script&gt;", out)
    def test_empty_column_says_none(self):
        groups = pk.collect(fixture({"1": {"title": "x", "state": "open"}}))
        out = pk.render(groups)
        self.assertIn("none", out)
    def test_self_contained(self):
        groups = pk.collect(fixture({"1": {"title": "x", "state": "open"}}))
        out = pk.render(groups)
        for load in ("src=", "<link", 'href="http', "url("):   # nothing loaded; a title may name a URL
            self.assertNotIn(load, out)
    def test_deterministic(self):
        groups = pk.collect(fixture({"3": {"title": "c", "state": "open"}, "1": {"title": "a", "state": "backlog"}}))
        self.assertEqual(pk.render(groups), pk.render(groups))

class PhaseTests(unittest.TestCase):
    """The strip (#37): every phase from the store alone; out-of-order phases flagged, never hidden."""
    def store(self, rows, plans=(), prov=None):
        root = fixture(rows)
        d = root / "agent-corpus" / "d-work"
        (d / "plans").mkdir(); (d / "provenance").mkdir()
        for rid in plans:
            (d / "plans" / f"{rid}.md").write_text("# Plan\n")
        for rid, text in (prov or {}).items():
            (d / "provenance" / f"{rid}.md").write_text(text)
        return root
    def test_full_life_cycle_all_lit(self):
        root = self.store({"1": {"title": "x", "state": "done", "disposed": "2026-09-14 Y plan; 2026-09-15 Y done (merges PR #6, #7)"}}, plans=("1",),
                          prov={"1": "# Provenance #1\n\n## 1 prompt 2026-09-14\n\n```\np\n```\n\n## 2 disposition 2026-09-14 plan\n\n```\nY\n```\n\n## 3 disposition 2026-09-15 done\n\n```\nY\n```\n"})
        r = pk.collect(root)["done"][0]
        life = pk.lifecycle(r, root)
        self.assertEqual(life["warn"], set())
        self.assertTrue(all(life["phases"][n][0] for n in pk.PHASES if n != "archived"))
        self.assertEqual(life["phases"]["PRs"][1], "#6, #7"); self.assertEqual(life["phases"]["plan-Y"][1], "2026-09-14")
        self.assertEqual(life["phases"]["provenance"][1], "1 prompt, 2 disposition")
        out = pk.render(pk.collect(root), root=root)
        self.assertNotIn("ph warn", out); self.assertIn('title="PRs: #6, #7"', out)
    def test_done_without_plan_y_is_flagged(self):
        root = self.store({"1": {"title": "x", "state": "done", "disposed": "2026-09-16 Y done"}}, plans=("1",))
        life = pk.lifecycle(pk.collect(root)["done"][0], root)
        self.assertIn("Done-Y", life["warn"])
        self.assertIn("ph warn", pk.render(pk.collect(root), root=root))
    def test_planned_without_plan_y_and_backlog_with_plan_file_are_flagged(self):
        root = self.store({"1": {"title": "x", "state": "planned"}, "2": {"title": "y", "state": "backlog"}}, plans=("2",))
        g = pk.collect(root)
        self.assertIn("plan-Y", pk.lifecycle(g["planned"][0], root)["warn"])
        self.assertIn("plan", pk.lifecycle(g["backlog"][0], root)["warn"])
    def test_provenance_count_mismatch_is_flagged(self):
        root = self.store({"1": {"title": "x", "state": "planned", "disposed": "2026-09-14 Y plan"}}, plans=("1",),
                          prov={"1": "# Provenance #1\n\n## 1 prompt 2026-09-14\n\n```\np\n```\n"})
        self.assertIn("provenance", pk.lifecycle(pk.collect(root)["planned"][0], root)["warn"])
    def test_no_root_reads_plan_and_provenance_as_unknown(self):
        root = fixture({"1": {"title": "x", "state": "open"}})
        life = pk.lifecycle(pk.collect(root)["open"][0])
        self.assertIsNone(life["phases"]["plan"][0]); self.assertEqual(life["phases"]["provenance"][1], "unknown")
        self.assertIn("ph unknown", pk.render(pk.collect(root)))
    def test_archived_phase_lit_only_when_archived(self):
        root = fixture({"1": {"title": "x", "state": "archived", "disposed": "2026-09-14 Y plan; 2026-09-15 Y done; 2026-09-16 Y archive"}})
        self.assertTrue(pk.lifecycle(pk.collect(root)["archived"][0])["phases"]["archived"][0])
    def test_strip_deterministic_and_escaped(self):
        root = self.store({"1": {"title": "<b>", "state": "open", "disposed": '2026-09-14 Y plan "<x>"'}}, plans=("1",))
        a, b = pk.render(pk.collect(root), root=root), pk.render(pk.collect(root), root=root)
        self.assertEqual(a, b); self.assertNotIn('"<x>"', a)

class LiveTests(unittest.TestCase):
    def test_live_run(self):
        root = dyadlib.repo_root()
        groups = pk.collect(root)
        out = pk.render(groups)
        self.assertIn("<html>", out)
        total = sum(len(v) for v in groups.values())
        self.assertEqual(total, len(dyadlib.read_rows(root)))   # every row of this instance is on the board, however many (dyad-system #1)

if __name__ == "__main__":
    unittest.main()
