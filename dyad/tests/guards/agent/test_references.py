"""Reference guard tests (agent/references.py, Rule-20): a fixture corpus where every kind resolves;
one broken reference per resolvable kind, each failing under its own kind name; ranges, `PR` and
`(pre-ledger)` segments, glob paths, generated-path acceptance, the empty-store skip of a
package-only scratch install; the register's shape (the frame's kinds 12 and 13 are listed as
`guard:agent/frame.py` since #151 and tested in test_frame.py); and a live run over the real repo
that must return no FAIL."""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
refint = dyadlib.load_guard("agent", "references")

RULE = """# Rule-{n}: t{n}

**Intent:** Do {n}.
**Target:** a thing{n}

## Boundaries (out of scope)
- Rule-{other} owns the rest.

## Conditions (triggers)
- `dyad/scripts/package.py check` runs; see `crafts/<craft>/projectors/project_<surface>.py`, `dyad/rules/`,
  `dyad/guards/infra/containment.py zones` and the craft rule `crafts/sysadmin/rules/x.md` (ledger #7).

## Provenance
Operator rule. Falsified; see `../falsification/rules/rule-{n}-x.md`.

Set: System Requirements.
"""
FRAME = "# frame\n@rules/RULE-1-x.md\n@rules/RULE-2-x.md\n\n@vocabulary/VOCABULARY.md\n@../preferences-corpus/PREFERENCES.md\n"
VOCAB = "| term | definition | owner | used by |\n|---|---|---|---|\n| thing | a thing | 1 | 1 2 |\n"
PREFS = "# prefs\n| key | value | allowed | read by |\n|---|---|---|---|\n| k | v | `a` \\| `b` | Rule-1 (x), Rule-2 |\n"
CHANGELOG = ("# Host change log (Rule-8)\n\n| date | d-work | class | action | undo | outcome |\n|---|---|---|---|---|---|\n"
             "| 2026-09-13 | #7 | reversible | H1, Operator-run: `bash workstation-corpus/ops/7-h1-x.sh` | rmdir | ok |\n"
             "| 2026-09-14 | #7 | reversible | H1 v2 (re-run): `bash workstation-corpus/ops/7-h1-x.sh` | as v1 | ok |\n"
             "| 2026-09-14 | #7 | reversible | run-book `start` through the runner | `stop` | ok; event: x-20260914T120000Z-start |\n")
INCIDENTS = ("# Incidents (Rule-3)\n\n| date | d-work | what | cause | consequence |\n|---|---|---|---|---|\n"
             "| 2026-09-12 | #1–#3 (pre-ledger) | w | c | q |\n| 2026-09-13 | #2-#3 | w | c | q |\n| 2026-09-14 | #7 | w | c | q |\n")
OPS = "#!/usr/bin/env bash\n# d-work: #7\n# class: reversible\n# undo: x\n# change-log: workstation-corpus/CHANGELOG.md row \"#7 H1\"\n# postcondition: p\n# destructive: none\nset -euo pipefail\n"
RECORD = "# record (ledger #{n})\n\n| # | Attack | Result | Survivor |\n|---|---|---|---|\n| 1 | a | Refuted | s |\n\nDisposition: see ledger #{n}.\n"
PACKAGE_PY = 'REGISTRY_FIELDS = ("surface", "craft", "module")\nPROJECTORS = {"erd": "crafts/sysarch/projectors/project_erd.py"}\n'   # discovered paths (#160)
RULES_TXT = "generated: *.pyc\ngenerated: projections/*\n"
RUNBOOK = "# x\n\n## Start\n```dyad-cmd\nname: start\nclass: reversible\nrole: any\nundo: stop\npostcondition: true\nscope: s\n\necho start\n```\n"
EVENTS = ('{"id": "x-20260914T120000Z-start", "ts": "2026-09-14T12:00:00Z", "role": "agent", "instance": "x", "name": "start", "cmd": "echo start", '
          '"class": "reversible", "scope": "s", "exit": 0, "duration_ms": 1, "postcondition": "ok", "output_sha256": "", "output_tail": "start", "commit": "abc", "runbook_sha256": ""}\n')

