"""naming.py (the syseng craft's guard, entity `name`; #162): data parsing, path globs, kind/mode/symbol/env/allow checks
over fixtures, the table-data agreement, and the live repo passes with every kind and mode a table row."""
import shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
naming = dyadlib.load_guard_file(Path(__file__).resolve().parents[2] / "guards" / "naming.py")

def repo(files: dict[str, str], track=True) -> Path:
    root = Path(tempfile.mkdtemp()); subprocess.run(["git", "init", "-q", str(root)], check=True)
    for rel, text in files.items():
        f = root / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
    if track:
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return root

RULES = """# t
kind: dyad/rules/RULE-<n>-<slug>.md = dyad/rules/* = dyad/rules/RULE-(?P<id>\\d+)-[a-z0-9-]+\\.md
kind: <entity>_rules.txt = dyad/guards/*/*.txt = dyad/guards/[a-z]+/(?P<beside>[a-z_]+)_rules\\.txt
kind: <instance>/d-work/rows/<id>.md = <instance>/d-work/rows/* = <instance>/d-work/rows/((?P<id>\\d+)|README)\\.md
symbol: dyad/guards/*/*.py : ENTITY check_\\w+
env: DYAD_INSTANCE
allow: dyad/rules/legacy.md # predates the pattern
"""
TABLE = "# n\n\n| pattern | names | owner | example | checkable |\n|---|---|---|---|---|\n| `dyad/rules/RULE-<n>-<slug>.md` | a Rule | Rule-4 | x | yes |\n| `<entity>_rules.txt` | data | guards.md | y | yes |\n| `<instance>/d-work/rows/<id>.md` | a row | Rule-16 | z | yes |\n"
GOOD = {"dyad/rules/RULE-1-a.md": "# a\n", "dyad/rules/RULE-2-b.md": "# b\n", "dyad/rules/legacy.md": "# l\n",
        "dyad/guards/agent/x.py": 'import os\nENTITY = "x"\ndef check_package(r): return os.environ.get("DYAD_INSTANCE")\n', "dyad/guards/agent/x_rules.txt": "#\n",
        "agent-corpus/d-work/rows/1.md": "id: 1\n", "agent-corpus/d-work/rows/README.md": "# r\n"}

MODE_RULES = "mode: dyad/bin/<name> = dyad/bin/* = 100755\n"
MODE_TABLE = "# n\n\n| pattern | names | owner | example | checkable |\n|---|---|---|---|---|\n| `dyad/bin/<name>` | the entrypoint | Rule-11 | `dyad/bin/dyad` | yes |\n"

class DataTests(unittest.TestCase):
    def test_parse_rules(self):
        r = naming.parse_rules(RULES + MODE_RULES)
        self.assertEqual(r["mode"], [("dyad/bin/<name>", "dyad/bin/*", "100755")])
        r = naming.parse_rules(RULES)
        self.assertEqual(r["mode"], [])
        self.assertEqual([k[0] for k in r["kind"]], ["dyad/rules/RULE-<n>-<slug>.md", "<entity>_rules.txt", "<instance>/d-work/rows/<id>.md"])
        self.assertEqual(r["symbol"], [("dyad/guards/*/*.py", ["ENTITY", "check_\\w+"])]); self.assertEqual(r["env"], ["DYAD_INSTANCE"])
        self.assertEqual(r["allow"], [("dyad/rules/legacy.md", "predates the pattern")]); self.assertEqual(r["bad"], [])
        self.assertEqual(naming.parse_rules("kind: x\nnope\n")["bad"], ["kind: x", "nope"])
    def test_glob_re_segments(self):
        self.assertTrue(naming.glob_re("crafts/*/rules/*").match("crafts/a/rules/b.md"))
        self.assertFalse(naming.glob_re("crafts/*/rules/*").match("crafts/a/falsification/rules/b.md"))   # `*` is one segment, unlike fnmatch
        self.assertTrue(naming.glob_re("crafts/*/**").match("crafts/a/x/y/z")); self.assertFalse(naming.glob_re("dyad/tests/*.py").match("dyad/tests/guards/a.py"))
    def test_table_patterns_and_rows(self):
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        t = d / "naming.md"; t.write_text(TABLE)
        self.assertEqual(naming.table_patterns(t), {"dyad/rules/RULE-<n>-<slug>.md", "<entity>_rules.txt", "<instance>/d-work/rows/<id>.md"})
        self.assertEqual([r["pattern"] for r in naming.rows(t)], ["`dyad/rules/RULE-<n>-<slug>.md`", "`<entity>_rules.txt`", "`<instance>/d-work/rows/<id>.md`"])
        self.assertEqual(naming.rows(d / "absent.md"), []); self.assertEqual(naming.table_patterns(d / "absent.md"), set())

class CheckTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.data = self.d / "naming_rules.txt"; self.data.write_text(RULES)
        self.table = self.d / "naming.md"; self.table.write_text(TABLE)
    def check(self, files, data=None, table=None, track=True):
        root = repo(files, track); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return naming.check_package(root, data=data or self.data, table=table or self.table)
    def test_good_tree_passes(self):
        self.assertEqual(self.check(GOOD), [])
    def test_untracked_files_are_seen(self):
        self.assertEqual(self.check({**GOOD, "dyad/rules/RULE-3-c.md": "#\n"}, track=False), [])
        self.assertIn("dyad/rules/Bad.md: does not match `dyad/rules/RULE-<n>-<slug>.md`", self.check({**GOOD, "dyad/rules/Bad.md": "#\n"}, track=False)[0])
    def test_bad_name_duplicate_id_and_missing_beside(self):
        msgs = self.check({**GOOD, "dyad/rules/RULE-1-dup.md": "#\n", "dyad/rules/RULE-x.md": "#\n", "dyad/guards/agent/y_rules.txt": "#\n", "agent-corpus/d-work/rows/1.md": "id: 1\n"})
        self.assertIn("dyad/rules/RULE-1-dup.md: id '1' already used by dyad/rules/RULE-1-a.md (`dyad/rules/RULE-<n>-<slug>.md`)", msgs)
        self.assertTrue(any(m.startswith("dyad/rules/RULE-x.md: does not match") for m in msgs), msgs)
        self.assertIn("dyad/guards/agent/y_rules.txt: no dyad/guards/agent/y.py beside it (`<entity>_rules.txt`)", msgs)
        self.assertEqual(len(msgs), 3, msgs)
    def test_instance_token_follows_dyad_instance(self):
        import os
        prev = os.environ.get("DYAD_INSTANCE"); os.environ["DYAD_INSTANCE"] = "inst"
        try:
            files = {k.replace("agent-corpus/", "inst/"): v for k, v in GOOD.items()}
            self.assertEqual(self.check(files), [])
            self.assertTrue(any("inst/d-work/rows/x.md: does not match" in m for m in self.check({**files, "inst/d-work/rows/x.md": "#\n"})))
        finally:
            os.environ.pop("DYAD_INSTANCE", None)
            if prev is not None: os.environ["DYAD_INSTANCE"] = prev
    def test_kind_not_in_table_fails(self):
        self.table.write_text(TABLE.replace("| `<entity>_rules.txt` | data | guards.md | y | yes |\n", ""))
        self.assertEqual(self.check(GOOD), ["naming_rules.txt: kind `<entity>_rules.txt` is not a row of rules/naming.md"])
    def test_symbols(self):
        msgs = self.check({**GOOD, "dyad/guards/agent/x.py": 'import os\nENTITY = "x"\ndef verify(r): return os.environ.get("DYAD_INSTANCE")\n'})
        self.assertEqual(msgs, ["dyad/guards/agent/x.py: no top-level name matches /check_\\w+/ (symbol rule dyad/guards/*/*.py)"])
        msgs = self.check({**GOOD, "dyad/guards/agent/x.py": 'import os\ndef check_package(r): return os.environ.get("DYAD_INSTANCE")\n'})
        self.assertEqual(msgs, ["dyad/guards/agent/x.py: defines no top-level `ENTITY` (symbol rule dyad/guards/*/*.py)"])
        self.assertEqual(self.check({**GOOD, "dyad/guards/agent/_helper.py": "X = 1\n"}), [])   # `_`-prefixed: not a guard, not judged
    def test_env_unlisted_and_stale(self):
        msgs = self.check({**GOOD, "dyad/guards/agent/x.py": 'import os\nENTITY = "x"\ndef check_package(r): return os.environ["DYAD_OTHER"]\n'})
        self.assertEqual(msgs, ["dyad/guards/agent/x.py: reads DYAD_OTHER, not in the naming table (`DYAD_<NAME>` row / `env:` line)",
                                "naming_rules.txt: env DYAD_INSTANCE is listed but no package code reads it (stale)"])
    def test_allow_reason_stale_unneeded(self):
        self.data.write_text(RULES.replace(" # predates the pattern", ""))
        self.assertIn("naming_rules.txt: allow dyad/rules/legacy.md has no reason", self.check(GOOD))
        self.data.write_text(RULES)
        self.assertEqual(self.check({k: v for k, v in GOOD.items() if k != "dyad/rules/legacy.md"}), ["naming_rules.txt: allow dyad/rules/legacy.md is stale (no such path); remove the line"])
        self.data.write_text(RULES + "allow: .github/workflows/x.yml # instance\n")   # an instance path absent here: a warning, the data travels to other installs
        self.assertEqual(self.check(GOOD), ["warning: naming_rules.txt: allow .github/workflows/x.yml names no path of this tree (an instance path; remove the line if it is gone for good)"])
        self.data.write_text(RULES + "allow: dyad/rules/RULE-1-a.md # fits anyway\n")
        self.assertEqual(self.check(GOOD), ["warning: naming_rules.txt: allow dyad/rules/RULE-1-a.md is no longer needed (the path matches its pattern)"])
    def test_malformed_line_fails(self):
        self.data.write_text(RULES + "kind: broken\n")
        self.assertIn("naming_rules.txt: malformed line 'kind: broken'", self.check(GOOD))

