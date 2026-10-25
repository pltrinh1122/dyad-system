"""Session presence guard tests (agent/sessions.py, Rule-16): the store shape check (missing
fields, an unparseable `seen`), touch's write/refresh/dedup behaviour, the `DYAD_SESSION` id vs
the random fallback, staleness, file-overlap detection, the optional `host`/`holder` lines (#294),
and files_touched's plan-line parser; the seat name and its form under `organization` (#369 C7, d-work #379)."""
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

class WriterCollisionTests(unittest.TestCase):
    """F1 (d-work #32): two processes configured with the same DYAD_SESSION collide on one file
    despite the "only that session writes it" promise; `touch()` now detects a different, still-
    live `writer` already in the file and warns instead of silently unioning. Since d-work #350 the
    writer is the harness holder's stable id, so the comparison means a different *holder* and not a
    different `dyad` invocation."""
    def setUp(self):
        self._env = mock.patch.dict(os.environ)
        self._env.start()
        os.environ.pop("CLAUDE_CODE_SESSION_ID", None)   # the fallback path unless a test sets a holder
    def tearDown(self):
        self._env.stop()
    def test_different_live_writer_warns_and_does_not_union(self):
        root = repo()
        os.environ["DYAD_SESSION"] = "shared-name"
        try:
            (root / "agent-corpus" / "d-work" / "sessions" / "shared-name.md").write_text(
                f"session: shared-name\nseen: {_now()}\nroot: /tmp/x\nrows: 9\nfiles: other.py\n"
                f"writer: deadbeef0000\n")
            import io, contextlib
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                p = sv.touch(root, ["1"], ["mine.py"])
            fields = sv.parse(p.read_text())
            self.assertEqual(fields["rows"], "1")     # not unioned with the other writer's "9"
            self.assertEqual(fields["files"], "mine.py")
            self.assertEqual(fields["writer"], sv.writer())
            self.assertIn("different, still-live process", stderr.getvalue())
        finally:
            del os.environ["DYAD_SESSION"]
    def test_same_writer_reunites_silently(self):
        root = repo()
        os.environ["DYAD_SESSION"] = "shared-name-2"
        try:
            import io, contextlib
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                sv.touch(root, ["1"], ["a.py"])
                p = sv.touch(root, ["2"], ["b.py"])   # same process: same writer, must not warn
            fields = sv.parse(p.read_text())
            self.assertEqual(fields["rows"], "1 2")
            self.assertEqual(fields["files"], "a.py b.py")
            self.assertEqual(stderr.getvalue(), "")
        finally:
            del os.environ["DYAD_SESSION"]
    def test_stale_other_writer_is_unioned_not_warned(self):
        root = repo()
        os.environ["DYAD_SESSION"] = "shared-name-3"
        try:
            (root / "agent-corpus" / "d-work" / "sessions" / "shared-name-3.md").write_text(
                "session: shared-name-3\nseen: 2020-01-01T00:00:00+00:00\nroot: /tmp/x\n"
                "rows: 9\nfiles: other.py\nwriter: deadbeef0000\n")
            import io, contextlib
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                p = sv.touch(root, ["1"], ["mine.py"])
            fields = sv.parse(p.read_text())
            self.assertEqual(fields["rows"], "1 9")   # a stale writer is not "still-live": unioned as before
            self.assertEqual(stderr.getvalue(), "")
        finally:
            del os.environ["DYAD_SESSION"]
    def test_writer_field_is_this_processs_id(self):
        root = repo()
        os.environ["DYAD_SESSION"] = "writer-field-test"
        try:
            p = sv.touch(root, [], [])
            self.assertEqual(sv.parse(p.read_text())["writer"], sv._PROCESS)
        finally:
            del os.environ["DYAD_SESSION"]

    def test_writer_is_the_holders_stable_id_when_the_harness_names_one(self):
        root = repo()
        os.environ["DYAD_SESSION"] = "holder-writer"; os.environ["CLAUDE_CODE_SESSION_ID"] = "sess-A"
        try:
            self.assertEqual(sv.writer(), "sess-A")
            self.assertEqual(sv.parse(sv.touch(root, [], []).read_text())["writer"], "sess-A")
        finally:
            del os.environ["DYAD_SESSION"]
    def test_same_holder_in_a_different_process_is_silent(self):
        # d-work #350: the case the per-process uuid got wrong — a session's own next `dyad` command
        root = repo()
        os.environ["DYAD_SESSION"] = "same-holder"; os.environ["CLAUDE_CODE_SESSION_ID"] = "sess-A"
        try:
            import io, contextlib
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with mock.patch.object(sv, "_PROCESS", "aaaaaaaaaaaa"):
                    sv.touch(root, ["1"], ["a.py"])
                with mock.patch.object(sv, "_PROCESS", "bbbbbbbbbbbb"):   # another process, same holder
                    p = sv.touch(root, ["2"], ["b.py"])
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(sv.parse(p.read_text())["rows"], "1 2")
        finally:
            del os.environ["DYAD_SESSION"]
    def test_a_different_holder_warns_and_is_not_unioned(self):
        root = repo()
        os.environ["DYAD_SESSION"] = "two-holders"; os.environ["CLAUDE_CODE_SESSION_ID"] = "sess-B"
        try:
            (root / "agent-corpus" / "d-work" / "sessions" / "two-holders.md").write_text(
                f"session: two-holders\nseen: {_now()}\nroot: /tmp/x\nrows: 9\nfiles: other.py\nwriter: sess-A\n")
            import io, contextlib
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                p = sv.touch(root, ["1"], ["mine.py"])
            self.assertIn("different, still-live process", stderr.getvalue())
            self.assertIn("sess-A", stderr.getvalue())
            self.assertEqual(sv.parse(p.read_text())["rows"], "1")
        finally:
            del os.environ["DYAD_SESSION"]
    def test_without_a_holder_the_writer_falls_back_to_the_process_id(self):
        self.assertNotIn("CLAUDE_CODE_SESSION_ID", os.environ)
        self.assertEqual(sv.writer(), sv._PROCESS)

