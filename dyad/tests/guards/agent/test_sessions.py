"""Session presence guard tests (agent/sessions.py, Rule-16): the store shape check (missing
fields, an unparseable `seen`), touch's write/refresh/dedup behaviour, the `DYAD_SESSION` id vs
the random fallback, staleness, file-overlap detection, and files_touched's plan-line parser."""
import os, sys, tempfile, unittest
from unittest import mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
sv = dyadlib.load_guard("agent", "sessions")

def repo():
    root = Path(tempfile.mkdtemp())
    (root / "agent-corpus" / "d-work" / "sessions").mkdir(parents=True)
    return root

class ContractTests(unittest.TestCase):
    def test_shape(self):
        self.assertEqual((sv.ENTITY, sv.CORPUS, sv.TRANSACTION), ("presence", "agent", False))
        self.assertEqual(sv.FIELDS, ("session", "seen", "root", "rows", "files"))

class CheckTests(unittest.TestCase):
    def test_good_record_passes(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "s1.md").write_text(
            "session: s1\nseen: 2026-09-14T10:00:00+00:00\nroot: /tmp/x\nrows: 1 2\nfiles: a.py b.py\n")
        self.assertEqual(sv.check_package(root), [])
    def test_missing_field_fails(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "s1.md").write_text("session: s1\nseen: 2026-09-14T10:00:00+00:00\n")
        msgs = sv.check_package(root)
        self.assertTrue(any("rows" in m and "missing" in m for m in msgs))
        self.assertTrue(any("files" in m and "missing" in m for m in msgs))
    def test_bad_timestamp_fails(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "s1.md").write_text(
            "session: s1\nseen: not-a-date\nroot: /tmp/x\nrows: \nfiles: \n")
        self.assertIn("not an ISO-8601 timestamp", " ".join(sv.check_package(root)))
    def test_empty_store_passes(self):
        self.assertEqual(sv.check_package(repo()), [])

class TouchTests(unittest.TestCase):
    def test_writes_and_refreshes(self):
        root = repo()
        os.environ["DYAD_SESSION"] = "test-session-a"
        try:
            p1 = sv.touch(root, ["3"], ["x.py"])
            self.assertEqual(p1.name, "test-session-a.md")
            f1 = sv.parse(p1.read_text())
            self.assertEqual(f1["rows"], "3"); self.assertEqual(f1["files"], "x.py")
            p2 = sv.touch(root, ["4"], ["y.py"])
            f2 = sv.parse(p2.read_text())
            self.assertEqual(f2["rows"], "3 4")   # accumulates, dedups
            self.assertEqual(f2["files"], "x.py y.py")
            self.assertTrue(f2["seen"])   # re-written each call (equality is a timing artefact, not asserted)
        finally:
            del os.environ["DYAD_SESSION"]
    def test_dedup(self):
        root = repo()
        os.environ["DYAD_SESSION"] = "test-session-b"
        try:
            sv.touch(root, ["1"], ["a.py"])
            p = sv.touch(root, ["1"], ["a.py"])
            self.assertEqual(sv.parse(p.read_text())["rows"], "1")
            self.assertEqual(sv.parse(p.read_text())["files"], "a.py")
        finally:
            del os.environ["DYAD_SESSION"]
    def test_unset_session_gets_a_fresh_id_each_time(self):
        root = repo()
        os.environ.pop("DYAD_SESSION", None)
        p1 = sv.touch(root, [], []); p2 = sv.touch(root, [], [])
        self.assertNotEqual(p1.name, p2.name)   # never silently overwrites another's file
    def test_bad_session_id_falls_back(self):
        root = repo()
        os.environ["DYAD_SESSION"] = "has a space/slash"
        try:
            p = sv.touch(root, [], [])
            self.assertNotIn("has a space", p.name)
        finally:
            del os.environ["DYAD_SESSION"]

class StaleTests(unittest.TestCase):
    def test_fresh_is_not_stale(self):
        import datetime
        now = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
        self.assertFalse(sv.is_stale(now))
    def test_old_is_stale(self):
        self.assertTrue(sv.is_stale("2020-01-01T00:00:00+00:00"))
    def test_garbage_is_stale(self):
        self.assertTrue(sv.is_stale("not-a-date"))

class OverlapTests(unittest.TestCase):
    def test_finds_overlap(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "other.md").write_text(
            "session: other\nseen: 2026-09-14T10:00:00+00:00\nrows: 9\nfiles: dyad/guards/agent/provenance.py\n")
        hits = sv.overlaps(root, {"dyad/guards/agent/provenance.py", "dyad/rules/RULE-7-provenance.md"})
        self.assertEqual(hits, [("other", {"dyad/guards/agent/provenance.py"})])
    def test_no_overlap(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "other.md").write_text(
            "session: other\nseen: 2026-09-14T10:00:00+00:00\nrows: 9\nfiles: unrelated.py\n")
        self.assertEqual(sv.overlaps(root, {"x.py"}), [])
    def test_excludes_self(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "me.md").write_text(
            "session: me\nseen: 2026-09-14T10:00:00+00:00\nrows: 1\nfiles: x.py\n")
        self.assertEqual(sv.overlaps(root, {"x.py"}, exclude="me"), [])

