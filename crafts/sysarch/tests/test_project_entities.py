"""sysarch projection.md entity-schema projector tests: fixture corpus -> one entity per guard of the registry
(sysarch guards.md: one guard, one card, over two roots — core and every Tended craft's, `dyad check --list`), every field name taken from the guard's FIELDS constant
(asserted against the loaded guards, never literals), one example per field from the instance;
relations from the Rule-20 register; determinism; a live run over the real instance yields a
well-formed self-contained HTML file."""
import os, shutil, subprocess, sys, tempfile, unittest
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projectors"))
import project_entities as pe
import dyadlib, livetest
G = {py.stem: dyadlib.load_guard_file(py) for py in dyadlib.guard_files()}
vocabulary, infrastructure, containment, rule_integrity, refint = G["vocabulary"], G["manifest"], G["containment"], G["rules"], G["references"]
# Tended crafts other than sysarch/syseng may be absent (a core-only-plus-sysarch system, dyad-system #1): their
# entities and guards are asserted only when installed; the sets below are derived from what is here, never literal.
INSTALLED = {d.name for d in dyadlib.craft_dirs()}
SYSADMIN, LANGIT = "sysadmin" in INSTALLED, "lan-git" in INSTALLED
ops_scripts, runbook = G.get("ops_scripts"), G.get("runbooks")
needs_sysadmin = unittest.skipUnless(SYSADMIN, "the sysadmin craft is not installed here; its entities are not on the surface")

RULE = """# Rule-{n}: {title}

**Intent:** Do the thing {n}.
**Target:** a thing{n}

## Boundaries (out of scope)
- boundary {n}
- another

## Conditions (triggers)
- condition {n}

## Provenance
Operator rule.

Set: System Requirements.
"""
VOCAB = """# vocab
| term | definition | owner | used by |
|------|------------|-------|---------|
| Operator | the human party | frame | 2 |
| zone | a set of paths | 1 | 1 |
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
# The changelog entity's schema is the sysadmin craft's own guard, discovered like any other
# (dyadlib.guard_files(), same as G); when that craft is installed here, its live FIELDS may carry
# more columns than this fixture's original six (#213: an "actor" column, workstation d-work #216).
# describe() must report exactly G["changelog"].FIELDS or project_entities.collect() raises (p59) —
# in setUp, before any single test runs — so the header and its one example row are built from the
# real FIELDS whenever they differ, instead of a fixed six-column literal (#213 d-work #46).
_CHANGELOG_BASE = ["date", "d-work", "class", "action", "undo", "outcome"]
_CHANGELOG_EXAMPLE_BASE = ["2026-09-13", "#7", "reversible", "mkdir /x", "rmdir /x", "applied"]
if "changelog" in G and list(G["changelog"].FIELDS) != _CHANGELOG_BASE:
    CHANGELOG_FIELDS = list(G["changelog"].FIELDS)
    CHANGELOG_EXAMPLE = [dict(zip(_CHANGELOG_BASE, _CHANGELOG_EXAMPLE_BASE)).get(f, f) for f in CHANGELOG_FIELDS]
else:
    CHANGELOG_FIELDS, CHANGELOG_EXAMPLE = _CHANGELOG_BASE, _CHANGELOG_EXAMPLE_BASE
CHANGELOG_T = ("# Host change log (Rule-8)\n\n| " + " | ".join(CHANGELOG_FIELDS) + " |\n|"
               + "|".join("-" * 6 for _ in CHANGELOG_FIELDS) + "|\n")
INCIDENTS_T = "# Incidents (Rule-3)\n\n| date | d-work | what | cause | consequence |\n|------|--------|------|-------|-------------|\n"
RECORD = """# Falsification record — x (ledger #{n})

**Claim:** c.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | a1 <b> | **Refuted** | s1 |
| 2 | a2 | Survives, scoped | s2 |

