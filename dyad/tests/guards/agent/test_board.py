"""board.py (the board store, entity `board`; d-work #535, cos mode P1). The form: `key: value` lines with two-space
continuations keep a question verbatim, blank and `#` lines inside a value included, and render back to the same
text. The guard: a well-formed entry for an open row passes; a missing holder, an unknown or repeated key, a bad
`waiting-on` or `since`, a name that is no id and a row that does not exist fail; a terminal row warns as stale; an
absent store passes. `board set` over a scratch world (a bare origin, a seat clone whose pre-push hook only logs):
it lands one ledger-only commit holding the entry, defaults holder, since and writer, merges into the entry as it
stands on origin/main, removes a key on `key=`, warns on another writer, refuses a terminal or unknown row, a typed
`writer` and an identical re-run, and `--drop` removes the file. `dyad board` renders the entries oldest first, and
`resume` prints the owed question verbatim, the gates and the seats to announce to."""
import contextlib, datetime, io, os, shutil, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib, livetest
bd = dyadlib.load_guard("agent", "board")

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
INST = "agent-corpus"
ROW = "id: {id}\ntitle: row {id}\nopened: 2026-11-01\nstate: {state}\ndisposed: 2026-11-01 Y plan\nrefs: \n"
QUESTION = "Release run 41331223332 is waiting.\n\n# not a comment: part of the words\nY/N: approve the release run?"
ENTRY = ("holder: program-aaaaaaaa\nowner: engineer-1537d8fb session_01x\nwaiting-on: operator\n"
         "next: re-present the question\nsince: 2026-11-02T10:00Z\nquestion: Release run 41331223332 is waiting.\n  \n"
         "  # not a comment: part of the words\n  Y/N: approve the release run?\nwriter: h1\n")


def git(d, *a):
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=dyadlib.git_env())
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)} in {d}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class FormTests(unittest.TestCase):
    def test_a_question_round_trips_verbatim(self):
        f, problems = bd.parse(ENTRY)
        self.assertEqual(problems, [])
        self.assertEqual(f["question"], QUESTION)
        self.assertEqual(bd.render(f, bd.FIELDS), ENTRY)

    def test_merged_defaults_holder_since_and_writer(self):
        new = bd.merged({}, {"waiting-on": "seat counsel"}, "program-a", "h2", "2026-11-02T12:00Z")
        self.assertEqual(new, {"waiting-on": "seat counsel", "holder": "program-a", "since": "2026-11-02T12:00Z", "writer": "h2"})
        again = bd.merged(new, {"next": "wait"}, "program-b", "h3", "2026-11-02T13:00Z")
        self.assertEqual((again["since"], again["holder"], again["writer"]), ("2026-11-02T12:00Z", "program-b", "h3"))
        moved = bd.merged(again, {"waiting-on": "operator", "next": ""}, None, "h3", "2026-11-02T14:00Z")
        self.assertEqual(moved["since"], "2026-11-02T14:00Z"); self.assertNotIn("next", moved)
        self.assertEqual(moved["holder"], "program-b")                     # no seat named: the holder stays

    def test_parse_set_refuses_misuse(self):
        for argv, says in ((["x", "next=a"], "not a row id"), (["5"], "usage"), (["5", "writer=me"], "never typed"),
                           (["5", "owner"], "not key=value"), (["5", "colour=red"], "unknown key"),
                           (["5", "holder="], "cannot be removed"), (["5", "waiting-on=bob"], "waiting-on is"),
                           (["5", "since=soon"], "since is"), (["5", "--drop", "next=a"], "--drop takes"),
                           (["_cos", "owner=x"], "unknown key")):
            with self.assertRaises(bd.Refused, msg=argv) as e:
                bd.parse_set(argv)
            self.assertIn(says, str(e.exception))
        self.assertEqual(bd.parse_set(["_cos", "queue=plan 1, done 2"]), ("_cos", {"queue": "plan 1, done 2"}, False))


class GuardTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, True)
        rows = self.root / INST / "d-work" / "rows"; rows.mkdir(parents=True)
        for rid, state in ((5, "planned"), (6, "done")):
            (rows / f"{rid}.md").write_text(ROW.format(id=rid, state=state))
        self.board = self.root / INST / "d-work" / "board"

    def put(self, name, text):
        self.board.mkdir(parents=True, exist_ok=True); (self.board / f"{name}.md").write_text(text)

    def test_an_absent_store_passes(self):
        self.assertEqual(bd.check_package(self.root), [])
        self.assertEqual(bd.summary(self.root), "0 board file(s)")

    def test_a_well_formed_entry_and_cos_pass(self):
        self.put("5", ENTRY)
        self.put("_cos", "holder: program-aaaaaaaa\nqueue: plan 0, done 1\nseats: counsel=session_015q\n  engineer=session_018L\n")
        self.assertEqual(bd.check_package(self.root), [])

    def test_each_defect_fails(self):
        cases = {"holder": ("5", ENTRY.replace("holder: program-aaaaaaaa\n", ""), "'holder' missing"),
                 "unknown": ("5", ENTRY + "colour: red\n", "unknown key 'colour'"),
                 "repeat": ("5", ENTRY + "next: again\n", "key 'next' repeated"),
                 "waiting": ("5", ENTRY.replace("waiting-on: operator", "waiting-on: bob"), "'waiting-on' is not"),
                 "since": ("5", ENTRY.replace("2026-11-02T10:00Z", "soon"), "'since' is not"),
                 "name": ("notes", ENTRY, "not `<id>.md`"),
                 "row": ("9", ENTRY, "no row #9"),
                 "orphan": ("5", "  dangling\n" + ENTRY, "continuation with no key"),
                 "line": ("5", ENTRY + "just words\n", "not `key: value`"),
                 "cos": ("_cos", "holder: p\nowner: x\n", "unknown key 'owner'")}
        for label, (name, text, says) in cases.items():
            shutil.rmtree(self.board, True); self.put(name, text)
            msgs = bd.check_package(self.root)
            self.assertTrue(any(says in m and not m.startswith("warning:") for m in msgs), (label, msgs))

    def test_a_terminal_row_is_a_stale_warning(self):
        self.put("6", ENTRY)
        msgs = bd.check_package(self.root)
        self.assertEqual(len(msgs), 1, msgs)
        self.assertTrue(msgs[0].startswith("warning: board/6.md: row #6 is done; a stale entry"), msgs)

    def test_render_and_resume(self):
        later = ENTRY.replace("2026-11-02T10:00Z", "2026-11-02T12:00Z").replace("waiting-on: operator",
                "waiting-on: external run 41331223332").replace("question:", "promised:")
        self.put("5", later)
        (self.root / INST / "d-work" / "rows" / "7.md").write_text(ROW.format(id=7, state="open"))
        self.put("7", ENTRY)
        self.put("_cos", "holder: program-aaaaaaaa\nqueue: plan 0, done 1\nseats: counsel=session_015q\nwriter: h1\n")
        now = datetime.datetime(2026, 11, 2, 14, tzinfo=datetime.timezone.utc)
        with unittest.mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "h2", "DYAD_SESSION": "program-bbbbbbbb"}):
            lines = bd.board_lines(self.root, now)
            res = bd.resume_lines(self.root)
        self.assertTrue(lines[1].startswith("#7 open     waiting-on operator for 4h"), lines)     # oldest first
        self.assertTrue(lines[3].startswith("#5 planned  waiting-on external run 41331223332 for 2h"), lines)
        self.assertIn("    question: Y/N: approve the release run?", lines)
        self.assertIn("_cos queue: plan 0, done 1", lines)
        self.assertIn("0 open, planned or blocked row(s) carry no board entry", lines)
        self.assertTrue(any(l.startswith("warn: board/5.md was last written by h1, not this session (h2)") for l in lines), lines)
        text = "\n".join(res)
        self.assertIn("owed to the Operator (1)", text)
        self.assertIn("  #7 since 2026-11-02T10:00Z:\n" + "\n".join("    " + l for l in QUESTION.split("\n")), text)
        self.assertIn("external gates (1): #5 external run 41331223332", text)
        self.assertIn("announce to (1): engineer-1537d8fb; seat table: counsel=session_015q", text)

    def test_resume_marks_a_terminal_rows_entry_stale_and_announces_every_owner(self):
        """#547: an entry whose row is done owes nothing; #551: every co-owner is announced to."""
        self.put("6", ENTRY)                                                   # row 6 is done: stale
        self.put("5", ENTRY.replace("owner: engineer-1537d8fb session_01x",
                                    "owner: engineer-1537d8fb session_01x; counsel-0032b4c0 session_015q")
                           .replace("waiting-on: operator", "waiting-on: seat distribute-a603e150").replace("question:", "promised:"))
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "program-bbbbbbbb", "CLAUDE_CODE_SESSION_ID": "h2"}):
            v = bd.resume_view(self.root)
            text = "\n".join(bd.resume_lines(self.root))
        self.assertEqual(([n for n, _ in v["live"]], [n for n, _ in v["stale"]], v["owed"]), (["5"], ["6"], []))
        self.assertEqual(v["seats"], ["counsel-0032b4c0", "distribute-a603e150", "engineer-1537d8fb"])
        self.assertIn("#6: stale — row #6 is done; nothing here is owed (`dyad board set 6 --drop`, #547)", text)
        self.assertIn("owed to the Operator (0)", text)
        self.assertIn("announce to (3): counsel-0032b4c0, distribute-a603e150, engineer-1537d8fb", text)
        self.assertIn("inbox program-bbbbbbbb: 0 unread", text)
        self.assertEqual(bd.owners({"owner": "a-1 s1; b-2 s2;  ; c-3"}), ["a-1", "b-2", "c-3"])

    def test_contract(self):
        self.assertEqual((bd.ENTITY, bd.CORPUS, bd.TRANSACTION), ("board", "agent", False))
        self.assertIsNone(dyadlib.contract_problem(bd, "core", "agent"))
        self.assertEqual(dyadlib.check_invariants(bd), len(bd.INVARIANTS))
        self.assertEqual([f[0] for f in bd.describe(self.root)["fields"]], list(bd.FIELDS))


