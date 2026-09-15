"""kanban projector tests (crafts/sysarch/rules/projection.md; d-work #186): fixture rows across
every state land in the right column, a blocked card shows its refs, the done column collapses,
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
        self.assertEqual(len(pk.COLUMNS), 5)

class CollectTests(unittest.TestCase):
    def test_groups_by_state_sorted_by_id(self):
        root = fixture({"3": {"title": "c", "state": "open"}, "1": {"title": "a", "state": "open"},
                         "2": {"title": "b", "state": "done"}})
        groups = pk.collect(root)
        self.assertEqual([r.id for r in groups["open"]], [1, 3])
        self.assertEqual([r.id for r in groups["done"]], [2])
        self.assertEqual(groups["planned"], []); self.assertEqual(groups["blocked"], []); self.assertEqual(groups["backlog"], [])
    def test_every_column_present_even_when_empty(self):
        groups = pk.collect(fixture({}))
        self.assertEqual(set(groups.keys()), set(pk.COLUMNS))

class RenderTests(unittest.TestCase):
    def test_card_shows_id_title_and_refs(self):
        groups = pk.collect(fixture({"7": {"title": "fix the thing", "state": "open", "refs": "#3"}}))
        out = pk.render(groups)
        self.assertIn("#7", out); self.assertIn("fix the thing", out); self.assertIn("refs: #3", out)
    def test_blocked_card_shows_refs(self):
        groups = pk.collect(fixture({"9": {"title": "waiting", "state": "blocked", "refs": "#5"}}))
        out = pk.render(groups)
        self.assertIn('id="d-9"', out); self.assertIn("refs: #5", out); self.assertIn("blocked", out)
    def test_done_column_collapsed_when_nonempty(self):
        groups = pk.collect(fixture({"1": {"title": "x", "state": "done"}}))
        out = pk.render(groups)
        self.assertIn("<details>", out); self.assertIn("<summary>", out)
    def test_done_column_not_collapsed_when_empty(self):
        groups = pk.collect(fixture({"1": {"title": "x", "state": "open"}}))
        out = pk.render(groups)
        self.assertNotIn("<details>", out)
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
