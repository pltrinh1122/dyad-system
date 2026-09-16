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