def _now():
    return sv.datetime.datetime.now(sv.datetime.UTC).isoformat(timespec="seconds")

class SameRootTests(unittest.TestCase):
    def test_finds_a_live_session_sharing_root(self):
        root = repo()
        me = str(root.resolve())
        (root / "agent-corpus" / "d-work" / "sessions" / "other.md").write_text(
            f"session: other\nseen: {_now()}\nroot: {me}\nrows: \nfiles: \n")
        self.assertEqual(sv.same_root(root), ["other"])
    def test_different_root_not_flagged(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "other.md").write_text(
            f"session: other\nseen: {_now()}\nroot: /somewhere/else\nrows: \nfiles: \n")
        self.assertEqual(sv.same_root(root), [])
    def test_stale_same_root_not_flagged(self):
        root = repo()
        me = str(root.resolve())
        (root / "agent-corpus" / "d-work" / "sessions" / "other.md").write_text(
            f"session: other\nseen: 2020-01-01T00:00:00+00:00\nroot: {me}\nrows: \nfiles: \n")
        self.assertEqual(sv.same_root(root), [])
    def test_excludes_self(self):
        root = repo()
        me = str(root.resolve())
        (root / "agent-corpus" / "d-work" / "sessions" / "me.md").write_text(
            f"session: me\nseen: {_now()}\nroot: {me}\nrows: \nfiles: \n")
        self.assertEqual(sv.same_root(root, exclude="me"), [])
    def test_touch_records_root(self):
        root = repo()
        import os
        os.environ["DYAD_SESSION"] = "test-root-session"
        try:
            p = sv.touch(root, [], [])
            self.assertEqual(sv.parse(p.read_text())["root"], str(root.resolve()))
        finally:
            del os.environ["DYAD_SESSION"]

class FilesTouchedTests(unittest.TestCase):
    def test_parses_the_plan_line(self):
        text = "# Plan #7\n\nsome prose\n\nfiles touched: dyad/scripts/a.py, dyad/tests/test_a.py\n"
        self.assertEqual(sv.files_touched(text), ["dyad/scripts/a.py", "dyad/tests/test_a.py"])
    def test_parses_the_annotated_form(self):
        text = "files touched (by zone): dyad/a.py\ncrafts/x/b.py\n"
        self.assertEqual(sv.files_touched(text), ["dyad/a.py", "crafts/x/b.py"])
    def test_brace_shorthand_dropped_not_garbled(self):
        # the exact shape that corrupted the real store the first time this ran (#185)
        text = "files touched: dyad/a.py, dyad/tests/{test_x.py,guards/test_y.py} (new),\ndyad/falsification/rules/{rule-16,rule-3}*.md.\n"
        out = sv.files_touched(text)
        self.assertEqual(out, ["dyad/a.py"])
        self.assertTrue(all("{" not in t and "}" not in t for t in out))
    def test_no_line_yields_nothing(self):
        self.assertEqual(sv.files_touched("# Plan #7\n\nno such line here\n"), [])

class ListCLITests(unittest.TestCase):
    def test_list_runs(self):
        # `sessions.py`'s repo root comes from the script's own location (dyadlib.repo_root),
        # not from cwd, so this always reads the real workstation repo's own sessions/ — just
        # confirm the CLI runs cleanly and prints a recognisable shape either way.
        import subprocess
        env = dict(os.environ); env.pop("DYAD_SESSION", None)
        r = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[3] / "guards" / "agent" / "sessions.py"), "list"],
                            capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue("no session presence files" in r.stdout or "live" in r.stdout or "stale" in r.stdout)

class LiveTests(unittest.TestCase):
    def test_live_store_passes(self):
        # a fixed test id so repeated runs overwrite one file instead of littering the real
        # store with a fresh random one each time; removed afterward, never left behind.
        root = dyadlib.repo_root()
        os.environ["DYAD_SESSION"] = "livetest-check"
        try:
            sv.touch_from_open_rows(root)
            self.assertEqual(sv.check_package(root), [])
        finally:
            del os.environ["DYAD_SESSION"]
            p = sv.sessions_dir(root) / "livetest-check.md"
            if p.exists(): p.unlink()


if __name__ == "__main__":
    unittest.main()

class DescribeTests(unittest.TestCase):
    def test_fields_are_six_tuples_in_FIELDS_order(self):
        d = sv.describe(dyadlib.repo_root())
        self.assertEqual([f[0] for f in d["fields"]], list(sv.FIELDS))
        for f in d["fields"]:
            self.assertIsInstance(f, tuple); self.assertEqual(len(f), 6)
    def test_absolute_instance_outside_root_does_not_raise(self):
        # pathlib joins an absolute DYAD_INSTANCE by discarding root; describe() must report it as given, not raise
        inst = Path(tempfile.mkdtemp()); root = Path(tempfile.mkdtemp())
        with mock.patch.dict(os.environ, {"DYAD_INSTANCE": str(inst)}):
            d = sv.describe(root)
        self.assertTrue(d["store"].startswith(str(inst)))

