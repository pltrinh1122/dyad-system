import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
bd = dyadlib.load_guard("infra", "bundle")

BUNDLE = """version: 0.5.0

| component | version |
|-----------|---------|
| dyad-operator | 0.5.0 |
| sysarch | 0.1.1 |
| syseng | 0.1.2 |
"""
LIVE = {"dyad-operator": "0.5.0", "sysarch": "0.1.1", "syseng": "0.1.2"}

def tree():
    """A tmp (pkg, root) pair: pkg/VERSION plus pkg.parent/crafts/<name>/VERSION for LIVE, and pkg
    is itself under root so `bundle_path(root)` and `pkg` agree on one tree, as the real repo does."""
    d = Path(tempfile.mkdtemp())
    pkg = d / "dyad"; pkg.mkdir()
    (pkg / "VERSION").write_text(LIVE["dyad-operator"] + "\n")
    crafts = d / "crafts"
    for name, ver in LIVE.items():
        if name == "dyad-operator":
            continue
        c = crafts / name; c.mkdir(parents=True)
        (c / "VERSION").write_text(ver + "\n")
    return d, pkg

class BundleTests(unittest.TestCase):
    def test_parse(self):
        version, rows = bd.parse(BUNDLE)
        self.assertEqual(version, "0.5.0")
        self.assertEqual(rows, [("dyad-operator", "0.5.0"), ("sysarch", "0.1.1"), ("syseng", "0.1.2")])
    def test_parse_no_version_line(self):
        version, rows = bd.parse(BUNDLE.split("\n\n", 1)[1])
        self.assertEqual(version, "")
        self.assertEqual(len(rows), 3)
    def test_check_passes(self):
        version, rows = bd.parse(BUNDLE)
        self.assertEqual(bd.check(version, rows, LIVE), [])
    def test_check_no_version(self):
        self.assertIn("no `version:` line", bd.check("", [("dyad-operator", "0.5.0")], {"dyad-operator": "0.5.0"}))
    def test_check_version_mismatch(self):
        msgs = bd.check("0.5.0", [("sysarch", "0.1.0")], {"sysarch": "0.1.1"})
        self.assertEqual(len(msgs), 1); self.assertIn("names 0.1.0, the tree has 0.1.1", msgs[0])
    def test_check_unknown_component(self):
        msgs = bd.check("0.5.0", [("lan-git", "1.0.0")], {})
        self.assertIn("'lan-git': not a craft in this tree", msgs)
    def test_check_missing_row(self):
        msgs = bd.check("0.5.0", [], {"sysarch": "0.1.1"})
        self.assertIn("'sysarch' is in the tree but has no bundle row", msgs)
    def test_check_duplicate(self):
        msgs = bd.check("0.5.0", [("sysarch", "0.1.1"), ("sysarch", "0.1.1")], {"sysarch": "0.1.1"})
        self.assertIn("'sysarch': declared twice", msgs)
    def test_check_malformed_row(self):
        msgs = bd.check("0.5.0", [("", "0.1.1")], {})
        self.assertTrue(any("malformed" in m for m in msgs))
    def test_live_components(self):
        d, pkg = tree()
        try:
            self.assertEqual(bd.live_components(pkg), LIVE)
        finally:
            import shutil; shutil.rmtree(d, ignore_errors=True)
    def test_check_bundle_absent_skips(self):
        d, pkg = tree()
        try:
            self.assertEqual(bd.check_bundle(d, pkg), ("", [], []))
        finally:
            import shutil; shutil.rmtree(d, ignore_errors=True)
    def test_check_bundle_present_passes(self):
        d, pkg = tree()
        try:
            (d / "BUNDLE.md").write_text(BUNDLE)
            version, rows, msgs = bd.check_bundle(d, pkg)
            self.assertEqual(version, "0.5.0"); self.assertEqual(len(rows), 3); self.assertEqual(msgs, [])
        finally:
            import shutil; shutil.rmtree(d, ignore_errors=True)
    def test_check_package_delegates(self):
        d, pkg = tree()
        try:
            (d / "BUNDLE.md").write_text(BUNDLE.replace("0.1.1", "9.9.9"))
            msgs = bd.check_package(d, pkg)
            self.assertTrue(any("9.9.9" in m for m in msgs))
        finally:
            import shutil; shutil.rmtree(d, ignore_errors=True)
    def test_summary_no_bundle(self):
        d, pkg = tree()
        try:
            self.assertEqual(bd.summary(d), "no bundle")
        finally:
            import shutil; shutil.rmtree(d, ignore_errors=True)
    def test_describe(self):
        d, pkg = tree()
        try:
            (d / "BUNDLE.md").write_text(BUNDLE)
            desc = bd.describe(d, pkg)
            self.assertEqual(desc["store"], "BUNDLE.md"); self.assertEqual(desc["observed"], 3)
            self.assertEqual([f[0] for f in desc["fields"]], list(bd.FIELDS))
        finally:
            import shutil; shutil.rmtree(d, ignore_errors=True)
    def test_main_no_bundle_is_ok(self):
        # main()'s pkg is bundle.py's own default (dyadlib.PKG); the skip path never reads it,
        # so an empty root (no BUNDLE.md) is a clean 0 regardless of which tree main() defaults to.
        d, _pkg = tree()
        try:
            self.assertEqual(bd.main([str(d)]), 0)
        finally:
            import shutil; shutil.rmtree(d, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()


import subprocess
def git(root, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=root, capture_output=True, text=True, check=True).stdout.strip()

def repo():
    """`tree()` as a git repo with one commit and every component tagged at that commit (#91)."""
    root, pkg = tree()
    git(root, "init", "-q"); git(root, "add", "-A"); git(root, "commit", "-qm", "seed")
    for comp, ver in LIVE.items():
        git(root, "tag", bd.tag_name(comp, ver))
    return root, pkg

class DriftTests(unittest.TestCase):
    """#91: a craft's tree at HEAD must equal its own `<name>-v<VERSION>` tag's; absent tag skips."""
    def test_tag_name_and_invariant(self):
        self.assertEqual(bd.tag_name("dyad-operator", "0.6.2"), "dyad-operator-v0.6.2")
        self.assertEqual(bd.tag_name("sysarch", "0.1.5"), "sysarch-v0.1.5")
        self.assertEqual([n for n, f in bd.INVARIANTS if not f()], []); self.assertEqual(len(bd.INVARIANTS), 2)
    def test_component_roots(self):
        root, pkg = tree()
        self.assertEqual({k: v.as_posix() for k, v in bd.component_roots(root, pkg).items()},
                         {"dyad-operator": "dyad", "sysarch": "crafts/sysarch", "syseng": "crafts/syseng"})
    def test_unchanged_tree_is_silent(self):
        root, pkg = repo()
        self.assertEqual(bd.check_drift(root, pkg), [])
    def test_changed_file_under_a_tagged_craft_fails(self):
        root, pkg = repo()
        (root / "crafts" / "sysarch" / "rules.md").write_text("changed\n"); git(root, "add", "-A"); git(root, "commit", "-qm", "drift")
        msgs = bd.check_drift(root, pkg)
        self.assertEqual(len(msgs), 1); self.assertTrue(msgs[0].startswith("'sysarch': crafts/sysarch/ differs from tag sysarch-v0.1.1 (1 file(s)) while VERSION is still 0.1.1"), msgs)
        self.assertIn(msgs[0], bd.check_package(root, pkg))          # reaches the runner as a FAIL, not a warning
    def test_core_is_a_component_too(self):
        root, pkg = repo()
        (pkg / "rule.md").write_text("changed\n"); git(root, "add", "-A"); git(root, "commit", "-qm", "drift")
        msgs = bd.check_drift(root, pkg)
        self.assertEqual(len(msgs), 1); self.assertIn("'dyad-operator': dyad/ differs from tag dyad-operator-v0.5.0", msgs[0])
    def test_bumped_version_has_no_tag_yet_and_skips(self):
        root, pkg = repo()
        (root / "crafts" / "sysarch" / "rules.md").write_text("changed\n")
        (root / "crafts" / "sysarch" / "VERSION").write_text("0.1.2\n"); git(root, "add", "-A"); git(root, "commit", "-qm", "bump")
        msgs = bd.check_drift(root, pkg)
        self.assertEqual(msgs, ["warning: skip 'sysarch': no tag sysarch-v0.1.2 here (not yet released, or tags not fetched)"])
        self.assertEqual([m for m in bd.check_package(root, pkg) if not m.startswith("warning:")], [])
    def test_no_tags_at_all_skips_every_component(self):
        root, pkg = tree()
        git(root, "init", "-q"); git(root, "add", "-A"); git(root, "commit", "-qm", "seed")
        msgs = bd.check_drift(root, pkg)
        self.assertEqual(len(msgs), 3); self.assertTrue(all(m.startswith("warning: skip") for m in msgs))
    def test_no_commit_skips(self):
        root, pkg = tree(); git(root, "init", "-q")
        self.assertEqual(bd.check_drift(root, pkg), ["warning: skip drift: no HEAD commit here"])
    def test_cli_prints_warn_for_skip_and_exits_zero(self):
        root, pkg = repo()
        (root / "crafts" / "syseng" / "VERSION").write_text("0.1.3\n"); git(root, "add", "-A"); git(root, "commit", "-qm", "bump")
        (root / "BUNDLE.md").write_text(BUNDLE.replace("| syseng | 0.1.2 |", "| syseng | 0.1.3 |"))
        r = subprocess.run([sys.executable, str(Path(bd.__file__)), str(root)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("warn [bundle] skip 'syseng'", r.stdout); self.assertIn("ok   [bundle] 3 components", r.stdout)
