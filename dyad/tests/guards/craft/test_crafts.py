"""Craft guard tests (dyad/guards/craft/crafts.py, Rule-11's craft shape; #156): a fixture craft passes; missing or
invalid VERSION fails; a host string fails; `events/x.jsonl` inside fails; a `REGISTRY.md` inside fails; a CRAFT.md
term equal to an Agent term fails; `the Agent` in a rule warns and does not fail; a guard lacking check_package
fails; unmet `requires` warns; `seeds:` (#180) — a mismatched destination zone fails, a missing template fails, a
collision between two crafts warns, `seed_status` warns only when the destination is absent and never writes; the
live sysadmin craft passes; the contract and CLI line."""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
cg = dyadlib.load_guard("craft", "crafts")
PKG = dyadlib.PKG

GUARD = 'ENTITY, CORPUS, TRANSACTION = "widget", "workstation", False\nFIELDS = ("a",)\ndef check_package(root): return []\n'
CRAFT = {"VERSION": "0.1.0\n", "rules/r.md": "# r\n\nThe operator keeps the widget.\n", "rules/README.md": "the Agent reads every file here\n",
         "vocabulary/CRAFT.md": "# v\n\n| term | definition | rule |\n|---|---|---|\n| widget | a thing | r |\n",
         "templates/CHANGELOG.md": "# Host change log\n", "guards/w.py": GUARD, "docs/d.md": "# d\n", "falsification/rules/r.md": "# rec\n"}

def fixture(name="fx", files=CRAFT) -> Path:
    r = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q", str(r)], check=True)
    for rel, text in files.items():
        f = r / "crafts" / name / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
    return r

def check(r: Path, name="fx"):
    return cg.check_craft(r, r / "crafts" / name, PKG)

HOME = "/ho" + "me/pt"; MARK = "/ho" + "me/"   # a package_rules.txt marker, assembled so this file carries none (Rule-11 p1)

def fails(msgs): return [m for m in msgs if not m.startswith("warning:")]
def warns(msgs): return [m for m in msgs if m.startswith("warning:")]