class SelfExclusionCLITests(unittest.TestCase):
    def test_touch_cli_never_warns_about_its_own_file(self):
        """F4 (d-work #32): `main()`'s touch handler passed a *fresh* `session_id()` call as
        `same_root`'s `exclude`, which — with DYAD_SESSION unset — almost never matched the id
        the file was actually written under, so a session's very first `dyad session touch`
        warned about itself. Runs `main()` itself (not `touch()` directly), with `repo_root`
        mocked to a scratch tree so the CLI's own code path is exercised without touching the
        real corpus."""
        import io, contextlib
        root = repo()
        os.environ.pop("DYAD_SESSION", None)
        with mock.patch.object(sv.dyadlib, "repo_root", return_value=root):
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                rc = sv.main(["touch", "-r", "1"])
        self.assertEqual(rc, 0)
        self.assertNotIn("same working tree", stdout.getvalue() + stderr.getvalue())
        files = list((root / "agent-corpus" / "d-work" / "sessions").glob("*.md"))
        self.assertEqual(len(files), 1, files)   # the CLI's own file, correctly excluded from its own check

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
    def _other(self, root, host=None, holder=None):
        (root / "agent-corpus" / "d-work" / "sessions" / "other.md").write_text(
            f"session: other\nseen: {_now()}\nroot: {root.resolve()}\nrows: \nfiles: \n"
            + (f"host: {host}\n" if host else "") + (f"holder: {holder}\n" if holder else ""))
    def test_separate_cloud_containers_do_not_share_a_root(self):
        """#434, the operate seat's report: one path in two cloud containers is two filesystems."""
        cases = [  # (my host, my holder, other host, other holder, flagged)
            ("cloud linux x86_64", "aaaa", "cloud linux x86_64", "bbbb", False),   # two containers
            ("cloud linux x86_64", "aaaa", "cloud linux x86_64", "aaaa", True),    # one holder, one container
            ("cloud linux x86_64", "aaaa", "cloud linux x86_64", None, True),      # cannot tell: warn
            ("terminal linux x86_64", "aaaa", "terminal linux x86_64", "bbbb", True),   # one machine, two sessions
            ("terminal macos arm64", "aaaa", "terminal linux x86_64", "aaaa", False),   # two machines
        ]
        for mine, my_holder, other, other_holder, flagged in cases:
            with self.subTest(mine=mine, other=other, other_holder=other_holder):
                root = repo(); self._other(root, other, other_holder)
                with mock.patch.object(sv, "host_line", return_value=mine), mock.patch.object(sv, "holder", return_value=my_holder):
                    self.assertEqual(sv.same_root(root), ["other"] if flagged else [])
    def test_touch_records_root(self):
        root = repo()
        import os
        os.environ["DYAD_SESSION"] = "test-root-session"
        try:
            p = sv.touch(root, [], [])
            self.assertEqual(sv.parse(p.read_text())["root"], str(root.resolve()))
        finally:
            del os.environ["DYAD_SESSION"]

