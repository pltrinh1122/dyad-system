"""sysarch projection.md schema projector tests: fixture corpus -> known box/arrow counts per label (owns vs
mentions, replaces vs stub, CI status verbatim from the manifest); determinism; a live run over
the real instance yields a well-formed self-contained HTML file with one section per layer."""
import os, shutil, subprocess, sys, tempfile, unittest
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projectors"))
import project_schema as ps
import dyadlib, livetest

RULE = """# Rule-{n}: {title}

**Intent:** Do the thing.
**Target:** a thing

## Boundaries (out of scope)
- {boundary}

## Conditions (triggers)
- always

{tail}
## Provenance
Operator rule.

Set: {set}.
"""
VOCAB = """# vocab
| term | definition | owner | used by |
|------|------------|-------|---------|
| Operator | the human party | frame | 2 3 |
| Agent | the model party | frame | 1 2 |
| audit | not a party | frame | 2 |
| zone | a set of paths | 1 | 1 |
"""
PREFS = """# prefs
| key | value | allowed | read by |
|-----|-------|---------|---------|
| merge-disposition | with-done | `separate` \\| `with-done` | Rule-2 (binding), Rule-3 (form) |
| import-licenses | MIT | SPDX | Rule-13 (absent) |
"""
MANIFEST = """# manifest
| component | partition | version | purpose | license | replacement |
|-----------|-----------|---------|---------|---------|-------------|
| Python | kernel | 3.12 | code | PSF | — |
| Git | kernel | 2.43 | repo | GPL | — |
| `gh` | library | 2.45 | PRs | MIT | REST via Python |
| jq | library | 1.7 | JSON | MIT | Python `json` (kernel) |
| GitHub Actions + `actions/checkout@v4` | library | — | runs the guards; absent since 2026-09-14 (billing) | MIT | LAN runner |
| Gitea | library | 1.27 | LAN git | MIT | Forgejo — same API |
| Linux (OS) | The World | 7.0 | provides the kernel | — | observed, never pinned |
"""
PACKAGE_PY = "def check_rule_11():\n    return []\nCHECKS = {'Rule-11': check_rule_11, 'infra/containment': lambda: []}\nPROJECTORS = {'erd': 'crafts/sysarch/projectors/project_erd.py', 'nope': 'crafts/sysarch/projectors/project_nope.py'}\n"

