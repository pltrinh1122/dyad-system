"""Disclosure projector tests (crafts/disclosure/projectors/project_disclosure.py): a fixture log ->
groups, counts and controlled consequence values; Agent prose pseudonymized; the gate refusing an
assembled document that carries a leak and writing nothing; determinism; one self-contained file; the
refusals (no AUDIENCE, bad LEVEL, no core incident guard); and a live run over this instance."""
import os, re, subprocess, sys, tempfile, unittest
from pathlib import Path
CRAFT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CRAFT.parents[1] / "dyad" / "scripts")); sys.path.insert(0, str(CRAFT / "projectors")); sys.path.insert(0, str(CRAFT / "scripts"))
import dyadlib
import project_disclosure as pd
import redaction as rd

HOMEDIR = "/ho" + "me/user/tree"          # assembled: a craft file carries no host-specific literal (Rule-11 p1)
LAN = "192." + "168.1.9"

HEAD = "# Incidents\n\n| date | d-work | what | cause | consequence |\n|---|---|---|---|---|\n"
LOG = (HEAD
       + "| 2026-09-01 | #1 | a | b | caught before any commit; nothing reached `main` |\n"
       + "| 2026-09-02 | #2 | a | b | it reached `main` and was corrected |\n"
       + "| 2026-08-30 | #3 | a | b | recovered without loss |\n"
       + "| 2026-08-31 | #4 | a | b | something else entirely |\n")
# The surface parses with the core's incident guard (the log's one parser, Rule-13). A system whose
# core predates it can still install and check this craft; the behaviour tests then skip and say so —
# the same shape crafts/sysarch/tests uses for a craft that is not installed (#171).
needs_incidents = unittest.skipUnless(pd.incidents_parser() is not None,
                                      "the core craft carries no incident parser here (dyad/scripts/incidents.py)")

MAP = "# map\n\n| real | pseudonym | kind | since |\n|---|---|---|---|\n| `Rule-16` | POLICY-A | rule number | #166 |\n"

def fixture(summary: str | None = None, mapped: bool = True):
    root = Path(tempfile.mkdtemp()); (root / "dyad").mkdir()
    inst = root / "agent-corpus"; (inst / "audits").mkdir(parents=True)
    (inst / "audits" / "INCIDENTS.md").write_text(LOG)
    (inst / "disclosure").mkdir(parents=True)
    if mapped:
        (inst / "disclosure" / "pseudonyms.md").write_text(MAP)
    if summary is not None:
        d = inst / "disclosure" / "summaries"; d.mkdir()
        (d / "2026-09.md").write_text(summary)
    return root

class ContractTests(unittest.TestCase):
    def test_invariants_hold(self):
        for name, pred in pd.INVARIANTS:
            self.assertTrue(pred(), name)
    def test_surface_and_levels(self):
        self.assertEqual(pd.SURFACE, "disclosure"); self.assertEqual(pd.LEVELS, ("standard", "minimal"))

@needs_incidents
class CollectTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_groups_by_month_with_counts_and_controlled_shapes(self):
        data = pd.collect(fixture())
        self.assertEqual([g["key"] for g in data["groups"]], ["2026-08", "2026-09"])
        self.assertEqual([g["count"] for g in data["groups"]], [2, 2])
        self.assertIn("covered through: 4 rows, latest 2026-09-02", data["watermark"])
        every = {s for g in data["groups"] for s in g["shapes"]}
        self.assertTrue(every <= {n for n, _ in pd.SHAPES}, every)           # controlled values only
    def test_unmatched_consequence_is_not_classified_never_guessed(self):
        self.assertEqual(pd.shape_of("something else entirely"), "not classified")
        self.assertEqual(pd.shape_of("caught before any commit"), pd.SHAPES[0][0])
    def test_no_source_cell_reaches_the_document(self):
        text, _ = pd.assemble(fixture(), "A Party", "standard")
        for cell in ("something else entirely", "it reached `main` and was corrected"):
            self.assertNotIn(cell, text)                                      # assembled, never copied