class SetTests(unittest.TestCase):
    """`board set` lands through land's loop, from a seat clone, onto a bare origin."""
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, "DYAD_SESSION": "program-aaaaaaaa",
                                                  "CLAUDE_CODE_SESSION_ID": "h1"})
        e.start(); self.addCleanup(e.stop)
        top = SCRATCH.mkdtemp()
        seed, self.origin, self.seat, hooks = top / "seed", top / "origin.git", top / "seat", top / "hooks"
        seed.mkdir(); git(seed, "init", "-q", "-b", "main")
        rows = seed / INST / "d-work" / "rows"; rows.mkdir(parents=True)
        for rid, state in ((5, "planned"), (6, "done")):
            (rows / f"{rid}.md").write_text(ROW.format(id=rid, state=state))
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "seed")
        git(top, "clone", "-q", "--bare", str(seed), str(self.origin))
        git(top, "clone", "-q", str(self.origin), str(self.seat))
        for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
            git(self.seat, "config", k, v)
        self.log = top / "hook.log"
        hooks.mkdir(); (hooks / "pre-push").write_text(f"#!/bin/sh\n{{ cat; echo --; }} >> '{self.log}'\nexit 0\n")
        (hooks / "pre-push").chmod(0o755)
        git(self.seat, "config", "core.hooksPath", str(hooks))

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = bd.cli(list(argv), self.seat)
        return rc, out.getvalue(), err.getvalue()

    def on_main(self, name="5"):
        r = subprocess.run(["git", "show", f"main:{INST}/d-work/board/{name}.md"], cwd=self.origin, capture_output=True, text=True)
        return bd.parse(r.stdout)[0] if r.returncode == 0 else None

    def test_set_lands_one_ledger_only_commit(self):
        before = git(self.origin, "rev-parse", "main")
        rc, out, err = self.run_cli("set", "5", "owner=engineer-1537d8fb session_01x", "waiting-on=seat engineer-1537d8fb",
                                    f"question={QUESTION}")
        self.assertEqual(rc, 0, err)
        f = self.on_main()
        self.assertEqual((f["holder"], f["writer"], f["owner"], f["question"]),
                         ("program-aaaaaaaa", "h1", "engineer-1537d8fb session_01x", QUESTION))
        self.assertIsNotNone(bd.parse_since(f["since"]))
        head = git(self.origin, "rev-parse", "main")
        self.assertEqual(git(self.origin, "rev-list", "--count", f"{before}..{head}"), "1")
        self.assertEqual(git(self.origin, "diff", "--name-only", before, head), f"{INST}/d-work/board/5.md")
        self.assertTrue(git(self.origin, "log", "-1", "--format=%s", head).startswith("ledger: board 5"))
        self.assertIn(f"landed {head} on main", out)
        git(self.seat, "fetch", "-q", "origin")
        self.assertTrue(dyadlib.ledger_only(self.seat, before, head))          # the plan gate and the fence admit it

    def test_set_merges_removes_warns_and_refuses(self):
        self.assertEqual(self.run_cli("set", "5", "waiting-on=operator", "next=ask")[0], 0)
        since = self.on_main()["since"]
        with unittest.mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "h2", "DYAD_SESSION": "program-bbbbbbbb"}):
            rc, _, err = self.run_cli("set", "5", "next=", "promised=a follow-up")
        self.assertEqual(rc, 0, err)
        self.assertIn("warn: board/5.md was last written by h1, not this session (h2)", err)
        f = self.on_main()
        self.assertEqual((f["holder"], f["writer"], f["since"], f["promised"]), ("program-bbbbbbbb", "h2", since, "a follow-up"))
        self.assertNotIn("next", f)
        with unittest.mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "h2", "DYAD_SESSION": "program-bbbbbbbb"}):
            rc, _, err = self.run_cli("set", "5", "promised=a follow-up")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)
        for argv, says in ((["set", "6", "next=x"], "row #6 is done"), (["set", "9", "next=x"], "no row #9"),
                           (["set", "5", "writer=x"], "never typed")):
            rc, _, err = self.run_cli(*argv)
            self.assertEqual(rc, 1, argv); self.assertIn(says, err)

    def test_drop_removes_the_file(self):
        self.assertEqual(self.run_cli("set", "5", "next=ask")[0], 0)
        rc, _, err = self.run_cli("set", "5", "--drop")
        self.assertEqual(rc, 0, err)
        self.assertIsNone(self.on_main())
        rc, _, err = self.run_cli("set", "5", "--drop")
        self.assertEqual(rc, 1); self.assertIn("already landed", err)

    def test_usage(self):
        rc, _, err = self.run_cli("bogus")
        self.assertEqual(rc, 2); self.assertIn(bd.USAGE, err)
        rc, _, err = self.run_cli("set")
        self.assertEqual(rc, 2); self.assertIn(bd.USAGE, err)


if __name__ == "__main__":
    unittest.main()