def fixture():
    """Temp repo root (not a git repo: counts come from disk). Package at dyad/, instance at
    agent-corpus/ so containment.ZONES patterns match. Guards under dyad/guards/<corpus>/ (sysarch guards.md),
    scripts under dyad/scripts/, projectors under crafts/sysarch/projectors/ (#160). 3 Rules: Rule-1 names containment.py (a guard) and hooks/pre-commit
    under `## Mechanisms` (owns) and ghost.py (absent, dropped); Rule-2 names rows.py (a guard) in
    prose only (mentions); Rule-14 names manifest.py and package.yml under `## Enforcement` (owns;
    workflow resolved with the dyad- prefix); Rule-2 also mentions dyadlib.py (a script)."""
    root = Path(tempfile.mkdtemp()); pkg = root / "dyad"; inst = root / "agent-corpus"
    (pkg / "rules").mkdir(parents=True)
    (pkg / "rules" / "RULE-1-x.md").write_text(RULE.format(n=1, title="containment", boundary="none", set="System Requirements",
        tail="## Mechanisms\nRuns `dyad/guards/infra/containment.py` from `dyad/hooks/pre-commit`; `ghost.py` does not exist.\n"))
    (pkg / "rules" / "RULE-2-x.md").write_text(RULE.format(n=2, title="ratify", boundary="`rows.py` is Rule-3's; `dyadlib.py` shared", set="System Requirements", tail=""))
    (pkg / "rules" / "RULE-14-x.md").write_text(RULE.format(n=14, title="infra", boundary="none", set="System Architecture",
        tail="## Enforcement\n`manifest.py`, wrapped by `package.yml`.\n"))
    (pkg / "vocabulary").mkdir(); (pkg / "vocabulary" / "VOCABULARY.md").write_text(VOCAB)
    (pkg / "scripts").mkdir()
    (pkg / "scripts" / "dyadlib.py").write_text("# stub\n")
    (root / "crafts" / "sysarch" / "projectors").mkdir(parents=True); (root / "crafts" / "sysarch" / "projectors" / "project_erd.py").write_text("# stub\n")   # discovered projector (#160); project_nope.py absent
    for rel in ("guards/infra/containment.py", "guards/infra/manifest.py", "guards/agent/rows.py", "guards/agent/_helper.py"):
        (pkg / rel).parent.mkdir(parents=True, exist_ok=True); (pkg / rel).write_text("# stub\n")
    (pkg / "scripts" / "package.py").write_text(PACKAGE_PY)
    (pkg / "scripts" / "package_rules.txt").write_text("generated: projections/*\n")
    (pkg / "hooks").mkdir()
    (pkg / "hooks" / "pre-commit").write_text('exec "$(git rev-parse --show-toplevel)/dyad/guards/infra/containment.py" staged\n')
    (pkg / "hooks" / "pre-push").write_text("exec python3 dyad/scripts/package.py check --guards\n")
    (pkg / "infrastructure").mkdir(); (pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
    (pkg / "falsification" / "rules").mkdir(parents=True); (pkg / "falsification" / "rules" / "rule-1-x.md").write_text("# r\n")
    wf = root / ".github" / "workflows"; wf.mkdir(parents=True)
    wf.joinpath("dyad-package.yml").write_text("steps:\n  - run: python3 dyad/scripts/package.py check\n  - run: |\n      python3 dyad/guards/infra/containment.py tree\n")
    wf.joinpath("dyad-d-work.yml").write_text("steps:\n  - run: python3 dyad/guards/agent/rows.py a b\n")
    wf.joinpath("server.yml").write_text("steps:\n  - run: python3 dyad/guards/agent/rows.py\n")   # not dyad-*: ignored
    (root / "preferences-corpus").mkdir(); (root / "preferences-corpus" / "PREFERENCES.md").write_text(PREFS)
    (root / "workstation-corpus").mkdir(); (root / "workstation-corpus" / "CHANGELOG.md").write_text("# log\nrow\n")
    rows = inst / "d-work" / "rows"; rows.mkdir(parents=True)
    for rid in (1, 2, 3):
        rows.joinpath(f"{rid}.md").write_text(f"id: {rid}\ntitle: r<b>&\nopened: d\nstate: open\ndisposed: \nrefs: \n")
    (inst / "d-work" / "plans").mkdir(); (inst / "d-work" / "plans" / "2.md").write_text("# p\n")
    (inst / "projections").mkdir(); (inst / "projections" / "erd.html").write_text("<x>")
    (inst / "audits").mkdir(); (inst / "audits" / "a.md").write_text("# a\n")
    return root, pkg, inst

class Balanced(HTMLParser):
    VOID = {"meta", "input", "br", "path", "rect"}
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

def check_html(tc, text, n_layers=5):
    tc.assertIn("<svg", text)
    tc.assertEqual(text.count("<section "), n_layers)
    for name in ps.LAYERS:
        tc.assertIn(f'<section data-layer="{name}">', text)
    for load in (" src=", "<link", 'href="http', "url("):   # self-contained = nothing loaded (projection.md p3): an attribute, not a data-src token; text may name a URL
        tc.assertNotIn(load, text)
    tc.assertNotIn("src=", text.replace("data-src=", "")); tc.assertNotIn("href=", text)
    p = Balanced(); p.feed(text); p.close()
    tc.assertEqual(p.errors, []); tc.assertEqual(p.stack, [], p.stack)

class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.root, self.pkg, self.inst = fixture()
        self.prev = os.environ.pop("DYAD_INSTANCE", None)
        self.s = ps.collect(self.root, self.pkg)
    def tearDown(self):
        if self.prev is not None: os.environ["DYAD_INSTANCE"] = self.prev
        shutil.rmtree(self.root, ignore_errors=True)
    def by_label(self):
        out = {}
        for a in self.s.arrows:
            out[a.label] = out.get(a.label, 0) + 1
        return out
    def box(self, bid):
        return next(b for b in self.s.boxes() if b.id == bid)
    def test_layers_and_boxes(self):
        self.assertEqual([n for n, _ in self.s.layers], list(ps.LAYERS))
        counts = {n: [b.id for b in bs] for n, bs in self.s.layers}
        self.assertEqual(counts[ps.LAYERS[0]], ["Agent", "Operator", "set:System Architecture", "set:System Requirements"])  # audit is frame-owned but no party
        self.assertEqual(counts[ps.LAYERS[1]], [f"zone:{z}" for z in sorted({z for z, _ in ps.containment.ZONES})] + ["tree:package", "tree:instance"])
        self.assertEqual(counts[ps.LAYERS[2]], ["hook:pre-commit", "hook:pre-push", "runner", "registry", "scripts", "projectors:sysarch", "guards:agent", "guards:infra", "ci:dyad-d-work.yml", "ci:dyad-package.yml"])
        self.assertEqual([k for k, _ in self.box("guards:agent").items], ["rows.py"])          # _helper.py is not a guard
        self.assertEqual([k for k, _ in self.box("guards:infra").items], ["containment.py", "manifest.py"])
        self.assertEqual([k for k, _ in self.box("scripts").items], ["dyadlib.py", "package.py"])
        self.assertEqual([k for k, _ in self.box("projectors:sysarch").items], ["project_erd.py"])
        self.assertEqual(counts[ps.LAYERS[3]], ["part:kernel", "part:library", "part:The World"])
        self.assertEqual(counts[ps.LAYERS[4]], ["store:<instance>/d-work/rows", "store:<instance>/d-work/plans", "store:<instance>/projections",
                                                "store:<instance>/audits", "store:dyad/falsification/rules", "store:changelog", "store:preferences"])
        self.assertEqual(len(self.s.boxes()), 4 + len(counts[ps.LAYERS[1]]) + 10 + 3 + 7)
    def test_rule_items_and_sets(self):
        self.assertEqual([t for _, t in self.box("set:System Requirements").items], ["Rule-1: containment", "Rule-2: ratify"])
        self.assertEqual([t for _, t in self.box("set:System Architecture").items], ["Rule-14: infra"])
    def test_owns_vs_mentions(self):
        owns = {(a.src, a.dst) for a in self.s.arrows if a.label == "owns"}
        self.assertEqual(owns, {("set:System Requirements/1", "guards:infra/containment.py"), ("set:System Requirements/1", "hook:pre-commit"),
                                ("set:System Architecture/14", "guards:infra/manifest.py"), ("set:System Architecture/14", "ci:dyad-package.yml")})
        self.assertEqual({(a.src, a.dst) for a in self.s.arrows if a.label == "mentions"}, {("set:System Requirements/2", "guards:agent/rows.py"), ("set:System Requirements/2", "scripts/dyadlib.py")})
        self.assertFalse(any("ghost" in a.dst for a in self.s.arrows))
    def test_contains(self):
        self.assertEqual({(a.src, a.dst) for a in self.s.arrows if a.label == "contains"},
                         {("zone:agent/dyad/*", "tree:package"), ("zone:agent/agent-corpus/*", "tree:instance"), ("zone:infra/.github/*", "tree:package"),
                          ("zone:workstation/workstation-corpus/*", "tree:instance"), ("zone:preferences/preferences-corpus/*", "tree:instance")})
    def test_runs_and_wraps(self):
        runs = {(a.src, a.dst) for a in self.s.arrows if a.label == "runs"}
        self.assertEqual(runs, {("hook:pre-commit/containment.py", "guards:infra/containment.py"), ("hook:pre-push/package.py", "scripts/package.py"),
                                ("registry/erd", "projectors:sysarch/project_erd.py"), ("runner/infra/containment", "guards:infra/containment.py")})   # project_nope.py absent: no arrow
        self.assertEqual([t for _, t in self.box("registry").items], ["erd: crafts/sysarch/projectors/project_erd.py", "nope: crafts/sysarch/projectors/project_nope.py"])
        self.assertEqual([t for _, t in self.box("runner").items], ["Rule-11: check_rule_11", "infra/containment: check_package"])
        wraps = {(a.src, a.dst) for a in self.s.arrows if a.label == "wraps"}
        self.assertEqual(wraps, {("ci:dyad-package.yml/package.py", "scripts/package.py"), ("ci:dyad-package.yml/containment.py", "guards:infra/containment.py"),
                                 ("ci:dyad-d-work.yml/rows.py", "guards:agent/rows.py")})
    def test_ci_status_verbatim(self):
        for wf in ("ci:dyad-package.yml", "ci:dyad-d-work.yml"):
            self.assertEqual(self.box(wf).items[0], ("status", "status: runs the guards; absent since 2026-09-14 (billing)"))
        self.assertIn("<title>status: runs the guards; absent since 2026-09-14 (billing)</title>", ps.render(self.s))
    def test_replaces_and_stubs(self):
        self.assertEqual({(a.src, a.dst) for a in self.s.arrows if a.label == "replaces"},
                         {("part:kernel/Python", "part:library/gh"), ("part:kernel/Python", "part:library/jq")})
        lib = dict(self.box("part:library").items)
        self.assertEqual(lib["Gitea~repl"], "  ↳ replacement: Forgejo — same API"); self.assertEqual(lib["GitHub Actions + actions/checkout@v4~repl"], "  ↳ replacement: LAN runner")
        self.assertNotIn("gh~repl", lib); self.assertNotIn("Python~repl", dict(self.box("part:kernel").items))
        self.assertEqual(len(self.box("part:kernel").items), 2); self.assertEqual(len(self.box("part:The World").items), 2)
    def test_reads(self):
        self.assertEqual({(a.src, a.dst) for a in self.s.arrows if a.label == "reads"},
                         {("set:System Requirements/2", "store:preferences/merge-disposition")})    # Rule-3, Rule-13 absent: dropped
    def test_stores(self):
        self.assertEqual(self.box("store:<instance>/d-work/rows").items, [("count", "3 files tracked")])
        self.assertEqual(self.box("store:<instance>/projections").title, "<instance>/projections/ (generated)")
        self.assertEqual(self.box("store:<instance>/projections").items, [("count", "untracked, generated")])
        self.assertEqual(self.box("store:changelog").items, [("count", "2 lines")])
        self.assertEqual([k for k, _ in self.box("store:preferences").items], ["merge-disposition", "import-licenses"])
    def test_label_totals(self):
        by = self.by_label()
        self.assertEqual(by, {"contains": 5, "owns": 4, "mentions": 2, "runs": 4, "wraps": 3, "replaces": 2, "reads": 1})
        self.assertEqual(len(self.s.arrows), sum(by.values()))
    def test_every_arrow_endpoint_exists(self):
        keys = {b.id for b in self.s.boxes()} | {k for b in self.s.boxes() for k in b.item_keys()}
        for a in self.s.arrows:
            self.assertIn(a.src, keys); self.assertIn(a.dst, keys)
    def test_render_deterministic_and_escaped(self):
        a = ps.render(self.s); b = ps.render(ps.collect(self.root, self.pkg))
        self.assertEqual(a, b); check_html(self, a)
        self.assertIn("GitHub Actions + actions/checkout@v4 — —", a)
        self.assertIn("&lt;instance&gt;/projections/ (generated)", a); self.assertNotIn("<instance>", a)
        self.assertEqual(a.count('<g class="arrow '), len(self.s.arrows)); self.assertEqual(a.count('<g class="box '), len(self.s.boxes()))
        for l in ps.LABELS:
            self.assertIn(f'<li class="arrow {l}">', a)

class LiveTests(livetest.LiveCase):
    """projection.md p2: the projector runs over the real instance and yields valid output. Empty instance
    (a fresh install): unchanged — every layer this projector draws is read from the package. The keys it
    asserts include the sysadmin craft's guards, so it needs that craft installed (#171)."""
    def test_live_run(self):
        self.require_craft("sysadmin")
        root = dyadlib.repo_root()
        with tempfile.TemporaryDirectory() as d:
            inst = Path(d) / "inst"   # DYAD_INSTANCE points main() at a copy so the tracked tree is never written
            shutil.copytree(dyadlib.instance(root), inst, ignore=shutil.ignore_patterns("projections"))
            env = dict(os.environ, DYAD_INSTANCE=str(inst))
            r = subprocess.run([sys.executable, str(Path(ps.__file__))], cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("[project] schema: 5 layers", r.stdout)
            out = inst / "projections" / "schema.html"; self.assertTrue(out.exists())
            text = out.read_text(); check_html(self, text)
            for name in ("Operator", "Agent", "set:System Requirements", "zone:agent", "hook:pre-push", "runner", "guards:agent", "guards:sysadmin", "part:kernel", "store:preferences"):   # guards:sysadmin: crafts/sysadmin/guards/ (#155)
                self.assertIn(f'data-key="{name}"', text)
            prev = os.environ.get("DYAD_INSTANCE"); os.environ["DYAD_INSTANCE"] = str(inst)
            try:
                self.assertEqual(ps.render(ps.collect(root, dyadlib.PKG)), text, "second render byte-identical")
            finally:
                os.environ.pop("DYAD_INSTANCE", None)
                if prev is not None: os.environ["DYAD_INSTANCE"] = prev


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the projector's INVARIANTS hold (the runner's pass runs them before any check)."""
    def test_invariants_hold(self):
        self.assertEqual(dyadlib.check_invariants(ps), len(ps.INVARIANTS)); self.assertTrue(ps.INVARIANTS)

if __name__ == "__main__":
    unittest.main()