def git(root, *a):
    return subprocess.check_output(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=root, text=True).strip()

def fixture(rows=(1, 2, 3, 7), plans=True):
    """A git repo: package at dyad/ (2 Rules, frame, vocabulary, 2 records, registry, rules data),
    instance at agent-corpus/ (rows, plans at HEAD, incidents), preferences, change log, one ops script."""
    root = Path(tempfile.mkdtemp()); pkg = root / "dyad"; inst = root / "agent-corpus"
    (pkg / "rules").mkdir(parents=True)
    for n, other in ((1, 2), (2, 1)):
        (pkg / "rules" / f"RULE-{n}-x.md").write_text(RULE.format(n=n, other=other))
    (pkg / "CLAUDE.md").write_text(FRAME)
    (pkg / "vocabulary").mkdir(); (pkg / "vocabulary" / "VOCABULARY.md").write_text(VOCAB)
    (pkg / "scripts").mkdir(); (pkg / "scripts" / "package.py").write_text(PACKAGE_PY)
    (pkg / "scripts" / "package_rules.txt").write_text(RULES_TXT)
    (root / "crafts" / "sysarch" / "projectors").mkdir(parents=True); (root / "crafts" / "sysarch" / "projectors" / "project_erd.py").write_text("def main(): return 0\n")
    (pkg / "guards" / "infra").mkdir(parents=True); (pkg / "guards" / "infra" / "containment.py").write_text("ZONES = []\n")
    (root / "crafts" / "sysadmin" / "rules").mkdir(parents=True)
    (root / "crafts" / "sysadmin" / "rules" / "x.md").write_text("# x\n\nText moved by d-work #5 (historical; #177: world, not checked against rows).\n")   # a craft path a Rule names (#155); a craft Tended rule's own ledger citation (#177)
    for c in ("sysadmin", "sysarch"):
        (root / "crafts" / c / "VERSION").write_text("0.1.0\n")   # a craft is a tree with a VERSION (dyadlib.craft_dirs): these two are installed here (#167)
    (pkg / "falsification" / "rules").mkdir(parents=True)
    for n in (1, 2):
        (pkg / "falsification" / "rules" / f"rule-{n}-x.md").write_text(RECORD.format(n=n))
    (root / "preferences-corpus").mkdir(); (root / "preferences-corpus" / "PREFERENCES.md").write_text(PREFS)
    ws = root / "workstation-corpus"; (ws / "ops").mkdir(parents=True)
    (ws / "CHANGELOG.md").write_text(CHANGELOG); (ws / "ops" / "7-h1-x.sh").write_text(OPS)
    (ws / "runbooks" / "events").mkdir(parents=True)
    (ws / "runbooks" / "x.md").write_text(RUNBOOK); (ws / "runbooks" / "events" / "x.jsonl").write_text(EVENTS)
    rd = inst / "d-work" / "rows"; rd.mkdir(parents=True); (rd / "README.md").write_text("# rows\n")
    for r in rows:
        (rd / f"{r}.md").write_text(f"id: {r}\ntitle: r{r}\nopened: 2026-09-13\nstate: done\ndisposed: 2026-09-13 Y done; merge #99\nrefs: PR #98 #97; #1, children #2–#3; Rule-2\n")
    (inst / "audits").mkdir(); (inst / "audits" / "INCIDENTS.md").write_text(INCIDENTS)
    (inst / "falsification").mkdir(); (inst / "falsification" / "gap.md").write_text(RECORD.format(n=7))
    git(root, "init", "-q"); git(root, "add", "-A"); git(root, "commit", "-qm", "x")
    if plans:
        pd = inst / "d-work" / "plans"; pd.mkdir()
        (pd / "7.md").write_text(f"# Plan #7\n\nbase commit: {git(root, 'rev-parse', '--short', 'HEAD')} (main)\n")
        (pd / "2.md").write_text(f"# Plan #2\n\nBase commit of `main`: {git(root, 'rev-parse', 'HEAD')}.\n")
    return root, pkg, inst

def fail_kinds(msgs):
    return {m[5:].split(":")[0] for m in msgs if m.startswith("FAIL ")}

