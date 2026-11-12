"""inbox.py (the inbox store, entity `message`; d-work #536, cos mode P2).

The form and the check:
- a message names its box as `to` and its file name's sender as `from`, with one of four kinds, a UTC `sent` and an
  existing row; each defect fails;
- a disposition-shaped body fails: a `Y/N:` line, or a ledger entry;
- a read marker needs its message and its box's seat;
- the transaction check fails a commit that modifies or deletes a message or a marker, and passes one that only adds.

Over a scratch world (a bare origin, two seat clones whose pre-push hook only logs):
- `post` lands one ledger-only commit holding one file in the addressee's box, addressed by seat and written by this
  session;
- `post` refuses a disposition-shaped body, an unknown row, a missing seat and a bad kind before anything lands;
- `read` with no names prints the unread messages verbatim, each under its name, and writes nothing (#587 S10);
  `read <message>...` marks exactly the named ones read in one land and refuses, before any write, an unknown name, a
  message of another seat's box, an already-read one and a name given twice; `--all` is refused (removed);
- on a row with a phased board entry the marking land fires the machine's `read`, which leaves board/<id>.md
  byte-identical and writes no board file;
- `list` reads the working tree;
- `session touch` prints the unread count."""
import contextlib, io, os, shutil, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib, livetest
ib = dyadlib.load_guard("agent", "inbox")

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
INST = "agent-corpus"
ROW = "id: {id}\ntitle: row {id}\nopened: 2026-11-01\nstate: planned\ndisposed: 2026-11-01 Y plan\nrefs: \n"
BODY = "PR #591 landed on main as 4157033.\n\n  indented: kept\n# not a comment"
MSG = ("from: engineer-1537d8fb\nto: program-59cec502\nrow: 5\nkind: report\nsent: 2026-11-02T17:44:00Z\n"
       "body: PR #591 landed on main as 4157033.\n  \n    indented: kept\n  # not a comment\nwriter: h1\n")
NAME = "20261102T174400Z-engineer-1537d8fb-1"