class HostAndHolderTests(unittest.TestCase):
    """d-work #294: `touch()` writes `host: <kernel> <os> <arch>` from the environment and
    `holder: <harness session id>` when `CLAUDE_CODE_SESSION_ID` is set; the check judges both
    only when present — exactly as the optional `writer` field — and never fails an absent one."""
    def _touch(self, env: dict[str, str]) -> dict[str, str]:
        root = repo()
        with mock.patch.dict(os.environ, {"DYAD_SESSION": "host-test", **env}):
            for k in ("CLAUDE_CODE_REMOTE", "CLAUDE_CODE_SESSION_ID"):
                if k not in env:
                    os.environ.pop(k, None)
            p = sv.touch(root, [], [])
        return sv.parse(p.read_text())
    def test_touch_writes_host_cloud_when_harness_reports_remote(self):
        f = self._touch({"CLAUDE_CODE_REMOTE": "true"})
        toks = f["host"].split()
        self.assertEqual(len(toks), 3)
        self.assertEqual(toks[0], "cloud")
    def test_touch_writes_host_terminal_when_harness_reports_nothing(self):
        f = self._touch({})
        toks = f["host"].split()
        self.assertEqual(len(toks), 3)
        self.assertEqual(toks[0], "terminal")
        self.assertEqual(toks[1], sv.host_line().split()[1])   # os and arch come from Python, whatever the kernel
    def test_darwin_reads_macos(self):
        with mock.patch.object(sv.platform, "system", return_value="Darwin"):
            self.assertEqual(sv.host_line().split()[1], "macos")
    def test_touch_writes_holder_when_harness_session_id_set(self):
        f = self._touch({"CLAUDE_CODE_SESSION_ID": "session_01ABC"})
        self.assertEqual(f["holder"], "session_01ABC")
    def test_touch_omits_holder_when_unset(self):
        f = self._touch({})
        self.assertNotIn("holder", f)
    def test_absent_host_and_holder_pass(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "s1.md").write_text(
            "session: s1\nseen: 2026-09-14T10:00:00+00:00\nroot: /tmp/x\nrows: 1\nfiles: a.py\nwriter: deadbeef0000\n")
        self.assertEqual(sv.check_package(root), [])
    def test_well_formed_host_and_holder_pass(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "s1.md").write_text(
            "session: s1\nseen: 2026-09-14T10:00:00+00:00\nroot: /tmp/x\nrows: 1\nfiles: a.py\n"
            "host: cloud linux x86_64\nholder: session_01ABC\n")
        self.assertEqual(sv.check_package(root), [])
    def test_malformed_host_fails(self):
        root = repo()
        store = root / "agent-corpus" / "d-work" / "sessions"
        base = "session: s1\nseen: 2026-09-14T10:00:00+00:00\nroot: /tmp/x\nrows: 1\nfiles: a.py\n"
        (store / "two.md").write_text(base + "host: cloud linux\n")
        (store / "kernel.md").write_text(base + "host: laptop linux x86_64\n")
        msgs = sv.check_package(root)
        self.assertTrue(any("two.md" in m and "three tokens" in m for m in msgs), msgs)
        self.assertTrue(any("kernel.md" in m and "kernel 'laptop'" in m for m in msgs), msgs)
    def test_malformed_holder_fails(self):
        root = repo()
        (root / "agent-corpus" / "d-work" / "sessions" / "s1.md").write_text(
            "session: s1\nseen: 2026-09-14T10:00:00+00:00\nroot: /tmp/x\nrows: 1\nfiles: a.py\nholder: has a space/slash\n")
        self.assertIn("'holder' is not a path-segment token", " ".join(sv.check_package(root)))

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
    def test_prose_after_a_real_list_is_not_read_as_paths(self):
        # d-work #350: the union on main held `amends`, `children`, `twenty-three`, `were`
        text = ("files touched: dyad/a.py dyad/tests/test_a.py\n"
                "amends as carried children core craft's twenty-three (PR-4) were `-q`/`-r` #1\n"
                "\nfiles touched here is a phrase in a sentence, then more prose\n")
        self.assertEqual(sv.files_touched(text), ["dyad/a.py", "dyad/tests/test_a.py"])
    def test_a_line_that_begins_with_the_phrase_but_names_no_path_takes_no_continuation(self):
        text = "files touched: nothing else changed this turn, honestly\nagent-corpus/not/a/list.md\n"
        self.assertEqual(sv.files_touched(text), [])
    def test_an_empty_first_line_still_reads_its_continuation(self):
        self.assertEqual(sv.files_touched("files touched:\ndyad/a.py\ncrafts/x/b.py\n"), ["dyad/a.py", "crafts/x/b.py"])
    def test_backticks_parens_and_extensionless_dirs(self):
        text = "files touched: `dyad/a.py` (new), crafts/ledgerd/ README.md Makefile\n"
        self.assertEqual(sv.files_touched(text), ["dyad/a.py", "crafts/ledgerd/", "README.md"])
    def test_every_plan_on_this_instance_yields_only_path_shaped_tokens(self):
        plans = Path(dyadlib.repo_root()) / "agent-corpus" / "d-work" / "plans"
        for f in sorted(plans.glob("*.md")):
            for tok in sv.files_touched(f.read_text(errors="ignore")):
                self.assertTrue(sv._is_path(tok), (f.name, tok))