Disposition: see ledger #{n}.
"""
OPS = """#!/usr/bin/env bash
# d-work: #7
# class: reversible
# undo: rmdir /x
# change-log: CHANGELOG.md row "#7 H1"
# postcondition: /x exists
# destructive: none
set -euo pipefail
postcondition() { [[ -d /x ]]; }
postcondition && exit 0
mkdir /x
postcondition
"""
RUNBOOK = "# x\n\n## Start\n```dyad-cmd\nname: start\nclass: reversible\nrole: any\nundo: stop\npostcondition: true\nscope: s\n\necho start\n```\n"
EVENT = ('{"id": "x-20260914T120000Z-start", "ts": "2026-09-14T12:00:00Z", "role": "agent", "instance": "x", "name": "start", "cmd": "echo start", '
         '"class": "reversible", "scope": "s", "exit": 0, "duration_ms": 1, "postcondition": "ok", "output_sha256": "", "output_tail": "start", "commit": "abc", "runbook_sha256": ""}\n')
PACKAGE_PY = 'REGISTRY_FIELDS = ("surface", "module")\nPROJECTORS = {"erd": "crafts/sysarch/projectors/project_erd.py", "entities": "crafts/sysarch/projectors/project_entities.py"}\n'

def fixture(with_incidents_sep=True):
    """Temp repo root: package at dyad/, instance at agent-corpus/. 2 Rules, 2 terms, 2 components,
    1 preference, 3 rows, 2 plans (one lacking `files touched`), 2 records (package + instance),
    1 change-log row, 2 incident rows, 1 ops script."""
    root = Path(tempfile.mkdtemp()); pkg = root / "dyad"; inst = root / "agent-corpus"
    (pkg / "rules").mkdir(parents=True)
    for n in (1, 2):
        (pkg / "rules" / f"RULE-{n}-x.md").write_text(RULE.format(n=n, title=f"t{n}"))
    (pkg / "vocabulary").mkdir(); (pkg / "vocabulary" / "VOCABULARY.md").write_text(VOCAB)
    (pkg / "infrastructure").mkdir(); (pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
    (pkg / "templates").mkdir()
    (pkg / "templates" / "PREFERENCES.md").write_text(PREFS)
    (pkg / "templates" / "CHANGELOG.md").write_text(CHANGELOG_T)
    (pkg / "templates" / "INCIDENTS.md").write_text(INCIDENTS_T if with_incidents_sep else INCIDENTS_T.splitlines()[0] + "\n\n| date | d-work | what | cause | consequence |\n")
    (pkg / "scripts").mkdir(); (pkg / "scripts" / "package.py").write_text(PACKAGE_PY)
    (pkg / "CLAUDE.md").write_text("# frame\n@rules/RULE-1-x.md\n@rules/RULE-2-x.md\n@vocabulary/VOCABULARY.md\n")
    (pkg / "falsification" / "rules").mkdir(parents=True); (pkg / "falsification" / "rules" / "rule-1-x.md").write_text(RECORD.format(n=1))
    (root / "preferences-corpus").mkdir(); (root / "preferences-corpus" / "PREFERENCES.md").write_text(PREFS)
    ws = root / "workstation-corpus"; (ws / "ops").mkdir(parents=True)
    (ws / "CHANGELOG.md").write_text(CHANGELOG_T + "| " + " | ".join(CHANGELOG_EXAMPLE) + " |\n")
    (ws / "ops" / "7-h1-x.sh").write_text(OPS)
    (ws / "runbooks" / "events").mkdir(parents=True); (ws / "runbooks" / "x.md").write_text(RUNBOOK); (ws / "runbooks" / "events" / "x.jsonl").write_text(EVENT)
    rows = inst / "d-work" / "rows"; rows.mkdir(parents=True)
    for rid, state in ((1, "done"), (2, "open"), (7, "planned")):
        rows.joinpath(f"{rid}.md").write_text(f"id: {rid}\ntitle: r{rid} <b>&\nopened: 2026-09-13\nstate: {state}\ndisposed: 2026-09-13 Y plan\nrefs: #1\n")
    plans = inst / "d-work" / "plans"; plans.mkdir()
    plans.joinpath("2.md").write_text("# Plan #2\nbase commit: abc\n\nintent as read: x\nmutation: y\nfiles touched: f\nfalsification: below\n")
    plans.joinpath("7.md").write_text("# Plan #7\nbase commit: def (main)\n\n## Intent as read\nx\n## Mutation\ny\nFalsification: none\n")
    (inst / "audits").mkdir(); (inst / "audits" / "INCIDENTS.md").write_text(INCIDENTS_T + "| 2026-09-13 | #2 | w1 | c1 | q1 |\n| 2026-09-14 | #7 | w2 | c2 | q2 |\n")
    (inst / "falsification").mkdir(); (inst / "falsification" / "gap.md").write_text(RECORD.format(n=2))
    return root, pkg, inst

class Balanced(HTMLParser):
    VOID = {"meta", "input", "br"}
    def __init__(self):
        super().__init__(); self.stack, self.errors = [], []
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced </{tag}> (stack top {self.stack[-1] if self.stack else None})")
        else:
            self.stack.pop()

def check_html(tc, text, n_entities):
    tc.assertEqual(text.count('<article class="card"'), n_entities)
    for load in (" src=", "<link", 'href="http', "url("):   # self-contained = nothing loaded (projection.md p3): an attribute, not a data-src token; text may name a URL
        tc.assertNotIn(load, text)
    tc.assertNotIn("src=", text); tc.assertNotIn("<link", text); tc.assertNotIn("@import", text)
    for m in __import__("re").findall(r'href="([^"]*)"', text):
        tc.assertTrue(m.startswith("#e-"), m)   # only in-page anchors
    p = Balanced(); p.feed(text); p.close()
    tc.assertEqual(p.errors, []); tc.assertEqual(p.stack, [], p.stack)

# every field name must come from a guard's FIELDS (or, for a plan, dyadlib.PLAN_PARTS the guard appends)
def parser_names(pkg):
    names = set(dyadlib.PLAN_PARTS)
    for g in G.values():
        names |= set(g.FIELDS)
    return names

# #98 (#100): derived from the guard registry itself (as #46 first fixed for KNOWN_CRAFTS) — never
# a hand-enumerated set gated by which crafts happen to be installed, the same bug class twice.
ENTITIES = {g.ENTITY for g in G.values()}

class ChangelogFixtureTests(unittest.TestCase):
    """#213 d-work #46: the synthetic changelog header/example track the real sysadmin changelog
    guard's FIELDS when that craft is installed, instead of a fixed six columns — FixtureTests'
    setUp calls project_entities.collect(), which raises on a field-count mismatch (p59), before
    any single test in the class runs."""
    def test_header_and_example_column_counts_agree(self):
        header_line = CHANGELOG_T.splitlines()[2]
        self.assertEqual(len(header_line.strip("|").split("|")), len(CHANGELOG_FIELDS))
        self.assertEqual(len(CHANGELOG_EXAMPLE), len(CHANGELOG_FIELDS))
    def test_unchanged_schema_or_no_sysadmin_keeps_the_original_six(self):
        if not SYSADMIN or list(G["changelog"].FIELDS) == _CHANGELOG_BASE:
            self.assertEqual(CHANGELOG_FIELDS, _CHANGELOG_BASE); self.assertEqual(CHANGELOG_EXAMPLE, _CHANGELOG_EXAMPLE_BASE)
    def test_derivation_places_base_values_and_names_extra_fields(self):
        # exercised directly (not through G, which reflects only what is actually installed here)
        fields = _CHANGELOG_BASE + ["actor"]
        example = [dict(zip(_CHANGELOG_BASE, _CHANGELOG_EXAMPLE_BASE)).get(f, f) for f in fields]
        self.assertEqual(example, _CHANGELOG_EXAMPLE_BASE + ["actor"])


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.root, self.pkg, self.inst = fixture()
        self.prev = {k: os.environ.pop(k, None) for k in ("DYAD_INSTANCE", "DYAD_OPS", "DYAD_RUNBOOKS")}
        self.ents = pe.collect(self.root, self.pkg)
        self.by = {e.key: e for e in self.ents}
    def tearDown(self):
        for k, v in self.prev.items():
            if v is not None: os.environ[k] = v
        shutil.rmtree(self.root, ignore_errors=True)
    def test_one_entity_per_guard_sorted_each_with_fields(self):
        self.assertEqual([e.key for e in self.ents], sorted(e.key for e in self.ents))
        self.assertEqual(set(self.by), ENTITIES); self.assertEqual(set(self.by), {g.ENTITY for g in G.values()})
        for e in self.ents:
            self.assertGreaterEqual(len(e.fields), 1, e.key)
            self.assertEqual(len({f.name for f in e.fields}), len(e.fields), f"{e.key}: duplicate field name")
            self.assertRegex(e.guard, r"^(guards/(agent|preferences|infra|craft)|crafts/[\w-]+/guards)/\w+\.py$")
            if e.guard.startswith("guards/"): self.assertEqual(e.corpus, e.guard.split("/")[1])
            else: self.assertEqual(e.corpus, {"sysadmin": "workstation", "sysarch": "craft", "syseng": "craft", "lan-git": "craft"}[e.guard.split("/")[1]])   # a craft guard's corpus is its store's zone (#155; sysarch checks crafts/*, #160; syseng #162; lan-git #181)
        self.assertEqual({e.guard for e in self.ents if e.guard.startswith("crafts/")},
                         ({f"crafts/sysadmin/guards/{n}.py" for n in ("changelog", "events", "ops_scripts", "runbooks")} if SYSADMIN else set())
                         | {"crafts/sysarch/guards/registry.py"} | {f"crafts/syseng/guards/{n}.py" for n in ("naming", "invariants", "tests")} | ({"crafts/lan-git/guards/image.py"} if LANGIT else set()))
        self.assertNotIn("incident", self.by); self.assertNotIn("registry", self.by)   # no guard, no card (sysarch guards.md): reported in plan #151
    def test_every_field_name_comes_from_a_parser(self):
        names = parser_names(self.pkg)
        for e in self.ents:
            for f in e.fields:
                self.assertIn(f.name, names, f"{e.key}.{f.name} is not a parser constant")
                self.assertTrue(f.source, f"{e.key}.{f.name} names no source")
    @needs_sysadmin
    def test_field_lists_equal_the_constants(self):
        for e in self.ents:
            g = next(g for g in G.values() if g.ENTITY == e.key)
            self.assertEqual([f.name for f in e.fields][:len(g.FIELDS)], list(g.FIELDS), e.key)
        self.assertEqual([f.name for f in self.by["row"].fields], list(dyadlib.FIELDS))
        self.assertEqual([f.name for f in self.by["plan"].fields], list(G["plans"].FIELDS) + [p for p in dyadlib.PLAN_PARTS if p not in G["plans"].FIELDS])
        self.assertEqual([f.name for f in self.by["rule"].fields], list(rule_integrity.BLOCK))
        self.assertEqual([f.name for f in self.by["term"].fields], list(vocabulary.COLUMNS))
        self.assertEqual([f.name for f in self.by["component"].fields], list(infrastructure.FIELDS))
        self.assertEqual([f.name for f in self.by["ops"].fields], list(ops_scripts.FIELDS))
        self.assertEqual([f.name for f in self.by["zone"].fields], list(containment.ZONE_FIELDS))
        self.assertEqual([f.name for f in self.by["command"].fields], list(runbook.FIELDS))
        self.assertEqual([f.name for f in self.by["event"].fields], list(G["events"].EVENT_FIELDS))
        for key, t in (("preference", "PREFERENCES.md"), ("changelog", "CHANGELOG.md")):
            self.assertEqual([f.name for f in self.by[key].fields], dyadlib.table_header((self.pkg / "templates" / t).read_text()))
        self.assertEqual([f.name for f in self.by["record"].fields], ["#", "Attack", "Result", "Survivor"])
        self.assertEqual([f.name for f in self.by["reference"].fields], list(G["references"].FIELDS)); self.assertEqual([f.name for f in self.by["frame"].fields], ["@rules/", "@"])
        self.assertEqual([f.name for f in self.by["pr"].fields], ["body"])
    @needs_sysadmin
    def test_allowed_values_come_from_constants(self):
        state = next(f for f in self.by["row"].fields if f.name == "state")
        for s in dyadlib.STATES: self.assertIn(s, state.allowed)
        for s in dyadlib.NEW_STATES: self.assertIn(s, state.allowed.split("new rows:")[1])
        for a, b in dyadlib.TRANSITIONS.items(): self.assertIn(f"{a} → {', '.join(sorted(b)) or '∅'}", self.by["row"].note)
        part = next(f for f in self.by["component"].fields if f.name == "partition")
        self.assertEqual(part.allowed, " | ".join(sorted(infrastructure.PARTITIONS)))
        zone = next(f for f in self.by["zone"].fields if f.name == "zone")
        self.assertEqual(zone.allowed, " | ".join(sorted({z for z, _ in containment.ZONES})))
        rule = {f.name: f.allowed for f in self.by["rule"].fields}
        self.assertEqual(rule, {"intent": "exactly 1", "target": "exactly 1", "boundaries": ">= 1", "conditions": ">= 1"})
        result = next(f for f in self.by["record"].fields if f.name == "Result")
        self.assertTrue(result.allowed.startswith("refuted | survives"), result.allowed)   # observed, emphasis stripped, first word
        cls = next(f for f in self.by["changelog"].fields if f.name == "class")
        self.assertEqual(cls.allowed, " | ".join(dyadlib.HOST_CLASSES) + " (observed: reversible)")
        cmd = {f.name: f.allowed for f in self.by["command"].fields}
        self.assertEqual(cmd["class"], " | ".join(runbook.CLASSES) + " (Rule-8)"); self.assertEqual(cmd["role"], " | ".join(runbook.ROLES))
        ev = {f.name: f.allowed for f in self.by["event"].fields}
        self.assertEqual(ev["postcondition"], " | ".join(G["events"].POSTCONDITION_RESULTS)); self.assertEqual(ev["role"], " | ".join(G["events"].RUN_ROLES))
    @needs_sysadmin
    def test_examples_and_counts_from_the_instance(self):
        row = {f.name: f.example for f in self.by["row"].fields}
        self.assertEqual(row, {"id": "7", "title": "r7 <b>&", "opened": "2026-09-13", "state": "planned", "disposed": "2026-09-13 Y plan", "refs": "#1"})  # highest id
        self.assertEqual(self.by["row"].observed, 3)
        plan = {f.name: (f.allowed, f.example) for f in self.by["plan"].fields}
        self.assertEqual(plan["files touched"], ("present in 1/2 plans (observed)", ""))          # plan 7 (the example) lacks it
        self.assertEqual(plan["base commit"][1], "def"); self.assertEqual(plan["id"][1], "7")
        self.assertEqual(plan["intent as read"][1], "## Intent as read"); self.assertEqual(plan["intent"][1], "## Intent as read")
        rule = {f.name: f.example for f in self.by["rule"].fields}
        self.assertEqual(rule, {"intent": "Do the thing 2.", "target": "a thing2", "boundaries": "boundary 2", "conditions": "condition 2"})
        self.assertEqual(self.by["rule"].observed, 2)
        self.assertEqual([f.example for f in self.by["term"].fields], ["Operator", "the human party", "frame", "2"])
        self.assertEqual([f.example for f in self.by["component"].fields][:2], ["Python", "kernel"])
        self.assertEqual([f.example for f in self.by["preference"].fields], ["merge-disposition", "with-done", "`separate` | `with-done`", "Rule-2 (binding), Rule-3 (form)"])
        self.assertEqual([f.example for f in self.by["changelog"].fields], CHANGELOG_EXAMPLE)
        self.assertEqual([f.example for f in self.by["record"].fields], ["1", "a1 <b>", "**Refuted**", "s1"]); self.assertEqual(self.by["record"].observed, 2)
        ops = {f.name: f for f in self.by["ops"].fields}
        self.assertEqual(ops["shebang"].example, ops_scripts.SHEBANG); self.assertEqual(ops["strict mode"].example, ops_scripts.STRICT)
        self.assertEqual(ops["d-work:"].example, "#7"); self.assertEqual(ops["postcondition()"].example, "postcondition() { [[ -d /x ]]; }")
        self.assertEqual(ops["confirm()"].example, ""); self.assertFalse(ops["confirm()"].required)
        self.assertEqual([f.example for f in self.by["frame"].fields], ["rules/RULE-1-x.md", "vocabulary/VOCABULARY.md"]); self.assertEqual(self.by["frame"].observed, 1)
        self.assertEqual(self.by["reference"].observed, len(refint.REFERENCES)); self.assertEqual(self.by["pr"].observed, 0)
        self.assertEqual([f.example for f in self.by["zone"].fields], [containment.ZONES[0][0], containment.ZONES[0][1]])
        self.assertEqual([f.example for f in self.by["command"].fields], ["start", "reversible", "any", "stop", "true", "s"]); self.assertEqual(self.by["command"].observed, 1)
        self.assertEqual([f.example for f in self.by["event"].fields][:5], ["x-20260914T120000Z-start", "2026-09-14T12:00:00Z", "agent", "x", "start"]); self.assertEqual(self.by["event"].observed, 1)
    @needs_sysadmin
    def test_relations_are_the_rule_20_register(self):
        # Rule-20 property 5: every drawn edge is a REFERENCES entry (core, or a craft's own
        # REFERENCES_CONTRIB, Rule-11 property 2's contribution mechanism, #101/#100) anchored on a
        # field or store token of an entity on the surface, and every such entry is drawn; the
        # projector has no table of its own. Computed, not hand-typed, so it holds whether or not a
        # craft's own contribution (e.g. sysadmin's changelog/ops/event rows, #100 PR 5) has landed.
        register = {(s, a, t) for _, s, a, _, t, _ in refint.REFERENCES} | {(row[1], row[2], row[4]) for _craft, row in refint.craft_references_contrib(dyadlib.PKG)}
        self.assertEqual(pe.RELATIONS, register)
        for e in self.ents:
            anchors = {f.name for f in e.fields} | set(__import__("re").findall(r"<[a-z]+>", e.store))
            expected = sorted({(a, t) for s, a, t in register if s == e.key and a in anchors and t in self.by})
            self.assertEqual(e.relations, expected, e.key)
        self.assertEqual(self.by["row"].relations, [("disposed", "pr"), ("refs", "craft"), ("refs", "row"), ("refs", "rule")])
        self.assertEqual(self.by["plan"].relations, [("<id>", "row")])
        self.assertEqual(self.by["term"].relations, [("owner", "rule"), ("used by", "rule")])
        self.assertEqual(self.by["event"].relations, [("name", "command")]); self.assertEqual(self.by["command"].relations, [])
        self.assertEqual(self.by["frame"].relations, [("@rules/", "rule")]); self.assertEqual(self.by["pr"].relations, [("body", "row")])
        self.assertEqual(self.by["preference"].relations, [("read by", "rule")])
    def test_a_guard_whose_description_departs_from_FIELDS_is_refused(self):
        d = Path(tempfile.mkdtemp()); shutil.copytree(dyadlib.PKG / "guards", d / "guards")
        (d / "guards" / "agent" / "rows.py").write_text((d / "guards" / "agent" / "rows.py").read_text().replace('"fields": [(f, types[f]', '"fields": [("x" + f, types[f]'))
        with self.assertRaises(ValueError) as cm:
            pe.collect(self.root, self.pkg, guards_pkg=d)
        self.assertIn("rows.py: describe() fields", str(cm.exception))
    def test_invariants_column_is_each_guards_list(self):
        """#162: every card lists its guard module's INVARIANTS names, sorted; the total is in the header line."""
        for e in self.ents:
            g = next(g for g in G.values() if g.ENTITY == e.key)
            self.assertEqual(e.invariants, sorted(n for n, _ in g.INVARIANTS), e.key); self.assertTrue(e.invariants, e.key)
        self.assertEqual(self.by["row"].invariants, ["fields-are-dyadlib-fields"]); self.assertIn("kinds-unique", self.by["reference"].invariants)
        a = pe.render(self.ents)
        self.assertIn(f"{sum(len(e.invariants) for e in self.ents)} invariants.", a); self.assertIn("<code>fields-are-dyadlib-fields</code>", a); self.assertNotIn("no invariant declared", a)
        self.assertEqual(dyadlib.check_invariants(pe), 1)
    def test_render_deterministic_escaped_and_self_contained(self):
        a = pe.render(self.ents); b = pe.render(pe.collect(self.root, self.pkg))
        self.assertEqual(a, b); check_html(self, a, len(self.ents))
        self.assertIn("r7 &lt;b&gt;&amp;", a); self.assertNotIn("r7 <b>&", a)
        self.assertEqual(a.count('<span class="tag">example</span>'), 2 + sum(1 for e in self.ents for f in e.fields if f.example))
        self.assertIn("none observed", a)   # confirm() has no example
        self.assertIn(f"{len(ENTITIES)} entities, ", a); self.assertIn("agent · guards/agent/rows.py", a)
        if SYSADMIN: self.assertIn("workstation · crafts/sysadmin/guards/events.py", a)
        for e in self.ents:
            self.assertIn(f'id="e-{e.key}"', a)