def git(d, *a):
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=dyadlib.git_env())
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)} in {d}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class FormTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, True)
        rows = self.root / INST / "d-work" / "rows"; rows.mkdir(parents=True)
        (rows / "5.md").write_text(ROW.format(id=5))
        self.box = self.root / INST / "d-work" / "inbox" / "program-59cec502"; self.box.mkdir(parents=True)

    def put(self, name, text, box=None):
        d = box or self.box; d.mkdir(parents=True, exist_ok=True); (d / name).write_text(text)

    def test_a_well_formed_message_and_marker_pass_and_keep_the_body(self):
        self.put(f"{NAME}.md", MSG)
        self.put(f"{NAME}.read", "read: 2026-11-02T17:50:00Z\nreader: program-59cec502\nwriter: h2\n")
        self.assertEqual(ib.check_package(self.root), [])
        (_, f, read), = ib.messages(self.root, "program-59cec502")
        self.assertEqual((f["body"], read), (BODY, True))
        self.assertEqual(ib.unread(self.root, "program-59cec502"), 0)
        self.assertEqual(ib.summary(self.root), "1 message(s) in 1 box(es)")

    def test_each_defect_fails(self):
        cases = {"to": (MSG.replace("to: program-59cec502", "to: counsel-0032b4c0"), "not its box"),
                 "from": (MSG.replace("from: engineer-1537d8fb", "from: counsel-0032b4c0"), "not its name's"),
                 "kind": (MSG.replace("kind: report", "kind: order"), "'kind' 'order'"),
                 "sent": (MSG.replace("2026-11-02T17:44:00Z", "today"), "'sent' is not"),
                 "row": (MSG.replace("row: 5", "row: 9"), "no row #9"),
                 "missing": (MSG.replace("kind: report\n", ""), "'kind' missing"),
                 "unknown": (MSG + "colour: red\n", "unknown key 'colour'"),
                 "ask": (MSG.replace("  # not a comment", "  Y/N: Done with #5?"), "disposition-shaped"),
                 "entry": (MSG.replace("body: PR #591", "body: 2026-11-02 Y done (merges PR #591 at abc) — PR #591"), "disposition-shaped")}
        for label, (text, says) in cases.items():
            shutil.rmtree(self.box); self.put(f"{NAME}.md", text)
            msgs = ib.check_package(self.root)
            self.assertTrue(any(says in m for m in msgs), (label, msgs))
        shutil.rmtree(self.box)
        self.put("notes.txt", "x")
        self.assertIn("not `<stamp>-<from-seat>-<n>.md` or `.read`", ib.check_package(self.root)[0])
        shutil.rmtree(self.box)
        self.put(f"{NAME}.read", "read: 2026-11-02T17:50:00Z\nreader: someone-else\n")
        msgs = ib.check_package(self.root)
        self.assertTrue(any("a read marker with no message" in m for m in msgs), msgs)
        self.assertTrue(any("'reader' is 'someone-else'" in m for m in msgs), msgs)

    def test_parse_post_refuses_misuse(self):
        for argv, says in ((["program-x", "--row", "5", "--kind", "report"], "not both and not neither"),
                           (["program-x", "--row", "5", "--kind", "order", "b"], "usage"),
                           (["program-x", "--kind", "report", "b"], "usage"),
                           (["program-x", "--row", "5", "--kind", "report", "Y/N: Done with #5?"], "disposition-shaped"),
                           (["program-x", "--row", "5", "--kind", "report", " \n"], "an empty body"),
                           (["a/b", "--row", "5", "--kind", "report", "b"], "usage")):
            with self.assertRaises(ib.Refused, msg=argv) as e:
                ib.parse_post(argv)
            self.assertIn(says, str(e.exception))
        self.assertEqual(ib.parse_post(["program-x", "--row", "5", "--kind", "ack", "seen\n"]), ("program-x", 5, "ack", "seen", ()))
        self.assertEqual(ib.parse_post(["program-x", "--cc", "orch-y", "--row", "5", "--kind", "report", "b"]),
                         ("program-x", 5, "report", "b", ("orch-y",)))
        for argv, says in ((["program-x", "--cc", "program-x", "--row", "5", "--kind", "report", "b"], "another seat"),
                           (["program-x", "--cc", "o", "--cc", "o", "--row", "5", "--kind", "report", "b"], "once each"),
                           (["program-x", "--cc", "o", "--row", "5", "--kind", "relay", "b"], "--cc is for a report")):
            with self.assertRaises(ib.Refused, msg=argv) as e:
                ib.parse_post(argv)
            self.assertIn(says, str(e.exception))

    def test_contract(self):
        self.assertEqual((ib.ENTITY, ib.CORPUS, ib.TRANSACTION), ("message", "agent", True))
        self.assertIsNone(dyadlib.contract_problem(ib, "core", "agent"))
        self.assertEqual(dyadlib.check_invariants(ib), len(ib.INVARIANTS))
        self.assertEqual([f[0] for f in ib.describe(self.root)["fields"]], list(ib.FIELDS))


class World(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        top = SCRATCH.mkdtemp()
        seed, self.origin, hooks = top / "seed", top / "origin.git", top / "hooks"
        seed.mkdir(); git(seed, "init", "-q", "-b", "main")
        rows = seed / INST / "d-work" / "rows"; rows.mkdir(parents=True)
        (rows / "5.md").write_text(ROW.format(id=5))
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "seed")
        git(top, "clone", "-q", "--bare", str(seed), str(self.origin))
        hooks.mkdir(); (hooks / "pre-push").write_text("#!/bin/sh\ncat >/dev/null\nexit 0\n"); (hooks / "pre-push").chmod(0o755)
        self.clones = {}
        for seat in ("engineer-1537d8fb", "program-59cec502"):
            d = top / seat
            git(top, "clone", "-q", str(self.origin), str(d))
            for k, v in (("user.email", "t@example.com"), ("user.name", "t"), ("core.hooksPath", str(hooks))):
                git(d, "config", k, v)
            self.clones[seat] = d

    def as_seat(self, seat, *argv, harness="h1"):
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": seat, "CLAUDE_CODE_SESSION_ID": harness}), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = ib.cli(list(argv), self.clones[seat])
        return rc, out.getvalue(), err.getvalue()

    def unread_names(self, seat):
        d = self.clones[seat]
        git(d, "fetch", "-q", "origin")
        names = git(d, "ls-tree", "-r", "--name-only", "origin/main", f"{INST}/d-work/inbox/{seat}").splitlines()
        reads = {n.removesuffix(".read") for n in names if n.endswith(".read")}
        return [Path(n).stem for n in names if n.endswith(".md") and n.removesuffix(".md") not in reads]