RESOLVABLE = {k for k, *_ , r in refint.REFERENCES if callable(r)}
# Kinds whose parser is a sysadmin-craft guard run only where that craft is installed (Rule-20 property 2 skips them
# elsewhere with one line each). The expected "ran" count and the sysadmin-kind tests derive from that (dyad-system #1).
SYSADMIN = all(m is not None for _, m in refint.GUARD_KINDS.values())
ABSENT_KINDS = {k for k, (_, m) in refint.GUARD_KINDS.items() if m is None}
RUNNABLE = RESOLVABLE - ABSENT_KINDS
needs_sysadmin = unittest.skipUnless(SYSADMIN, "the sysadmin craft's guards are not installed here; their kinds skip by design")

class Fixtured(unittest.TestCase):
    """A scratch corpus per test, with the `DYAD_*` locations off; holds no test of its own."""
    def setUp(self):
        self.root, self.pkg, self.inst = fixture()
        self.prev = {k: os.environ.pop(k, None) for k in ("DYAD_INSTANCE", "DYAD_OPS", "DYAD_RUNBOOKS")}
    def tearDown(self):
        for k, v in self.prev.items():
            if v is not None: os.environ[k] = v
        shutil.rmtree(self.root, ignore_errors=True)
    def check(self):
        return refint.check(self.root, self.pkg)
    def rewrite(self, p, old, new):
        p.write_text(p.read_text().replace(old, new))