class CraftGuardTests(unittest.TestCase):
    def setUp(self): self.r = fixture()
    def tearDown(self): shutil.rmtree(self.r, ignore_errors=True)
    def craft(self): return self.r / "crafts" / "fx"
    def test_contract(self):
        self.assertEqual((cg.ENTITY, cg.CORPUS, cg.TRANSACTION), ("craft", "craft", False))
        self.assertEqual(cg.FIELDS, ("name", "version", "rules", "vocabulary", "templates", "guards", "docs", "falsification", "requires", "seeds"))
        self.assertIsNone(dyadlib.contract_problem(cg, "core", "craft")); self.assertTrue(callable(cg.describe))
        self.assertEqual([f[0] for f in cg.describe(self.r)["fields"]], list(cg.FIELDS))
    def test_fixture_passes(self):
        self.assertEqual(fails(check(self.r)), []); self.assertEqual(warns(check(self.r)), [])   # README exempt from the token scan
        self.assertEqual(cg.parse(self.craft()), {"name": "fx", "version": "0.1.0", "rules": True, "vocabulary": True, "templates": True, "guards": True, "docs": True, "falsification": True, "requires": "", "seeds": ""})
    def test_version_missing_or_invalid(self):
        (self.craft() / "VERSION").unlink(); self.assertIn("crafts/fx/VERSION: missing", fails(check(self.r)))
        (self.craft() / "VERSION").write_text("v1\n"); self.assertTrue(any("not one MAJOR.MINOR.PATCH" in f for f in fails(check(self.r))))
        (self.craft() / "VERSION").write_text("1.0.0\n2.0.0\n"); self.assertTrue(any("not one MAJOR.MINOR.PATCH" in f for f in fails(check(self.r))))
    def test_host_string_fails(self):
        (self.craft() / "docs/d.md").write_text(f"backups live in {HOME}/b\n")
        self.assertTrue(any(f"docs/d.md: host-specific string '{MARK}' inside a craft" in f for f in fails(check(self.r))), check(self.r))
    def test_instance_state_inside_fails(self):
        (self.craft() / "events").mkdir(); (self.craft() / "events/x.jsonl").write_text("{}\n")
        (self.craft() / "REGISTRY.md").write_text("| craft |\n")
        f = fails(check(self.r))
        self.assertTrue(any("events/x.jsonl" in m for m in f), f); self.assertTrue(any("REGISTRY.md: instance artifact by name 'REGISTRY.md'" in m for m in f), f)
        self.assertFalse(any("templates/CHANGELOG.md" in m for m in f), f)   # a seed is not instance state
    def test_term_equal_to_agent_term_fails(self):
        (self.craft() / "vocabulary/CRAFT.md").write_text("| term | definition | rule |\n|---|---|---|\n| Plan | mine | r |\n")
        f = fails(check(self.r)); self.assertTrue(any("'Plan': equals the Agent vocabulary term 'plan'" in m for m in f), f)
    def test_vocabulary_shape(self):
        (self.craft() / "vocabulary/CRAFT.md").write_text("| term | definition | rule |\n|---|---|---|\n| widget | a thing | r |\n| widget | again | r |\n| gadget | x | nope |\n| bare | | r |\n")
        f = fails(check(self.r))
        self.assertTrue(any("'widget': defined twice" in m for m in f), f); self.assertTrue(any("'gadget': rule 'nope' is not crafts/fx/rules/nope.md" in m for m in f), f)
        self.assertTrue(any("'bare': malformed row" in m for m in f), f)
        (self.craft() / "vocabulary/CRAFT.md").unlink(); self.assertIn("crafts/fx: no vocabulary/CRAFT.md", fails(check(self.r)))
    def test_agent_token_in_rule_warns_not_fails(self):
        (self.craft() / "rules/r.md").write_text("# r\n\nBefore this the Agent asks `Y/N:` for the ratification.\n")
        msgs = check(self.r)
        self.assertEqual(fails(msgs), []); self.assertEqual(len(warns(msgs)), 1)
        self.assertIn("crafts/fx/rules/r.md: mentions 'the Agent', 'Y/N:', 'ratif' — binds the Agent's process? (Rule-4 guard: inference decides)", warns(msgs)[0])
    def test_guard_lacking_contract_fails(self):
        (self.craft() / "guards/bad.py").write_text("ENTITY = 'b'\n")
        (self.craft() / "guards/zone.py").write_text(GUARD.replace('"workstation"', '"nowhere"'))
        (self.craft() / "guards/broken.py").write_text("raise RuntimeError('boom')\n")
        f = fails(check(self.r))
        self.assertTrue(any("guards/bad.py: lacks CORPUS, FIELDS, TRANSACTION, check_package (guard contract, crafts/sysarch/rules/guards.md)" in m for m in f), f)
        self.assertTrue(any("guards/zone.py: declares CORPUS 'nowhere', not a zone" in m for m in f), f)
        self.assertTrue(any("guards/broken.py: does not load: boom" in m for m in f), f)
    def test_requires_warns_at_check(self):
        (self.craft() / "MANIFEST.md").write_text("name: fx\nrequires: syseng>=0.2.0 dyad-operator>=0.1.0\n")
        msgs = check(self.r)
        self.assertEqual(fails(msgs), [])
        self.assertIn("warning: crafts/fx: requires syseng>=0.2.0: not installed (checked at install)", msgs)
        self.assertIn("warning: crafts/fx: requires dyad-operator>=0.1.0: not installed (checked at install)", msgs)   # no dyad/ in the fixture repo
        self.assertEqual(cg.requires(self.craft()), [("syseng", "0.2.0"), ("dyad-operator", "0.1.0")])
        (self.r / "crafts/syseng").mkdir(); (self.r / "crafts/syseng/VERSION").write_text("0.1.0\n")
        self.assertEqual(cg.unmet(self.r, self.craft()), ["requires syseng>=0.2.0: found 0.1.0", "requires dyad-operator>=0.1.0: not installed"])
        (self.r / "crafts/syseng/VERSION").write_text("0.2.0\n"); (self.r / "dyad").mkdir(); (self.r / "dyad/VERSION").write_text("0.1.0\n")
        self.assertEqual(cg.unmet(self.r, self.craft()), [])
    def test_seeds_zone_and_template_checks(self):
        self.assertEqual(cg.seeds(self.craft()), [])   # no MANIFEST.md yet
        (self.craft() / "MANIFEST.md").write_text("name: fx\nseeds: CHANGELOG.md->workstation-corpus/CHANGELOG.md\n")
        self.assertEqual(cg.seeds(self.craft()), [("CHANGELOG.md", "workstation-corpus/CHANGELOG.md")])
        self.assertEqual(fails(check(self.r)), [])   # templates/CHANGELOG.md ships in the fixture; workstation matches the fixture guard's CORPUS
        (self.craft() / "templates/CHANGELOG.md").unlink()
        f = fails(check(self.r))
        self.assertIn("crafts/fx/MANIFEST.md: seeds 'CHANGELOG.md->workstation-corpus/CHANGELOG.md': no templates/CHANGELOG.md", f)
        (self.craft() / "templates/CHANGELOG.md").write_text("# Host change log\n")   # restore
        (self.craft() / "MANIFEST.md").write_text("name: fx\nseeds: CHANGELOG.md->agent-corpus/d-work/rows/README.md\n")
        f = fails(check(self.r))
        self.assertTrue(any("destination zone 'agent' is not one this craft's own guards claim as CORPUS (workstation)" in m for m in f), f)
    def test_seeds_host_token_resolves_per_repo(self):
        """#175: `<host>` in a seed destination is the receiving repo's host path; under `host-zone:
        infra` the destination classifies `infra` and the logical corpus `workstation` still claims it."""
        prev = {k: os.environ.pop(k, None) for k in ("DYAD_HOST", "DYAD_HOST_ZONE")}
        try:
            (self.craft() / "MANIFEST.md").write_text("name: fx\nseeds: CHANGELOG.md-><host>/CHANGELOG.md\n")
            self.assertEqual(cg.seeds(self.craft(), self.r), [("CHANGELOG.md", "workstation-corpus/CHANGELOG.md")])
            self.assertEqual(fails(check(self.r)), [])
            os.environ["DYAD_HOST"], os.environ["DYAD_HOST_ZONE"] = "infrastructure", "infra"
            self.assertEqual(cg.seeds(self.craft(), self.r), [("CHANGELOG.md", "infrastructure/CHANGELOG.md")])
            self.assertEqual(fails(check(self.r)), [])   # the guard's CORPUS `workstation` resolves to the infra host zone
            self.assertEqual(cg.seed_status(self.r, self.craft()), [
                "warning: crafts/fx: seed 'CHANGELOG.md' not copied to infrastructure/CHANGELOG.md — copy it by hand: cp crafts/fx/templates/CHANGELOG.md infrastructure/CHANGELOG.md"])
        finally:
            for k, v in prev.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v
    def test_seed_status_warns_only_when_absent_and_never_writes(self):
        (self.craft() / "MANIFEST.md").write_text("name: fx\nseeds: CHANGELOG.md->workstation-corpus/CHANGELOG.md\n")
        self.assertEqual(cg.seed_status(self.r, self.craft()),
            ["warning: crafts/fx: seed 'CHANGELOG.md' not copied to workstation-corpus/CHANGELOG.md — copy it by hand: cp crafts/fx/templates/CHANGELOG.md workstation-corpus/CHANGELOG.md"])
        self.assertFalse((self.r / "workstation-corpus").exists())   # never written
        (self.r / "workstation-corpus").mkdir(); (self.r / "workstation-corpus/CHANGELOG.md").write_text("# Host change log\n")
        self.assertEqual(cg.seed_status(self.r, self.craft()), [])
    def test_seed_destination_collision_between_crafts_warns(self):
        (self.craft() / "MANIFEST.md").write_text("name: fx\nseeds: CHANGELOG.md->workstation-corpus/CHANGELOG.md\n")
        d = self.r / "crafts/gy"; shutil.copytree(self.craft(), d)
        (d / "MANIFEST.md").write_text("name: gy\nseeds: CHANGELOG.md->workstation-corpus/CHANGELOG.md\n")
        msgs = cg.check_package(self.r)
        self.assertEqual(fails(msgs), [])
        self.assertTrue(any("seed destination(s) also declared by crafts/gy (workstation-corpus/CHANGELOG.md)" in m for m in warns(msgs)), msgs)
    def test_manifest_name_must_match(self):
        (self.craft() / "MANIFEST.md").write_text("name: other\n")
        self.assertTrue(any("MANIFEST.md: name 'other' is not the directory name 'fx'" in m for m in fails(check(self.r))))
    def test_shared_word_between_crafts_warns(self):
        d = self.r / "crafts/gy"; shutil.copytree(self.craft(), d)
        msgs = cg.check_package(self.r)
        self.assertEqual(fails(msgs), []); self.assertTrue(any("terms also defined by crafts/gy (widget)" in m for m in warns(msgs)), msgs)
    def test_check_package_over_repo_and_summary(self):
        self.assertEqual(fails(cg.check_package(self.r)), []); self.assertEqual(cg.summary(self.r), "1 craft(s)")
        self.assertEqual(cg.check_package(Path(tempfile.mkdtemp())), [])   # no crafts/: nothing to check (a core-only install)
    def test_live_sysadmin_craft_passes(self):
        root = dyadlib.repo_root()
        if not (root / "crafts" / "sysadmin").is_dir(): self.skipTest("no sysadmin craft here")
        msgs = cg.check_craft(root, root / "crafts" / "sysadmin", PKG)
        self.assertEqual(fails(msgs), [], msgs)
        self.assertEqual(cg.seeds(root / "crafts" / "sysadmin", root), [("CHANGELOG.md", "workstation-corpus/CHANGELOG.md")])   # `<host>` resolved to this repo's host path (#175)
        self.assertEqual(cg.seed_status(root, root / "crafts" / "sysadmin"), [
            "warning: crafts/sysadmin: seed 'CHANGELOG.md' not copied to workstation-corpus/CHANGELOG.md — "
            "copy it by hand: cp crafts/sysadmin/templates/CHANGELOG.md workstation-corpus/CHANGELOG.md"])
        # this instance authors sysadmin but tends no host of its own (d-work #58): no workstation-corpus/, so never seeded here
    def test_cli_line(self):
        r = subprocess.run([sys.executable, str(PKG / "guards" / "craft" / "crafts.py")], capture_output=True, text=True, cwd=dyadlib.repo_root())
        self.assertEqual(r.returncode, 0, r.stderr); self.assertTrue(any(l.startswith("ok   [craft] crafts/") for l in r.stdout.splitlines()) or "crafts/" not in r.stdout)
        r = subprocess.run([sys.executable, str(PKG / "guards" / "craft" / "crafts.py"), "no-such"], capture_output=True, text=True, cwd=dyadlib.repo_root())
        self.assertEqual(r.returncode, 2)


