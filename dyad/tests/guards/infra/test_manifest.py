import os, shutil, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
inf = dyadlib.load_guard("infra", "manifest")

MANIFEST = """| component | partition | version | purpose | license | replacement | profile |
|-----------|-----------|---------|---------|---------|-------------|---------|
| Python | kernel | 3.12 | code | PSF | — | both |
| Git | kernel | 2.43 | repo | GPL-2.0 | — | both |
| `actions/checkout@v4` | library | v4 | CI checkout | MIT | LAN runner | authoring |
| Linux (OS) | The World | 7.0 | provides | — | observed | both |
"""
RULES = "# map\nPython: python3 python\nGit: git\nactions/checkout@v4: actions/checkout@v4\nLinux (OS): -\n"
TOKENS = {"python3": ["scripts/x.py:1"], "git": ["scripts/x.py"], "actions/checkout@v4": ["dyad-x.yml"]}

def run(manifest=MANIFEST, rules=RULES, tokens=TOKENS):
    return inf.check(inf.parse_manifest(manifest), inf.parse_rules(rules), tokens)

class InfrastructureTests(unittest.TestCase):
    def test_passes(self):
        self.assertEqual(run(), [])
    def test_malformed_row(self):
        self.assertIn("malformed", run(MANIFEST + "| jq | library | 1.7 | | MIT | json | both |\n", RULES + "jq: jq\n")[0])
    def test_bad_partition(self):
        self.assertIn("partition 'host'", run(MANIFEST + "| jq | host | 1.7 | json | MIT | json | both |\n", RULES + "jq: jq\n")[0])
    def test_undeclared_token_fails(self):
        msgs = run(tokens={**TOKENS, "curl": ["hooks/pre-push"]})
        self.assertEqual(len(msgs), 1); self.assertIn("'curl' invoked by hooks/pre-push", msgs[0]); self.assertFalse(msgs[0].startswith("warning:"))
    def test_rules_naming_undeclared_component_fails(self):
        self.assertIn("does not declare", run(rules=RULES + "jq: jq\n")[0])
    def test_declared_never_invoked_warns_only(self):
        msgs = run(MANIFEST + "| jq | library | 1.7 | json | MIT | json | both |\n")
        self.assertEqual(len(msgs), 1); self.assertTrue(msgs[0].startswith("warning:")); self.assertIn("'jq'", msgs[0])
    def test_shell_words(self):
        text = 'set -e\nT=$(mktemp -d); git -C "$T" init -q\ncd "$T"; [ -f x ] || { echo no; exit 1; }\nexec "$(git rev-parse --show-toplevel)/dyad/scripts/c.py" staged\n'
        self.assertEqual(sorted(set(inf.shell_words(text))), ["echo", "git", "mktemp"])
    def test_workflow_words_and_python_calls(self):
        wf = "steps:\n  - uses: actions/checkout@v4\n  - run: python3 a.py\n  - run: |\n      set -e\n      grep -q x y\n  - name: n\n"
        self.assertEqual(sorted(inf.workflow_words(wf)), ["actions/checkout@v4", "grep", "python3"])
        py = 'subprocess.run([sys.executable, "-m"])\nsubprocess.check_output(["git", *a])\nsubprocess.Popen([cmd])\n'
        self.assertEqual(inf.python_calls(py), ["python3", "git", "<cmd>"])
        self.assertEqual(inf.shebang("#!/usr/bin/env bash\n"), "bash"); self.assertEqual(inf.shebang("#!/bin/sh\n"), "sh")
    def test_contract(self):
        self.assertEqual((inf.ENTITY, inf.CORPUS, inf.TRANSACTION), ("component", "infra", False)); self.assertEqual(len(inf.FIELDS), 7); self.assertEqual(inf.FIELDS[-1], "profile")
        self.assertTrue(inf.RULES_FILE.exists()); self.assertEqual(inf.RULES_FILE.parent, Path(inf.__file__).parent)
    def test_live_package(self):
        n, m, msgs = inf.check_manifest()
        self.assertEqual([x for x in msgs if not x.startswith("warning:")], [])
        self.assertGreaterEqual(n, 10); self.assertGreaterEqual(m, 8)


IMPORT_MANIFEST = MANIFEST + "| requests | library | 2.32 | http | Apache-2.0 | urllib | both |\n"
IMPORT_RULES = RULES + "requests: import:requests\n"