class FixtureTests(Fixtured):
    def test_every_kind_resolves(self):
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), set(), msgs)
        self.assertEqual(k, len(RUNNABLE), "every resolvable kind ran (nothing skipped but an absent craft guard's)")
        self.assertEqual({m[5:].split(":")[0] for m in msgs if m.startswith("skip ")}, ABSENT_KINDS, msgs)
        self.assertGreaterEqual(n, 40)
        world = [m for m in msgs if m.startswith("warn ")]
        self.assertEqual({m[5:].split(":")[0] for m in world}, {k for k, *_, r in refint.REFERENCES if r == "world"})
        self.assertTrue(any("inference" in m for m in world))
        self.assertEqual(refint.check_package(self.root, self.pkg), [f"warning: {m}" for m in msgs])   # the runner's convention (no FAIL here)
        self.assertEqual((refint.ENTITY, refint.CORPUS, refint.TRANSACTION), ("reference", "agent", False)); self.assertEqual(len(refint.FIELDS), 5)

    def test_register_shape(self):
        kinds = [r[0] for r in refint.REFERENCES]
        self.assertEqual(len(kinds), 30); self.assertEqual(len(set(kinds)), 30, "one entry per kind")
        self.assertEqual(kinds[-3:], ["record.ledger->provenance", "craft_rule.text->provenance", "bundle.component->craft"])   # #177, #196 appended; order stable
        for kind, src, field, ext, tgt, res in refint.REFERENCES:
            self.assertRegex(kind, r"^[a-z_]+\.[a-z_#]+->[a-z]+$")
            self.assertTrue(callable(res) or res == "world" or res.startswith("guard:"), kind)
            if isinstance(res, str) and res.startswith("guard:"):
                self.assertTrue((dyadlib.PKG / "guards" / res[6:]).exists(), f"{kind}: {res} names no guard module")
            self.assertTrue(ext is None or callable(ext), kind)
            self.assertTrue(callable(ext) or not callable(res), f"{kind}: a resolvable kind needs an extractor")
        self.assertEqual(len(RESOLVABLE), 18)   # rule.text->row and record.ledger->row moved to `world` by source (#177); provenance.id->row (#164) unaffected

    # one broken reference per resolvable kind, failing under its own kind name only
    def broken(self, mutate, kind):
        mutate()
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), {kind}, msgs)
    def row(self, r): return self.inst / "d-work" / "rows" / f"{r}.md"
    def test_row_refs_row(self):
        self.broken(lambda: self.rewrite(self.row(7), "#1,", "#42,"), "row.refs->row")
    def test_row_refs_rule(self):
        self.broken(lambda: self.rewrite(self.row(7), "Rule-2", "Rule-9"), "row.refs->rule")
    def test_plan_id_row(self):
        self.broken(lambda: (self.inst / "d-work" / "plans" / "8.md").write_text("# Plan #8\n"), "plan.id->row")
    def test_plan_base_commit(self):
        self.broken(lambda: self.rewrite(self.inst / "d-work" / "plans" / "7.md", "base commit: ", "base commit: deadbeef0"), "plan.base->commit")
    def test_rule_text_rule(self):
        self.broken(lambda: self.rewrite(self.pkg / "rules" / "RULE-1-x.md", "Rule-2 owns", "Rule-7 owns"), "rule.text->rule")
    def test_rule_text_row_is_world_never_fails(self):
        # #177: a package Rule's own `ledger #N` citation is historical provenance of the
        # authoring instance, not a reference a receiving instance can resolve — world, not row_exists.
        # A citation of a *non-existent* row (a typo, or simply "not this instance's ledger")
        # must never fail the guard, whether or not the number happens to exist.
        self.rewrite(self.pkg / "rules" / "RULE-1-x.md", "(ledger #7)", "(ledger #70)")
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), set(), msgs)
        self.assertIn("warn rule.text->row: 2 reference(s) to row; unresolvable (The World), inference", msgs)
    def test_record_ledger_package_and_craft_records_are_world_never_fail(self):
        # #177: a Rule's own falsification record — package (`dyad/falsification/rules/`) or a
        # Tended craft's (`crafts/*/falsification/rules/`) — is historical provenance too; a bad
        # citation there must never fail, unlike an instance record's own (test_record_ledger).
        self.rewrite(self.pkg / "falsification" / "rules" / "rule-2-x.md", "ledger #2", "ledger #200")
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), set(), msgs)
        self.assertIn("warn record.ledger->provenance: 4 reference(s) to row; unresolvable (The World), inference", msgs)
    def test_record_ledger_instance_vs_package_split_by_source_path(self):
        # the two kinds partition the same `ledger #` field by the citing file's own path, never by
        # whether the number happens to exist (attack 2, plan #177: quoting content never reclassifies)
        c = refint.Corpus(self.root, self.pkg)
        self.assertEqual({t for _, t in refint.record_ledger(c)}, {"7"})            # instance only: agent-corpus/falsification/gap.md
        self.assertEqual({t for _, t in refint.record_ledger_world(c)}, {"1", "2"})  # package only: dyad/falsification/rules/*.md
    def test_craft_rule_text_provenance_is_world_never_fails(self):
        # #177: a Tended craft rule's own text (`crafts/*/rules/*.md`) cites ledger numbers too
        # (e.g. real `crafts/sysadmin/rules/host-mutation.md`: "d-work #155") and is package-shipped
        # with that craft; previously unscanned by any kind, now correctly world, never failing.
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), set(), msgs)
        self.assertIn("warn craft_rule.text->provenance: 1 reference(s) to row; unresolvable (The World), inference", msgs)
        c = refint.Corpus(self.root, self.pkg)
        self.assertEqual(refint.craft_rule_ledger(c), [("crafts/sysadmin/rules/x.md", "5")])
    def test_rule_provenance_record(self):
        self.broken(lambda: (self.pkg / "falsification" / "rules" / "rule-2-x.md").unlink(), "rule.provenance->record")
    def test_rule_text_path(self):
        self.broken(lambda: self.rewrite(self.pkg / "rules" / "RULE-2-x.md", "`dyad/rules/`", "`dyad/nope/`"), "rule.text->path")
    def test_rule_text_craft_path(self):
        # #155: kind 11 resolves `crafts/…` paths too — a kernel cites "the active craft's <rule> rule" by path
        self.assertIn(("dyad/rules/RULE-1-x.md", "crafts/sysadmin/rules/x.md"), refint.package_paths(refint.Corpus(self.root, self.pkg)))
        self.broken(lambda: (self.root / "crafts" / "sysadmin" / "rules" / "x.md").unlink(), "rule.text->path")
    def test_core_only_install_skips_craft_paths(self):
        # property 4: a Rule naming `crafts/…` resolves nothing on an install with no crafts/ tree — one skip line, no FAIL
        shutil.rmtree(self.root / "crafts")
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), set(), msgs); self.assertTrue(any(m.startswith("skip rule.text->path: `crafts/…` tokens") for m in msgs))
        self.assertEqual(k, len(RUNNABLE), "the kind still ran for its dyad/ tokens")
    @needs_sysadmin
    def test_absent_craft_guard_skips_its_kinds(self):
        # #155 attack 6: a kind whose parser is a craft guard no installed craft provides skips with a line, never fails
        saved = dict(refint.GUARD_KINDS)
        try:
            for kind, (ent, _) in saved.items(): refint.GUARD_KINDS[kind] = (ent, None)
            n, k, msgs = self.check()
            self.assertEqual(fail_kinds(msgs), set(), msgs)
            skipped = {m[5:].split(":")[0] for m in msgs if m.startswith("skip ")}
            self.assertEqual(skipped, set(saved)); self.assertTrue(any("guard sysadmin/ops_scripts absent" in m for m in msgs))
            self.assertEqual(k, len(RESOLVABLE) - len(saved))
        finally:
            refint.GUARD_KINDS.update(saved)
        self.assertEqual(set(refint.GUARD_KINDS), {"changelog.action->ops", "ops.dwork->row", "ops.changelog->changelog", "event.command->command", "changelog.event->event"})
        self.assertTrue(all(m is not None for _, m in refint.GUARD_KINDS.values()), "the live repo has the sysadmin craft")
    def test_rule_text_glob_needs_a_match(self):
        self.broken(lambda: self.rewrite(self.pkg / "rules" / "RULE-2-x.md", "project_<surface>.py", "render_<surface>.py"), "rule.text->path")
    def test_rule_text_command_word_cut(self):
        # `dyad/scripts/containment.py zones` resolves to the file; the trailing word is never a path
        self.assertIn(("dyad/rules/RULE-1-x.md", "dyad/guards/infra/containment.py"), refint.package_paths(refint.Corpus(self.root, self.pkg)))
    def test_generated_path_accepted(self):
        self.rewrite(self.pkg / "rules" / "RULE-2-x.md", "`dyad/rules/`", "`dyad/x/projections/out.html`")
        self.assertEqual(fail_kinds(self.check()[2]), set())
    def test_frame_kinds_are_the_frame_guards(self):
        by = {k: r for k, *_, r in refint.REFERENCES}
        self.assertEqual(by["frame.import->rule"], "guard:agent/frame.py"); self.assertEqual(by["frame.import->file"], "guard:agent/frame.py")
        self.rewrite(self.pkg / "CLAUDE.md", "@rules/RULE-2-x.md\n", "")
        self.assertEqual(fail_kinds(self.check()[2]), set(), "listed, not re-checked here (the frame guard fails it)")
    def test_preference_read_by(self):
        self.broken(lambda: self.rewrite(self.root / "preferences-corpus" / "PREFERENCES.md", "Rule-2 |", "Rule-5 |"), "preference.read_by->rule")
    def test_changelog_dwork(self):
        self.broken(lambda: self.rewrite(self.root / "workstation-corpus" / "CHANGELOG.md", "| 2026-09-14 | #7 |", "| 2026-09-14 | #8 |"), "changelog.dwork->row")
    @needs_sysadmin
    def test_changelog_action_ops(self):
        self.broken(lambda: self.rewrite(self.root / "workstation-corpus" / "CHANGELOG.md", "ops/7-h1-x.sh` | as v1", "ops/7-h2-x.sh` | as v1"), "changelog.action->ops")
    def test_incident_dwork_range(self):
        self.broken(lambda: self.rewrite(self.inst / "audits" / "INCIDENTS.md", "#2-#3", "#2-#4"), "incident.dwork->row")
    def test_incident_pre_ledger_segment_is_not_a_reference(self):
        self.assertEqual(refint.hash_ids("#1–#3 (pre-ledger)"), [])
        self.assertEqual(refint.hash_ids("#2–#4, #9; PR #1 #5; was #6"), ["2", "3", "4", "9", "6"])
        self.assertEqual(refint.hash_ids("PRs #61 #62"), [])
    @needs_sysadmin
    def test_ops_dwork(self):
        self.broken(lambda: self.rewrite(self.root / "workstation-corpus" / "ops" / "7-h1-x.sh", "# d-work: #7", "# d-work: #77"), "ops.dwork->row")
    @needs_sysadmin
    def test_ops_changelog_key(self):
        self.broken(lambda: self.rewrite(self.root / "workstation-corpus" / "ops" / "7-h1-x.sh", '"#7 H1"', '"#7 H3"'), "ops.changelog->changelog")
    def test_ops_changelog_key_matches_first_row_of_a_rerun(self):
        # v1 and v2 rows share the key `#7 H1`; the key resolves while at least one remains
        self.rewrite(self.root / "workstation-corpus" / "CHANGELOG.md", "| 2026-09-13 | #7 | reversible | H1, Operator-run", "| 2026-09-13 | #7 | reversible | H9, Operator-run")
        self.assertEqual(fail_kinds(self.check()[2]), set())
    def test_record_ledger(self):
        self.broken(lambda: self.rewrite(self.inst / "falsification" / "gap.md", "Disposition: see ledger #7", "Disposition: see ledger #71"), "record.ledger->row")
    @needs_sysadmin
    def test_event_command(self):
        self.broken(lambda: self.rewrite(self.root / "workstation-corpus" / "runbooks" / "events" / "x.jsonl", '"name": "start"', '"name": "launch"'), "event.command->command")
    @needs_sysadmin
    def test_event_command_needs_the_instance_runbook(self):
        self.broken(lambda: (self.root / "workstation-corpus" / "runbooks" / "x.md").rename(self.root / "workstation-corpus" / "runbooks" / "y.md"), "event.command->command")
    @needs_sysadmin
    def test_changelog_event(self):
        self.broken(lambda: self.rewrite(self.root / "workstation-corpus" / "CHANGELOG.md", "event: x-20260914T120000Z-start", "event: x-20260914T120001Z-start"), "changelog.event->event")
    def test_changelog_event_token_forms(self):
        self.assertEqual(refint._EVENT.findall("ok; event: `x-1-a`, and event: y-2-b"), ["x-1-a", "y-2-b"])
        self.assertEqual(refint._EVENT.findall("a ratification event: none"), ["none"])   # a word after `event:` is a token; the resolver decides
    def test_rules_components_read_beside_the_manifest_guard(self):
        (self.pkg / "guards" / "infra" / "manifest_rules.txt").write_text("Python: python3\n")
        self.assertEqual(refint.rules_components(refint.Corpus(self.root, self.pkg)), [("dyad/guards/infra/manifest_rules.txt", "Python")])
    def test_registry_module(self):
        self.broken(lambda: self.rewrite(self.pkg / "scripts" / "package.py", 'project_erd.py', 'project_nope.py'), "registry.module->file")
    def test_failure_names_file_field_and_token(self):
        self.rewrite(self.row(7), "#1,", "#42,")
        fails = [m for m in self.check()[2] if m.startswith("FAIL ")]
        self.assertEqual(fails, ["FAIL row.refs->row: agent-corpus/d-work/rows/7.md refs -> 42 does not resolve"])

