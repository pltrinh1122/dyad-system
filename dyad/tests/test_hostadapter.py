"""hostadapter.py (crafts/syseng/rules/host-facts.md, d-work #179): `resolve` collapses a symlink (a
real one, built here — the one host fact this Linux kernel can exercise directly, standing in for
the macOS /var -> /private/var case G5 was actually about) and is otherwise a plain passthrough to
Path.resolve(); `ignore_patterns` derives from package_rules.txt's generated: entries, never a
hand-copied list, and its gitignore translation is checked against all three pattern shapes;
`write_gitignore` seeds once and never overwrites."""
import json, os, shutil, sys, tempfile, unittest
from unittest import mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import hostadapter


class ResolveTests(unittest.TestCase):
    def test_resolve_collapses_a_symlink(self):
        d = Path(tempfile.mkdtemp())
        real = d / "real"; real.mkdir()
        link = d / "link"; link.symlink_to(real, target_is_directory=True)
        self.assertEqual(hostadapter.resolve(link), real.resolve())
        self.assertNotEqual(hostadapter.resolve(link), link)   # the symlink is not its own resolution
        shutil.rmtree(d, ignore_errors=True)
    def test_resolve_matches_path_resolve(self):
        """No behavior change, only relocation: hostadapter.resolve is Path(...).resolve()."""
        self.assertEqual(hostadapter.resolve(__file__), Path(__file__).resolve())
        self.assertEqual(hostadapter.resolve("."), Path(".").resolve())


class ToGitignoreTests(unittest.TestCase):
    """The translation d-work #179's G9 fix depends on: check_generated matches a `generated:`
    pattern at any path depth (component-wise); the gitignore line it produces must match at the
    same depths, which gitignore's own anchoring rule does not do for free (a bare `dir/*` or
    `sub/*.log` is anchored to the .gitignore's own directory unless made unanchored)."""
    def test_dir_star_becomes_trailing_slash_unanchored(self):
        self.assertEqual(hostadapter._to_gitignore("__pycache__/*"), "__pycache__/")
        self.assertEqual(hostadapter._to_gitignore("projections/*"), "projections/")
    def test_slash_free_pattern_is_untouched(self):
        self.assertEqual(hostadapter._to_gitignore("*.pyc"), "*.pyc")
        self.assertEqual(hostadapter._to_gitignore("LEDGER.md"), "LEDGER.md")
    def test_interior_slash_gets_any_depth_prefix(self):
        self.assertEqual(hostadapter._to_gitignore("ops/*.log"), "**/ops/*.log")


class IgnorePatternsTests(unittest.TestCase):
    def test_matches_live_package_rules_generated_entries(self):
        raw = {l.partition(":")[2].strip() for l in (PKG / "scripts" / "package_rules.txt").read_text().splitlines()
               if l.strip().startswith("generated:")}
        got = hostadapter.ignore_patterns(PKG.parent)
        self.assertEqual(set(got), {hostadapter._to_gitignore(p) for p in raw})
        self.assertIn("*.pyc", got); self.assertIn("__pycache__/", got)
        self.assertIn("LEDGER.md", got); self.assertIn("projections/", got); self.assertIn("**/ops/*.log", got)
    def test_sorted_and_deduplicated(self):
        got = hostadapter.ignore_patterns(PKG.parent)
        self.assertEqual(got, sorted(set(got)))
    def test_absent_package_rules_file_yields_empty(self):
        d = Path(tempfile.mkdtemp())
        self.assertEqual(hostadapter.ignore_patterns(d), [])
        shutil.rmtree(d, ignore_errors=True)