class SeatNameTests(unittest.TestCase):
    """#369 C7 (d-work #379): the seat-name form, its advisory reading in `touch()` under `organization: m4`,
    silence under `flat`, and the `name` verb's report."""
    PREFS = ("# Operator preferences\n\n| key | value | allowed | read by |\n|-----|-------|---------|---------|\n"
             "| organization | {v} | `flat` \\| `m4` | Rule-16 |\n")
    def _root(self, org=None):
        root = repo()
        if org:
            (root / "preferences-corpus").mkdir(); (root / "preferences-corpus" / "PREFERENCES.md").write_text(self.PREFS.format(v=org))
        return root
    def _touch(self, root, sid, holder="1537d8fb-d96b-5c89-933a-d3ee36793d70"):
        import io, contextlib
        env = {"DYAD_SESSION": sid}
        if holder: env["CLAUDE_CODE_SESSION_ID"] = holder
        with mock.patch.dict(os.environ, env):
            if not holder: os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                sv.touch(root, ["1"], [])
        return err.getvalue()
    def test_bare_form_parses_the_three_shapes_and_refuses_the_old_names(self):
        self.assertEqual(sv.parse_seat("engineer-1537d8fb"), {"function": "engineer", "topic": None, "hp": "1537d8fb"})
        self.assertEqual(sv.parse_seat("engineer-ledgerd-1537d8fb")["topic"], "ledgerd")
        self.assertEqual(sv.parse_seat("program-alice-59cec502")["topic"], "alice")
        for old in ("cos-1", "cos", "unnamed-c0af8891f0a0", "ds-cabinet-term-1", "Engineer-1537d8fb"):   # `cab-2-8c27a6fd` happens to fit (function cab, topic 2): the craft's list is what refuses it
            self.assertIsNone(sv.parse_seat(old), old)
    def test_kind_reads_the_tokens_alone(self):
        fns = ["program", "counsel", "engineer"]
        self.assertEqual(sv.seat_kind(sv.parse_seat("program-59cec502"), fns), "leader")
        self.assertEqual(sv.seat_kind(sv.parse_seat("engineer-1537d8fb"), fns), "secretary")
        self.assertEqual(sv.seat_kind(sv.parse_seat("engineer-ledgerd-1537d8fb"), fns), "desk")
        self.assertEqual(sv.seat_kind(sv.parse_seat("ops-1537d8fb"), fns), "unknown-function")
        self.assertEqual(sv.seat_kind(sv.parse_seat("ops-1537d8fb"), None), "secretary")   # no craft: no list to be outside
    def test_organization_defaults_to_m4_and_reads_flat(self):
        self.assertEqual(sv.organization(self._root()), "flat")        # no preferences corpus at all: one pair, no form read
        self.assertEqual(sv.organization(self._root("flat")), "flat")
        self.assertEqual(sv.organization(self._root("m4")), "m4")
        self.assertEqual(sv.organization(self._root("tree")), "m4")   # a value outside the enumeration reads as the default
        root = repo(); (root / "preferences-corpus").mkdir()
        (root / "preferences-corpus" / "PREFERENCES.md").write_text(self.PREFS.format(v="x").replace("organization", "concise-mode"))
        self.assertEqual(sv.organization(root), "m4")                   # a corpus without the key: the seeded default
    def test_seat_form_falls_back_to_the_bare_form_without_the_craft(self):
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
            form, functions, source = sv.seat_form()
        self.assertEqual((form, functions, source), (sv.SEAT_FORM, None, "core"))
    def test_seat_form_reads_the_installed_crafts_data(self):
        import re
        craft = mock.Mock(); craft.rules = lambda: (re.compile(r"^(?P<function>[a-z]+)(?:-(?P<topic>[a-z]+))?-(?P<hp>[0-9a-f]{8})$"), ("program", "engineer"))
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=craft):
            form, functions, source = sv.seat_form()
        self.assertEqual((functions, source), (["program", "engineer"], "craft"))
        self.assertIsNotNone(form.match("engineer-1537d8fb"))
    def test_touch_warns_once_on_a_name_outside_the_form_under_m4(self):
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
            err = self._touch(self._root("m4"), "cos-1")
        self.assertIn("outside the form", err); self.assertEqual(err.count("warning:"), 1)
    def test_touch_warns_on_a_foreign_hp_and_is_silent_on_the_holders(self):
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
            self.assertIn("is not this holder's", self._touch(self._root("m4"), "engineer-deadbeef"))
            self.assertEqual(self._touch(self._root("m4"), "engineer-1537d8fb"), "")
            self.assertEqual(self._touch(self._root("m4"), "engineer-deadbeef", holder=None), "")   # no holder reported: nothing to compare
    def test_touch_is_silent_under_flat(self):
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
            self.assertEqual(self._touch(self._root("flat"), "cos-1"), "")
    def test_touch_names_a_function_the_craft_does_not_list(self):
        import re
        craft = mock.Mock(); craft.rules = lambda: (sv.SEAT_FORM, ("program", "engineer"))
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=craft):
            self.assertIn("function 'ops' is none of program, engineer", self._touch(self._root("m4"), "ops-1537d8fb"))
    def test_name_verb_prints_the_seat_and_the_title_from_the_environment(self):
        root = self._root()
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "1537d8fb-d96b-5c89-933a-d3ee36793d70", "CLAUDE_CODE_REMOTE": "true", "DYAD_SESSION": "engineer-1537d8fb"}):
            with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
                rc, lines = sv.seat_name_report(root, ["--system", "ds", "--on", "#369 C4 C7"])
        self.assertEqual(rc, 0)
        self.assertEqual(lines[0], "seat:   engineer-1537d8fb (secretary; form: core)")
        self.assertEqual(lines[2], "title:  engineer-1537d8fb: cloud (ds) - #369 C4 C7")
        self.assertEqual(len(lines), 3)   # DYAD_SESSION equals the seat: no note
    def test_name_verb_takes_the_function_and_topic_from_flags_and_notes_a_differing_dyad_session(self):
        root = self._root()
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "23d654aa-0000-0000-0000-000000000000", "DYAD_SESSION": "cab-8-23d654aa"}):
            os.environ.pop("CLAUDE_CODE_REMOTE", None)
            with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
                rc, lines = sv.seat_name_report(root, ["--function", "operate", "--topic", "host"])
        self.assertEqual(rc, 0)
        self.assertEqual(lines[0], "seat:   operate-host-23d654aa (desk; form: core)")
        self.assertTrue(lines[2].startswith("title:  operate-host-23d654aa: terminal (") and lines[2].endswith(") - host"))
        self.assertIn("DYAD_SESSION is 'cab-8-23d654aa'", lines[3])
    def test_name_verb_refuses_without_a_function_or_a_holder(self):
        root = self._root()
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "1537d8fb-d96b-5c89-933a-d3ee36793d70"}):
            os.environ.pop("DYAD_SESSION", None)
            with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
                rc, lines = sv.seat_name_report(root, [])
        self.assertEqual(rc, 2); self.assertIn("no function", lines[0])
        with mock.patch.dict(os.environ, {"DYAD_SESSION": "engineer-1537d8fb"}):
            os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
            with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
                rc, lines = sv.seat_name_report(root, [])
        self.assertEqual(rc, 2); self.assertIn("no <hp>", lines[0])
        rc, lines = sv.seat_name_report(root, ["--bogus"])
        self.assertEqual(rc, 2); self.assertIn("usage:", lines[0])
    def test_system_handle_is_the_directorys_initials(self):
        self.assertEqual(sv.system_handle(Path("/tmp/x/dyad-system")), "ds")
        self.assertEqual(sv.system_handle(Path("/tmp/x/countersign")), "c")
    def test_name_verb_through_main(self):
        import io, contextlib
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "1537d8fb-d96b-5c89-933a-d3ee36793d70", "DYAD_SESSION": "engineer-1537d8fb"}):
            with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    rc = sv.main(["name"])
        self.assertEqual(rc, 0); self.assertIn("seat:   engineer-1537d8fb", out.getvalue())

