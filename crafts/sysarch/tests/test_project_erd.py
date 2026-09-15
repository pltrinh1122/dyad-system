"""sysarch projection.md projector tests: fixture corpus -> known entity/edge counts; refs parsing; determinism;
a live run over the real instance yields a well-formed self-contained HTML file."""
import os, subprocess, sys, tempfile, unittest
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projectors"))
import project_erd as pe
import dyadlib, livetest

RULE = """# Rule-{n}: {title}

**Intent:** Do the thing.
**Target:** a {target}

## Boundaries (out of scope)
- nothing

## Conditions (triggers)
- always

## Provenance
Operator rule. Falsified; see `../falsification/rules/rule-{n}-x.md`.

Set: {set}.
"""
VOCAB = """# vocab
| term | definition | owner | used by |
|------|------------|-------|---------|
| alpha | first | 1 | 1 2 |
| beta | second | 2 | 2 |
| gamma | third | frame | 1 |
"""
PREFS = """# prefs
| key | value | allowed | read by |
|-----|-------|---------|---------|
| merge-disposition | with-done | `separate` \\| `with-done` | Rule-2 (binding), Rule-3 (form) |
"""
MANIFEST = """# manifest
| component | partition | version | purpose | license | replacement |
|-----------|-----------|---------|---------|---------|-------------|
| Python | kernel | 3.12 | code | PSF | — |
| `gh` | library | 2.45 | PRs | MIT | REST |
"""