CRAFT_REGISTRY = "# Craft registry (fixture)\n\n| craft | version | source | sha256 | d-work |\n|---|---|---|---|---|\n"

def craft_registry(*names):
    """`crafts/REGISTRY.md` as `craft.registry_rows` parses it (the installing CLI's format, #156)."""
    return CRAFT_REGISTRY + "".join(f"| {n} | 0.1.0 | src | {'a' * 64} | #7 |\n" for n in names)


class CraftPresenceTests(Fixtured):
    """#167: a `crafts/<name>/…` citation resolves against the *craft*, not the whole tree. An install
    holding some crafts and not others (core+sysadmin, the shape #156 built and #162 hit) must not fail
    on a Rule's citation of a craft it does not have; a name neither a tree nor a registry row claims is
    still stated, so a typo is never skipped forever."""
    def cite(self, *tokens):
        """Rule-1 of the fixture cites these paths in place of its craft citation."""
        self.rewrite(self.pkg / "rules" / "RULE-1-x.md", "`crafts/sysadmin/rules/x.md`", ", ".join(f"`{t}`" for t in tokens))
    def lines(self, prefix, msgs):
        return [m for m in msgs if m.startswith(f"{prefix} rule.text->path")]
    def registry(self, *names):
        (self.root / "crafts" / "REGISTRY.md").write_text(craft_registry(*names))

    def test_craft_token_classifier(self):
        self.assertEqual(refint.craft_token("crafts/sysadmin/rules/x.md"), ("craft", "sysadmin"))
        self.assertEqual(refint.craft_token("crafts/sysadmin"), ("craft", "sysadmin"))
        self.assertEqual(refint.craft_token("crafts/REGISTRY.md"), ("registry", None))
        for t in ("crafts/<craft>/VERSION", "crafts/*/rules/", "crafts/*", "crafts/", "crafts/x.txt"):
            self.assertEqual(refint.craft_token(t), (None, None), t)   # a glob or a placeholder keeps the ordinary path resolution

    def test_craft_set_is_derived_from_craft_dirs(self):
        c = refint.Corpus(self.root, self.pkg)
        self.assertEqual(c.installed_crafts, {p.name for p in dyadlib.craft_dirs(self.pkg)})
        self.assertEqual(c.craft_registry, None, "no crafts/REGISTRY.md on this install")
        (self.root / "crafts" / "sysarch" / "VERSION").unlink()        # a tree without a VERSION is not a craft
        self.assertEqual(refint.Corpus(self.root, self.pkg).installed_crafts, {"sysadmin"})
        self.registry("sysadmin")
        self.assertEqual(refint.Corpus(self.root, self.pkg).craft_registry, {"sysadmin"})

    def test_absent_craft_skips_once_per_craft(self):
        # core+sysadmin: a Rule cites a craft this install has not got, twice, and no registry judges the name
        self.cite("crafts/syseng/rules/a.md", "crafts/syseng/rules/b.md", "crafts/sysadmin/rules/x.md")
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), set(), msgs)
        self.assertEqual([m for m in self.lines("skip", msgs) if "craft guard" not in m and "absent (no installed craft" not in m], ["skip rule.text->path: craft syseng absent (Rule-20 property 4); 2 token(s) unresolved here"])
        self.assertEqual(k, len(RUNNABLE), "the kind still ran for every other token")

    def test_one_line_per_craft_not_per_token(self):
        self.cite("crafts/syseng/rules/a.md", "crafts/sysdoc/rules/b.md", "crafts/syseng/rules/c.md")
        msgs = self.check()[2]
        self.assertEqual(fail_kinds(msgs), set(), msgs)
        self.assertEqual(self.lines("skip", msgs),
                         ["skip rule.text->path: craft syseng absent (Rule-20 property 4); 2 token(s) unresolved here",
                          "skip rule.text->path: craft sysdoc absent (Rule-20 property 4); 1 token(s) unresolved here"])

    def test_unknown_craft_warns_when_the_registry_has_no_row(self):
        # the typo attack: `sysadmn` is no craft here and no registry row claims it — warned, never silent
        self.cite("crafts/sysadmn/rules/x.md")
        self.registry("sysadmin")
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), set(), msgs)
        self.assertEqual(self.lines("warn", msgs),
                         ["warn rule.text->path: craft sysadmn absent and not in crafts/REGISTRY.md (unknown craft: never installed here, or a typo); 1 token(s) unresolved here"])
        self.assertTrue(all(m.startswith("warning: ") for m in refint.check_package(self.root, self.pkg)), "a warn never fails the runner")

    def test_registry_row_without_a_tree_fails(self):
        # installed-then-deleted: the registry says the craft is here and it is not
        self.cite("crafts/syseng/rules/a.md")
        self.registry("sysadmin", "syseng")
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), {"rule.text->path"})
        self.assertEqual([m for m in msgs if m.startswith("FAIL ")],
                         ["FAIL rule.text->path: dyad/rules/RULE-1-x.md -> crafts/syseng/rules/a.md does not resolve "
                          "(craft syseng is installed per crafts/REGISTRY.md and crafts/syseng/ is missing)"])

    def test_bad_path_inside_an_installed_craft_still_fails(self):
        # core+all: presence of the craft is what makes its paths checkable, registry or not
        self.registry("sysadmin", "sysarch")
        (self.root / "crafts" / "sysadmin" / "rules" / "x.md").unlink()
        self.assertEqual(fail_kinds(self.check()[2]), {"rule.text->path"})

    def test_registry_token_skips_when_absent_and_resolves_when_present(self):
        self.cite("crafts/REGISTRY.md")
        n, k, msgs = self.check()
        self.assertEqual(fail_kinds(msgs), set(), msgs)
        self.assertEqual(self.lines("skip", msgs), ["skip rule.text->path: crafts/REGISTRY.md absent (no craft installed here); 1 token(s) unresolved here"])
        self.registry("sysadmin")
        n2, k2, msgs2 = self.check()
        self.assertEqual(fail_kinds(msgs2), set(), msgs2); self.assertEqual(self.lines("skip", msgs2), [])
        self.assertEqual(n2, n + 1, "the registry token counts as a resolved reference once the file is there")

    def test_core_only_install_prints_the_tree_line_only(self):
        self.cite("crafts/syseng/rules/a.md")
        shutil.rmtree(self.root / "crafts")
        msgs = self.check()[2]
        self.assertEqual(fail_kinds(msgs), set(), msgs)
        self.assertEqual(self.lines("skip", msgs), ["skip rule.text->path: `crafts/…` tokens; no crafts/ tree is installed (a core-only install)"])


