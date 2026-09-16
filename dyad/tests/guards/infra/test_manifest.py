import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
inf = dyadlib.load_guard("infra", "manifest")

MANIFEST = """| component | partition | version | purpose | license | replacement |
|-----------|-----------|---------|---------|---------|-------------|
| Python | kernel | 3.12 | code | PSF | — |
| Git | kernel | 2.43 | repo | GPL-2.0 | — |
| `actions/checkout@v4` | library | v4 | CI checkout | MIT | LAN runner |
| Linux (OS) | The World | 7.0 | provides | — | observed |
"""
RULES = "# map\nPython: python3 python\nGit: git\nactions/checkout@v4: actions/checkout@v4\nLinux (OS): -\n"
TOKENS = {"python3": ["scripts/x.py:1"], "git": ["scripts/x.py"], "actions/checkout@v4": ["dyad-x.yml"]}

def run(manifest=MANIFEST, rules=RULES, tokens=TOKENS):
    return inf.check(inf.parse_manifest(manifest), inf.parse_rules(rules), tokens)

class InfrastructureTests(unittest.TestCase):
    def test_passes(self):
        self.assertEqual(run(), [])
    def test_malformed_row(self):
        self.assertIn("malformed", run(MANIFEST + "| jq | library | 1.7 | | MIT | json |\n", RULES + "jq: jq\n")[0])
    def test_bad_partition(self):
        self.assertIn("partition 'host'", run(MANIFEST + "| jq | host | 1.7 | json | MIT | json |\n", RULES + "jq: jq\n")[0])
    def test_undeclared_token_fails(self):
        msgs = run(tokens={**TOKENS, "curl": ["hooks/pre-push"]})
        self.assertEqual(len(msgs), 1); self.assertIn("'curl' invoked by hooks/pre-push", msgs[0]); self.assertFalse(msgs[0].startswith("warning:"))
    def test_rules_naming_undeclared_component_fails(self):
        self.assertIn("does not declare", run(rules=RULES + "jq: jq\n")[0])
    def test_declared_never_invoked_warns_only(self):
        msgs = run(MANIFEST + "| jq | library | 1.7 | json | MIT | json |\n")
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
        self.assertEqual((inf.ENTITY, inf.CORPUS, inf.TRANSACTION), ("component", "infra", False)); self.assertEqual(len(inf.FIELDS), 6)
        self.assertTrue(inf.RULES_FILE.exists()); self.assertEqual(inf.RULES_FILE.parent, Path(inf.__file__).parent)
    def test_live_package(self):
        n, m, msgs = inf.check_manifest()
        self.assertEqual([x for x in msgs if not x.startswith("warning:")], [])
        self.assertGreaterEqual(n, 10); self.assertGreaterEqual(m, 8)


IMPORT_MANIFEST = MANIFEST + "| requests | library | 2.32 | http | Apache-2.0 | urllib |\n"
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


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(inf, "core", inf.CORPUS)
        self.assertEqual(dyadlib.check_invariants(inf, extra), len(inf.INVARIANTS) + 4)
        names = [n for n, _ in inf.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