class AttendanceTests(unittest.TestCase):
    """d-work #393 (children 1–3 of #388): the record-derived reading, the mode over the live seats, the route of a
    seat's counter-prompt; d-work #414 (#412 C2): attendance declared by `attended-seats`, the records its fence."""
    TODAY = __import__("datetime").date(2026, 10, 22)
    def _repo(self, prefs=None, declared=None):
        root = repo()
        (root / "agent-corpus" / "d-work" / "provenance").mkdir()
        if prefs is not None or declared is not None:
            (root / "preferences-corpus").mkdir()
            (root / "preferences-corpus" / "PREFERENCES.md").write_text(
                "# Operator preferences\n\n| key | value | allowed | read by |\n|-----|-------|---------|---------|\n"
                + (f"| attendance-window | {prefs} | days | Rule-16 |\n" if prefs is not None else "")
                + (f"| attended-seats | {declared} | seat names | Rule-16 |\n" if declared is not None else ""))
        return root
    def _read(self, root):
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
            return sv.attendance(root, self.TODAY)
    def _record(self, root, rid, seat, entries):
        body = f"# Provenance #{rid}\n\n" + (f"session: {seat}\n\n" if seat else "")
        for n, (kind, date, note) in enumerate(entries, 1):
            body += f"## {n} {kind} {date}{(' ' + note) if note else ''}\n\n```\nY\n```\n\n"
        (root / "agent-corpus" / "d-work" / "provenance" / f"{rid}.md").write_text(body)
    def _presence(self, root, seat, live=True):
        seen = _now() if live else "2026-01-01T00:00:00+00:00"
        (root / "agent-corpus" / "d-work" / "sessions" / f"{seat}.md").write_text(f"session: {seat}\nseen: {seen}\nroot: /x\nrows: 1\nfiles: \n")
    def test_own_disposition_excludes_mandate_and_relayed_notes(self):
        self.assertTrue(sv.own_disposition("plan")); self.assertTrue(sv.own_disposition("")); self.assertTrue(sv.own_disposition("done (merges PR #3)"))
        self.assertFalse(sv.own_disposition("mandate #369, 2026-10-21")); self.assertFalse(sv.own_disposition("plan, relayed via program-59cec502"))
    # d-work #422: the three note forms a disposition entry carries, each read in a declared and an undeclared seat.
    NOTES = {"plain": ("plan", True),
             "mandate-at-start": ("mandate #412, 2026-10-21", False),                      # `dwork new|state --mandate`
             "mandate-inside": ("Y done (mandate #412, 2026-10-21)", False),              # the pre-#422 close workaround
             "relayed": ("plan, relayed via program-59cec502", False)}                    # `--relayed-via` with `--said`
    def test_own_disposition_excludes_a_mandate_or_relayed_note_anywhere(self):
        for form, (note, own) in self.NOTES.items():
            self.assertEqual(sv.own_disposition(note), own, form)
        self.assertFalse(sv.own_disposition("done (mandate #413, 2026-10-25), relayed via program-59cec502"))
    def test_three_note_forms_in_a_declared_and_an_undeclared_seat(self):
        for form, (note, own) in self.NOTES.items():
            for declared in (True, False):
                with self.subTest(form=form, declared=declared):
                    root = self._repo(declared="counsel" if declared else None)
                    for s in ("program-59cec502", "counsel-0032b4c0"):
                        self._presence(root, s)
                    self._record(root, 20, "counsel-0032b4c0", [("disposition", "2026-10-22", note)])
                    a = self._read(root)
                    if declared:   # the declaration decides attendance; the record only checks it (`warn` when silent)
                        self.assertEqual((a["undeclared"], a["warnings"]), ([], [] if own else ["counsel"]))
                    else:          # an undeclared seat is flagged only for a disposition given in it
                        self.assertEqual((a["undeclared"], a["warnings"]), ([("counsel-0032b4c0", "2026-10-22")] if own else [], []))
    def test_record_413_reads_silent_in_an_undeclared_seat(self):
        """#421's defect, on #413's record exactly as it was written: an accreted row born and closed under #412's
        mandate, whose entry 2 the pre-#422 workaround noted `Y done (mandate #412, …)` — a false `undeclared`."""
        root = self._repo()
        (root / "agent-corpus" / "d-work" / "provenance" / "413.md").write_text(
            "# Provenance #413\n\nsession: engineer-1537d8fb\n\n"
            "## 1 disposition 2026-10-25 mandate #412, 2026-10-25\n\n```\nY\n```\n\n"
            "## 2 disposition 2026-10-25 Y done (mandate #412, 2026-10-25)\n\n```\nY\n```\n")
        for s in ("program-59cec502", "engineer-1537d8fb"):
            self._presence(root, s)
        today = __import__("datetime").date(2026, 10, 25)
        self.assertEqual(sv.attendance_index(root, today), {})
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
            a = sv.attendance(root, today)
        self.assertEqual((a["undeclared"], sv.fence_lines(a)), ([], []))
    def test_attended_reads_the_latest_own_disposition_within_the_window(self):
        root = self._repo()
        self._record(root, 1, "counsel-0032b4c0", [("prompt", "2026-10-20", ""), ("disposition", "2026-10-20", "plan"), ("disposition", "2026-10-21", "done")])
        self._record(root, 2, "engineer-1537d8fb", [("disposition", "2026-10-22", "mandate #369, 2026-10-21")])     # an accreted row's copied words
        self._record(root, 3, "audit-aaaaaaaa", [("disposition", "2026-10-21", "plan, relayed via program-59cec502")])
        self._record(root, 4, "operate-bbbbbbbb", [("disposition", "2026-10-01", "plan")])                            # outside the window
        self._record(root, 5, None, [("disposition", "2026-10-22", "plan")])                                           # no session line: no seat
        self.assertEqual(sv.attended("counsel-0032b4c0", root, self.TODAY), "2026-10-21")
        for seat in ("engineer-1537d8fb", "audit-aaaaaaaa", "operate-bbbbbbbb", "nobody"):
            self.assertIsNone(sv.attended(seat, root, self.TODAY), seat)
        self.assertEqual(sv.attendance_index(root, self.TODAY), {"counsel-0032b4c0": "2026-10-21"})
    def test_window_is_the_preference_default_seven(self):
        root = self._repo()
        self.assertEqual(sv.attendance_window(root).days, 7)
        self.assertEqual(sv.attendance_window(self._repo("30")).days, 30)
        self.assertEqual(sv.attendance_window(self._repo("none")).days, 7)      # malformed: the default
        self.assertEqual(sv.attendance_window(self._repo("-2")).days, 7)        # not positive: the default
        root = self._repo("1"); self._record(root, 1, "counsel-0032b4c0", [("disposition", "2026-10-20", "plan")])
        self.assertIsNone(sv.attended("counsel-0032b4c0", root, self.TODAY))
    def test_mode_m4_when_every_live_seat_is_declared_attended(self):
        root = self._repo(declared="counsel-0032b4c0")
        for s in ("program-59cec502", "counsel-0032b4c0"):
            self._presence(root, s); self._record(root, hash(s) % 1000 + 10, s, [("disposition", "2026-10-22", "plan")])
        self._presence(root, "operate-bbbbbbbb", live=False)                      # stale: not a live seat
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
            a = sv.attendance(root, self.TODAY)
        self.assertEqual((a["mode"], a["relayed"], a["leaders"]), ("M4", [], ["program-59cec502"]))
        self.assertEqual(sv.route("counsel-0032b4c0", root, self.TODAY), "chat")
    def test_default_none_reads_m3_with_only_the_leader_attended(self):
        root = self._repo()                                                        # no preferences corpus: the default `none`
        for s in ("program-59cec502", "counsel-0032b4c0", "engineer-1537d8fb"):
            self._presence(root, s)
        a = self._read(root)
        self.assertEqual((a["mode"], a["attended"], sorted(a["relayed"])), ("M3", {"program-59cec502": ""}, ["counsel-0032b4c0", "engineer-1537d8fb"]))
        self.assertEqual((a["declared"], a["undeclared"], a["warnings"]), ([], [], []))
        self.assertEqual(sv.route("engineer-1537d8fb", root, self.TODAY), "relayed")
        self.assertEqual(sv.route("program-59cec502", root, self.TODAY), "chat")
        self.assertEqual(sv.declared_seats(self._repo(declared="none")), [])
        self.assertEqual(sv.declared_seats(self._repo(declared="none counsel, engineer")), ["counsel", "engineer"])
    def test_declared_seat_is_attended_and_a_bare_function_topic_declares_every_holder(self):
        root = self._repo(declared="counsel")
        for s in ("program-59cec502", "counsel-0032b4c0", "engineer-1537d8fb"):
            self._presence(root, s)
        self._record(root, 11, "counsel-0032b4c0", [("disposition", "2026-10-22", "plan")])
        a = self._read(root)
        self.assertEqual((a["mode"], a["attended"], a["relayed"]), ("hybrid", {"program-59cec502": "", "counsel-0032b4c0": "2026-10-22"}, ["engineer-1537d8fb"]))
        self.assertEqual((a["undeclared"], a["warnings"]), ([], []))
        self.assertEqual(sv.route("counsel-0032b4c0", root, self.TODAY), "chat")
        self.assertTrue(sv.declares(["ds-cabinet"], "ds-cabinet-1537d8fb")); self.assertFalse(sv.declares(["ds"], "ds-cabinet-1537d8fb"))
    def test_fence_undeclared_disposition_prints_undeclared(self):
        root = self._repo()                                                        # the Operator disposed in a member seat it never declared
        for s in ("program-59cec502", "counsel-0032b4c0", "engineer-1537d8fb"):
            self._presence(root, s)
        self._record(root, 12, "counsel-0032b4c0", [("disposition", "2026-10-22", "plan")])
        self._record(root, 13, "operate-bbbbbbbb", [("disposition", "2026-10-22", "plan")])    # no presence file: off the board
        a = self._read(root)
        self.assertEqual((a["mode"], a["undeclared"]), ("M3", [("counsel-0032b4c0", "2026-10-22")]))
        self.assertEqual(sv.route("counsel-0032b4c0", root, self.TODAY), "relayed")   # the declaration decides, never the record
        self.assertEqual(sv.fence_lines(a), ["undeclared: counsel-0032b4c0 holds an own disposition of 2026-10-22 but `attended-seats` does not declare it (Rule-16 Presence)"])
    def test_fence_declared_seat_silent_past_the_window_is_a_warning(self):
        root = self._repo(declared="engineer-1537d8fb counsel")
        for s in ("program-59cec502", "counsel-0032b4c0", "engineer-1537d8fb"):
            self._presence(root, s)
        self._record(root, 14, "engineer-1537d8fb", [("disposition", "2026-10-01", "plan")])   # outside the window
        a = self._read(root)
        self.assertEqual((a["mode"], a["relayed"], a["undeclared"]), ("M4", [], []))
        self.assertEqual(a["warnings"], ["counsel", "engineer-1537d8fb"])
        self.assertEqual(sv.fence_lines(a)[0], "warn: counsel is declared attended but holds no own disposition within 7 day(s)")
    def test_no_live_seat_reads_m3(self):
        root = self._repo()
        with mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
            a = sv.attendance(root, self.TODAY)
        self.assertEqual((a["mode"], a["attended"], a["relayed"]), ("M3", {}, []))
        self.assertIn("mode: M3 — 0 of 0 live seat(s) attended; declared: none beside the leader", sv.attendance_line(a))
    def test_absent_store_gives_no_attendance(self):
        self.assertEqual(sv.attendance_index(repo(), self.TODAY), {})

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
        if "no session presence files" not in r.stdout:
            self.assertRegex(r.stdout, r"^mode: (M3|M4|hybrid) — \d+ of \d+ live seat\(s\) attended; declared: ")   # #393, #414

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