def fixture():
    """A temp repo root + package: 3 Rules (14 among them, so components attach), 3 terms,
    2 records, 1 preference, 2 components, 4 rows with refs, 2 plans, 1 audit."""
    root = Path(tempfile.mkdtemp()); pkg = root / "pkg"
    (pkg / "rules").mkdir(parents=True)
    for n, s in ((1, "System Requirements"), (2, "System Requirements"), (14, "System Architecture")):
        (pkg / "rules" / f"RULE-{n}-x.md").write_text(RULE.format(n=n, title=f"t{n}", target=f"thing{n}", set=s))
    (pkg / "vocabulary").mkdir(); (pkg / "vocabulary" / "VOCABULARY.md").write_text(VOCAB)
    (pkg / "falsification" / "rules").mkdir(parents=True)
    (pkg / "falsification" / "rules" / "rule-1-x.md").write_text("# r1\n")
    (pkg / "falsification" / "rules" / "rules-1-2-promotion.md").write_text("# r12\n")
    (pkg / "infrastructure").mkdir(); (pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
    (root / "preferences-corpus").mkdir(); (root / "preferences-corpus" / "PREFERENCES.md").write_text(PREFS)
    inst = root / "inst"; rows = inst / "d-work" / "rows"; rows.mkdir(parents=True)
    for rid, refs in ((1, ""), (2, "parent #1"), (3, "children #4–#5; PRs #65 #66"), (4, "#1; PR #9"), (5, "parent #3")):
        rows.joinpath(f"{rid}.md").write_text(f"id: {rid}\ntitle: r{rid} <b>&\nopened: d\nstate: open\ndisposed: \nrefs: {refs}\n")
    (inst / "d-work" / "plans").mkdir(); (inst / "d-work" / "plans" / "2.md").write_text("# p2\n")
    (inst / "d-work" / "plans" / "99.md").write_text("# orphan plan\n")
    (inst / "audits").mkdir(); (inst / "audits" / "a.md").write_text("# a\n"); (inst / "audits" / "INCIDENTS.md").write_text("# i\n")
    return root, pkg, inst

class Balanced(HTMLParser):
    VOID = {"meta", "input", "br", "path", "rect"}
    def __init__(self):
        super().__init__(); self.stack, self.errors = [], []
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag in self.VOID and (not self.stack or self.stack[-1] != tag):
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced </{tag}> (stack top {self.stack[-1] if self.stack else None})")
        else:
            self.stack.pop()

class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.root, self.pkg, self.inst = fixture()
        self.prev = os.environ.get("DYAD_INSTANCE"); os.environ["DYAD_INSTANCE"] = str(self.inst)
        self.g = pe.collect(self.root, self.pkg)
    def tearDown(self):
        os.environ.pop("DYAD_INSTANCE", None)
        if self.prev is not None: os.environ["DYAD_INSTANCE"] = self.prev
    def kinds(self):
        return {k: len(v) for k, v in self.g.by_kind().items()}
    def test_entity_counts(self):
        k = self.kinds()
        self.assertEqual(k["Set"], 2); self.assertEqual(k["Rule"], 3); self.assertEqual(k["Term"], 3)
        self.assertEqual(k["Record"], 2); self.assertEqual(k["Preference"], 1); self.assertEqual(k["Component"], 2)
        self.assertEqual(k["Zone"], len({z for z, _ in pe.containment.ZONES})); self.assertEqual(k["Path"], len(pe.containment.ZONES))
        self.assertEqual(k["Row"], 5); self.assertEqual(k["Plan"], 2); self.assertEqual(k["Audit"], 1)
        self.assertEqual(len(self.g.entities), sum(k.values()))
    def test_edge_counts_by_label(self):
        by = {}
        for e in self.g.edges:
            by[e.label] = by.get(e.label, 0) + 1
        self.assertEqual(by["in set"], 3)                    # every Rule has a Set line
        self.assertEqual(by["owner"], 2)                     # gamma's owner is frame: no Rule edge
        self.assertEqual(by["used by"], 2)                   # alpha->2, gamma->1 (owner edge not repeated)
        self.assertEqual(by["falsifies"], 3)                 # rule-1 ->1; rules-1-2 -> 1, 2
        self.assertEqual(by["read by"], 1)                   # Rule-2 exists, Rule-3 does not -> dropped
        self.assertEqual(by["declared by"], 2)               # both components -> Rule 14
        self.assertEqual(by["claims"], len(pe.containment.ZONES))
        self.assertEqual(by["parent"], 2); self.assertEqual(by["child"], 2); self.assertEqual(by["refs"], 1)
        self.assertEqual(by["plans"], 1)                     # plan 99 has no row
        self.assertEqual(len(self.g.edges), sum(by.values()))
    def test_every_edge_endpoint_exists(self):
        keys = {e.key for e in self.g.entities}
        for e in self.g.edges:
            self.assertIn(e.src, keys); self.assertIn(e.dst, keys)
    def test_audit_count_excludes_incidents(self):
        aud = next(e for e in self.g.entities if e.kind == "Audit")
        self.assertEqual(dict(aud.attrs)["count"], "1")
    def test_rule_attrs(self):
        r14 = next(e for e in self.g.entities if e.key == "Rule:14")
        self.assertEqual(dict(r14.attrs), {"set": "System Architecture", "target": "a thing14", "owned terms": "0"})
        r1 = next(e for e in self.g.entities if e.key == "Rule:1")
        self.assertEqual(dict(r1.attrs)["owned terms"], "1")
    def test_render_deterministic_and_escaped(self):
        a = pe.render(self.g); b = pe.render(pe.collect(self.root, self.pkg))
        self.assertEqual(a, b); self.assertIn("<svg", a)
        self.assertIn("r1 &lt;b&gt;&amp;", a); self.assertNotIn("<b>&", a)
        for k in self.kinds():
            self.assertIn(f'<section data-kind="{k}">', a)
        for load in (" src=", "<link", 'href="http', "url("):   # self-contained = nothing loaded (projection.md p3): an attribute, not a data-src token; text may name a URL
            self.assertNotIn(load, a)
    def test_render_balanced(self):
        p = Balanced(); p.feed(pe.render(self.g)); p.close()
        self.assertEqual(p.errors, []); self.assertEqual(p.stack, [], p.stack)

class RefsTests(unittest.TestCase):
    def test_parent(self):
        self.assertEqual(pe.parse_refs("parent #59; PRs #65 #66"), [(59, "parent")])
    def test_children_range_en_dash(self):
        self.assertEqual(pe.parse_refs("children #4–#6"), [(4, "child"), (5, "child"), (6, "child")])
    def test_children_list(self):
        self.assertEqual(pe.parse_refs("children #4 #7"), [(4, "child"), (7, "child")])
    def test_bare_and_pr_skipped(self):
        self.assertEqual(pe.parse_refs("#24"), [(24, "refs")])
        self.assertEqual(pe.parse_refs("PR #9"), []); self.assertEqual(pe.parse_refs(""), [])
        self.assertEqual(pe.parse_refs("#24; PR #63; gaps E1–E11 await prompt"), [(24, "refs")])

class LiveTests(livetest.LiveCase):
    """projection.md p2: the projector runs over the real instance and yields valid output. Empty instance
    (a fresh install): the package kinds are still drawn and `render` emits a section only for a kind that
    has an entity, so Row and Plan are absent — asserted both ways rather than skipped (#171)."""
    PACKAGE_KINDS = ("Rule", "Term", "Set", "Component", "Zone")   # from the package: in every install
    INSTANCE_KINDS = ("Row", "Plan")                               # from the instance: absent while its store is

    def test_live_run(self):
        root = dyadlib.repo_root()
        with tempfile.TemporaryDirectory() as d:
            # DYAD_INSTANCE points main() at a copy so the tracked tree is never written
            inst = Path(d) / "inst"; import shutil
            shutil.copytree(dyadlib.instance(root), inst, ignore=shutil.ignore_patterns("projections"))
            env = dict(os.environ, DYAD_INSTANCE=str(inst))
            r = subprocess.run([sys.executable, str(pe.Path(pe.__file__))], cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("[project] erd:", r.stdout)
            out = inst / "projections" / "erd.html"; self.assertTrue(out.exists())
            text = out.read_text(); self.assertIn("<svg", text)
            for k in self.PACKAGE_KINDS:
                self.assertIn(f'<section data-kind="{k}">', text)
            stores = {"Row": dyadlib.rows_dir(root), "Plan": dyadlib.instance(root) / "d-work" / "plans"}
            for k in self.INSTANCE_KINDS:
                drawn = not livetest.store_empty(stores[k], pattern=livetest.ROW_GLOB)
                self.assertEqual(f'<section data-kind="{k}">' in text, drawn, k)
            self.assertEqual(livetest.instance_is_empty(root), not any(f'<section data-kind="{k}">' in text for k in self.INSTANCE_KINDS))
            p = Balanced(); p.feed(text); p.close()
            self.assertEqual(p.errors, []); self.assertEqual(p.stack, [])
            self.assertEqual(text, out.read_text())
            prev = os.environ.get("DYAD_INSTANCE"); os.environ["DYAD_INSTANCE"] = str(inst)
            try:
                self.assertEqual(pe.render(pe.collect(root, dyadlib.PKG)), text, "second render byte-identical")
            finally:
                os.environ.pop("DYAD_INSTANCE", None)
                if prev is not None: os.environ["DYAD_INSTANCE"] = prev


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the projector's INVARIANTS hold (the runner's pass runs them before any check)."""
    def test_invariants_hold(self):
        self.assertEqual(dyadlib.check_invariants(pe), len(pe.INVARIANTS)); self.assertTrue(pe.INVARIANTS)

if __name__ == "__main__":
    unittest.main()
