"""Redaction tests (crafts/disclosure/scripts/redaction.py): the class data parsed and checked, the
key shapes imported from the core rather than re-listed, the gate finding Class A and unmapped Class B
while ignoring a value the map already carries, the map's uniqueness rules, and the CLI's exit codes."""
import os, re, subprocess, sys, tempfile, unittest
from pathlib import Path
CRAFT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CRAFT.parents[1] / "dyad" / "scripts")); sys.path.insert(0, str(CRAFT / "scripts"))
import dyadlib
import redaction as rd

HOMEDIR = "/ho" + "me/user/tree"          # assembled: a craft file carries no host-specific literal (Rule-11 p1)
LAN = "192." + "168.1.9"

MAP = """# map
| real | pseudonym | kind | since |
|------|-----------|------|-------|
| `dyad/guards/agent/rows.py` | COMPONENT-1 | guard module | #166 |
| `Rule-16` | POLICY-A | rule number | #166 |
"""

def fixture(map_text: str | None = MAP):
    root = Path(tempfile.mkdtemp()); (root / "dyad").mkdir()
    if map_text is not None:
        d = root / "agent-corpus" / "disclosure"; d.mkdir(parents=True)
        (d / "pseudonyms.md").write_text(map_text)
    return root

class ContractTests(unittest.TestCase):
    def test_contract(self):
        self.assertEqual(rd.FIELDS, ("class", "name", "pattern"))
        self.assertFalse(hasattr(rd, "ENTITY"), "a script, not a guard: no registry entry (row #170)")
    def test_invariants_hold(self):
        for name, pred in rd.INVARIANTS:
            self.assertTrue(pred(), name)
    def test_data_parses_and_every_class_has_a_shape(self):
        shapes, allowed, problems = rd.rules()
        self.assertEqual(problems, [])
        self.assertTrue(allowed)
        for cls in rd.CLASSES:
            self.assertTrue(any(c == cls for c, _, _ in shapes), cls)
    def test_key_shapes_are_imported_not_relisted(self):
        # Rule-13: the core provenance guard owns them; this craft must not carry its own copies
        names = [n for n, _ in rd.credential_shapes()]
        self.assertTrue(names, "the core provenance guard's FAIL_SHAPES did not load")
        prov = dyadlib.load_guard("agent", "provenance")
        self.assertEqual(names, [n for n, _ in prov.FAIL_SHAPES])            # borrowed whole, never a subset copied by hand
        self.assertNotIn("40-hex", " ".join(names))                          # WARN_SHAPES is not a gate
        data = (CRAFT / "scripts" / "redaction_rules.txt").read_text()
        for token in ("github_pat_", "Authorization", "BEGIN"):
            self.assertNotIn(token, data, "a key shape is re-listed in the craft's own data")

class DataTests(unittest.TestCase):
    def _with(self, text: str):
        d = Path(tempfile.mkdtemp()) / "redaction_rules.txt"; d.write_text(text); return d
    def test_bad_regex_and_unknown_key_are_reported(self):
        _, _, problems = rd.rules(self._with("a: broken = (unclosed\nz: nope = x\nb: ok = y\n"))
        self.assertEqual(len(problems), 2, problems)
        self.assertTrue(any("does not compile" in p for p in problems))
        self.assertTrue(any("unknown key" in p for p in problems))
    def test_missing_name_or_pattern_is_reported(self):
        _, _, problems = rd.rules(self._with("a: = x\nb: name =\n"))
        self.assertEqual(len(problems), 2, problems)

class GateTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_class_a_identity_is_a_finding(self):
        root = fixture()
        for probe in (HOMEDIR, LAN, "someone@example.com",
                      "https://github.com/owner/repo", "session_01LtSYzYp92J", "PR #177"):
            self.assertTrue(rd.findings(probe, root), probe)
    def test_unmapped_class_b_is_a_finding_and_a_mapped_one_is_not(self):
        root = fixture()
        self.assertTrue(rd.findings("Rule-20 was breached", root))          # not in the map
        self.assertEqual(rd.findings("POLICY-A held", root), [])            # the pseudonym itself is clean
        self.assertEqual(rd.findings("COMPONENT-1 was the cause", root), [])
    def test_a_mapped_real_value_is_not_a_finding_because_the_map_carries_it(self):
        root = fixture()
        self.assertEqual([f for f in rd.findings("Rule-16", root) if f[1] == "rule number"], [])
    def test_clean_assembled_prose_passes(self):
        self.assertEqual(rd.findings("2026-09: 12 incidents in SUBSYSTEM-3, 4 of one failure mode.", fixture()), [])
    def test_unmapped_lists_only_what_the_map_lacks(self):
        root = fixture()
        u = rd.unmapped("Rule-16 and Rule-20 and dyad/scripts/package.py", root)
        self.assertNotIn("Rule-16", u); self.assertIn("Rule-20", u)

class MapTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_absent_map_warns_and_never_fails(self):
        msgs = rd.check(fixture(map_text=None))
        self.assertTrue(all(m.startswith("warning:") for m in msgs), msgs)
    def test_reused_pseudonym_fails(self):
        root = fixture(MAP + "| `Rule-17` | POLICY-A | rule number | #166 |\n")
        self.assertTrue(any("is reused" in m for m in rd.check(root)), rd.check(root))
    def test_doubly_mapped_real_fails(self):
        root = fixture(MAP + "| `Rule-16` | POLICY-B | rule number | #166 |\n")
        self.assertTrue(any("mapped twice" in m for m in rd.check(root)), rd.check(root))
    def test_live_check_passes(self):
        msgs = [m for m in rd.check(dyadlib.repo_root()) if not m.startswith("warning:")]
        self.assertEqual(msgs, [], msgs)

class CliTests(unittest.TestCase):
    def _run(self, *a):
        return subprocess.run([sys.executable, str(CRAFT / "scripts" / "redaction.py"), *a],
                              capture_output=True, text=True, cwd=dyadlib.repo_root(),
                              env={**os.environ, "DYAD_NO_NESTED_TESTS": "1"})
    def test_verify_refuses_a_leak_and_passes_clean_text(self):
        bad = self._run("verify", "the host is " + LAN)
        self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
        self.assertIn("class A", bad.stderr)
        good = self._run("verify", "12 incidents in SUBSYSTEM-3")
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertIn("gate passes", good.stdout)
    def test_verify_without_a_file_is_usage(self):
        self.assertEqual(self._run("verify").returncode, 2)
    def test_check_cli_is_zero_here(self):
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ok   [redaction]", r.stdout)

if __name__ == "__main__":
    unittest.main()
