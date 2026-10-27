"""DMC guard tests (agent/dmc.py, plan #507): over temp fixture trees, a valid record in each container (core, craft,
instance) passes; each failure class fails with a recognisable message; paths, the whitespace collapse, the
absent-craft warning, the exempt path fields, a null implementation, a duplicate @id and the empty case."""
import copy, json, os, shutil, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
g = dyadlib.load_guard("agent", "dmc")

HOME = "# Host mutation\n\nThree classes:\n- **Read-only**  — free.\n- **Reversible\n  action** — undoable.\n"

def record(container: str, ident: str = "action-class", home: str = "rules/home.md", **over) -> dict:
    r = {"@context": copy.deepcopy(g.CONTEXT), "@id": f"urn:dyad:dmc:{container}/{ident}",
         "@type": ["DefinedTermSet", "dyad:DecisionCriterion"], "identifier": ident, "name": "Action class",
         "description": "Which class a host action falls in.", "dyad:decides": "Which class is this action?",
         "dyad:inputs": ["the action"],
         "hasDefinedTerm": [
             {"@type": "DefinedTerm", "termCode": "ro", "name": "read-only", "dyad:when": "nothing changes", "dyad:then": "free"},
             {"@type": ["DefinedTerm"], "termCode": "rev", "name": "reversible action", "dyad:when": "it can be undone", "dyad:then": "plan-Y"}],
         "dyad:judgedBy": {"dyad:kind": "inference", "dyad:implementation": None},
         "isPartOf": "urn:dyad:instance" if container == "instance" else f"urn:dyad:craft:{container}",
         "dyad:home": home, "dyad:owner": "Rule-8"}
    r.update(over)
    return r

class Tree:
    """A temp repo root: `dyad/` (the core, with its context), `crafts/<c>/`, `agent-corpus/` (the instance)."""
    def __init__(self):
        self.root = Path(tempfile.mkdtemp()); self.pkg = self.root / "dyad"
        (self.pkg / "dmc").mkdir(parents=True)
        (self.pkg / "dmc" / "context.jsonld").write_text(json.dumps({"@context": g.CONTEXT}, indent=2))
        (self.pkg / "rules").mkdir(); (self.pkg / "rules" / "home.md").write_text(HOME)
    def craft(self, name: str) -> Path:
        d = self.root / "crafts" / name; (d / "rules").mkdir(parents=True, exist_ok=True)
        (d / "VERSION").write_text("0.1.0\n"); (d / "rules" / "home.md").write_text(HOME); return d
    def put(self, base: Path, rec, ident: str | None = None) -> Path:
        d = base / "dmc"; d.mkdir(parents=True, exist_ok=True)
        p = d / f"{ident or rec['identifier']}.jsonld"
        p.write_text(rec if isinstance(rec, str) else json.dumps(rec, indent=2)); return p
    def check(self) -> list[str]:
        return g.check_package(self.root, self.pkg)

class DmcGuardTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("DYAD_INSTANCE", None); self.t = Tree()
    def tearDown(self):
        shutil.rmtree(self.t.root, ignore_errors=True)
    def fails(self, *needles):
        msgs = self.t.check(); bad = [m for m in msgs if not m.startswith("warning:")]
        for n in needles:
            self.assertTrue(any(n in m for m in bad), (n, msgs))
        return msgs

    def test_contract(self):
        self.assertIsNone(dyadlib.contract_problem(g, "core", "agent"))
        self.assertEqual((g.ENTITY, g.CORPUS, g.TRANSACTION, g.OWNER), ("dmc", "agent", False, "Rule-12"))

    def test_no_records_passes_with_skip_summary(self):
        self.assertEqual(self.t.check(), [])
        self.assertIn("skip", g.summary(self.t.root, self.t.pkg))

    def test_valid_record_per_container_passes(self):
        self.t.put(self.t.pkg, record("dyad-operator"))
        self.t.put(self.t.craft("sysadmin"), record("sysadmin"))
        inst = self.t.root / "agent-corpus"; (inst / "notes").mkdir(parents=True); (inst / "notes" / "h.md").write_text(HOME)
        self.t.put(inst, record("instance", home="agent-corpus/notes/h.md"))
        self.assertEqual(self.t.check(), [])
        self.assertEqual(g.summary(self.t.root, self.t.pkg), "3 records (dyad-operator 1, sysadmin 1, instance 1)")
        self.assertEqual(g.describe(self.t.root, self.t.pkg)["observed"], 3)

    def test_instance_follows_dyad_instance(self):
        inst = self.t.root / "elsewhere"; inst.mkdir(); (inst / "h.md").write_text(HOME)
        self.t.put(inst, record("instance", home="elsewhere/h.md"))
        self.assertEqual(self.t.check(), [])               # default instance: not read
        os.environ["DYAD_INSTANCE"] = "elsewhere"
        try:
            self.assertEqual(g.summary(self.t.root, self.t.pkg), "1 records (instance 1)"); self.assertEqual(self.t.check(), [])
        finally:
            os.environ.pop("DYAD_INSTANCE", None)

    def test_context_file_is_skipped(self):
        self.t.put(self.t.pkg, record("dyad-operator"))
        self.assertEqual(len(g.records(self.t.root, self.t.pkg)), 1)

    def test_parse_error(self):
        self.t.put(self.t.pkg, "{not json", ident="broken"); self.fails("broken.jsonld: not JSON")

    def test_missing_required_key(self):
        r = record("dyad-operator"); del r["dyad:owner"]; del r["dyad:inputs"]
        self.t.put(self.t.pkg, r); self.fails("missing required key(s) dyad:inputs, dyad:owner")

    def test_context_must_equal_core(self):
        self.t.put(self.t.pkg, record("dyad-operator", **{"@context": "https://schema.org"})); self.fails("@context differs")

    def test_type_needs_both(self):
        self.t.put(self.t.pkg, record("dyad-operator", **{"@type": ["DefinedTermSet"]})); self.fails("@type must hold")

    def test_id_identifier_and_part_of(self):
        self.t.put(self.t.pkg, record("dyad-operator", **{"@id": "urn:dyad:dmc:sysadmin/action-class"}))
        self.t.put(self.t.pkg, record("dyad-operator", ident="other", identifier="wrong", isPartOf="urn:dyad:instance"), ident="other")
        self.fails("@id 'urn:dyad:dmc:sysadmin/action-class' is not 'urn:dyad:dmc:dyad-operator/action-class'",
                   "identifier 'wrong' differs from the file stem 'other'", "isPartOf 'urn:dyad:instance' is not 'urn:dyad:craft:dyad-operator'")

    def test_inputs_shape(self):
        self.t.put(self.t.pkg, record("dyad-operator", **{"dyad:inputs": []})); self.fails("dyad:inputs is not a non-empty list")

    def test_outcomes_shape(self):
        r = record("dyad-operator"); r["hasDefinedTerm"] = r["hasDefinedTerm"][:1]
        self.t.put(self.t.pkg, r); self.fails("at least two outcomes")
    def test_outcome_fields_and_type(self):
        r = record("dyad-operator"); r["hasDefinedTerm"][0]["@type"] = "Thing"; r["hasDefinedTerm"][1]["dyad:then"] = ""
        self.t.put(self.t.pkg, r); self.fails("hasDefinedTerm[0] @type is not DefinedTerm", "hasDefinedTerm[1] dyad:then is not a non-empty string")
    def test_term_codes_unique(self):
        r = record("dyad-operator"); r["hasDefinedTerm"][1]["termCode"] = "ro"
        self.t.put(self.t.pkg, r); self.fails("termCode 'ro' used twice")

    def test_judged_by(self):
        self.t.put(self.t.pkg, record("dyad-operator", **{"dyad:judgedBy": {"dyad:kind": "vibes", "dyad:implementation": "nope.py"}}))
        self.fails("dyad:kind 'vibes' is not one of", "dyad:implementation 'nope.py' does not exist")
    def test_implementation_present_for_any_kind(self):
        (self.t.pkg / "guards").mkdir(); (self.t.pkg / "guards" / "x.py").write_text("")
        self.t.put(self.t.pkg, record("dyad-operator", **{"dyad:judgedBy": {"dyad:kind": "declared", "dyad:implementation": "guards/x.py"}}))
        self.assertEqual(self.t.check(), [])
    def test_null_implementation_allowed(self):
        for k in g.KINDS:
            self.t.put(self.t.pkg, record("dyad-operator", **{"dyad:judgedBy": {"dyad:kind": k, "dyad:implementation": None}}))
            self.assertEqual(self.t.check(), [], k)

    def test_home_and_also_in_must_exist(self):
        self.t.put(self.t.pkg, record("dyad-operator", home="rules/missing.md", **{"dyad:alsoIn": ["rules/home.md", "rules/gone.md"]}))
        self.fails("dyad:home 'rules/missing.md' does not exist", "dyad:alsoIn 'rules/gone.md' does not exist")

    def test_cross_craft_path_inside_root(self):
        self.t.craft("sysadmin")
        self.t.put(self.t.pkg, record("dyad-operator", **{"dyad:alsoIn": ["../crafts/sysadmin/rules/home.md"]}))
        self.assertEqual(self.t.check(), [])
    def test_path_outside_root_fails(self):
        self.t.put(self.t.pkg, record("dyad-operator", **{"dyad:alsoIn": ["../../etc/passwd"]})); self.fails("resolves outside the repo")
    def test_absent_craft_warns(self):
        self.t.put(self.t.pkg, record("dyad-operator", **{"dyad:alsoIn": ["../crafts/lan-git/rules/x.md"]}))
        msgs = self.t.check()
        self.assertEqual([m for m in msgs if not m.startswith("warning:")], [], msgs)
        self.assertTrue(any(m.startswith("warning:") and "craft lan-git, absent here" in m for m in msgs), msgs)
    def test_present_craft_missing_file_fails(self):
        self.t.craft("sysadmin")
        self.t.put(self.t.pkg, record("dyad-operator", **{"dyad:alsoIn": ["../crafts/sysadmin/rules/none.md"]})); self.fails("does not exist")

    def test_outcome_name_in_home_with_whitespace_collapse(self):
        self.t.put(self.t.pkg, record("dyad-operator"))       # "Reversible\n  action" in HOME matches "reversible action"
        self.assertEqual(self.t.check(), [])
    def test_outcome_name_absent_from_home(self):
        r = record("dyad-operator"); r["hasDefinedTerm"][0]["name"] = "destructive"
        self.t.put(self.t.pkg, r); self.fails("outcome name 'destructive' not found in dyad:home rules/home.md")

    def test_forbidden_values(self):
        r = record("dyad-operator", description="Set on 2026-10-27 at v1.2.3 by a@b.org in " + "a" * 40 + ".")
        self.t.put(self.t.pkg, r)
        self.fails("forbidden date '2026-10-27'", "forbidden version 'v1.2.3'", "forbidden email 'a@b.org'", "forbidden commit")
    def test_forbidden_nested(self):
        r = record("dyad-operator"); r["hasDefinedTerm"][0]["dyad:then"] = "since 1.0.0"
        self.t.put(self.t.pkg, r); self.fails("forbidden version '1.0.0'")
    def test_dates_allowed_in_path_fields_and_owner(self):
        d = self.t.pkg / "audits"; d.mkdir(); (d / "2026-09-24-x.md").write_text(HOME); (d / "2026-09-25-y.py").write_text("")
        self.t.put(self.t.pkg, record("dyad-operator", home="audits/2026-09-24-x.md", **{
            "dyad:alsoIn": ["audits/2026-09-24-x.md"], "dyad:owner": "Rule-8 (2026-09-12)",
            "dyad:judgedBy": {"dyad:kind": "mechanical", "dyad:implementation": "audits/2026-09-25-y.py"}}))
        self.assertEqual(self.t.check(), [])

    def test_duplicate_id_fails(self):
        self.t.put(self.t.pkg, record("dyad-operator"))
        self.t.put(self.t.pkg, record("dyad-operator", identifier="dup", **{"@id": "urn:dyad:dmc:dyad-operator/action-class"}), ident="dup")
        self.fails("@id urn:dyad:dmc:dyad-operator/action-class declared by 2 records")

    def test_absent_context_fails_when_records_exist(self):
        (self.t.pkg / "dmc" / "context.jsonld").unlink()
        self.t.put(self.t.pkg, record("dyad-operator")); self.fails("the core context is absent")


if __name__ == "__main__":
    unittest.main()