class CliTests(World):
    def test_post_lands_one_message_in_the_addressees_box(self):
        before = git(self.origin, "rev-parse", "main")
        rc, out, err = self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "5", "--kind", "report", BODY)
        self.assertEqual(rc, 0, err)
        head = git(self.origin, "rev-parse", "main")
        (path,) = git(self.origin, "diff", "--name-only", before, head).splitlines()
        self.assertRegex(path, rf"^{INST}/d-work/inbox/program-59cec502/\d{{8}}T\d{{6}}Z-engineer-1537d8fb-1\.md$")
        f = dyadlib.load_guard("agent", "board").parse(git(self.origin, "show", f"main:{path}"))[0]
        self.assertEqual((f["from"], f["to"], f["row"], f["kind"], f["body"], f["writer"]),
                         ("engineer-1537d8fb", "program-59cec502", "5", "report", BODY, "h1"))
        self.assertTrue(git(self.origin, "log", "-1", "--format=%s", head).startswith("ledger: inbox program-59cec502"))
        git(self.clones["engineer-1537d8fb"], "fetch", "-q", "origin")
        self.assertTrue(dyadlib.ledger_only(self.clones["engineer-1537d8fb"], before, head))
        self.assertEqual(ib.check_transaction(self.clones["engineer-1537d8fb"], before, head), [])

    def test_cc_lands_one_commit_in_every_box(self):
        """#572 K6: a report to home copied to orchestrate is one land, one message per box, each `to` its own box."""
        before = git(self.origin, "rev-parse", "main")
        rc, out, err = self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--cc", "orchestrate-d688fecf",
                                    "--row", "5", "--kind", "report", "PR up")
        self.assertEqual(rc, 0, err)
        head = git(self.origin, "rev-parse", "main")
        self.assertEqual(git(self.origin, "rev-list", "--count", f"{before}..{head}"), "1")
        paths = git(self.origin, "diff", "--name-only", before, head).splitlines()
        self.assertEqual(sorted(p.split("/")[3] for p in paths), ["orchestrate-d688fecf", "program-59cec502"])
        for p in paths:
            f = dyadlib.load_guard("agent", "board").parse(git(self.origin, "show", f"main:{p}"))[0]
            self.assertEqual((f["to"], f["body"]), (p.split("/")[3], "PR up"))
        self.assertIn("(cc orchestrate-d688fecf)", git(self.origin, "log", "-1", "--format=%s", head))
        git(self.clones["program-59cec502"], "pull", "-q", "--ff-only", "origin", "main")
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "program-59cec502"}):
            self.assertEqual(ib.check_package(self.clones["program-59cec502"]), [])

    def test_ring_line_follows_the_landed_line_and_only_then(self):
        """K-21 (#652): a landed actionable post prints `ring:` after `landed <sha> on main`; a notice, a self-addressed
        unit, a refused post and an unlanded one ring nobody."""
        rc, out, err = self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--cc", "counsel-0032b4c0",
                                    "--cc", "engineer-1537d8fb", "--row", "5", "--kind", "report", "PR up")
        self.assertEqual(rc, 0, err)
        lines = out.splitlines()
        landed = next(i for i, l in enumerate(lines) if l.startswith("landed ") and l.endswith(" on main"))
        ring = [i for i, l in enumerate(lines) if l.startswith("ring: ")]
        self.assertEqual(len(ring), 1, out); self.assertGreater(ring[0], landed)
        self.assertTrue(lines[ring[0]].startswith("ring: program-59cec502, counsel-0032b4c0 ("), lines[ring[0]])
        rc, out, err = self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "5", "--kind", "notice", "fyi")
        self.assertEqual(rc, 0, err); self.assertIn("landed ", out); self.assertNotIn("ring:", out)
        rc, out, err = self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "9", "--kind", "report", "x")
        self.assertEqual(rc, 1); self.assertNotIn("ring:", out + err)                     # refused
        before = git(self.origin, "rev-parse", "main")
        hook = Path(self.clones["engineer-1537d8fb"]).parent / "hooks" / "pre-push"
        saved = hook.read_text()
        hook.write_text("#!/bin/sh\ncat >/dev/null\nexit 1\n"); self.addCleanup(hook.write_text, saved)
        rc, out, err = self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "5", "--kind", "report", "y")
        self.assertEqual(rc, 1); self.assertNotIn("ring:", out + err)                     # the push failed: unlanded
        self.assertEqual(git(self.origin, "rev-parse", "main"), before)

    def test_post_ring_rule(self):
        self.assertEqual(ib.post_ring("a", "report", ("b", "a", "c"), "c"), ["a", "b"])
        self.assertEqual(ib.post_ring("a", "relay", (), "z"), ["a"])
        self.assertEqual(ib.post_ring("a", "notice", ("b",), "z"), [])
        self.assertEqual(ib.post_ring("z", "ack", (), "z"), [])

    def test_post_refuses_before_anything_lands(self):
        before = git(self.origin, "rev-parse", "main")
        for argv, says in ((["post", "program-59cec502", "--row", "5", "--kind", "report", "2026-11-02 Y plan"], "disposition-shaped"),
                           (["post", "program-59cec502", "--row", "9", "--kind", "report", "x"], "no row #9")):
            rc, _, err = self.as_seat("engineer-1537d8fb", *argv)
            self.assertEqual(rc, 1, argv); self.assertIn(says, err)
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": ""}):
            self.assertEqual(ib.cli(["post", "program-59cec502", "--row", "5", "--kind", "ack", "x"], self.clones["engineer-1537d8fb"]), 1)
        self.assertEqual(self.as_seat("engineer-1537d8fb", "bogus")[0], 2)
        self.assertEqual(git(self.origin, "rev-parse", "main"), before)

    def test_read_prints_and_marks_nothing_naming_marks_exactly_the_named(self):
        """#587 S10: printing is no side effect; marking is an event naming what was read."""
        for body in ("first", "second\n  kept", "third"):
            self.assertEqual(self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "5", "--kind", "report", body)[0], 0)
        before = git(self.origin, "rev-parse", "main")
        rc, out, err = self.as_seat("program-59cec502", "read", harness="h2")
        self.assertEqual(rc, 0, err)
        self.assertIn("    first", out); self.assertIn("    second\n      kept", out)
        self.assertIn("inbox program-59cec502: 3 unread, none marked", out)
        self.assertEqual(git(self.origin, "rev-parse", "main"), before)                  # printing landed nothing
        a, b, c = self.unread_names("program-59cec502")
        self.assertIn(f"* {a}  row #5 report from engineer-1537d8fb", out)                   # the printed name is the one to give
        rc, out, err = self.as_seat("program-59cec502", "read", a, f"{c}.md", harness="h2")
        self.assertEqual(rc, 0, err)
        self.assertIn(f"marked read: {a}", out); self.assertIn("inbox program-59cec502: 2 marked read", out)
        head = git(self.origin, "rev-parse", "main")
        self.assertEqual(git(self.origin, "rev-list", "--count", f"{before}..{head}"), "1")
        changed = git(self.origin, "diff", "--name-only", before, head).splitlines()
        self.assertEqual(sorted(Path(x).name for x in changed if x.endswith(".read")), sorted([f"{a}.read", f"{c}.read"]))
        self.assertEqual(self.unread_names("program-59cec502"), [b])                      # exactly the named
        rc, out, _ = self.as_seat("program-59cec502", "read", harness="h2")
        self.assertIn("inbox program-59cec502: 1 unread, none marked", out); self.assertNotIn("    first", out)
        git(self.clones["program-59cec502"], "pull", "-q", "--ff-only", "origin", "main")
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "program-59cec502"}):
            self.assertEqual(ib.check_package(self.clones["program-59cec502"]), [])
        rc, out, _ = self.as_seat("program-59cec502", "list", harness="h2")
        self.assertIn("inbox program-59cec502: 3 message(s), 1 unread", out)

    def test_naming_refuses_before_any_write(self):
        self.assertEqual(self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--cc", "orchestrate-d688fecf",
                                      "--row", "5", "--kind", "report", "PR up")[0], 0)
        self.assertEqual(self.as_seat("program-59cec502", "post", "engineer-1537d8fb", "--row", "5", "--kind", "ack", "seen")[0], 0)
        (mine,) = self.unread_names("program-59cec502")
        (theirs,) = self.unread_names("engineer-1537d8fb")
        rc, _, err = self.as_seat("program-59cec502", "read", mine, harness="h2")
        self.assertEqual(rc, 0, err)
        before = git(self.origin, "rev-parse", "main")
        for names, says in (([mine], "already read"),
                            ([theirs], "a message of engineer-1537d8fb's box, not this seat's (program-59cec502)"),
                            ([f"orchestrate-d688fecf/{mine}"], "a message of orchestrate-d688fecf's box"),
                            (["20261102T174400Z-nobody-1"], "no message of program-59cec502's box"),
                            (["not-a-name"], "is not a message name"),
                            (["--all"], "`--all` is removed")):
            rc, _, err = self.as_seat("program-59cec502", "read", *names, harness="h2")
            self.assertEqual(rc, 1, (names, err)); self.assertIn(says, err)
        self.assertEqual(self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "5", "--kind", "report", "x")[0], 0)
        before = git(self.origin, "rev-parse", "main")
        (new,) = self.unread_names("program-59cec502")
        for names, says in (([new, new], "named twice"), ([new, mine], "already read")):
            rc, _, err = self.as_seat("program-59cec502", "read", *names, harness="h2")
            self.assertEqual(rc, 1, err); self.assertIn(says, err)
        self.assertEqual(git(self.origin, "rev-parse", "main"), before)                   # nothing landed, not even the good name
        self.assertEqual(self.unread_names("program-59cec502"), [new])

    def test_naming_a_message_on_a_phased_row_fires_read_and_writes_no_board(self):
        """#587 S10: the machine's `read` is a self-loop with no effect: board/5.md stays byte-identical."""
        bd = dyadlib.load_guard("agent", "board")
        f = {"holder": "program-59cec502", "owner": "engineer-1537d8fb", "since": "2026-11-04T10:00Z", "writer": "h1",
             "phase": bd.phase_render("verifying", {"unit": ["engineer-1537d8fb"], "pr": ["638 at " + "2" * 40]})}
        f.update(bd.derive(5, f))
        d = self.clones["program-59cec502"]
        git(d, "pull", "-q", "--ff-only", "origin", "main")
        (d / INST / "d-work" / "board").mkdir(parents=True)
        (d / INST / "d-work" / "board" / "5.md").write_text(bd.render(f, bd.FIELDS))
        git(d, "add", "-A"); git(d, *livetest.IDENTITY, "commit", "-qm", "ledger: board 5"); git(d, "push", "-q", "origin", "HEAD:main")
        entry = git(self.origin, "show", f"main:{INST}/d-work/board/5.md")
        self.assertEqual(self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "5", "--kind", "report", "PR #638 up")[0], 0)
        (name,) = self.unread_names("program-59cec502")
        before = git(self.origin, "rev-parse", "main")
        rc, out, err = self.as_seat("program-59cec502", "read", name, harness="h2")
        self.assertEqual(rc, 0, err)
        self.assertIn("board #5: read at verifying, nothing changed", out)
        head = git(self.origin, "rev-parse", "main")
        changed = git(self.origin, "diff", "--name-only", before, head).splitlines()
        self.assertNotIn(f"{INST}/d-work/board/5.md", changed)
        self.assertEqual(git(self.origin, "show", f"main:{INST}/d-work/board/5.md"), entry)   # byte-identical
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "program-59cec502"}), \
             contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(bd.cli(["advance", "5", "read", "--expect", "verifying"], d), 1)   # never board advance's
        self.assertIn("fired by `dyad inbox read <message>…`", err.getvalue())

    def test_the_transaction_check_is_append_only(self):
        self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "5", "--kind", "report", "first")
        d = self.clones["program-59cec502"]
        git(d, "pull", "-q", "--ff-only", "origin", "main")
        base = git(d, "rev-parse", "HEAD")
        (msg,) = (d / INST / "d-work" / "inbox" / "program-59cec502").glob("*.md")
        msg.write_text(msg.read_text().replace("first", "edited"))
        git(d, "commit", "-qam", "edit")
        got = ib.check_transaction(d, base, "HEAD")
        self.assertEqual(len(got), 1); self.assertIn("is modified; the inbox is append-only", got[0])
        git(d, "rm", "-q", str(msg)); git(d, "commit", "-qm", "delete")
        self.assertIn("is deleted", ib.check_transaction(d, base, "HEAD")[-1])

    def test_session_touch_prints_the_unread_count(self):
        self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "5", "--kind", "notice", "hello")
        d = self.clones["program-59cec502"]
        git(d, "pull", "-q", "--ff-only", "origin", "main")
        sg = dyadlib.load_guard("agent", "sessions")
        out = io.StringIO()
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "program-59cec502", "CLAUDE_CODE_SESSION_ID": "h2"}), \
             unittest.mock.patch.object(sg.dyadlib, "repo_root", lambda *a: d), contextlib.redirect_stdout(out), \
             contextlib.redirect_stderr(io.StringIO()):
            sg.main(["touch", "-r", "5"])
        self.assertIn("inbox program-59cec502: 1 unread — `dyad inbox read`", out.getvalue())