class WriteGitignoreTests(unittest.TestCase):
    def test_writes_from_live_patterns(self):
        d = Path(tempfile.mkdtemp())
        (d / "dyad" / "scripts").mkdir(parents=True)
        shutil.copy(PKG / "scripts" / "package_rules.txt", d / "dyad" / "scripts" / "package_rules.txt")
        self.assertTrue(hostadapter.write_gitignore(d))
        text = (d / ".gitignore").read_text()
        for p in hostadapter.ignore_patterns(d):
            self.assertIn(p, text)
        shutil.rmtree(d, ignore_errors=True)
    def test_never_overwrites_existing_content(self):
        d = Path(tempfile.mkdtemp())
        (d / ".gitignore").write_text("custom\n")
        self.assertFalse(hostadapter.write_gitignore(d))
        self.assertEqual((d / ".gitignore").read_text(), "custom\n")
        shutil.rmtree(d, ignore_errors=True)
    def test_no_patterns_writes_nothing(self):
        d = Path(tempfile.mkdtemp())   # no dyad/scripts/package_rules.txt here
        self.assertFalse(hostadapter.write_gitignore(d))
        self.assertFalse((d / ".gitignore").exists())
        shutil.rmtree(d, ignore_errors=True)




class SessionTitleTests(unittest.TestCase):
    """d-work #350: the Operator's own name for a harness session, read where the harness records it."""
    def _config(self, td, sessions=(), titles=()):
        base = Path(td)
        (base / "sessions").mkdir()
        for name, rec in sessions:
            (base / "sessions" / name).write_text(rec if isinstance(rec, str) else json.dumps(rec))
        for holder, rec in titles:
            d = base / "projects" / "slug" / holder
            d.mkdir(parents=True)
            (d / "custom-title.json").write_text(json.dumps(rec))
        return base
    def test_reads_the_user_named_pid_record(self):
        with tempfile.TemporaryDirectory() as td:
            base = self._config(td, sessions=[("1.json", {"sessionId": "S", "name": "cab-1: terminal (ds)", "nameSource": "user", "nameSince": 5})])
            self.assertEqual(hostadapter.session_title("S", base), "cab-1: terminal (ds)")
    def test_a_name_the_harness_generated_is_not_the_operators(self):
        with tempfile.TemporaryDirectory() as td:
            base = self._config(td, sessions=[("1.json", {"sessionId": "S", "name": "fix the bug", "nameSource": "auto", "nameSince": 5})])
            self.assertIsNone(hostadapter.session_title("S", base))
    def test_the_latest_rename_across_pids_wins(self):
        with tempfile.TemporaryDirectory() as td:
            base = self._config(td, sessions=[
                ("1.json", {"sessionId": "S", "name": "old", "nameSource": "user", "nameSince": 5}),
                ("2.json", {"sessionId": "S", "name": "new", "nameSource": "user", "nameSince": 9}),
                ("3.json", {"sessionId": "OTHER", "name": "other", "nameSource": "user", "nameSince": 99})])
            self.assertEqual(hostadapter.session_title("S", base), "new")
    def test_falls_back_to_custom_title(self):
        with tempfile.TemporaryDirectory() as td:
            base = self._config(td, titles=[("S", {"customTitle": "from the file"})])
            self.assertEqual(hostadapter.session_title("S", base), "from the file")
    def test_malformed_missing_and_unsafe_give_none_not_an_error(self):
        with tempfile.TemporaryDirectory() as td:
            base = self._config(td, sessions=[("1.json", "{not json")])
            self.assertIsNone(hostadapter.session_title("S", base))
            self.assertIsNone(hostadapter.session_title("", base))
            self.assertIsNone(hostadapter.session_title("../x", base))
            self.assertIsNone(hostadapter.session_title(".hidden", base))
        self.assertIsNone(hostadapter.session_title("S", Path(td) / "does-not-exist"))
    def test_a_title_is_one_bounded_line(self):
        with tempfile.TemporaryDirectory() as td:
            base = self._config(td, sessions=[("1.json", {"sessionId": "S", "name": "a\nb: c\n" + "z" * 500, "nameSource": "user"})])
            got = hostadapter.session_title("S", base)
            self.assertNotIn("\n", got)
            self.assertLessEqual(len(got), hostadapter.TITLE_MAX)
            self.assertTrue(got.startswith("a b: c "))
    def test_environment_selects_the_config_dir(self):
        with tempfile.TemporaryDirectory() as td:
            base = self._config(td, titles=[("S", {"customTitle": "via env"})])
            with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": str(base)}):
                self.assertEqual(hostadapter.session_title("S"), "via env")


if __name__ == "__main__":
    unittest.main()