GUARD_W = ('ENTITY, CORPUS, TRANSACTION = "widget", "workstation", False\n'
           'FIELDS = ("a",)\n'
           'def check_package(root): return []\n'
           'import dyadlib\n'
           'INVARIANTS = [("widget-exists", lambda: getattr(dyadlib, "WIDGET", False))]\n')

# The real craft-file pattern (every guard/projector in this repo): its own `sys.path.insert(0, ...)`
# to its *real, on-disk* dyad/scripts -- here, this fixture's own live one, exactly the shape that
# defeated an earlier version of the floor check (D3-style path games override a plain sys.path
# insertion done first; only pre-seeding sys.modules survives it).
GUARD_W_SELF_PATH = (
    'import sys\nfrom pathlib import Path\n'
    'sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))\n'
    'import dyadlib\n'
    'ENTITY, CORPUS, TRANSACTION = "widget3", "workstation", False\nFIELDS = ("a",)\n'
    'def check_package(root): return []\n'
    'INVARIANTS = [("widget-exists", lambda: getattr(dyadlib, "WIDGET", False))]\n'
)


class FloorTests(unittest.TestCase):
    """D1 (#100): a craft's own `INVARIANTS` re-run against the `requires:` floor tag's real code,
    not a hand-maintained 'feature added in version N' table (refuted: that recreates the bug)."""
    def setUp(self):
        self.r = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(self.r)], check=True)
        subprocess.run(["git", "-C", str(self.r), "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", str(self.r), "config", "user.name", "t"], check=True)
        scripts = self.r / "dyad" / "scripts"; scripts.mkdir(parents=True)
        (scripts / "dyadlib.py").write_text("PKG = None\n")   # v0.1.0: no WIDGET
        subprocess.run(["git", "-C", str(self.r), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.r), "commit", "-qm", "v0.1.0"], check=True)
        subprocess.run(["git", "-C", str(self.r), "tag", "dyad-operator-v0.1.0"], check=True)
        (scripts / "dyadlib.py").write_text("PKG = None\nWIDGET = True\n")   # live: has WIDGET
        subprocess.run(["git", "-C", str(self.r), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.r), "commit", "-qm", "live"], check=True)
        self.d = self.r / "crafts" / "fx"; (self.d / "guards").mkdir(parents=True)
        (self.d / "VERSION").write_text("0.1.0\n")
        (self.d / "MANIFEST.md").write_text("name: fx\nrequires: dyad-operator>=0.1.0\n")
        (self.d / "guards" / "w.py").write_text(GUARD_W)
    def tearDown(self):
        shutil.rmtree(self.r, ignore_errors=True)
    def test_floor_fails_when_invariant_is_false_at_the_tag(self):
        msgs = cg.floor_problems(self.r, self.d)
        self.assertEqual(msgs, ["crafts/fx/guards/w.py: floor dyad-operator>=0.1.0: widget-exists is false against 0.1.0 — raise the floor"])
    def test_floor_holds_when_the_invariant_is_true_at_the_tag_too(self):
        (self.d / "MANIFEST.md").write_text("name: fx\nrequires: dyad-operator>=0.1.0\n")
        subprocess.run(["git", "-C", str(self.r), "tag", "-d", "dyad-operator-v0.1.0"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.r), "tag", "dyad-operator-v0.1.0", "HEAD"], check=True)   # tag the commit that already has WIDGET
        self.assertEqual(cg.floor_problems(self.r, self.d), [])
    def test_no_local_tag_skips(self):
        (self.d / "MANIFEST.md").write_text("name: fx\nrequires: dyad-operator>=9.9.9\n")
        msgs = cg.floor_problems(self.r, self.d)
        self.assertEqual(msgs, ["warning: fx: floor dyad-operator>=9.9.9: no tag dyad-operator-v9.9.9 here (not yet released, or tags not fetched)"])
    def test_no_requires_is_silent(self):
        (self.d / "MANIFEST.md").write_text("name: fx\n")
        self.assertEqual(cg.floor_problems(self.r, self.d), [])
    def test_hooked_into_check_craft(self):
        # the fixture craft has no rules/, vocabulary/, templates/, docs/, falsification/ — enough
        # to isolate floor_problems' own messages among check_craft's other fails
        f = fails(cg.check_craft(self.r, self.d))
        self.assertTrue(any("widget-exists is false against 0.1.0" in m for m in f), f)
    def test_own_sys_path_insert_does_not_defeat_the_floor_check(self):
        # caught live against crafts/sysarch/projectors/project_kanban.py: every declared floor
        # "passed" because the file's own sys.path.insert(0, .../dyad/scripts) — its real, live
        # location, since crafts/ is never archived by a core tag — ran after this check's own
        # insert and won, so `import dyadlib` inside the target always resolved to the live module,
        # never the floor's. Pre-seeding sys.modules for every core script before loading the
        # target closes it: a plain `import dyadlib` finds the cache and never touches sys.path.
        (self.d / "guards" / "w3.py").write_text(GUARD_W_SELF_PATH)
        msgs = cg.floor_problems(self.r, self.d)
        self.assertIn("crafts/fx/guards/w3.py: floor dyad-operator>=0.1.0: widget-exists is false against 0.1.0 — raise the floor", msgs)
    def test_transitive_plain_import_not_contaminated_by_an_earlier_live_load(self):
        # crafts/sysadmin/guards/runbooks.py's own shape: a craft guard plain-imports a second core
        # script (`import runbook as _rb`), which itself does `import dyadlib` -- if that second
        # script is already cached in this process, live-bound, from an earlier unrelated load
        # (exactly what package.py's own invariant pass does for `runbook` before any craft check
        # runs), an in-process `sys.modules['dyadlib']` swap alone cannot fix its binding; only full
        # subprocess isolation can. The floor and live commits here are identical on purpose: the
        # floor genuinely holds, so any FAIL below is contamination, not a real floor problem.
        scripts = self.r / "dyad" / "scripts"
        (scripts / "dyadlib.py").write_text("PKG = None\nWIDGET = object()\n")   # a fresh object per execution, unlike `True`'s singleton identity
        (scripts / "helper.py").write_text(
            'import sys\nfrom pathlib import Path\n'
            'sys.path.insert(0, str(Path(__file__).resolve().parent))\n'
            'import dyadlib\nX = dyadlib.WIDGET\n')
        subprocess.run(["git", "-C", str(self.r), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.r), "commit", "-qm", "add helper, WIDGET is now a fresh object"], check=True)
        subprocess.run(["git", "-C", str(self.r), "tag", "-d", "dyad-operator-v0.1.0"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.r), "tag", "dyad-operator-v0.1.0", "HEAD"], check=True)
        (self.d / "guards" / "w2.py").write_text(
            'import sys\nfrom pathlib import Path\n'
            'sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))\n'
            'import dyadlib\nimport helper as _h\n'
            'ENTITY, CORPUS, TRANSACTION = "widget2", "workstation", False\nFIELDS = ("a",)\n'
            'def check_package(root): return []\n'
            'INVARIANTS = [("helper-x-is-dyadlib-widget", lambda: _h.X is dyadlib.WIDGET)]\n')
        # simulate the contaminating earlier load, bound to a *different* dyadlib module object
        # than any fresh floor-subprocess would create
        live_dyadlib = dyadlib.load_module(scripts / "dyadlib.py", "dyad_test_live_dyadlib_for_fx")
        prev = sys.modules.get("dyadlib")
        sys.modules["dyadlib"] = live_dyadlib
        try:
            dyadlib.load_module(scripts / "helper.py", "helper")
        finally:
            if prev is not None: sys.modules["dyadlib"] = prev
            else: sys.modules.pop("dyadlib", None)
        self.assertIn("helper", sys.modules)   # contamination is genuinely present in this process
        msgs = cg.floor_problems(self.r, self.d)
        self.assertEqual(msgs, [], msgs)   # the floor genuinely holds; unaffected by the cache above
    def test_live_repo_no_local_stale_tag_skips_cleanly(self):
        # the live sysarch/syseng/sysadmin crafts still declare the stale requires: dyad-operator
        # >=0.2.0 (raised properly in a later, craft-zone d-work, #100 PR3-5); the tag is not fetched
        # here, so this is a graceful skip, never a FAIL, on the repo as it stands today
        root = dyadlib.repo_root()
        if not (root / "crafts" / "sysarch").is_dir(): self.skipTest("no sysarch craft here")
        msgs = cg.floor_problems(root, root / "crafts" / "sysarch")
        self.assertTrue(all(m.startswith("warning:") for m in msgs), msgs)


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(cg, "core", cg.CORPUS)
        self.assertEqual(dyadlib.check_invariants(cg, extra), len(cg.INVARIANTS) + 4)
        names = [n for n, _ in cg.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
