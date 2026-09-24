"""countersign projector tests (crafts/countersign/rules/schema.md; d-work #156): a fixture system with every
store the mapping reads projects to a document that validates against `countersign-core.json`; each derivation
rule (D1-D7) yields what the rule says; the validator rejects what the schema rejects; determinism (collect and
render twice, byte-equal); and a live run over this instance: every instance validates, every mode is one of
the three, every countersignature's signer is a human party."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts")); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projectors"))
import project_countersign as pc
import dyadlib, livetest

PREFS = """# Operator preferences (preferences zone)

| key | value | allowed | read by |
|-----|-------|---------|---------|
| merge-disposition | with-done | `separate` \\| `with-done` | Rule-2 (binding) |
| ledger-pr-merge | agent | `ask` \\| `agent` | Rule-2 (not-ratification list) |
"""
INCIDENTS = """# Incidents (Rule-3)

| date | d-work | what | cause | consequence |
|------|--------|------|-------|-------------|
| 2026-09-20 | #2 | a check failed | a cause | a consequence |
| 2026-09-19 | #99 | an incident of a row not in this instance | c | c |
"""
PROV1 = ("# Provenance #1\n\n## 1 prompt 2026-09-18\n\n```\ndo the thing\n```\n\n"
         "## 2 disposition 2026-09-18 plan\n\n```\nY\n```\n\n## 3 disposition 2026-09-19 done\n\n```\nY, release demo-v1.0.0\n```\n")

def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=dyadlib.git_env())

def fixture(git: bool = False) -> Path:
    """A small system: three rows (one with a verbatim record, one intake, one without a record), a plan file,
    the preferences table, the incident log, one run-book's events; with `git`, a repository whose preferences
    commit cites `d-work #1` and one release tag."""
    root = Path(tempfile.mkdtemp())
    d = root / "agent-corpus" / "d-work"
    for sub in ("rows", "plans", "provenance"):
        (d / sub).mkdir(parents=True)
    rows = [dyadlib.Row(1, "first", "2026-09-18", "done", "2026-09-18 Y plan; 2026-09-19 Y done (merges PR #3)", ""),
            dyadlib.Row(2, "an intake", "2026-09-19", "planned", "2026-09-19 Y intake; 2026-09-19 N plan; 2026-09-20 Y plan", "workstation-7 parent-1 Rule-3"),
            dyadlib.Row(3, "a backlog row", "2026-09-20", "backlog", "", "")]
    for r in rows:
        (d / "rows" / f"{r.id}.md").write_text(dyadlib.format_row_file(r))
    (d / "plans" / "1.md").write_text("# Plan #1 — first\n\nBase commit of `main`: abc1234.\n\n## Intent as read\nx\n")
    (d / "provenance" / "1.md").write_text(PROV1)
    (root / "preferences-corpus").mkdir()
    (root / "preferences-corpus" / "PREFERENCES.md").write_text(PREFS)
    (root / "agent-corpus" / "audits").mkdir()
    (root / "agent-corpus" / "audits" / "INCIDENTS.md").write_text(INCIDENTS)
    ev = root / "workstation-corpus" / "runbooks" / "events"
    ev.mkdir(parents=True)
    (ev / "git-server.jsonl").write_text("".join(json.dumps({"id": f"git-server-2026091{i}T101500Z-status", "ts": f"2026-09-1{i}T10:15:00Z",
                                                             "role": "agent", "name": "status", "cmd": "docker ps", "class": "read-only",
                                                             "exit": 0}) + "\n" for i in (4, 5)))
    if git:
        _git(root, "init", "-q")
        _git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A")
        _git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "d-work #1: ledger-pr-merge preference")
        _git(root, "tag", "demo-v1.0.0")
        _git(root, "tag", "not-a-release")
    return root

class Env:
    """DYAD_INSTANCE / DYAD_RUNBOOKS at their defaults for the fixture (a caller's environment may set them)."""
    def setUp(self):
        self._saved = {k: os.environ.pop(k) for k in ("DYAD_INSTANCE", "DYAD_RUNBOOKS") if k in os.environ}
    def tearDown(self):
        os.environ.update(self._saved)

class ContractTests(unittest.TestCase):
    def test_invariants_hold(self):
        self.assertEqual(dyadlib.check_invariants(pc.INVARIANTS), len(pc.INVARIANTS))
    def test_schema_enums_equal_module_constants(self):
        s = pc.schema()["$defs"]
        self.assertEqual(tuple(s["act"]["properties"]["mode"]["enum"]), pc.MODES)
        self.assertEqual(tuple(s["party"]["properties"]["kind"]["enum"]), pc.PARTY_KINDS)
        self.assertEqual(tuple(s["countersignature"]["properties"]["answer"]["enum"]), pc.ANSWERS)
        self.assertEqual(tuple(s["countersignature"]["properties"]["basis"]["enum"]), pc.BASES)
        self.assertEqual(tuple(s["check"]["properties"]["timing"]["enum"]), pc.TIMINGS)
        self.assertEqual(pc.schema()["properties"]["schema_version"]["const"], pc.SCHEMA_VERSION)
    def test_schema_version_is_the_craft_version(self):
        self.assertEqual((Path(pc.__file__).resolve().parents[1] / "VERSION").read_text().strip(), pc.SCHEMA_VERSION)
    def test_top_level_arrays_are_the_eight_entities(self):
        req = pc.schema()["required"]
        self.assertEqual([k for k in req if k not in ("schema_version", "system")], list(pc.ENTITIES))

class ValidatorTests(unittest.TestCase):
    def doc(self):
        return {"schema_version": "0.1.0", "system": "x", **{e: [] for e in pc.ENTITIES}}
    def test_empty_document_validates(self):
        self.assertEqual(pc.check(self.doc()), [])
    def test_missing_entity_array_fails(self):
        d = self.doc(); del d["events"]
        self.assertTrue(any("missing 'events'" in e for e in pc.check(d)))
    def test_bad_enum_and_extra_key_fail(self):
        d = self.doc(); d["parties"] = [{"id": "p", "kind": "robot", "colour": "red"}]
        errs = pc.validate(d, pc.schema())
        self.assertTrue(any("not in" in e for e in errs)); self.assertTrue(any("unexpected 'colour'" in e for e in errs))
    def test_bad_mode_fails(self):
        d = self.doc(); d["parties"] = [{"id": "agent", "kind": "agent"}]
        d["acts"] = [{"id": "act-1", "title": "t", "mode": "manual", "processor": "agent", "state": "open", "refs": []}]
        self.assertTrue(any("'manual' not in" in e for e in pc.check(d)))
    def test_non_human_signer_fails(self):
        d = self.doc(); d["parties"] = [{"id": "agent", "kind": "agent"}]
        d["acts"] = [{"id": "act-1", "title": "t", "mode": "explicit", "processor": "agent", "state": "open", "refs": []}]
        d["proposals"] = [{"id": "proposal-1-plan", "act": "act-1", "author": "agent", "body_ref": None, "artifact_hash": None}]
        d["countersignatures"] = [{"id": "c-1", "subject": "proposal-1-plan", "signer": "agent", "answer": "yes", "basis": "per-act",
                                   "text": "Y", "bound_hash": None, "at": "2026-09-24"}]
        self.assertTrue(any("is not human" in e for e in pc.check(d)))
    def test_automatic_act_processed_by_agent_fails(self):
        d = self.doc(); d["parties"] = [{"id": "agent", "kind": "agent"}]
        d["acts"] = [{"id": "act-1", "title": "t", "mode": "automatic", "processor": "agent", "state": "open", "refs": []}]
        self.assertTrue(any("executor a automatic act requires" in e for e in pc.check(d)))
    def test_unresolved_reference_fails(self):
        d = self.doc(); d["parties"] = [{"id": "agent", "kind": "agent"}]
        d["events"] = [{"id": "event-x-0", "act": "act-9", "seq": 0, "payload": {}, "at": ""}]
        self.assertTrue(any("act act-9 unresolved" in e for e in pc.check(d)))
    def test_unsupported_keyword_is_an_error(self):
        self.assertTrue(pc.validate(1, {"oneOf": []}))
    def test_boolean_is_not_integer(self):
        self.assertTrue(pc.validate(True, {"type": "integer"}))

class FixtureTests(Env, unittest.TestCase):
    def setUp(self):
        super().setUp(); self.root = fixture(); self.doc = pc.collect(self.root)
    def test_fixture_validates(self):
        self.assertEqual(pc.check(self.doc), [])
    def test_counts(self):
        self.assertEqual(pc.counts(self.doc), "parties=2 acts=4 proposals=4 countersignatures=5 mandates=1 releases=0 events=2 escalations=3")
    def test_d1_every_act_explicit_agent(self):
        self.assertEqual({(a["mode"], a["processor"]) for a in self.doc["acts"]}, {("explicit", "agent")})
    def test_d2_plan_file_is_a_proposal_with_its_hash(self):
        p = next(p for p in self.doc["proposals"] if p["id"] == "proposal-1-plan")
        self.assertEqual(p["body_ref"], "agent-corpus/d-work/plans/1.md"); self.assertTrue(p["artifact_hash"].startswith("sha256:"))
    def test_d3_verbatim_text_from_provenance_else_ledger(self):
        s = {c["id"]: c for c in self.doc["countersignatures"]}
        self.assertEqual(s["countersignature-1-2"]["text"], "Y, release demo-v1.0.0")
        self.assertEqual(s["countersignature-1-2"]["profile"]["text_source"], "provenance")
        self.assertEqual(s["countersignature-2-2"]["profile"]["text_source"], "ledger")
        self.assertEqual(s["countersignature-2-2"]["answer"], "no")
        self.assertEqual(s["countersignature-2-2"]["subject"], "proposal-2-plan")
        self.assertEqual({c["basis"] for c in s.values()}, {"per-act"})
    def test_d4_mandate_without_git_has_no_countersignature(self):
        m, = self.doc["mandates"]
        self.assertEqual(m["id"], "mandate-ledger-pr-merge"); self.assertIsNone(m["countersignature"])
    def test_d4_no_mandate_when_value_is_ask(self):
        f = self.root / "preferences-corpus" / "PREFERENCES.md"
        f.write_text(f.read_text().replace("| ledger-pr-merge | agent |", "| ledger-pr-merge | ask |"))
        self.assertEqual(pc.collect(self.root)["mandates"], [])
    def test_d6_events_of_one_runbook_act(self):
        self.assertEqual([e["seq"] for e in self.doc["events"]], [0, 1])
        self.assertEqual({e["act"] for e in self.doc["events"]}, {"act-runbook-git-server"})
    def test_d7_intake_and_incidents(self):
        x = {e["id"]: e for e in self.doc["escalations"]}
        self.assertIn("escalation-intake-2-workstation-7", x)
        self.assertEqual(x["escalation-intake-2-workstation-7"]["opens"], "act-2")
        self.assertFalse(any("parent-1" in i for i in x))                            # a parent ref is no origin system
        froms = sorted(e["from"] for e in x.values() if e["profile"]["source"] == "incident")
        self.assertEqual(froms, ["act-2", "ext:#99"])
    def test_absent_stores_yield_empty_arrays(self):
        root = Path(tempfile.mkdtemp()); (root / "agent-corpus" / "d-work" / "rows").mkdir(parents=True)
        doc = pc.collect(root)
        self.assertEqual(pc.counts(doc), "parties=2 acts=0 proposals=0 countersignatures=0 mandates=0 releases=0 events=0 escalations=0")
        self.assertEqual(pc.check(doc), [])
    def test_deterministic(self):
        self.assertEqual(pc.render(pc.collect(self.root)), pc.render(pc.collect(self.root)))
        self.assertEqual(pc.render(self.doc), json.dumps(json.loads(pc.render(self.doc)), sort_keys=True, indent=1, ensure_ascii=False) + "\n")

class GitFixtureTests(Env, unittest.TestCase):
    def setUp(self):
        super().setUp(); self.root = fixture(git=True); self.doc = pc.collect(self.root)
    def test_d4_mandate_countersigned_by_the_introducing_d_works_done(self):
        self.assertEqual(self.doc["mandates"][0]["countersignature"], "countersignature-1-2")
    def test_d5_release_tags(self):
        r, = self.doc["releases"]                                                     # `not-a-release` is not a release tag
        self.assertEqual((r["id"], r["definition_ref"], r["version"], r["countersignature"]), ("release-demo-v1.0.0", "crafts/demo", "1.0.0", "countersignature-1-2"))
        self.assertTrue(r["hash"].startswith("git:"))
        self.assertEqual(pc.check(self.doc), [])

class LiveTests(livetest.LiveCase):
    def setUp(self):
        self.require_instance()
        self.doc = pc.collect(dyadlib.repo_root())
    def test_live_every_instance_validates(self):
        self.assertEqual(pc.check(self.doc), [])
    def test_live_one_act_per_row(self):
        rows = dyadlib.read_rows(dyadlib.repo_root())
        self.assertEqual({f"act-{r.id}" for r in rows}, {a["id"] for a in self.doc["acts"] if not a["id"].startswith("act-runbook-")})
    def test_live_mode_is_one_of_three(self):
        self.assertTrue(all(a["mode"] in pc.MODES for a in self.doc["acts"]))
    def test_live_every_signer_is_human(self):
        kind = {p["id"]: p["kind"] for p in self.doc["parties"]}
        self.assertTrue(all(kind[s["signer"]] == "human" for s in self.doc["countersignatures"]))
    def test_live_deterministic(self):
        self.assertEqual(pc.render(self.doc), pc.render(pc.collect(dyadlib.repo_root())))

if __name__ == "__main__":
    unittest.main()