@needs_incidents
class GateTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_agent_prose_is_pseudonymized(self):
        root = fixture(summary="Rule-16 was the policy involved.")
        text, manifest = pd.assemble(root, "A Party", "standard")
        self.assertIn("POLICY-A", text); self.assertNotIn("Rule-16", text)
        self.assertEqual(manifest["replaced"], 1)
    def test_an_unmapped_internal_in_prose_is_caught_by_the_gate(self):
        root = fixture(summary="Rule-20 was the policy involved.")
        text, _ = pd.assemble(root, "A Party", "standard")
        self.assertTrue(rd.findings(text, root), "an unmapped Class B value passed the gate")
    def test_identity_in_prose_is_caught_by_the_gate(self):
        root = fixture(summary=f"seen on {LAN} under {HOMEDIR}")
        text, _ = pd.assemble(root, "A Party", "standard")
        classes = {c for c, _, _ in rd.findings(text, root)}
        self.assertIn("a", classes)
    def test_minimal_level_drops_prose_entirely(self):
        root = fixture(summary="Rule-16 was the policy involved.")
        text, manifest = pd.assemble(root, "A Party", "minimal")
        self.assertNotIn("POLICY-A", text); self.assertEqual(manifest["replaced"], 0)
    def test_audience_is_on_the_document(self):
        text, _ = pd.assemble(fixture(), "Alchemic Solutions Group, Inc.", "standard")
        self.assertIn("Alchemic Solutions Group, Inc.", text)

@needs_incidents
class DocumentTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_deterministic(self):
        root = fixture(summary="Rule-16 held.")
        a, _ = pd.assemble(root, "A Party", "standard")
        b, _ = pd.assemble(root, "A Party", "standard")
        self.assertEqual(a, b)
    def test_self_contained_no_external_reference(self):
        text, _ = pd.assemble(fixture(), "A Party", "standard")
        for token in ("<link", "src=", "@import", "http://", "https://"):
            self.assertNotIn(token, text, token)
        self.assertIn("<style>", text)
    def test_html_is_escaped(self):
        text, _ = pd.assemble(fixture(summary="a <b>& c"), "A <b>Party", "standard")
        self.assertIn("&lt;b&gt;", text); self.assertNotIn("<b>Party", text)

class CliTests(unittest.TestCase):
    def _run(self, **env):
        return subprocess.run([sys.executable, str(CRAFT / "projectors" / "project_disclosure.py")],
                              capture_output=True, text=True, cwd=dyadlib.repo_root(),
                              env={**os.environ, "DYAD_NO_NESTED_TESTS": "1", **env})
    @needs_incidents   # the parameter checks are reached only once the surface has a parser
    def test_missing_audience_refuses(self):
        r = self._run(AUDIENCE="")
        self.assertEqual(r.returncode, 2); self.assertIn("AUDIENCE is required", r.stderr)
    @needs_incidents   # the parameter checks are reached only once the surface has a parser
    def test_bad_level_refuses(self):
        r = self._run(AUDIENCE="A Party", LEVEL="loose")
        self.assertEqual(r.returncode, 2); self.assertIn("LEVEL must be one of", r.stderr)
    def test_absent_core_incident_parser_refuses_rather_than_parsing_the_log_twice(self):
        real = pd.incidents_parser
        try:
            pd.incidents_parser = lambda: None
            self.assertEqual(pd.main(), 2)
        finally:
            pd.incidents_parser = real

class LiveTests(unittest.TestCase):
    def test_live_run_writes_a_clean_document(self):
        root = dyadlib.repo_root()
        if pd.incidents_parser() is None:
            self.skipTest("the core craft carries no incident parser here")
        text, manifest = pd.assemble(root, "A Party", "standard")
        self.assertEqual(rd.findings(text, root), [])                         # the gate over this instance's own log
        self.assertGreaterEqual(manifest["groups"], 1)
        self.assertIn("covered through:", text)

if __name__ == "__main__":
    unittest.main()