class LiveTests(livetest.LiveCase):
    """projection.md p2: the projector runs over the real instance and yields valid output. Empty instance
    (a fresh install): unchanged — every entity this projector draws is read from the package, not the
    instance, so ENTITIES is the same set there (#171)."""
    def test_empty_instance_changes_nothing(self):
        self.assertEqual({e.key for e in pe.collect(dyadlib.repo_root(), dyadlib.PKG)}, ENTITIES)
        self.assertFalse(livetest.instance_is_empty() and not ENTITIES, "package entities are drawn on an empty instance")
    def test_live_run(self):
        root = dyadlib.repo_root()
        with tempfile.TemporaryDirectory() as d:
            inst = Path(d) / "inst"   # DYAD_INSTANCE points main() at a copy so the tracked tree is never written
            shutil.copytree(dyadlib.instance(root), inst, ignore=shutil.ignore_patterns("projections"))
            env = dict(os.environ, DYAD_INSTANCE=str(inst))
            r = subprocess.run([sys.executable, str(Path(pe.__file__))], cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr); self.assertIn(f"[project] entities: {len(ENTITIES)} entities", r.stdout)
            out = inst / "projections" / "entities.html"; self.assertTrue(out.exists())
            text = out.read_text(); check_html(self, text, len(ENTITIES))
            prev = os.environ.get("DYAD_INSTANCE"); os.environ["DYAD_INSTANCE"] = str(inst)
            try:
                ents = pe.collect(root, dyadlib.PKG)
                self.assertEqual(pe.render(ents), text, "second render byte-identical")
                names = parser_names(dyadlib.PKG)
                for e in ents:
                    self.assertGreaterEqual(len(e.fields), 1, e.key)
                    for f in e.fields:
                        self.assertIn(f.name, names, f"{e.key}.{f.name}")
                self.assertEqual({e.key for e in ents}, ENTITIES)
            finally:
                os.environ.pop("DYAD_INSTANCE", None)
                if prev is not None: os.environ["DYAD_INSTANCE"] = prev

if __name__ == "__main__":
    unittest.main()