def fixture(files: dict[str, str]) -> Path:
    """A scratch package tree: scripts/ and tests/ with the given `.py` files."""
    pkg = Path(tempfile.mkdtemp(prefix="dyad-imp-"))
    (pkg / "scripts").mkdir(); (pkg / "tests").mkdir()
    for rel, text in files.items():
        (pkg / rel).write_text(text)
    return pkg

class ImportScanTests(unittest.TestCase):
    def test_stdlib_only_passes(self):
        pkg = fixture({"scripts/a.py": "import os, sys\nfrom pathlib import Path\nimport importlib.util\n"})
        self.assertEqual(inf.python_imports(pkg), {})
        self.assertEqual(run(tokens=inf.python_imports(pkg) | TOKENS), [])
    def test_internal_cross_import_passes(self):
        pkg = fixture({"scripts/dyadlib.py": "X = 1\n", "scripts/a.py": "import dyadlib\nfrom dyadlib import X\n",
                       "tests/test_a.py": "import a as m\nimport dyadlib\n"})
        self.assertEqual(inf.python_imports(pkg), {})
    def test_undeclared_import_fails(self):
        pkg = fixture({"scripts/a.py": "import os\ndef f():\n    import requests.adapters\n"})
        toks = inf.python_imports(pkg)
        self.assertEqual(toks, {"import:requests": ["scripts/a.py"]})
        msgs = run(tokens=toks | TOKENS)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0], "'import:requests' imported by scripts/a.py is an undeclared Python import")
    def test_declared_import_passes(self):
        pkg = fixture({"scripts/a.py": "import requests\n"})
        self.assertEqual(run(IMPORT_MANIFEST, IMPORT_RULES, inf.python_imports(pkg) | TOKENS), [])
    def test_relative_import_is_internal(self):
        pkg = fixture({"scripts/a.py": "from . import b\nfrom .b import c\nfrom ..pkg import d\n"})
        self.assertEqual(inf.python_imports(pkg), {})
    def test_guards_and_nested_tests_are_scanned_and_internal(self):
        pkg = fixture({"scripts/a.py": "import os\n", "scripts/dyadlib.py": "X = 1\n"}); (pkg / "guards" / "agent").mkdir(parents=True); (pkg / "tests" / "guards" / "agent").mkdir(parents=True)
        (pkg / "guards" / "agent" / "rows.py").write_text("import dyadlib\nimport requests\n")
        (pkg / "tests" / "guards" / "agent" / "test_rows.py").write_text("import dyadlib\nimport guards.agent\n")
        self.assertEqual(inf.python_imports(pkg), {"import:requests": ["guards/agent/rows.py"]})
    def test_live_package_has_no_third_party_import(self):
        self.assertEqual(inf.python_imports(dyadlib.PKG), {})
        self.assertIn("import:", inf.RULES_FILE.read_text())
        n, m, msgs = inf.check_manifest()
        self.assertEqual([x for x in msgs if not x.startswith("warning:")], [])


CRAFT_INFRA = """| component | partition | version | purpose | license | replacement | profile |
|-----------|-----------|---------|---------|---------|-------------|---------|
| Anthropic API | library | v1 | fetches research briefs | proprietary | — | operating |
"""

def craft_root(files: dict[str, str] | None = None) -> Path:
    """A scratch repo root: `pkg` at `root/dyad` (scripts/, tests/) with `crafts/` as its sibling —
    the real layout `dyadlib.craft_dirs` assumes (`crafts_dir(pkg) = pkg.parent / "crafts"`); the
    ImportScanTests `fixture()` above returns a bare tempdir with no such sibling, so it is not
    reused here."""
    import subprocess
    root = Path(tempfile.mkdtemp(prefix="dyad-craft-"))
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    pkg = root / "dyad"
    (pkg / "scripts").mkdir(parents=True); (pkg / "tests").mkdir()
    for rel, text in (files or {}).items():
        (pkg / rel).write_text(text)
    return pkg

def craft_fixture(pkg: Path, name="automaton", infra=CRAFT_INFRA) -> Path:
    """A scratch craft tree beside `pkg` (`pkg.parent / "crafts" / name`) with a VERSION
    (`dyadlib.craft_dirs` requires one) and, when given, an `infrastructure_contrib.md`."""
    d = pkg.parent / "crafts" / name
    (d / "guards").mkdir(parents=True)
    (d / "VERSION").write_text("0.1.0\n")
    if infra is not None:
        (d / "infrastructure_contrib.md").write_text(infra)
    return d