class ModeTests(unittest.TestCase):
    """#141: `mode:` judges the mode git records, not the bit on disk (`core.fileMode=false` shows 755 for a
    file tracked 100644 — how an entrypoint that could not exec reached an image, #135)."""
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.data = self.d / "naming_rules.txt"; self.data.write_text(MODE_RULES)
        self.table = self.d / "naming.md"; self.table.write_text(MODE_TABLE)
    def tree(self, disk=0o755, index="100755") -> Path:
        """A scratch repo holding `dyad/bin/dyad` at `disk` on disk and `index` in git (None: untracked)."""
        root = repo({"dyad/bin/dyad": "#!/usr/bin/env python3\n"}, track=index is not None)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "dyad/bin/dyad").chmod(disk)
        if index is not None:
            subprocess.run(["git", "-C", str(root), "update-index", f"--chmod={'+' if index == '100755' else '-'}x", "--", "dyad/bin/dyad"], check=True)
        return root
    def check(self, root):
        return naming.check_package(root, data=self.data, table=self.table)
    def test_tracked_non_executable_fails_though_the_disk_bit_is_set(self):
        self.assertEqual(self.check(self.tree(disk=0o755, index="100644")),
                         ["dyad/bin/dyad: tracked mode 100644, not 100755 (`dyad/bin/<name>`) (git update-index --chmod=+x)"])
    def test_tracked_executable_passes_though_the_disk_bit_is_absent(self):
        self.assertEqual(self.check(self.tree(disk=0o644, index="100755")), [])
    def test_untracked_warns_and_falls_back_to_the_disk_bit(self):
        self.assertEqual(self.check(self.tree(disk=0o755, index=None)),
                         ["warning: dyad/bin/dyad: untracked: disk mode used (`dyad/bin/<name>` wants 100755)"])
        self.assertEqual(self.check(self.tree(disk=0o644, index=None)),
                         ["warning: dyad/bin/dyad: untracked: disk mode used (`dyad/bin/<name>` wants 100755)",
                          "dyad/bin/dyad: not executable on disk and not tracked (`dyad/bin/<name>` wants 100755)"])
    def test_mode_pattern_must_be_a_table_row(self):
        self.table.write_text(MODE_TABLE.replace("`dyad/bin/<name>`", "`something/else`"))
        self.assertIn("naming_rules.txt: mode `dyad/bin/<name>` is not a row of rules/naming.md", self.check(self.tree()))

