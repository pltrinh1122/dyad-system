"""countersign projector tests (dyad/scripts/project_countersign.py, the core's since #378; the model `dyad/playbooks/countersign-model.md`; d-work #156): a fixture system with every
store the mapping reads projects to a document that validates against `countersign-core.json`; each derivation
rule (D1-D7) yields what the rule says; the validator rejects what the schema rejects; determinism (collect and
render twice, byte-equal); the I6 interaction check (the model's interaction section; d-work #152): D8
derives each act's initiation, an act without one is flagged as a warning; and a live run over this instance: every
instance validates, every mode is one of the three, every countersignature's signer is a human party."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
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
PROV5 = ("# Provenance #5\n\n## 1 prompt 2026-09-21\n\n```\nopen the mandate\n```\n\n"            # D-2: an `N` followed by its revision's words
         "## 2 disposition 2026-09-21 plan\n\n```\nN: narrower, one child per failure mode\n```\n\n"
         "## 3 prompt 2026-09-21\n\n```\nnarrower, one child per failure mode\n```\n\n"
         "## 4 disposition 2026-09-21 plan (revision 2)\n\n```\nY\n```\n")
PROV6 = "# Provenance #6\n\n## 1 disposition 2026-09-21 mandate #5, 2026-09-21\n\n```\nY\n```\n"   # Rule-7 property 4: the mandate's own words

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
            dyadlib.Row(3, "a backlog row", "2026-09-20", "backlog", "", ""),
            dyadlib.Row(5, "a mandate", "2026-09-21", "planned", "2026-09-21 N plan; 2026-09-21 Y plan (revision 2)", ""),        # D-2, D-3 (#330)
            dyadlib.Row(6, "an accreted child", "2026-09-21", "open", "2026-09-21 Y plan (mandate #5)", "parent-5", "implicit")]   # D-1: `mode: implicit`
    for r in rows:
        (d / "rows" / f"{r.id}.md").write_text(dyadlib.format_row_file(r))
    (d / "plans" / "1.md").write_text("# Plan #1 — first\n\nBase commit of `main`: abc1234.\n\n## Intent as read\nx\n")
    (d / "provenance" / "1.md").write_text(PROV1)
    (d / "provenance" / "5.md").write_text(PROV5)
    (d / "provenance" / "6.md").write_text(PROV6)
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
    def test_schema_version_is_the_schema_files_own(self):
        """The schema's version is the shape countersign-v0.3.0 published, carried by the file's `$comment`; it moves with
        the file, never with dyad/VERSION (#378 attack 3) — so the core's version and the schema's are allowed to differ."""
        self.assertIn(f"schema version {pc.SCHEMA_VERSION} ", pc.schema()["$comment"])
        self.assertRegex(pc.SCHEMA_VERSION, r"^\d+\.\d+\.\d+$")
        self.assertNotEqual((dyadlib.PKG / "VERSION").read_text().strip(), pc.SCHEMA_VERSION)
        self.assertEqual(pc.SCHEMA_PATH, Path(pc.__file__).resolve().parent / "countersign-core.json")   # beside its reader
    def test_top_level_arrays_are_the_eight_entities(self):
        req = pc.schema()["required"]
        self.assertEqual([k for k in req if k not in ("schema_version", "system")], list(pc.ENTITIES))

class ValidatorTests(unittest.TestCase):
    def doc(self):
        return {"schema_version": pc.SCHEMA_VERSION, "system": "x", **{e: [] for e in pc.ENTITIES}}
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
        # Carries the claim `InteractionTests.test_warning_never_fails_the_document` held until #186
        # (its body was character-identical to this one under an equivalent setUp): the fixture
        # already contains the uninitiated `act-3` that D8 flags, so the I6 warning
        # (the model's I6, asserted at test_d8_act_without_initiation_is_flagged)
        # is a warning only — it never becomes a validation error.
        self.assertEqual(pc.check(self.doc), [])
    def test_counts(self):
        self.assertEqual(pc.counts(self.doc), "parties=2 acts=6 proposals=6 countersignatures=8 mandates=2 releases=0 events=2 escalations=3")
    def test_d1_an_acts_mode_is_its_rows_mode(self):
        """#330 D-1: `mode` is read off the row (`implicit` under a mandate), the processor is the agent in both modes;
        a row with no `mode` line reads `explicit` (`dyadlib.DEFAULT_MODE`)."""
        mode = {a["id"]: (a["mode"], a["processor"]) for a in self.doc["acts"]}
        self.assertEqual(mode["act-6"], ("implicit", "agent"))
        self.assertEqual({mode[f"act-{i}"] for i in (1, 2, 3, 5)}, {("explicit", "agent")})
        self.assertEqual(pc.DERIVED_MODE, dyadlib.DEFAULT_MODE)
    def test_d2_an_n_followed_by_its_revisions_prompt_is_amend(self):
        """#330 D-2 (Rule-3 Answer grammar): row 5's first `N` is followed in its record by a `prompt` entry — `amend`;
        row 2's `N` has no record (ledger text) and stays `no`; a `Y` is never `amend`."""
        s = {c["id"]: c for c in self.doc["countersignatures"]}
        self.assertEqual((s["countersignature-5-1"]["answer"], s["countersignature-5-1"]["text"]), ("amend", "N: narrower, one child per failure mode"))
        self.assertEqual(s["countersignature-5-2"]["answer"], "yes")
        self.assertEqual(s["countersignature-2-2"]["answer"], "no")
    def test_d3_a_mandate_note_is_the_mandate_basis_and_the_mandate_is_projected(self):
        """#330 D-3: row 6's one entry, `Y plan (mandate #5)`, has basis `mandate` and names `mandate-5` in its profile;
        `mandate-5` is a Mandate countersigned by row 5's own plan-`Y` (its last `yes` on the plan proposal)."""
        s = {c["id"]: c for c in self.doc["countersignatures"]}
        self.assertEqual((s["countersignature-6-1"]["basis"], s["countersignature-6-1"]["profile"]["mandate"]), ("mandate", "mandate-5"))
        self.assertEqual(s["countersignature-6-1"]["subject"], "proposal-6-plan")
        m = {m["id"]: m for m in self.doc["mandates"]}
        self.assertEqual(sorted(m), ["mandate-5", "mandate-ledger-pr-merge"])
        self.assertEqual(m["mandate-5"]["countersignature"], "countersignature-5-2")
        self.assertEqual(m["mandate-5"]["scope"]["plan_template"], "proposal-5-plan")
        self.assertEqual(pc.check(self.doc), [])
    def test_d3_a_dangling_mandate_note_is_listed_without_a_countersignature(self):
        d = self.root / "agent-corpus" / "d-work"
        (d / "rows" / "7.md").write_text(dyadlib.format_row_file(dyadlib.Row(7, "orphan", "2026-09-22", "open", "2026-09-22 Y plan (mandate #40)", "parent-40", "implicit")))
        doc = pc.collect(self.root)
        m = next(m for m in doc["mandates"] if m["id"] == "mandate-40")
        self.assertEqual((m["countersignature"], m["profile"]["act"], m["scope"]["plan_template"]), (None, None, None))
        self.assertEqual(pc.check(doc), [])
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
        self.assertEqual({c["basis"] for c in s.values() if not c["id"].startswith("countersignature-6-")}, {"per-act"})
    def test_d4_mandate_without_git_has_no_countersignature(self):
        m = next(m for m in self.doc["mandates"] if m["id"] == "mandate-ledger-pr-merge")
        self.assertIsNone(m["countersignature"])
    def test_d4_no_mandate_when_value_is_ask(self):
        f = self.root / "preferences-corpus" / "PREFERENCES.md"
        f.write_text(f.read_text().replace("| ledger-pr-merge | agent |", "| ledger-pr-merge | ask |"))
        self.assertEqual([m["id"] for m in pc.collect(self.root)["mandates"]], ["mandate-5"])   # the row mandate stays (D-3)
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

class InteractionTests(Env, unittest.TestCase):
    """I6 (the model's interaction section): every act has an initiation — a prompt, a signal or a release trigger (D8 derives it)."""
    def setUp(self):
        super().setUp(); self.root = fixture(); self.doc = pc.collect(self.root)
        self.ini = {a["id"]: a["profile"]["initiation"] for a in self.doc["acts"]}
    def test_d8_prompt_from_provenance(self):
        self.assertEqual(self.ini["act-1"], {"kind": "prompt", "source": "provenance", "entry": 1})
    def test_d8_intake_origin_is_a_signal(self):
        self.assertEqual(self.ini["act-2"], {"kind": "signal", "source": "intake", "origin": "workstation-7"})
    def test_d8_an_accreted_row_is_a_signal_its_mandate_covers(self):
        """#378: row 6 holds one entry, `Y plan (mandate #5)`, and a record whose entry 1 is that `Y` (Rule-7 property 4),
        no prompt — its initiation is the mandate, a signal the mandate covers (the model's implicit mode)."""
        self.assertEqual(self.ini["act-6"], {"kind": "signal", "source": "mandate", "mandate": "mandate-5"})
    def test_d8_act_without_initiation_is_flagged(self):
        self.assertEqual(self.ini["act-3"]["kind"], None)
        i = pc.interaction(self.doc)
        self.assertEqual(i["uninitiated"], [("act-3", "no provenance record")])
        self.assertEqual((i["initiated"], i["underivable"]), (4, ["act-runbook-git-server"]))   # acts 1, 2, 5 (a prompt) and 6 (its mandate)
        self.assertTrue(pc.interaction_line(i).startswith("warn [project] countersign: I6 initiated=4 uninitiated=1 underivable=1"))
    def test_d8_record_without_prompt_is_named(self):
        d = self.root / "agent-corpus" / "d-work"
        (d / "provenance" / "3.md").write_text("# Provenance #3\n")
        ini = {a["id"]: a["profile"]["initiation"] for a in pc.collect(self.root)["acts"]}
        self.assertEqual(ini["act-3"]["missing"], "no prompt entry in the provenance record")
    def test_d8_opening_disposition_is_a_prompt(self):
        d = self.root / "agent-corpus" / "d-work"
        r = dyadlib.Row(4, "deferred", "2026-09-20", "backlog", "2026-09-20 Y (opened from #1, deferred)", "1")
        (d / "rows" / "4.md").write_text(dyadlib.format_row_file(r))
        ini = {a["id"]: a["profile"]["initiation"] for a in pc.collect(self.root)["acts"]}
        self.assertEqual((ini["act-4"]["kind"], ini["act-4"]["source"]), ("prompt", "opening-disposition"))
    def test_act_without_profile_counts_as_uninitiated(self):
        d = {"acts": [{"id": "act-9", "title": "t", "mode": "explicit", "processor": "agent", "state": "open", "refs": []}]}
        self.assertEqual(pc.interaction(d)["uninitiated"], [("act-9", "no initiation derived")])
    def test_all_initiated_is_ok(self):
        d = {"acts": [{"id": "act-1", "profile": {"initiation": {"kind": "prompt"}}}]}
        self.assertTrue(pc.interaction_line(pc.interaction(d)).startswith("ok   [project] countersign: I6 initiated=1 uninitiated=0"))
    def test_deterministic_with_initiation(self):
        self.assertEqual(pc.render(pc.collect(self.root)), pc.render(self.doc))

class GitFixtureTests(Env, unittest.TestCase):
    def setUp(self):
        super().setUp(); self.root = fixture(git=True); self.doc = pc.collect(self.root)
    def test_d4_mandate_countersigned_by_the_introducing_d_works_done(self):
        m = next(m for m in self.doc["mandates"] if m["id"] == "mandate-ledger-pr-merge")
        self.assertEqual(m["countersignature"], "countersignature-1-2")
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
    def test_live_every_act_has_an_initiation_profile(self):
        self.assertTrue(all("initiation" in a.get("profile", {}) for a in self.doc["acts"]))
        i = pc.interaction(self.doc)
        self.assertEqual(i["initiated"] + len(i["uninitiated"]) + len(i["underivable"]), len(self.doc["acts"]))
    def test_live_deterministic(self):
        self.assertEqual(pc.render(self.doc), pc.render(pc.collect(dyadlib.repo_root())))

if __name__ == "__main__":
    unittest.main()