class ScratchInstallTests(unittest.TestCase):
    """Property 4: a package-only install (rows/ holding README only, no plans, empty templates)
    skips the row-target kinds with a line and fails nothing — the Rule-11 p5 CI path."""
    def test_empty_store_skips(self):
        root, pkg, inst = fixture(rows=(), plans=False)
        try:
            (root / "workstation-corpus" / "CHANGELOG.md").write_text(CHANGELOG.splitlines()[0] + "\n\n| date | d-work | class | action | undo | outcome |\n|---|---|---|---|---|---|\n")
            (inst / "audits" / "INCIDENTS.md").write_text("# Incidents (Rule-3)\n\n| date | d-work | what | cause | consequence |\n|---|---|---|---|---|\n")
            (root / "workstation-corpus" / "runbooks" / "events" / "x.jsonl").unlink(); (root / "workstation-corpus" / "runbooks" / "x.md").unlink()
            prev = {k: os.environ.pop(k, None) for k in ("DYAD_INSTANCE", "DYAD_OPS", "DYAD_RUNBOOKS")}
            try:
                n, k, msgs = refint.check(root, pkg)
            finally:
                for kk, v in prev.items():
                    if v is not None: os.environ[kk] = v
            self.assertEqual(fail_kinds(msgs), set(), msgs)
            skipped = {m[5:].split(":")[0] for m in msgs if m.startswith("skip ")}
            self.assertEqual(skipped, {kind for kind, *_, tgt, r in refint.REFERENCES if callable(r) and tgt in ("row", "changelog", "command", "event")} | ABSENT_KINDS)
            self.assertTrue(any("row store is empty or absent" in m for m in msgs))
            self.assertEqual(k, len(RESOLVABLE) - len(skipped))
        finally:
            shutil.rmtree(root, ignore_errors=True)

class LiveTests(unittest.TestCase):
    def test_live_repo_resolves(self):
        root = dyadlib.repo_root()
        n, k, msgs = refint.check(root, dyadlib.PKG)
        self.assertEqual([m for m in msgs if m.startswith("FAIL ")], [])
        skipped = [m for m in msgs if m.startswith("skip ")]   # an empty event store (before the first run) skips its kinds
        self.assertGreaterEqual(n, 300); self.assertEqual(k, len(RESOLVABLE) - len(skipped))
    def test_main_prints_ok_line(self):
        r = subprocess.run([sys.executable, str(Path(refint.__file__))], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(r.stdout.strip().splitlines()[-1], r"^ok   \[rule-20\] \d+ references, \d+ kinds resolve$")
        self.assertIn("warn [rule-20] row.disposed->pr", r.stdout)


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(refint, "core", refint.CORPUS)
        self.assertEqual(dyadlib.check_invariants(refint, extra), len(refint.INVARIANTS) + 4)
        names = [n for n, _ in refint.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