class ReconcileTests(unittest.TestCase):
    """d-work #434 (child C1 of #431): `reconcile` reads the live presence files against the harness's own session
    list, through a fake harness store (`DYAD_HARNESS_DIR`) read by `hostadapter.harness_sessions`."""
    A, B, C = ("1537d8fb-d96b-5c89-933a-d3ee36793d70", "59cec502-0000-4000-8000-000000000000",
               "0032b4c0-0000-4000-8000-000000000000")
    def _env(self):
        root, base = Path(tempfile.mkdtemp()) / "dyad-system", Path(tempfile.mkdtemp())   # system handle `ds`
        (root / "agent-corpus" / "d-work" / "sessions").mkdir(parents=True)
        proj = base / "projects" / sv.hostadapter._slug(sv.hostadapter.resolve(root))
        proj.mkdir(parents=True)
        return root, base, proj
    def _harness(self, proj, sid, title=None, kind="custom-title"):
        recs = [{"type": "user", "sessionId": sid}]
        if title is not None:
            recs.append({"type": kind, "sessionId": sid, ("customTitle" if kind == "custom-title" else "aiTitle"): title})
        (proj / f"{sid}.jsonl").write_text("".join(sv.hostadapter.json.dumps(r) + "\n" for r in recs))
    def _presence(self, root, seat, holder=None, live=True, host="cloud linux x86_64"):
        seen = _now() if live else "2026-01-01T00:00:00+00:00"
        (root / "agent-corpus" / "d-work" / "sessions" / f"{seat}.md").write_text(
            f"session: {seat}\nseen: {seen}\nroot: /x\nrows: 1\nfiles: \nhost: {host}\n" + (f"holder: {holder}\n" if holder else ""))
    def _run(self, root, base):
        with mock.patch.dict(os.environ, {"DYAD_HARNESS_DIR": str(base)}), \
             mock.patch.object(sv.dyadlib, "find_guard", return_value=None):
            return sv.reconcile(root), sv.reconcile_report(root)
    def test_aligned_passes(self):
        root, base, proj = self._env()
        self._presence(root, "engineer-1537d8fb", self.A)
        self._harness(proj, self.A, "engineer-1537d8fb: cloud (ds) - ledger")
        self._harness(proj, self.B, "an untitled-form session")      # not in the seat form: not the check's
        lines, (rc, report) = self._run(root, base)
        self.assertEqual((lines, rc), ([], 0)); self.assertTrue(report[0].startswith("ok   [reconcile] 1 live"))
    def test_no_harness_session(self):
        root, base, proj = self._env()
        self._presence(root, "program-59cec502", self.B)
        self._presence(root, "cos", None)                            # no holder line and no <hp>: unmatched
        self._harness(proj, self.A, None)
        lines, (rc, _) = self._run(root, base)
        self.assertEqual(lines, ["no harness session: cos (no holder line)", "no harness session: program-59cec502"]); self.assertEqual(rc, 1)
    def test_holder_matched_by_hp_prefix(self):
        root, base, proj = self._env()
        self._presence(root, "engineer-1537d8fb", "1537d8fb")        # an 8-hex holder, as a seat's <hp>
        self._harness(proj, self.A, "engineer-1537d8fb: cloud (ds)")
        self.assertEqual(self._run(root, base)[0], [])
    def test_no_presence(self):
        root, base, proj = self._env()
        self._harness(proj, self.C, "counsel-0032b4c0: cloud (ds) - rules", kind="ai-title")
        lines, (rc, _) = self._run(root, base)
        self.assertEqual(lines, ["no presence: counsel-0032b4c0: cloud (ds) - rules"]); self.assertEqual(rc, 1)
    def test_title_differs(self):
        for title in ("engineer-1537d8fb: terminal (ds)", "program-1537d8fb: cloud (ds)", "engineer-1537d8fb: cloud (w4)",
                      "engineer-1537d8fb: cloud (ds)x", "dyad-system-ea", None):
            with self.subTest(title=title):
                root, base, proj = self._env()
                self._presence(root, "engineer-1537d8fb", self.A)
                self._harness(proj, self.A, title)
                lines = self._run(root, base)[0]
                self.assertEqual(len(lines), 1); self.assertTrue(lines[0].startswith("title differs: engineer-1537d8fb ("), lines)
    def test_suffixed_title_matches_by_its_prefix(self):
        """The operate seat's observation: the harness appends a suffix (`operate-8cce8b10: cloud (ds) - operate`); the
        prefix `dyad session name` prints is what is compared, for `title differs` and for `no presence` alike."""
        for suffix in ("", " - operate", " — ledger work", " | x", ": y"):
            with self.subTest(suffix=suffix):
                root, base, proj = self._env()
                self._presence(root, "operate-8cce8b10", "8cce8b10-0000-4000-8000-000000000000")
                self._harness(proj, "8cce8b10-0000-4000-8000-000000000000", f"operate-8cce8b10: cloud (ds){suffix}")
                self._harness(proj, self.C, f"counsel-0032b4c0: cloud (ds){suffix}")
                self.assertEqual(self._run(root, base)[0], [f"no presence: counsel-0032b4c0: cloud (ds){suffix}"])
    def test_report_line_forms(self):
        root, base, proj = self._env()
        self._presence(root, "engineer-1537d8fb", self.A)
        self._harness(proj, self.A, "engineer-1537d8fb: cloud (ds)")
        self.assertEqual(self._run(root, base)[1], (0, ["ok   [reconcile] 1 live presence file(s), 1 harness session(s) aligned"]))
        self._presence(root, "program-59cec502", self.B)
        self.assertEqual(self._run(root, base)[1], (1, ["no harness session: program-59cec502",
            "1 mismatch(es) — 2 live presence file(s), 1 harness session(s) (Rule-16 Presence; the writer remedies)"]))
    def test_custom_title_wins_over_ai_title(self):
        root, base, proj = self._env()
        (proj / f"{self.A}.jsonl").write_text(
            '{"type": "custom-title", "customTitle": "engineer-1537d8fb: cloud (ds)"}\n'
            '{"type": "ai-title", "aiTitle": "Fix the ledger"}\n')
        self._presence(root, "engineer-1537d8fb", self.A)
        self.assertEqual(self._run(root, base)[0], [])
    def test_stale_while_titled(self):
        root, base, proj = self._env()
        self._presence(root, "operate-59cec502", self.B, live=False)
        self._harness(proj, self.B, "operate-59cec502: cloud (ds)")
        self._presence(root, "audit-0032b4c0", self.C, live=False)   # stale and untitled: silent
        self._harness(proj, self.C, None)
        lines, (rc, _) = self._run(root, base)
        self.assertEqual(lines, ["stale while titled: operate-59cec502"]); self.assertEqual(rc, 1)
    def test_no_harness_store_is_silent(self):
        root = repo(); base = Path(tempfile.mkdtemp())
        self._presence(root, "engineer-1537d8fb", self.A)
        lines, (rc, report) = self._run(root, base)
        self.assertEqual((lines, rc), ([], 0)); self.assertIn("reports no session", report[0])
    def test_check_package_never_reads_the_harness(self):
        root, base, proj = self._env()
        self._presence(root, "program-59cec502", self.B)
        self._harness(proj, self.A, None)
        with mock.patch.dict(os.environ, {"DYAD_HARNESS_DIR": str(base)}):
            self.assertEqual(sv.check_package(root), [])            # advisory: a mismatch is never a guard failure
