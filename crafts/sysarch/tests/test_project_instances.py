"""sysarch projection.md projector tests (d-work #50): fixture corpus -> known node/edge counts and
target-normalization behaviour; determinism; a live run over the real instance yields well-formed,
self-contained HTML with GRAPH embedded. Interactive drawer behaviour (open/close, lazy nesting, the
cycle guard) is DOM/event behaviour a stdlib test cannot exercise (no browser in the kernel, Rule-14
property 2); it was verified manually against a real browser during d-work #50's own execution and
is named as a stated limitation of this suite, in the manner of `project_entities.py`'s own inline JS
carrying no runtime-behaviour test either."""
import json, os, re, subprocess, sys, tempfile, unittest
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projectors"))
import project_instances as pi
import dyadlib, livetest

RULE = """# Rule-{n}: {title}

**Intent:** Do the thing.
**Target:** a {target}

## Boundaries (out of scope)
- nothing

## Conditions (triggers)
- always

{body}
## Provenance
Operator rule. Falsified; see `../falsification/rules/rule-{n}-x.md`.

Set: System Requirements.
"""

def fixture():
    """A temp repo root + package: 3 Rules (1 references 2 and 3 in its text; 3 references nothing —
    a leaf), 2 rows (1 refs 2; 2 has no refs, a leaf), 1 plan (of row 1), a falsification record (of
    Rule-1) and one deliberately unresolved reference (Rule-1's text names `crafts/absent/x.py`, a
    path with no craft installed) so the `world`/`fail`-adjacent path is exercised too."""
    root = Path(tempfile.mkdtemp()); pkg = root / "pkg"
    (pkg / "rules").mkdir(parents=True)
    (pkg / "rules" / "RULE-1-x.md").write_text(RULE.format(
        n=1, title="t1", target="thing1",
        body="Cites Rule-2 and Rule-3 in prose, and a path this fixture never creates: `crafts/absent/x.py`.\n\n"))
    (pkg / "rules" / "RULE-2-x.md").write_text(RULE.format(n=2, title="t2", target="thing2", body=""))
    (pkg / "rules" / "RULE-3-x.md").write_text(RULE.format(n=3, title="t3", target="thing3", body=""))
    (pkg / "vocabulary").mkdir(); (pkg / "vocabulary" / "VOCABULARY.md").write_text(
        "# vocab\n| term | definition | owner | used by |\n|------|------------|-------|---------|\n"
        "| alpha | first | 1 | 1 2 |\n")
    (pkg / "falsification" / "rules").mkdir(parents=True)
    (pkg / "falsification" / "rules" / "rule-1-x.md").write_text("# r1\n")
    inst = root / "inst"; rows = inst / "d-work" / "rows"; rows.mkdir(parents=True)
    rows.joinpath("1.md").write_text("id: 1\ntitle: r1\nopened: d\nstate: open\ndisposed: \nrefs: #2\n")
    rows.joinpath("2.md").write_text("id: 2\ntitle: r2\nopened: d\nstate: open\ndisposed: \nrefs: \n")
    (inst / "d-work" / "plans").mkdir(); (inst / "d-work" / "plans" / "1.md").write_text("# p1\n")
    (inst / "audits").mkdir(); (inst / "audits" / "INCIDENTS.md").write_text(
        "# Incidents (Rule-3)\n\n| date | d-work | what | cause | consequence |\n|------|--------|------|-------|-------------|\n"
        "| d | #1 | x | y | z |\n")
    return root, pkg, inst

class Balanced(HTMLParser):
    VOID = {"meta", "input", "br"}
    def __init__(self):
        super().__init__(); self.stack, self.errors = [], []
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID and (not self.stack or self.stack[-1] != tag):
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced </{tag}> (stack top {self.stack[-1] if self.stack else None})")
        else:
            self.stack.pop()

def rowkey(rid): return f"row:inst/d-work/rows/{rid}.md"
def rulekey(n): return f"rule:pkg/rules/RULE-{n}-x.md"

