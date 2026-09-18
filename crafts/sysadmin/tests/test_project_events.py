"""sysarch projection.md events projector tests (d-work #150): fixture store -> one section per instance, one row per
event sorted by ts then id, every table column an EVENT_FIELDS name, badges for exit / postcondition /
role / class, escaped output tails, an inline filter, a valid page for an empty store; determinism;
a live run over the real instance (whose store may be empty) yields a well-formed self-contained
HTML file."""
import json, os, re, shutil, subprocess, sys, tempfile, unittest
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projectors"))
import project_events as pv
import dyadlib, livetest
runbook = pv.runbook                                        # the core runner: EVENT_FIELDS, the store's reader (#155)
DEFAULT_RUNBOOKS = runbook.DEFAULT_RUNBOOKS
self_check = dyadlib.load_guard("workstation", "events")   # the craft guard re-exports the same names
assert self_check.EVENT_FIELDS is runbook.EVENT_FIELDS

def event(**kw):
    e = {"id": "x-20260914T120000Z-status", "ts": "2026-09-14T12:00:00Z", "role": "agent", "instance": "x", "name": "status", "cmd": "docker ps <b>",
         "class": "read-only", "scope": "container (read)", "exit": 0, "duration_ms": 12, "postcondition": "n/a", "output_sha256": "ab" * 32,
         "output_tail": "up & running\n<ok>", "commit": "abc1234", "runbook_sha256": "cd" * 32}
    e.update(kw); return e

def fixture(instances: dict[str, list[dict]] | None):
    root = Path(tempfile.mkdtemp(prefix="dyad-ev-"))
    if instances is not None:
        d = root / DEFAULT_RUNBOOKS / "events"; d.mkdir(parents=True)
        for inst, evs in instances.items():
            (d / f"{inst}.jsonl").write_text("".join(json.dumps(e) + "\n" for e in evs))
    return root

class Balanced(HTMLParser):
    VOID = {"meta", "input", "br"}
    def __init__(self):
        super().__init__(); self.stack, self.errors = [], []
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID: self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack or self.stack[-1] != tag: self.errors.append(f"unbalanced </{tag}>")
        else: self.stack.pop()

def check_html(tc, text, n_events, n_instances):
    tc.assertEqual(text.count('<tr class="ev"'), n_events); tc.assertEqual(text.count('<section class="inst"'), n_instances)
    # self-contained (projection.md p3): nothing is *loaded*; a command shown as text may name a URL
    for load in ("src=", "<link", 'href="http', "url("):
        tc.assertNotIn(load, text)
    tc.assertIn('<input id="q"', text); tc.assertIn("<script>", text)
    p = Balanced(); p.feed(text); p.close(); tc.assertEqual(p.errors, []); tc.assertEqual(p.stack, [])

class FixtureTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("DYAD_RUNBOOKS", None)
        self.evs = {"x": [event(id="x-20260914T130000Z-start", ts="2026-09-14T13:00:00Z", name="start", **{"class": "reversible"}, exit=0, postcondition="ok", role="operator"),
                          event(),
                          event(id="x-20260914T120000Z-health", name="health", postcondition="failed", exit=1, output_tail="")],
                    "a": [event(id="a-20260914T110000Z-drop", instance="a", name="drop", **{"class": "destructive"}, postcondition="already", exit=0)]}
        self.root = fixture(self.evs); self.store = pv.collect(self.root)
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
    def test_collect_sorted_by_instance_ts_id_with_every_field(self):
        self.assertEqual(list(self.store), ["a", "x"])
        self.assertEqual([e["id"] for e in self.store["x"]], ["x-20260914T120000Z-health", "x-20260914T120000Z-status", "x-20260914T130000Z-start"])
        for evs in self.store.values():
            for e in evs: self.assertEqual(list(e), list(runbook.EVENT_FIELDS))
    def test_columns_are_event_fields(self):
        for c in pv.COLUMNS: self.assertIn(c, runbook.EVENT_FIELDS)
    def test_render_rows_badges_escaping_and_counts(self):
        a = pv.render(self.store, "workstation-corpus/runbooks/events")
        check_html(self, a, 4, 2)
        self.assertIn("4 events in 2 instances", a)
        self.assertIn('<span class="badge exit bad">1</span>', a); self.assertEqual(a.count('<span class="badge exit ok">0</span>'), 3 + 1)   # three rows + the legend
        self.assertIn('<span class="badge postcondition bad">failed</span>', a); self.assertIn('<span class="badge postcondition ok">already</span>', a)
        self.assertIn('<span class="badge role role-operator">operator</span>', a); self.assertIn('<span class="badge class class-destructive">destructive</span>', a)
        self.assertIn("up &amp; running\n&lt;ok&gt;", a); self.assertNotIn("<ok>", a); self.assertIn("docker ps &lt;b&gt;", a)
        self.assertIn("(no output)", a)                                             # health has an empty tail
        self.assertIn("3 events, 1 with a non-zero exit or a failed postcondition", a)
        self.assertIn("<code>health</code> ×1", a); self.assertIn('id="ev-x-20260914T130000Z-start"', a); self.assertIn('id="i-a"', a)
        self.assertNotIn('id="empty"', a)
    def test_render_deterministic(self):
        a = pv.render(self.store, "r/events"); b = pv.render(pv.collect(self.root), "r/events")
        self.assertEqual(a, b)
    def test_empty_and_absent_store_render_a_valid_page(self):
        for root in (fixture({}), fixture(None), fixture({"x": []})):
            try:
                store = pv.collect(root); a = pv.render(store, "r/events")
                check_html(self, a, 0, len(store)); self.assertIn("0 events in", a)
                self.assertEqual('id="empty"' in a, not store)
            finally:
                shutil.rmtree(root, ignore_errors=True)
    def test_missing_field_in_an_event_renders_blank(self):
        root = fixture({"x": [{"id": "x-1", "name": "n"}]})
        try:
            a = pv.render(pv.collect(root), "r/events"); check_html(self, a, 1, 1); self.assertIn('<span class="badge exit bad"></span>', a)
        finally:
            shutil.rmtree(root, ignore_errors=True)
    def test_malformed_store_raises(self):
        (self.root / DEFAULT_RUNBOOKS / "events" / "x.jsonl").write_text("{\n")
        with self.assertRaises(ValueError): pv.collect(self.root)

class LiveTests(livetest.LiveCase):
    """projection.md p2: the projector runs over the real instance and yields valid output. Empty instance
    (a fresh install): the page is still rendered and says "No events recorded yet" — the documented empty
    behaviour, asserted below rather than skipped (#171)."""
    def test_live_run(self):
        root = dyadlib.repo_root()
        with tempfile.TemporaryDirectory() as d:
            inst = Path(d) / "inst"
            shutil.copytree(dyadlib.instance(root), inst, ignore=shutil.ignore_patterns("projections"))
            env = dict(os.environ, DYAD_INSTANCE=str(inst)); env.pop("DYAD_RUNBOOKS", None)
            r = subprocess.run([sys.executable, str(Path(pv.__file__))], cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr); self.assertRegex(r.stdout, r"\[project\] events: \d+ events, \d+ instances")
            out = inst / "projections" / "events.html"; self.assertTrue(out.exists())
            text = out.read_text()
            store = pv.collect(root)
            check_html(self, text, sum(len(v) for v in store.values()), len(store))
            self.assertEqual(pv.render(store, pv.runbooks.runbooks_rel() + "/events"), text, "second render byte-identical")
            if not store:
                self.assertIn("No events recorded yet", text)


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the projector's INVARIANTS hold (the runner's pass runs them before any check)."""
    def test_invariants_hold(self):
        self.assertEqual(dyadlib.check_invariants(pv), len(pv.INVARIANTS)); self.assertTrue(pv.INVARIANTS)

if __name__ == "__main__":
    unittest.main()