class CraftContributionTests(unittest.TestCase):
    """Rule-11 property 2's craft-shipped contribution (`agent-corpus/falsification/extensibility.md`
    #101): a craft's own infrastructure_contrib.md rows join the core manifest; a colliding
    component name fails, naming both sources; a craft's own guard/scripts/projectors imports and
    invocations join the scan (ImportScanTests above already covers python_imports; this covers
    the row-merge and collision-detection half)."""
    def setUp(self):
        self.pkg = craft_root({"scripts/a.py": "import os\n"})
    def tearDown(self):
        shutil.rmtree(self.pkg.parent, ignore_errors=True)
    def test_no_craft_no_contribution(self):
        self.assertEqual(inf.craft_infra_rows(self.pkg), [])
    def test_craft_row_joins_the_manifest(self):
        craft_fixture(self.pkg)
        rows = inf.craft_infra_rows(self.pkg)
        self.assertEqual(rows, [("automaton", ("Anthropic API", "library", "v1", "fetches research briefs", "proprietary", "—", "operating"))])
    def test_check_manifest_includes_craft_rows(self):
        (self.pkg / "infrastructure").mkdir(); (self.pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
        (self.pkg / "guards" / "infra").mkdir(parents=True); (self.pkg / "guards" / "infra" / "manifest_rules.txt").write_text(RULES)
        craft_fixture(self.pkg)
        n, m, msgs = inf.check_manifest(self.pkg)
        self.assertEqual(n, 5)   # 4 core rows + 1 craft row
        self.assertTrue(any(x.startswith("warning: 'Anthropic API' declared but no token maps to it") for x in msgs), msgs)
    def test_colliding_component_name_fails_naming_both_sources(self):
        (self.pkg / "infrastructure").mkdir(); (self.pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
        (self.pkg / "guards" / "infra").mkdir(parents=True); (self.pkg / "guards" / "infra" / "manifest_rules.txt").write_text(RULES)
        craft_fixture(self.pkg, infra="| component | partition | version | purpose | license | replacement | profile |\n"
                      "|-----------|-----------|---------|---------|---------|-------------|---------|\n"
                      "| Python | library | 1.0 | craft's own | MIT | — | both |\n")
        n, m, msgs = inf.check_manifest(self.pkg)
        self.assertTrue(any("'Python' (crafts/automaton/infrastructure_contrib.md): already declared by the manifest" in x for x in msgs), msgs)
    def test_second_craft_colliding_with_first_craft_is_named(self):
        (self.pkg / "infrastructure").mkdir(); (self.pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
        (self.pkg / "guards" / "infra").mkdir(parents=True); (self.pkg / "guards" / "infra" / "manifest_rules.txt").write_text(RULES)
        craft_fixture(self.pkg, name="automaton")
        craft_fixture(self.pkg, name="researcher")
        n, m, msgs = inf.check_manifest(self.pkg)
        self.assertTrue(any("'Anthropic API' (crafts/researcher/infrastructure_contrib.md): already declared by crafts/automaton/infrastructure_contrib.md" in x for x in msgs), msgs)
    def test_no_craft_no_rules_contribution(self):
        self.assertEqual(inf.craft_manifest_rules(self.pkg), [])
    def test_craft_manifest_rules_contrib_parsed(self):
        d = craft_fixture(self.pkg, infra=None)
        (d / "manifest_rules_contrib.txt").write_text("X: tok1 tok2\n")
        self.assertEqual(inf.craft_manifest_rules(self.pkg), [("automaton", {"X": ["tok1", "tok2"]})])
    def test_craft_token_unresolved_without_the_contrib_file(self):
        """#105 mechanism 2, before the fix: a craft's own script invokes a tool only that craft
        knows about; declaring the component (infrastructure_contrib.md) is not enough — the
        *token* still resolves against the core's manifest_rules.txt alone."""
        (self.pkg / "infrastructure").mkdir(); (self.pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
        (self.pkg / "guards" / "infra").mkdir(parents=True); (self.pkg / "guards" / "infra" / "manifest_rules.txt").write_text(RULES)
        d = craft_fixture(self.pkg); (d / "scripts").mkdir()
        (d / "scripts" / "fetch.sh").write_text("anthropic-cli fetch\n")
        n, m, msgs = inf.check_manifest(self.pkg)
        self.assertTrue(any("anthropic-cli" in x and "maps to no declared component" in x for x in msgs), msgs)
    def test_craft_manifest_rules_contrib_resolves_the_same_token(self):
        """#105 fix: the craft's own manifest_rules_contrib.txt resolves the token the core map
        never could, for the component the craft already declared."""
        (self.pkg / "infrastructure").mkdir(); (self.pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
        (self.pkg / "guards" / "infra").mkdir(parents=True); (self.pkg / "guards" / "infra" / "manifest_rules.txt").write_text(RULES)
        d = craft_fixture(self.pkg); (d / "scripts").mkdir()
        (d / "scripts" / "fetch.sh").write_text("anthropic-cli fetch\n")
        (d / "manifest_rules_contrib.txt").write_text("Anthropic API: anthropic-cli\n")
        n, m, msgs = inf.check_manifest(self.pkg)
        self.assertEqual([x for x in msgs if not x.startswith("warning:")], [])
    def test_craft_rules_contrib_never_overrides_a_core_token(self):
        """A craft's own rules can add tokens to a core component but a core-resolved token stays
        resolved to the core's own mapping (first-wins, `tok2comp.setdefault`) -- a craft cannot
        silently redirect an existing token's component."""
        (self.pkg / "infrastructure").mkdir(); (self.pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
        (self.pkg / "guards" / "infra").mkdir(parents=True); (self.pkg / "guards" / "infra" / "manifest_rules.txt").write_text(RULES)
        d = craft_fixture(self.pkg, infra=None)
        (d / "manifest_rules_contrib.txt").write_text("Anthropic API: python3\n")   # python3 is already Python's token
        n, m, msgs = inf.check_manifest(self.pkg)
        self.assertTrue(any("rules map 'Anthropic API' which the manifest does not declare" in x for x in msgs), msgs)
    def test_craft_non_script_file_is_not_swept_as_shell_text(self):
        """#105 mechanism 1: a craft's own guards/README.md is prose, not a shell script; scan()
        must not extract "shell words" from it."""
        d = craft_fixture(self.pkg, infra=None)
        (d / "guards" / "README.md").write_text("Run curl against the endpoint, then check the output with grep.\n")
        toks = inf.scan(self.pkg)
        self.assertNotIn("curl", toks); self.assertNotIn("grep", toks); self.assertNotIn("Run", toks)
    def test_craft_sh_file_is_still_scanned_as_shell(self):
        d = craft_fixture(self.pkg, infra=None); (d / "scripts").mkdir()
        (d / "scripts" / "x.sh").write_text("#!/usr/bin/env bash\ncurl https://example\n")
        toks = inf.scan(self.pkg)
        self.assertIn("curl", toks)
    def test_craft_server_dir_is_scanned_for_internal_imports(self):
        """#105 mechanism 3: crafts/syseng/rules/invariants.md already anticipates crafts/*/server/
        as a craft-file location; craft_python_dirs must include it so a sibling test's import of
        the craft's own server module is not misread as an undeclared third-party import."""
        d = craft_fixture(self.pkg, infra=None)
        (d / "server").mkdir(); (d / "server" / "app.py").write_text("import flask\n")
        (d / "tests").mkdir(); (d / "tests" / "test_app.py").write_text("import app\nimport server\n")
        self.assertIn(d / "server", inf.craft_python_dirs(self.pkg))
        toks = inf.python_imports(self.pkg)
        self.assertEqual(toks, {"import:flask": ["crafts/automaton/server/app.py"]})


INSTANCE_INFRA = """| component | partition | version | purpose | license | replacement | profile |
|-----------|-----------|---------|---------|---------|-------------|---------|
| Gitea | library | 1.27 | LAN git server | MIT | Forgejo | operating |
"""

class ProfileTests(unittest.TestCase):
    """#175: the seventh cell `profile`; a kernel row is `both`."""
    def test_bad_profile_fails(self):
        msgs = run(MANIFEST + "| jq | library | 1.7 | json | MIT | json | sometimes |\n", RULES + "jq: jq\n")
        self.assertEqual(len(msgs), 1); self.assertIn("profile 'sometimes' not in", msgs[0])
    def test_kernel_row_must_be_both(self):
        msgs = run(MANIFEST.replace("| GPL-2.0 | — | both |", "| GPL-2.0 | — | authoring |"))
        self.assertEqual(len(msgs), 1); self.assertIn("'Git': a kernel row serves both profiles", msgs[0])
    def test_six_cell_row_is_malformed(self):
        self.assertIn("malformed", run(MANIFEST + "| jq | library | 1.7 | json | MIT | json |\n", RULES + "jq: jq\n")[0])
    def test_live_core_rows_all_carry_a_profile(self):
        rows = inf.parse_manifest((dyadlib.PKG / "infrastructure" / "INFRASTRUCTURE.md").read_text())
        self.assertTrue(rows and all(r[6] in inf.PROFILES for r in rows))
        self.assertTrue(all(r[6] == "both" for r in rows if r[1] == "kernel"))
        self.assertFalse({"Gitea", "Docker Engine + Compose", "GHCR (ghcr.io)", "curl"} & {dyadlib.plain(r[0]) for r in rows})   # operating rows are instance


class InstanceContributionTests(unittest.TestCase):
    """#175: `<host path>/INFRASTRUCTURE.md` joins the core and craft rows as one manifest."""
    def setUp(self):
        self.prev = {k: os.environ.pop(k, None) for k in ("DYAD_HOST", "DYAD_HOST_ZONE")}
        self.pkg = craft_root({"scripts/a.py": "import os\n"}); self.root = self.pkg.parent
        (self.pkg / "infrastructure").mkdir(); (self.pkg / "infrastructure" / "INFRASTRUCTURE.md").write_text(MANIFEST)
        (self.pkg / "guards" / "infra").mkdir(parents=True); (self.pkg / "guards" / "infra" / "manifest_rules.txt").write_text(RULES)
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
        for k, v in self.prev.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    def instance(self, text=INSTANCE_INFRA, host="workstation-corpus"):
        d = self.root / host; d.mkdir(parents=True, exist_ok=True); (d / "INFRASTRUCTURE.md").write_text(text)
    def test_absent_file_adds_nothing(self):
        self.assertEqual(inf.instance_infra_rows(self.root), [])
        n, m, msgs = inf.check_manifest(self.pkg, self.root)
        self.assertEqual(n, 4); self.assertEqual([x for x in msgs if not x.startswith("warning:")], [])
    def test_instance_rows_join_without_a_token(self):
        self.instance()
        rows, msgs = inf.manifest_rows(self.pkg, self.root)
        self.assertEqual(msgs, []); self.assertEqual(rows[-1][0], "workstation-corpus/INFRASTRUCTURE.md")
        n, m, msgs = inf.check_manifest(self.pkg, self.root)
        self.assertEqual(n, 5); self.assertEqual(msgs, [])   # no "declared but no token" warning for an instance row
    def test_host_path_moves_the_instance_file(self):
        os.environ["DYAD_HOST"], os.environ["DYAD_HOST_ZONE"] = "infrastructure", "infra"
        self.instance(host="infrastructure")
        self.assertEqual(inf.instance_source(self.root), "infrastructure/INFRASTRUCTURE.md")
        self.assertEqual([r[0] for r in inf.instance_infra_rows(self.root)], ["Gitea"])
    def test_duplicate_across_core_and_instance_fails(self):
        self.instance(INSTANCE_INFRA + "| Python | kernel | 3.12 | again | PSF | — | both |\n")
        n, m, msgs = inf.check_manifest(self.pkg, self.root)
        self.assertIn("'Python' (workstation-corpus/INFRASTRUCTURE.md): already declared by the manifest", msgs)
    def test_duplicate_across_craft_and_instance_fails(self):
        craft_fixture(self.pkg); self.instance(INSTANCE_INFRA + "| Anthropic API | library | v2 | again | proprietary | — | operating |\n")
        n, m, msgs = inf.check_manifest(self.pkg, self.root)
        self.assertIn("'Anthropic API' (workstation-corpus/INFRASTRUCTURE.md): already declared by crafts/automaton/infrastructure_contrib.md", msgs)
    def test_live_union_is_unchanged_in_content(self):
        """The live union is exactly core + crafts + this instance's own file, nothing dropped or
        duplicated, and the core ships no `operating` row (they moved to the instance, #175). Derived
        from the live repo's own files, never from dyad-system's counts (#179: on dyad-system this is
        core 11 + instance 4 = 15; another system has its own instance rows)."""
        rows, msgs = inf.manifest_rows()
        self.assertEqual(msgs, [])
        core = inf.parse_manifest((dyadlib.PKG / "infrastructure" / "INFRASTRUCTURE.md").read_text())
        crafts, instance = inf.craft_infra_rows(dyadlib.PKG), inf.instance_infra_rows(dyadlib.PKG.parent)
        self.assertEqual(len(rows), len(core) + len(crafts) + len(instance))
        self.assertEqual({dyadlib.plain(r[0]) for s, r in rows if s != "the manifest"},
                         {dyadlib.plain(r[0]) for _, r in crafts} | {dyadlib.plain(r[0]) for r in instance})
        self.assertEqual([r[0] for r in core if r[-1] == "operating"], [])


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(inf, "core", inf.CORPUS)
        self.assertEqual(dyadlib.check_invariants(inf, extra), len(inf.INVARIANTS) + 4)
        names = [n for n, _ in inf.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
