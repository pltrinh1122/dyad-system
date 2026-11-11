"""scripts/tidy.py (the cabinet craft's unit and session census; d-work #640, #669): each of the six classes over a
fixture store of presence files, rows and a mandates table; the window read from `attendance-window`; the account
list from a file, its repository column read; each class's act and the record's order; a session on another
repository, or on none, counted outside and never listed, unless a presence file names it; the count lines and the
batch question; the record is the master of the acts; it never fails and writes nothing."""
import contextlib, datetime, io, json, os, shutil, sys, tempfile, unittest, unittest.mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))
import dyadlib
tidy = dyadlib.load_module(Path(__file__).resolve().parents[1] / "scripts" / "tidy.py", "cabinet_tidy")
NOW = datetime.datetime(2026, 11, 8, 12, 0, tzinfo=datetime.UTC)
FRESH, OLD = "2026-11-07T12:00:00+00:00", "2026-10-01T00:00:00+00:00"
ROW = "id: {id}\ntitle: t{id}\nopened: 2026-10-01\nstate: {state}\ndisposed: 2026-10-01 Y plan\nrefs: \n"
MANDATES = ("| seat | function | domain | fence | ceiling | escalations | revocation |\n|---|---|---|---|---|---|---|\n"
            "| program-aaaaaaaa | program | d | f | 1 | e | r |\n| orchestrate-<hp> | orchestrate | d | f | 0 | e | r |\n")


class CensusTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus"}); e.start(); self.addCleanup(e.stop)
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, True)
        self.sessions = self.root / "agent-corpus" / "d-work" / "sessions"; self.sessions.mkdir(parents=True)
        rows = self.root / "agent-corpus" / "d-work" / "rows"; rows.mkdir(parents=True)
        for rid, state in ((1, "open"), (2, "planned"), (3, "done"), (4, "archived")):
            (rows / f"{rid}.md").write_text(ROW.format(id=rid, state=state))
        (self.root / "preferences-corpus").mkdir(); (self.root / "preferences-corpus" / "MANDATES.md").write_text(MANDATES)

    def unit(self, name, seen=FRESH, rows="", holder=None):
        (self.sessions / f"{name}.md").write_text(f"session: {name}\nseen: {seen}\nroot: /r\nrows: {rows}\nfiles: \n"
                                                  + (f"holder: {holder}\n" if holder else ""))

    def census(self, harness=(), repo="o/dyad-system", outside=None):
        return {c["unit"]: c for c in tidy.census(self.root, list(harness), NOW, repo=repo, outside=outside)}

    def test_each_class(self):
        self.unit("program-aaaaaaaa")                                   # chartered by name, fresh
        self.unit("orchestrate-bbbbbbbb", rows="3")                     # chartered by its form, fresh
        self.unit("engineer-ledger-cccccccc", rows="1")                 # a desk holding an open row, fresh
        self.unit("counsel-dddddddd", seen=OLD, rows="2 3")             # an open (planned) row, past the window
        self.unit("audit-eeeeeeee", seen=OLD, rows="3 4")               # every row terminal
        self.unit("cab-2", seen=OLD)                                    # no row
        self.unit("engineer-done-ffffffff", rows="3")                   # a desk within the window, nothing open: the default
        self.unit("communicate-abababab", rows="1")                     # within the window, no charter row, no desk
        got = self.census([{"id": "99999999-0000", "title": "communicate-99999999: cloud (dyad-system)"},
                           {"id": "aaaaaaaa-1111", "title": "program-aaaaaaaa: cloud"}])
        self.assertEqual({u: c["class"] for u, c in got.items()},
                         {"program-aaaaaaaa": "live-seat", "orchestrate-bbbbbbbb": "live-seat",
                          "engineer-ledger-cccccccc": "live-desk", "counsel-dddddddd": "neglected",
                          "audit-eeeeeeee": "done", "cab-2": "stale", "engineer-done-ffffffff": "unclassed",
                          "communicate-abababab": "unclassed",
                          "99999999-0000": "never-registered"})
        self.assertEqual({u: c["act"] for u, c in got.items()},
                         {"program-aaaaaaaa": "keep", "orchestrate-bbbbbbbb": "keep", "engineer-ledger-cccccccc": "keep",
                          "counsel-dddddddd": "re-home", "audit-eeeeeeee": "archive", "cab-2": "archive",
                          "engineer-done-ffffffff": "keep", "communicate-abababab": "keep",
                          "99999999-0000": "archive"})
        self.assertEqual(got["orchestrate-bbbbbbbb"]["charter"], "yes")
        self.assertEqual(got["counsel-dddddddd"]["charter"], "no")

    def test_the_window_is_the_attendance_window(self):
        self.unit("program-aaaaaaaa", seen="2026-11-03T12:00:00+00:00")   # 5 days old
        self.assertEqual(self.census()["program-aaaaaaaa"]["class"], "live-seat")
        (self.root / "preferences-corpus" / "PREFERENCES.md").write_text(
            "| key | value | allowed | read by |\n|---|---|---|---|\n| attendance-window | 3 | n | Rule-16 |\n")
        self.assertEqual(self.census()["program-aaaaaaaa"]["class"], "stale")

    def test_a_holder_or_a_title_registers_a_harness_session(self):
        self.unit("counsel-dddddddd", holder="dddddddd-1c5b")
        got = self.census([{"id": "dddddddd-1c5b-5779", "title": ""}, {"id": "12345678-x", "title": "counsel-dddddddd: cloud"}])
        self.assertEqual(sorted(got), ["counsel-dddddddd"])

    def test_order_lines_and_counts(self):
        self.unit("program-aaaaaaaa"); self.unit("cab-2", seen=OLD); self.unit("audit-eeeeeeee", seen=OLD, rows="3")
        rows = tidy.census(self.root, [], NOW, repo="o/dyad-system")
        self.assertEqual([c["class"] for c in rows], ["done", "stale", "live-seat"])
        self.assertEqual(tidy.line(rows[0]), f"archive done audit-eeeeeeee seen={OLD} rows=3 charter=no holder=-")
        self.assertEqual(tidy.question(rows), "question: Y/N: tidy audit-eeeeeeee: archive, cab-2: archive?")
        self.assertEqual(tidy.question(rows[2:]), "question: none (nothing to propose)")
        self.assertEqual(tidy.counts(rows), "census: 3 session(s); done 1, stale 1, never-registered 0, live-seat 1, "
                                            "neglected 0, live-desk 0, unclassed 0")
        self.assertTrue(tidy.counts(rows[2:]).endswith("; pass"))

    def test_main_reads_a_harness_file_and_writes_nothing(self):
        self.unit("program-aaaaaaaa")
        h = self.root / "harness.txt"; h.write_text("# transcribed from the app\n77777777-aaaa some title\n\n"
                                                    "88888888-bbbb other/repo secret title\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), unittest.mock.patch.object(tidy, "census", wraps=tidy.census) as c:
            self.assertEqual(tidy.main([str(self.root), "--harness", str(h)]), 0)
        self.assertEqual(c.call_args.args[1], [{"id": "77777777-aaaa", "repo": None, "has_repo": False, "title": "some title"},
                                               {"id": "88888888-bbbb", "repo": "other/repo", "has_repo": True, "title": "secret title"}])
        self.assertIn("archive never-registered 77777777-aaaa ", out.getvalue())
        self.assertIn("\noutside: 1 sessions (not this system's; not read)\n", out.getvalue())
        self.assertNotIn("88888888", out.getvalue()); self.assertNotIn("secret", out.getvalue())
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(tidy.main([str(self.root), "--harness", str(self.root / "none.txt")]), 1)
            self.assertEqual(tidy.main([str(self.root), "--harness"]), 1)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["agent-corpus", "harness.txt", "preferences-corpus"])

    def test_the_repository_column_draws_the_boundary(self):
        """#669: a session on another repository, or on none, that no presence file names, is outside: counted, never
        listed; one a presence file names by holder is this system's whatever its repository; one on this repository
        with no presence file is never-registered and archived; a list with no column is read as before."""
        self.unit("counsel-dddddddd", holder="dddddddd-1c5b")
        out = []
        got = self.census([{"id": "aaaa1111-x", "repo": "someone/else", "has_repo": True, "title": "a private project"},
                           {"id": "bbbb2222-x", "repo": None, "has_repo": True, "title": "no repo"},
                           {"id": "dddddddd-1c5b-5779", "repo": "someone/else", "has_repo": True, "title": "counsel-dddddddd: x"},
                           {"id": "cccc3333-x", "repo": "o/dyad-system", "has_repo": True, "title": ""},
                           {"id": "eeee4444-x", "repo": None, "has_repo": False, "title": "transcribed"}], outside=out)
        self.assertEqual(sorted(got), ["cccc3333-x", "counsel-dddddddd", "eeee4444-x"])
        self.assertEqual(sorted(out), ["aaaa1111-x", "bbbb2222-x"])
        self.assertEqual((got["cccc3333-x"]["class"], got["cccc3333-x"]["act"]), ("never-registered", "archive"))
        self.assertEqual(got["eeee4444-x"]["class"], "never-registered")              # no column: read as before
        self.assertEqual(tidy.outside_line(len(out)), "outside: 2 sessions (not this system's; not read)")

    def test_a_title_that_differs_retitles_a_kept_unit(self):
        self.unit("program-aaaaaaaa", holder="aaaaaaaa-1111")
        got = self.census([{"id": "aaaaaaaa-1111-2222", "repo": "o/dyad-system", "has_repo": True, "title": "General coding session"}])
        self.assertEqual((got["program-aaaaaaaa"]["class"], got["program-aaaaaaaa"]["act"]), ("live-seat", "retitle"))
        got = self.census([{"id": "aaaaaaaa-1111-2222", "repo": "o/dyad-system", "has_repo": True, "title": "program-aaaaaaaa: cloud"}])
        self.assertEqual(got["program-aaaaaaaa"]["act"], "keep")

    def test_read_harness_reads_both_forms(self):
        h = self.root / "a.txt"
        h.write_text("1111-a o/dyad-system program-aaaaaaaa: cloud\n2222-b - untitled\n3333-c plain title words\n4444-d\n")
        self.assertEqual([(e["id"], e["repo"], e["has_repo"], e["title"]) for e in tidy.read_harness(h)],
                         [("1111-a", "o/dyad-system", True, "program-aaaaaaaa: cloud"), ("2222-b", None, True, "untitled"),
                          ("3333-c", None, False, "plain title words"), ("4444-d", None, False, "")])

    def test_the_record_is_the_master(self):
        self.assertFalse(hasattr(tidy, "check_package"))               # a script, no guard: nothing discovers it
        codes = tidy.record_codes()
        if codes is None:
            self.skipTest("the master record crafts/cabinet/dmc/session-tidy.jsonld is not on this tree yet")
        self.assertEqual(set(codes), set(tidy.ACTS))
        self.assertTrue(set(tidy.ACT_OF.values()) <= set(codes))
        self.assertEqual(tidy.PROPOSE, ("archive", "retire", "re-home", "retitle", "register"))
        rec = tidy.record_codes(self.root / "absent.jsonld")
        self.assertIsNone(rec)


if __name__ == "__main__":
    unittest.main()