class LiveTests(unittest.TestCase):
    def test_live_repo_passes_and_every_kind_is_a_row(self):
        msgs = naming.check_package(dyadlib.repo_root())
        self.assertEqual([m for m in msgs if not m.startswith("warning:")], [])
        r = naming.load_rules(); pats = naming.table_patterns()
        for pattern, _g, _r in r["kind"] + r["mode"]: self.assertIn(pattern, pats)
        self.assertTrue(r["mode"])   # the executables a host runs by name are checked at all (#141)
        self.assertGreaterEqual(len(naming.rows()), 20); self.assertEqual(r["bad"], [])
        self.assertEqual(sorted(r["env"]), ["DYAD_INSTANCE", "DYAD_NO_NESTED_TESTS", "DYAD_OPS@sysadmin", "DYAD_ROLE", "DYAD_RUNBOOKS", "DYAD_SESSION"])   # @craft: checked only where that craft is installed (dyad-system #1)
        self.assertRegex(naming.summary(), r"^\d+ patterns, \d+ kinds, \d+ mode rules, \d+ symbol rules, \d+ allowed$")
    def test_contract_card_and_invariants(self):
        self.assertEqual((naming.ENTITY, naming.CORPUS, naming.TRANSACTION), ("name", "craft", False))
        d = naming.describe(dyadlib.repo_root()); self.assertEqual([f[0] for f in d["fields"]], list(naming.FIELDS)); self.assertGreater(d["observed"], 0)
        self.assertEqual(dyadlib.check_invariants(naming, dyadlib.contract_invariants(naming, "craft", "syseng", {"craft"})), len(naming.INVARIANTS) + 4)



class EnvScopeTests(unittest.TestCase):
    def test_qualified_token_checked_only_when_its_craft_is_installed(self):
        found = {"DYAD_A": ["dyad/scripts/a.py"]}
        self.assertEqual(naming.check_env(found, ["DYAD_A", "DYAD_B@sysadmin"], {"sysarch"}),
                         ["warning: naming_rules.txt: env DYAD_B is read by a craft not installed here; not checked"])
        self.assertEqual(naming.check_env(found, ["DYAD_A", "DYAD_B@sysadmin"], {"sysadmin"}),
                         ["naming_rules.txt: env DYAD_B is listed but no package code reads it (stale)"])
        self.assertEqual(naming.check_env({"DYAD_A": ["a.py"], "DYAD_B": ["crafts/sysadmin/guards/o.py"]}, ["DYAD_A", "DYAD_B@sysadmin"], {"sysadmin"}), [])
    def test_unqualified_tokens_unchanged(self):
        self.assertEqual(naming.check_env({}, ["DYAD_A"], None), ["naming_rules.txt: env DYAD_A is listed but no package code reads it (stale)"])
        self.assertEqual(naming.check_env({"DYAD_Z": ["z.py"]}, [], None), ["z.py: reads DYAD_Z, not in the naming table (`DYAD_<NAME>` row / `env:` line)"])

if __name__ == "__main__":
    unittest.main()