class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.root, self.pkg, self.inst = fixture()
        self.prev = os.environ.get("DYAD_INSTANCE"); os.environ["DYAD_INSTANCE"] = str(self.inst)
        self.m = pi.collect(self.root, self.pkg)
    def tearDown(self):
        os.environ.pop("DYAD_INSTANCE", None)
        if self.prev is not None: os.environ["DYAD_INSTANCE"] = self.prev

    def test_every_store_instance_is_seeded_even_with_no_edge(self):
        """A row with no `refs`, a Rule nobody cites, is still a node (the #50 intent: browse
        everything, not only what an edge happens to touch)."""
        self.assertIn(rowkey(2), self.m.nodes)               # row 2: no refs of its own
        self.assertEqual(self.m.nodes[rowkey(2)].edges, [])
        self.assertIn(rulekey(3), self.m.nodes)              # Rule-3: cited by nobody

    def test_row_refs_row_resolves_to_the_same_node_row_seeds(self):
        """The bug this d-work caught live: an id-keyed seed and a path-keyed edge target must be
        the SAME node, not two disconnected ones."""
        n1 = self.m.nodes[rowkey(1)]
        self.assertEqual(len(n1.edges), 1)
        e = n1.edges[0]
        self.assertEqual(e.kind, "row.refs->row")
        self.assertEqual(e.target, rowkey(2))
        self.assertEqual(e.terminal_text, "")
        self.assertEqual(e.status, "ok")
        self.assertIs(self.m.nodes[e.target], self.m.nodes[rowkey(2)])   # identical object, not a lookalike

    def test_rule_text_rule_resolves_by_normalized_path_not_bare_digit(self):
        """Rule-1's title line ("# Rule-1: ...") itself matches `\\bRule-(\\d+)\\b`, so every rule
        self-cites once — real behaviour of `references.rule_text_rules`, not this projector's; the
        targets asserted here are what the fixture's *prose* adds on top of that self-citation."""
        n1 = self.m.nodes[rulekey(1)]
        targets = {e.target for e in n1.edges if e.kind == "rule.text->rule"}
        self.assertEqual(targets, {rulekey(1), rulekey(2), rulekey(3)})

    def test_unresolved_craft_path_is_world_not_a_false_fail(self):
        """`crafts/absent/x.py` has no crafts/ tree at all in this fixture: `c.crafts_absent` is
        True, so `_edge_status` reads this as `world` (declared, unwalkable here) rather than the
        bare resolver's `fail` — matching `references.check()`'s own severity, never a harsher one."""
        n1 = self.m.nodes[rulekey(1)]
        path_edges = [e for e in n1.edges if e.kind == "rule.text->path" and "absent" in e.terminal_text]
        self.assertEqual(len(path_edges), 1)
        self.assertEqual(path_edges[0].status, "world")
        self.assertEqual(path_edges[0].target, "")

    def test_label_is_never_doubled(self):
        """`where`'s remainder already names the field; #50's own incident was `label = f"{field}
        {remainder}"` producing "refs refs" when the remainder IS the bare field name."""
        n1 = self.m.nodes[rowkey(1)]
        self.assertEqual(n1.edges[0].label, "refs")

    def test_every_kind_note_row_matches_the_live_register(self):
        self.assertEqual(len(self.m.kind_notes), len(pi.references.REFERENCES))

    def test_render_deterministic_self_contained_and_balanced(self):
        a = pi.render(self.m); b = pi.render(pi.collect(self.root, self.pkg))
        self.assertEqual(a, b)
        for load in (" src=", "<link", 'href="http', "url("):
            self.assertNotIn(load, a)
        p = Balanced(); p.feed(a); p.close()
        self.assertEqual(p.errors, []); self.assertEqual(p.stack, [], p.stack)
        m = re.search(r"const GRAPH=(\{.*?\});\n", a, re.S)
        self.assertIsNotNone(m)
        graph = json.loads(m.group(1))
        self.assertEqual(set(graph), set(self.m.nodes))
        self.assertEqual(graph[rowkey(1)]["edges"][0]["target"], rowkey(2))
    def test_no_details_open_by_default(self):
        """Every drawer closed by default is structural: no rendered `<details>` ever carries the
        `open` attribute (the top-level tree is built entirely by JS from GRAPH; only the empty
        shells for kind groups are in the static HTML, and none of those are `open` either)."""
        a = pi.render(self.m)
        self.assertNotIn("<details open", a)
        self.assertNotIn('open="', a)

class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the projector's INVARIANTS hold."""
    def test_invariants_hold(self):
        self.assertEqual(dyadlib.check_invariants(pi), len(pi.INVARIANTS)); self.assertTrue(pi.INVARIANTS)
    def test_status_titles_cover_every_status_the_code_can_return(self):
        emitted = {"ok", "fail", "world", "delegated", "unresolved"}
        self.assertEqual(emitted, pi.EDGE_STATUSES)

class LiveTests(livetest.LiveCase):
    """A live run over this instance: no crash, well-formed output, every seeded row/plan actually
    drawn (never skipped by accident) — `livetest.py`: assert the documented behaviour or skip with
    a stated reason, never guess at a real instance's shape."""
    def test_live_run(self):
        root = dyadlib.repo_root()
        with tempfile.TemporaryDirectory() as d:
            inst = Path(d) / "inst"; import shutil
            shutil.copytree(dyadlib.instance(root), inst, ignore=shutil.ignore_patterns("projections"))
            env = dict(os.environ, DYAD_INSTANCE=str(inst))
            r = subprocess.run([sys.executable, str(pi.Path(pi.__file__))], cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("[project] instances:", r.stdout)
            out = inst / "projections" / "instances.html"; self.assertTrue(out.exists())
            text = out.read_text()
            p = Balanced(); p.feed(text); p.close()
            self.assertEqual(p.errors, []); self.assertEqual(p.stack, [])
            rows = self.require_store("rows", dyadlib.rows_dir(root), pattern=livetest.ROW_GLOB)
            m = re.search(r"const GRAPH=(\{.*?\});\n", text, re.S)
            graph = json.loads(m.group(1))
            row_nodes = [k for k, n in graph.items() if n["kind"] == "row"]
            self.assertEqual(len(row_nodes), len(rows), "every row file on disk is a node in the graph")

if __name__ == "__main__":
    unittest.main()