class WriteAheadTests(World):
    """The write-ahead fence on a relay (d-work #552, mode A): `post --kind relay <seat> --row N` lands only when
    `board/N.md` on origin/main names <seat> among its owners and this session wrote it last."""
    def board_set(self, *pairs, harness="h2"):
        bd = dyadlib.load_guard("agent", "board")
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "program-59cec502", "CLAUDE_CODE_SESSION_ID": harness}), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(bd.cli(["set", "5", *pairs], self.clones["program-59cec502"]), 0)

    def relay(self, to="engineer-1537d8fb", harness="h2"):
        return self.as_seat("program-59cec502", "post", to, "--row", "5", "--kind", "relay", "do task-5", harness=harness)

    def test_reading_a_relay_claims_its_row_in_the_same_land(self):
        """#567 F2: the executor's own inbox read of the relay lands its presence touch with the markers, claiming the
        row the board names it owner of, with the files the row's plan names; a later read of a notice that hands it
        nothing claims nothing more, and only refreshes `seen`."""
        d = self.clones["program-59cec502"]
        plans = d / INST / "d-work" / "plans"; plans.mkdir(parents=True)
        (plans / "5.md").write_text("# Plan #5\n\nFiles touched: dyad/scripts/x.py, dyad/tests/test_x.py\n")
        git(d, "add", "-A"); git(d, *livetest.IDENTITY, "commit", "-qm", "ledger: plan 5"); git(d, "push", "-q", "origin", "HEAD:main")
        self.board_set("owner=engineer-1537d8fb session_x", "waiting-on=unit engineer-1537d8fb", "next=send task-5")
        self.assertEqual(self.relay()[0], 0)
        before = git(self.origin, "rev-parse", "main")
        rc, out, err = self.as_seat("engineer-1537d8fb", "read")
        self.assertEqual((rc, git(self.origin, "rev-parse", "main")), (0, before), err)   # printing claims nothing (#587 S10)
        rc, out, err = self.as_seat("engineer-1537d8fb", "read", *self.unread_names("engineer-1537d8fb"))
        self.assertEqual(rc, 0, err)
        head = git(self.origin, "rev-parse", "main")
        changed = git(self.origin, "diff", "--name-only", before, head).splitlines()
        presence = f"{INST}/d-work/sessions/engineer-1537d8fb.md"
        self.assertIn(presence, changed); self.assertEqual(len(changed), 2, changed)   # the marker and the presence, one commit
        f = dyadlib.load_guard("agent", "sessions").parse(git(self.origin, "show", f"main:{presence}"))
        self.assertEqual((f["rows"], f["files"]), ("5", "dyad/scripts/x.py dyad/tests/test_x.py"))
        self.assertEqual(f["root"], str(self.clones["engineer-1537d8fb"].resolve()))   # the reader's checkout, not land's worktree
        self.assertEqual(self.as_seat("program-59cec502", "post", "engineer-1537d8fb", "--row", "5", "--kind", "notice", "fyi")[0], 0)
        rc, _, err = self.as_seat("engineer-1537d8fb", "read", *self.unread_names("engineer-1537d8fb"))
        self.assertEqual(rc, 0, err)
        f2 = dyadlib.load_guard("agent", "sessions").parse(git(self.origin, "show", f"main:{presence}"))
        self.assertEqual(f2["rows"], "5"); self.assertGreaterEqual(f2["seen"], f["seen"])

    def test_the_holders_relay_adds_its_receiver_as_owner_in_one_commit(self):
        """#586 E1: today's #573 relay to orchestrate, refused twice because orchestrate was no owner, lands with
        orchestrate added to the entry's owners in the same commit; a post from a unit that is not the holder is still
        refused."""
        self.board_set("owner=engineer-1537d8fb session_x", "waiting-on=unit engineer-1537d8fb", "next=send task-5")
        before = git(self.origin, "rev-parse", "main")
        rc, out, err = self.relay(to="orchestrate-d688fecf")
        self.assertEqual(rc, 0, err); self.assertIn("added orchestrate-d688fecf to board/5.md's owners", out)
        head = git(self.origin, "rev-parse", "main")
        self.assertEqual(git(self.origin, "rev-list", "--count", f"{before}..{head}"), "1")
        changed = git(self.origin, "diff", "--name-only", before, head).splitlines()
        self.assertIn(f"{INST}/d-work/board/5.md", changed)
        f = dyadlib.load_guard("agent", "board").parse(git(self.origin, "show", f"main:{INST}/d-work/board/5.md"))[0]
        self.assertEqual(dyadlib.load_guard("agent", "board").owners(f), ["engineer-1537d8fb", "orchestrate-d688fecf"])
        rc, _, err = self.as_seat("engineer-1537d8fb", "post", "counsel-0032b4c0", "--row", "5", "--kind", "relay", "x")
        self.assertEqual(rc, 1); self.assertIn("names owner(s)", err)                  # not the holder: refused
        self.assertEqual(git(self.origin, "rev-parse", "main"), head)

    def test_only_the_holder_adds_an_owner_and_never_on_a_terminal_row(self):
        """The holder condition alone (the entry's last writer, but another seat holds it), and a terminal row."""
        self.board_set("holder=engineer-1537d8fb", "owner=engineer-1537d8fb session_x", "waiting-on=unit engineer-1537d8fb")
        rc, _, err = self.relay(to="orchestrate-d688fecf")                    # program wrote it last, engineer holds it
        self.assertEqual(rc, 1); self.assertIn("names owner(s) engineer-1537d8fb, not orchestrate-d688fecf", err)
        self.board_set("holder=program-59cec502")
        d = self.clones["program-59cec502"]
        git(d, "pull", "-q", "--ff-only", "origin", "main")
        rows = d / INST / "d-work" / "rows" / "5.md"
        rows.write_text(rows.read_text().replace("state: planned", "state: done"))
        git(d, "commit", "-qam", "ledger: #5 done"); git(d, "push", "-q", "origin", "HEAD:main")
        rc, _, err = self.relay(to="orchestrate-d688fecf")
        self.assertEqual(rc, 1); self.assertIn("names owner(s)", err)

    def test_a_relay_without_its_board_entry_is_refused(self):
        before = git(self.origin, "rev-parse", "main")
        rc, _, err = self.relay()
        self.assertEqual(rc, 1); self.assertIn("board/5.md is not on origin/main", err)
        self.assertEqual(git(self.origin, "rev-parse", "main"), before)
        rc, _, err = self.as_seat("engineer-1537d8fb", "post", "program-59cec502", "--row", "5", "--kind", "report", "done")
        self.assertEqual(rc, 0, err)                                         # a report needs no board entry

    def test_the_entry_must_name_the_seat_and_be_this_sessions(self):
        self.board_set("owner=engineer-1537d8fb session_x; counsel-0032b4c0 session_y", "waiting-on=unit engineer-1537d8fb", "next=send task-5")
        rc, _, err = self.relay(to="distribute-a603e150", harness="h3")    # not the entry's last writer: no owner added
        self.assertEqual(rc, 1); self.assertIn("names owner(s) engineer-1537d8fb, counsel-0032b4c0, not distribute-a603e150", err)
        rc, _, err = self.relay(harness="h3")                                # the same seat, another holder
        self.assertEqual(rc, 1); self.assertIn("was last written by h2, not this session (h3)", err)
        rc, out, err = self.relay()
        self.assertEqual(rc, 0, err); self.assertIn("posted ", out)
        rc, _, err = self.relay(to="counsel-0032b4c0")                       # a co-owner is an owner
        self.assertEqual(rc, 0, err)


if __name__ == "__main__":
    unittest.main()
