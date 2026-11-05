"""board.py (the board store, entity `board`; d-work #535, cos mode P1). The form: `key: value` lines with two-space
continuations keep a question verbatim, blank and `#` lines inside a value included, and render back to the same
text. The guard: a well-formed entry for an open row passes; a missing holder, an unknown or repeated key, a bad
`waiting-on` or `since`, a name that is no id and a row that does not exist fail; a terminal row warns as stale; an
absent store passes. `board set` over a scratch world (a bare origin, a seat clone whose pre-push hook only logs):
it lands one ledger-only commit holding the entry, defaults holder, since and writer, merges into the entry as it
stands on origin/main, removes a key on `key=`, warns on another writer, refuses a terminal or unknown row, a typed
`writer` and an identical re-run, and `--drop` removes the file. `dyad board` renders the entries oldest first, and
`resume` prints the owed question verbatim, the gates and the seats to announce to."""
import contextlib, datetime, io, os, re, shutil, subprocess, sys, tempfile, unittest, unittest.mock
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
        self.assertEqual((again["since"], again["holder"], again["writer"]), ("2026-11-02T12:00Z", "program-a", "h3"))   # #572 K7: kept
        moved = bd.merged(again, {"waiting-on": "operator", "next": ""}, None, "h3", "2026-11-02T14:00Z")
        self.assertEqual(moved["since"], "2026-11-02T14:00Z"); self.assertNotIn("next", moved)
        self.assertEqual(moved["holder"], "program-a")                     # no seat named: the holder stays
        self.assertEqual(bd.merged(moved, {"holder": "program-b"}, "program-c", "h4", "x")["holder"], "program-b")   # given: taken

    def test_unit_is_the_form_and_seat_its_alias(self):
        """#553: `waiting-on unit <name>` is the form; `seat <name>` is read until the release after next and written
        as `unit <name>` by `board set`."""
        self.assertEqual(bd.parse_set(["5", "waiting-on=seat engineer-1537d8fb"])[1], {"waiting-on": "unit engineer-1537d8fb"})
        self.assertEqual(bd.parse_set(["5", "waiting-on=unit engineer-1537d8fb"])[1], {"waiting-on": "unit engineer-1537d8fb"})
        self.assertEqual(bd.check_entry("5", ENTRY.replace("waiting-on: operator", "waiting-on: unit engineer-1537d8fb"), {5: "planned"}), [])
        (w,) = bd.check_entry("5", ENTRY.replace("waiting-on: operator", "waiting-on: seat engineer-1537d8fb"), {5: "planned"})
        self.assertTrue(w.startswith("warning: board/5.md: `waiting-on: seat engineer-1537d8fb` uses the alias"), w)   # #573 step 5
        self.assertIn("write `unit engineer-1537d8fb`", w)

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
        self.assertIn("queue (derived, #572): plan-ready 0, done-ready 0", lines)
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

    def test_resume_shows_each_seats_last_ledger_act_as_information(self):
        """#567 F8: the presence file's `seen` per announced seat, `none` without one; never a state."""
        self.put("5", ENTRY.replace("owner: engineer-1537d8fb session_01x",
                                    "owner: engineer-1537d8fb session_01x; counsel-0032b4c0 session_015q"))
        seen = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2, minutes=5)).isoformat(timespec="seconds")
        d = self.root / INST / "d-work" / "sessions"; d.mkdir(parents=True)
        (d / "engineer-1537d8fb.md").write_text(f"session: engineer-1537d8fb\nseen: {seen}\nroot: /x\nrows: 5\nfiles: \n")
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": "program-bbbbbbbb", "CLAUDE_CODE_SESSION_ID": "h2"}):
            v = bd.resume_view(self.root)
            text = "\n".join(bd.resume_lines(self.root))
        self.assertEqual(v["last_act"], {"counsel-0032b4c0": "", "engineer-1537d8fb": seen})
        self.assertIn("last ledger act (presence `seen`, information only, #567): counsel-0032b4c0 none, engineer-1537d8fb 2h", text)
        self.assertEqual([n for n, _ in v["live"]], ["5"])                    # the board, not presence, says what is live

    def test_the_queue_is_derived_from_records(self):
        """#572 K4: plan-ready is an open row with a stored plan and no plan disposition (not accreted); done-ready an
        entry whose question is a Done question."""
        rows, plans = self.root / INST / "d-work" / "rows", self.root / INST / "d-work" / "plans"
        plans.mkdir(parents=True)
        (rows / "7.md").write_text(ROW.format(id=7, state="open").replace("2026-11-01 Y plan", "2026-11-01 Y open"))
        (rows / "8.md").write_text(ROW.format(id=8, state="open").replace("2026-11-01 Y plan", "2026-11-01 Y plan (mandate #5)"))
        for i in (5, 7, 8):
            (plans / f"{i}.md").write_text("# Plan\n")
        self.put("5", ENTRY.replace("Y/N: approve the release run?", "Y/N: Done with #5 five (merges PR #1)?"))
        q = bd.derived_queue(self.root)
        self.assertEqual(q, {"plan-ready": [7], "done-ready": [5]})
        self.assertEqual(bd.queue_line(q), "queue (derived, #572): plan-ready 1 (#7), done-ready 1 (#5)")

    def test_contract(self):
        self.assertEqual((bd.ENTITY, bd.CORPUS, bd.TRANSACTION), ("board", "agent", False))
        self.assertIsNone(dyadlib.contract_problem(bd, "core", "agent"))
        self.assertEqual(dyadlib.check_invariants(bd), len(bd.INVARIANTS) + len(bd.TREE_INVARIANTS))   # #587: a tree list
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
        since, holder = self.on_main()["since"], self.on_main()["holder"]
        with unittest.mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "h2", "DYAD_SESSION": "program-bbbbbbbb"}):
            rc, _, err = self.run_cli("set", "5", "next=", "promised=a follow-up")
        self.assertEqual(rc, 0, err)
        self.assertIn("warn: board/5.md was last written by h1, not this session (h2)", err)
        f = self.on_main()
        self.assertEqual((f["holder"], f["writer"], f["since"], f["promised"]), (holder, "h2", since, "a follow-up"))   # #572 K7
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


# ---- d-work #587 PR2: the orchestration machine (X1, X2, X3, X4, X9)
H1, H2, H3 = "9bbb5cc8", "f35eb112", "a1b2c3d4"
EV = "0123456789abcdef" * 4
HOME, ENG, COU = "program-aaaaaaaa", "engineer-bbbbbbbb", "counsel-cccccccc"


def phased(rid, phase, sub, holder=HOME, owner=f"{ENG}; {COU}", question=None, note=None, since="2026-11-04T10:00Z", writer="h1"):
    """A phased entry as `board advance` writes it: the derived fields from `derive`."""
    f = {"holder": holder, "phase": bd.phase_render(phase, sub), "owner": owner, "since": since, "writer": writer}
    f.update(bd.derive(rid, f))
    if question:
        f["question"] = question
    if note:
        f["note"] = note
    return bd.render(f, bd.FIELDS)


class Row:   # the fields `question` reads
    def __init__(self, id, title, state="planned", disposed="", refs=""):
        self.id, self.title, self.state, self.disposed, self.refs = id, title, state, disposed, refs


class MachineTests(unittest.TestCase):
    def test_phase_round_trips_with_repeated_pr(self):
        value = f"verifying\nunit: {ENG}\npr: 650 at {H1}\npr: 651 at {H2}\nevidence: {EV}"
        name, sub = bd.phase_of(value)
        self.assertEqual((name, sub["pr"]), ("verifying", [f"650 at {H1}", f"651 at {H2}"]))
        self.assertEqual(bd.phase_render(name, sub), value)
        self.assertEqual(bd.phase_of("landing\n  unit: u\n  pr: 1 at abc1234")[1]["unit"], ["u"])   # indented is read
        text = phased(5, "verifying", sub)
        self.assertEqual(bd.render(bd.parse(text)[0], bd.FIELDS), text)
        for bad in ("", "two words", "planning\nunit u", "planning\ncolour: red", "planning\nunit: a\nunit: b"):
            with self.assertRaises(ValueError, msg=bad):
                bd.phase_of(bad)

    def test_pr_replaces_the_head_of_a_listed_pr(self):
        sub = bd.pr_add(bd.pr_add({"unit": ["u"]}, 650, H1), 651, H2)
        self.assertEqual(bd.pr_list(bd.pr_add(sub, 650, H3)), [(650, H3), (651, H2)])
        self.assertEqual(bd.prs_text(sub), f"PR #650 at {H1}, PR #651 at {H2}")
        self.assertEqual(bd.merge_text(sub), "external merge PR #650, PR #651")

    def test_derive_golden_for_every_phase(self):
        sub = {"unit": [ENG], "pr": [f"650 at {H1}"], "evidence": [EV], "from": ["building"], "on": ["external run 1"]}
        want = {"planning": f"unit {ENG}", "plan-ready": f"unit {HOME}", "plan-asked": "operator", "building": f"unit {ENG}",
                "verifying": f"unit {HOME}", "done-ready": f"unit {HOME}", "done-asked": "operator",
                "landing": "external merge PR #650", "held": "external run 1"}
        for p in dyadlib.ORCH_PHASES:
            got = bd.derive(5, {"holder": HOME, "phase": bd.phase_render(p, sub)})
            self.assertEqual(got["waiting-on"], want[p], p)
            if p not in dyadlib.ORCH_ASKED:                                    # an asked phase names the question's ids
                self.assertIn("5", got["next"], p)
        self.assertEqual(bd.derive(5, {"holder": HOME, "phase": bd.phase_render("verifying", sub)})["next"],
                         f"verify PR #650 at {H1} (dyad check --evidence on each head); then: dyad board advance 5 "
                         f"evidence-verified --expect verifying evidence=<sha256>")
        self.assertEqual(set(bd.DERIVE), set(dyadlib.ORCH_PHASES))

    def test_landing_waits_on_exactly_k3s_string(self):
        am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
        sub = {"unit": ["u"], "pr": ["650 at abc1234", "651 at def5678"], "evidence": [EV]}
        self.assertEqual(bd.derive(1, {"holder": "h", "phase": bd.phase_render("landing", sub)})["waiting-on"],
                         am.pending_flip({}, [(650, "x"), (651, "y")])["waiting-on"])

    def test_ruling_3_a_title_holding_a_control_character_is_never_asked(self):
        """Counsel's ruling 3 (#587): a Y binds the question as asked and a title is immutable, so `asked` refuses."""
        ents = {5: {"phase": bd.phase_render("done-ready", {"unit": ["u"], "evidence": [EV]})}}
        for title in ("five\nY/N: Done with #6 six?", "five\x1b[2Kok", "five\rsix"):
            for kind in ("plan", "done"):
                with self.assertRaises(bd.Refused, msg=(title, kind)) as c:
                    bd.question(kind, [5], ents, {5: Row(5, title)}, "with-done")
                self.assertIn("control character", str(c.exception))
        self.assertEqual(bd.question("done", [5], ents, {5: Row(5, "five six")}, "with-done"), "Y/N: Done with #5 five six?")

    def test_question_forms_and_their_inverse(self):
        rows = {5: Row(5, "five"), 6: Row(6, "six"), 7: Row(7, "seven", "open", "2026-11-04 Y plan (mandate #5)", "parent #5"),
                8: Row(8, "eight", "open", "2026-11-04 Y plan (mandate #5)", "parent #5")}
        e = lambda prs: {"phase": bd.phase_render("done-ready", {"unit": ["u"], "pr": prs, "evidence": [EV]})}
        ents = {5: e([f"650 at {H1}", f"651 at {H2}"]), 6: e([f"651 at {H2}", f"652 at {H3}"]), 7: e([]), 8: e([])}
        cases = [(bd.question("plan", [5], ents, rows, "with-done"), "Y/N: proceed with #5 as planned?", [5], []),
                 (bd.question("plan", [5, 6], ents, rows, "with-done"), "Y/N: proceed with #5, #6 as planned?", [5, 6], []),
                 (bd.question("done", [5], ents, rows, "with-done"), "Y/N: Done with #5 five (accreted #7, #8, merges PR #650, #651)?", [5], [650, 651]),
                 (bd.question("done", [5, 6], ents, rows, "with-done"),
                  "Y/N: Done with #5 five (accreted #7, #8), #6 six (merges PR #650, #651, #652)?", [5, 6], [650, 651, 652]),
                 (bd.question("done", [7], ents, rows, "separate"), "Y/N: Done with #7 seven?", [7], [])]
        for got, want, ids, merges in cases:
            self.assertEqual(got, want)
            self.assertEqual((bd.ids_of(got), bd.merges_of(got)), (ids, merges), got)
        with self.assertRaises(bd.Refused) as c:
            bd.question("done", [5], ents, rows, "separate")
        self.assertIn("not with-done", str(c.exception))

    def test_relay_lines_for_every_row_of_the_table(self):
        import shlex
        sub = {"unit": [ENG], "pr": [f"650 at {H1}"], "evidence": [EV]}
        entry = {"holder": HOME, "owner": f"{ENG}; {COU}", "phase": bd.phase_render("verifying", sub)}
        want = {("opened", "planning"): (ENG, "relay", []), ("plan-landed", "plan-ready"): (HOME, "report", []),
                ("answered-Y", "building"): (ENG, "notice", []), ("answered-N", "planning"): (ENG, "relay", []),
                ("pr-up", "verifying"): (HOME, "report", ["--cc", COU]),
                ("evidence-verified", "done-ready"): (HOME, "report", []),
                ("evidence-failed", "building"): (ENG, "relay", []), ("answered-Y", "landing"): (ENG, "notice", ["--cc", COU]),
                ("answered-Y", dyadlib.ORCH_DROP): (ENG, "notice", ["--cc", COU]), ("answered-N", "building"): (ENG, "relay", []),
                ("hold", "held"): (ENG, "notice", ["--cc", COU]), ("release", dyadlib.ORCH_FROM): (ENG, "notice", ["--cc", COU]),
                ("head-moved", "verifying"): (HOME, "report", ["--cc", ENG, "--cc", COU]),   # #587 X6: the owners relayed
                ("withdrawn", "done-ready"): (HOME, "report", [])}                     # X6 for a batch's other rows
        self.assertEqual(set(want), set(bd.RELAYS))
        ib = dyadlib.load_guard("agent", "inbox")
        for (event, target), (to, kind, cc) in want.items():
            if (event, target) == ("answered-Y", "building"):
                continue                                                         # one per owner: below
            sender = ENG if (event, target) == ("pr-up", "verifying") else "someone-else"
            (line,) = bd.relay_lines(5, event, "plan-ready" if target == dyadlib.ORCH_FROM else target, entry, sender,
                                     "parts: engineer: the verb", {"pr": "650", "head": H1})
            toks = shlex.split(line)
            self.assertEqual(toks[:6], ["post", to, "--row", "5", "--kind", kind], (event, target))
            self.assertEqual(toks[6:-1], cc, (event, target))
            self.assertFalse(ib.DISPOSITION.search(toks[-1]), toks[-1])          # X2: information, never authority
        (y,) = bd.relay_lines(5, "answered-Y", "building", {**entry, "owner": ENG}, HOME, "parts: engineer: the verb")
        self.assertEqual(shlex.split(y)[-1], "row #5 planned; read plans/5.md; yours: the verb")   # K2's plan notice
        self.assertEqual(bd.relay_lines(5, "opened", "planning", {**entry, "phase": bd.phase_render("planning", {"unit": [HOME]})}, HOME), [])
        self.assertEqual(bd.relay_lines(5, "asked", "plan-asked", entry, HOME), [])
        self.assertEqual(dyadlib.false_invariants(bd.TREE_INVARIANTS), [])

    def test_the_plan_notice_reaches_every_owner_with_its_own_part(self):
        """K2's shape for a phased entry: one `notice` per owner (co-owners included), each quoting its own part, never
        to the sender; the kind `inbox.handed_rows` reads as handing the row."""
        import shlex
        entry = {"holder": HOME, "owner": f"{ENG}; {COU}", "phase": bd.phase_render("building", {"unit": [ENG]})}
        lines = bd.relay_lines(5, "answered-Y", "building", entry, HOME, "parts: engineer: the verb; counsel: the Rule")
        self.assertEqual([shlex.split(x) for x in lines],
                         [["post", ENG, "--row", "5", "--kind", "notice", "row #5 planned; read plans/5.md; yours: the verb"],
                          ["post", COU, "--row", "5", "--kind", "notice", "row #5 planned; read plans/5.md; yours: the Rule"]])
        ib = dyadlib.load_guard("agent", "inbox")
        self.assertEqual(ib.handed_rows([(None, {"kind": "notice", "row": "5", "body": shlex.split(x)[-1]}) for x in lines]), ["5"])
        self.assertEqual(len(bd.relay_lines(5, "answered-Y", "building", entry, COU, "")), 1)   # not to the sender

    def test_transition_is_pure_and_keeps_since_on_a_self_loop(self):
        row = Row(5, "five")
        old = bd.parse(phased(5, "verifying", {"unit": [ENG], "pr": [f"650 at {H1}"]}))[0]
        target, new = bd.transition(5, old, row, "pr-up", {"pr": "651", "head": H2}, COU, "2026-11-04T12:00Z")
        self.assertEqual((target, new["since"]), ("verifying", "2026-11-04T10:00Z"))
        self.assertEqual(bd.pr_list(bd.phase_of(new["phase"])[1]), [(650, H1), (651, H2)])
        target, new = bd.transition(5, new, row, "hold", {"note": "waits on run 1", "on": "external run 1"}, HOME, "2026-11-04T13:00Z")
        self.assertEqual((target, new["waiting-on"], new["since"], new["note"]), ("held", "external run 1", "2026-11-04T13:00Z", "waits on run 1"))
        target, new = bd.transition(5, new, row, "release", {}, HOME, "2026-11-04T14:00Z")
        self.assertEqual(target, "verifying"); self.assertNotIn("from", bd.phase_of(new["phase"])[1])
        asked = bd.parse(phased(5, "done-asked", {"unit": [ENG], "evidence": [EV]}, question="Y/N: Done with #5 five?"))[0]
        held = bd.transition(5, asked, row, "hold", {"note": "n", "on": "operator"}, HOME, "x")[1]
        self.assertNotIn("question", held)                                       # hold takes the question down
        self.assertEqual(bd.transition(5, held, row, "release", {}, HOME, "y")[0], "done-ready")   # and steps back
        self.assertEqual(bd.transition(5, asked, row, "answered-Y", {}, HOME, "z"), (dyadlib.ORCH_DROP, None))
        for event, sender, says in (("asked", HOME, "not an event from there"), ("pr-up", "stranger-1", "a unit event")):
            with self.assertRaises(bd.Refused, msg=event) as c:
                bd.transition(5, old, row, event, {"pr": "1", "head": H1}, sender, "t")
            self.assertIn(says, str(c.exception))

    def test_head_moved_withdraws_the_question_and_the_evidence(self):
        """#587 X6: from verifying, done-ready or done-asked a moved head goes back to verifying with the new head
        recorded, the evidence and any stored question dropped; only the automaton fires it."""
        row = Row(5, "five")
        for phase, q in (("verifying", None), ("done-ready", None), ("done-asked", "Y/N: Done with #5 five (merges PR #650)?")):
            sub = {"unit": [ENG], "pr": [f"650 at {H1}", f"651 at {H2}"]} | ({} if phase == "verifying" else {"evidence": [EV]})
            old = bd.parse(phased(5, phase, sub, question=q))[0]
            target, new = bd.transition(5, old, row, "head-moved", {"pr": "650", "head": H3}, "automaton", "2026-11-04T12:00Z",
                                        automaton=True)
            got = bd.phase_of(new["phase"])[1]
            self.assertEqual((target, bd.pr_list(got), got.get("evidence")), ("verifying", [(650, H3), (651, H2)], None), phase)
            self.assertNotIn("question", new, phase)
            self.assertEqual(new["waiting-on"], f"unit {HOME}")
            self.assertEqual(bd.check_phased("5", new, None), [], phase)
            with self.assertRaises(bd.Refused, msg=phase) as c:                    # never from a seat
                bd.transition(5, old, row, "head-moved", {"pr": "650", "head": H3}, HOME, "t")
            self.assertIn("an automaton event never comes from the CLI", str(c.exception))
        with self.assertRaises(bd.Refused):                                      # not from building
            bd.transition(5, bd.parse(phased(5, "building", {"unit": [ENG]}))[0], row, "head-moved",
                          {"pr": "650", "head": H3}, "automaton", "t", automaton=True)

    def test_withdrawn_steps_a_batch_sibling_back_to_done_ready(self):
        """#587 X6 for a batch: the other rows a withdrawn batch Done question named step back from done-asked to
        done-ready, their own heads and evidence kept, the question dropped, the note recorded; only the automaton
        fires it, and only from done-asked."""
        row = Row(6, "six")
        sub = {"unit": [ENG], "pr": [f"651 at {H2}"], "evidence": [EV]}
        old = bd.parse(phased(6, "done-asked", sub, question="Y/N: Done with #5 five, #6 six (merges PR #650, #651)?"))[0]
        target, new = bd.transition(6, old, row, "withdrawn", {"note": "PR #650 of #5 moved to 0123456789ab"}, "automaton",
                                    "2026-11-04T12:00Z", automaton=True)
        got = bd.phase_of(new["phase"])[1]
        self.assertEqual((target, bd.pr_list(got), got.get("evidence")), ("done-ready", [(651, H2)], [EV]))
        self.assertNotIn("question", new)
        self.assertEqual(new["note"], "PR #650 of #5 moved to 0123456789ab")
        self.assertEqual(bd.check_phased("6", new, None), [])
        with self.assertRaises(bd.Refused) as c:                                 # never from a seat
            bd.transition(6, old, row, "withdrawn", {"note": "n"}, HOME, "t")
        self.assertIn("an automaton event never comes from the CLI", str(c.exception))
        with self.assertRaises(bd.Refused):                                      # not from done-ready
            bd.transition(6, bd.parse(phased(6, "done-ready", sub))[0], row, "withdrawn", {"note": "n"}, "automaton", "t",
                          automaton=True)

    def test_the_automaton_fires_only_its_own_events(self):
        """#587 X5: evidence-verified and evidence-failed from verifying are home's or the automaton's; the automaton
        may not fire a home-only event (an answer, asked, hold) nor a unit's."""
        row = Row(5, "five")
        ver = bd.parse(phased(5, "verifying", {"unit": [ENG], "pr": [f"650 at {H1}"]}))[0]
        t, new = bd.transition(5, ver, row, "evidence-verified", {"evidence": EV}, "automaton", "t", automaton=True)
        self.assertEqual((t, bd.first(bd.phase_of(new["phase"])[1], "evidence")), ("done-ready", EV))
        t, new = bd.transition(5, ver, row, "evidence-failed", {"note": "combined merge: conflict"}, "automaton", "t", automaton=True)
        self.assertEqual((t, new["note"]), ("building", "combined merge: conflict"))
        self.assertEqual(bd.transition(5, ver, row, "evidence-verified", {"evidence": EV}, HOME, "t")[0], "done-ready")   # home still may
        for event, pairs in (("hold", {"note": "n", "on": "operator"}), ("pr-up", {"pr": "651", "head": H2})):
            with self.assertRaises(bd.Refused, msg=event) as c:
                bd.transition(5, ver, row, event, pairs, "automaton", "t", automaton=True)
            self.assertIn("never the automaton's", str(c.exception))
        bd_ = bd.parse(phased(5, "building", {"unit": [ENG]}))[0]
        with self.assertRaises(bd.Refused):                                      # building's evidence-verified is home's
            bd.transition(5, bd_, row, "evidence-verified", {"evidence": EV}, "automaton", "t", automaton=True)
        with self.assertRaises(bd.Refused) as c:                                 # the CLI never names head-moved
            bd.parse_advance(["5", "head-moved", "--expect", "verifying", "pr=650", f"head={H3}"])
        self.assertIn("is not an event", str(c.exception))

    def test_ledger_lines_compose_the_answer(self):
        rows = {5: Row(5, "five", "open"), 6: Row(6, "six", "planned"),
                7: Row(7, "seven", "open", "2026-11-04 Y plan (mandate #5)", "parent #5")}
        q = lambda text, prs: {"question": text, "phase": bd.phase_render("done-asked", {"unit": ["u"], "pr": prs, "evidence": [EV]})}
        self.assertEqual(bd.ledger_lines([5], {5: {"question": "Y/N: proceed with #5 as planned?"}}, rows, "answered-Y", "/w"),
                         ["state 5 planned -d 'Y plan' --said-file /w"])
        self.assertEqual(bd.ledger_lines([5, 6], {i: {"question": "Y/N: proceed with #5, #6 as planned?"} for i in (5, 6)}, rows, "answered-Y", "/w"),
                         ["state 5 planned -d 'Y plan (batch #5,#6)' --said-file /w", "state 6 planned -d 'Y plan (batch #5,#6)' --said-file /w"])
        self.assertEqual(bd.ledger_lines([5], {5: {"question": "Y/N: proceed with #5 as planned?"}}, rows, "answered-N", "/w"),
                         ["state 5 open -d 'N plan' --said-file /w"])
        one = {5: q("Y/N: Done with #5 five (accreted #7, merges PR #650, #651)?", [f"650 at {H1}", f"651 at {H2}"])}
        self.assertEqual(bd.ledger_lines([5], one, rows, "answered-Y", "/w", "with-done"),
                         [f"state 5 open -d 'Y done (accreted #7, merges PR #650 at {H1}, PR #651 at {H2})' --said-file /w"])
        both = {5: q("Y/N: Done with #5 five (accreted #7), #6 six (merges PR #650, #651)?", [f"650 at {H1}"]),
                6: q("Y/N: Done with #5 five (accreted #7), #6 six (merges PR #650, #651)?", [f"651 at {H2}"])}
        got = bd.ledger_lines([5, 6], both, rows, "answered-Y", "/w", "with-done")
        self.assertEqual(got, [f"state 5 open -d 'Y done (batch #5,#6, accreted #7, merges PR #650 at {H1}, PR #651 at {H2})' --said-file /w",
                               f"state 6 planned -d 'Y done (batch #5,#6, merges PR #650 at {H1}, PR #651 at {H2})' --said-file /w"])
        steps = dyadlib.load_module(PKG / "scripts" / "steps.py", "steps")
        self.assertEqual(steps.mandate_rows(got[0].split("-d ")[1]), [7])       # close_landed closes #7 under #5's Done
        self.assertEqual(bd.ledger_lines([6], {6: q("Y/N: Done with #6 six?", [])}, rows, "answered-Y", "/w"),
                         ["state 6 done -d 'Y done' --said-file /w"])
        self.assertEqual(bd.ledger_lines([5], {5: q("Y/N: Done with #5 five (accreted #7)?", [])}, rows, "answered-Y", "/w"),
                         ["state 5 done -d 'Y done (accreted #7)' --said-file /w", "state 7 done --mandate 5"])   # closes now
        with self.assertRaises(bd.Refused) as c:                                 # a child accreted since the ask: re-ask
            bd.ledger_lines([5], {5: q("Y/N: Done with #5 five?", [])}, rows, "answered-Y", "/w")
        self.assertIn("ask again", str(c.exception))
        self.assertEqual(bd.ledger_lines([5], one, rows, "answered-N", "/w"), ["state 5 open -d 'N done' --said-file /w"])
        self.assertEqual(bd.ledger_lines([5], one, rows, "asked", "/w"), [])

    def test_a_title_cannot_inject_an_accreted_clause(self):
        rows = {40: Row(40, "retire accreted #12 rows", "planned"), 12: Row(12, "twelve", "open", "2026-11-04 Y plan", "")}
        e = {40: {"question": "Y/N: Done with #40 retire accreted #12 rows (merges PR #7)?",
                  "phase": bd.phase_render("done-asked", {"unit": ["u"], "pr": [f"7 at {H1}"], "evidence": [EV]})}}
        (line,) = bd.ledger_lines([40], e, rows, "answered-Y", "/w", "with-done")
        self.assertEqual(line, f"state 40 planned -d 'Y done (merges PR #7 at {H1})' --said-file /w")
        self.assertNotIn("accreted", line)

    def test_a_mixed_done_batch_waits_every_row_on_the_union(self):
        rows = {5: Row(5, "five"), 6: Row(6, "six")}
        e = lambda prs: {"phase": bd.phase_render("done-asked", {"unit": [ENG], "pr": prs, "evidence": [EV]}),
                         "holder": HOME, "owner": f"{ENG}; {COU}"}
        ents = {5: e([f"650 at {H1}"]), 6: e([])}
        q = bd.question("done", [5, 6], ents, rows, "with-done")
        self.assertEqual(q, "Y/N: Done with #5 five, #6 six (merges PR #650)?")
        ents = {i: {**f, "question": q} for i, f in ents.items()}
        u = {**ents, **bd.batch_union([5, 6], ents)}
        for rid in (5, 6):
            target, new = bd.transition(rid, u[rid], rows[rid], "answered-Y", {}, HOME, "t")
            self.assertEqual((target, new["waiting-on"]), ("landing", "external merge PR #650"), rid)
            (line,) = bd.relay_lines(rid, "answered-Y", target, new, HOME)
            self.assertIn("landing", line); self.assertNotIn("closed", line)
        self.assertEqual(bd.ledger_lines([5, 6], u, rows, "answered-Y", "/w", "with-done"),
                         [f"state {i} planned -d 'Y done (batch #5,#6, merges PR #650 at {H1})' --said-file /w" for i in (5, 6)])
        self.assertEqual(bd.batch_union([5, 6], {5: e([]), 6: e([])}), {})       # no PR anywhere: each drops, row done

    def test_recorded_done_heads_cover_the_phase_or_a_batch(self):
        sub = {"unit": ["u"], "pr": [f"650 at {H1}"]}
        r = lambda d: Row(5, "five", "planned", f"2026-11-01 Y plan; {d}")
        self.assertEqual(bd.recorded_done_heads(5, r(f"2026-11-04 Y done (merges PR #650 at {H3})"), sub), [(650, H3)])
        self.assertIsNone(bd.recorded_done_heads(5, r(f"2026-11-04 Y done (merges PR #651 at {H2})"), sub))
        self.assertIsNone(bd.recorded_done_heads(5, r(f"2026-11-04 Y done (merges PR #650 at {H1}, PR #651 at {H2})"), sub))
        self.assertEqual(bd.recorded_done_heads(5, r(f"2026-11-04 Y done (batch #5,#6, merges PR #650 at {H1}, PR #651 at {H2})"), sub),
                         [(650, H1), (651, H2)])
        self.assertIsNone(bd.recorded_done_heads(5, r(f"2026-11-04 Y done (batch #6,#8, merges PR #650 at {H1}, PR #651 at {H2})"), sub))

    def test_ledger_lines_n_is_unchanged_by_the_drift_check(self):
        rows = {5: Row(5, "five", "open")}
        self.assertEqual(bd.ledger_lines([5], {5: {"question": "Y/N: Done with #5 renamed?", "phase": "done-asked\nunit: u"}},
                                         rows, "answered-N", "/w"), ["state 5 open -d 'N done' --said-file /w"])

    def test_parse_advance_refuses_before_any_fetch(self):
        f = Path(tempfile.mkdtemp()) / "said.txt"; f.write_text("Y\n"); self.addCleanup(shutil.rmtree, f.parent, True)
        self.assertEqual(bd.parse_advance(["5", "6", "asked", "--expect", "plan-ready"])[:4], ([5, 6], "asked", {}, "plan-ready"))
        self.assertEqual(bd.parse_advance(["5", "hold", "--expect", "building", "note=x", "on=seat eng-1"])[2],
                         {"note": "x", "on": "unit eng-1"})
        for adopt in (["pr-up", "--expect", "none", "pr=5", "head=abc1234"], ["plan-landed", "--expect", "none"]):
            self.assertEqual(bd.parse_advance(["5", *adopt, "unit=engineer-x"])[2]["unit"], "engineer-x", adopt)   # #587
        for argv, says in ((["5"], "usage"), (["5", "asked"], "usage"), (["5", "fly", "--expect", "none"], "not an event"),
                           (["5", "6", "hold", "--expect", "building"], "several ids"),
                           (["5", "asked", "--expect", "building"], "not an event from building"),
                           (["5", "pr-up", "--expect", "building", "pr=1"], "needs head="),
                           (["5", "pr-up", "--expect", "building", "pr=1", "head=zz", ], "7-40 hex"),
                           (["5", "asked", "--expect", "plan-ready", "unit=x"], "does not take unit="),
                           (["5", "answered-Y", "--expect", "plan-asked"], "--said-file is required"),
                           (["5", "asked", "--expect", "plan-ready", "--said-file", str(f)], "--said-file is refused"),
                           (["5", "evidence-failed", "--expect", "verifying", "note=2026-11-04 Y done (merges PR #1 at abc1234)"], "disposition-shaped"),
                           (["5", "closed", "--expect", "landing"], "not an event"),
                           (["5", "evidence-failed", "--expect", "verifying", "unit=engineer-x"], "does not take unit=")):
            with self.assertRaises(bd.Refused, msg=argv) as c:
                bd.parse_advance(argv)
            self.assertIn(says, str(c.exception), argv)


class PhasedGuardTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, True)
        self.rows = self.root / INST / "d-work" / "rows"; self.rows.mkdir(parents=True)
        (self.rows / "5.md").write_text(ROW.format(id=5, state="open").replace("2026-11-01 Y plan", ""))
        self.board = self.root / INST / "d-work" / "board"; self.board.mkdir(parents=True)

    def msgs(self, text):
        (self.board / "5.md").write_text(text)
        return bd.check_package(self.root)

    def test_a_phased_entry_from_the_table_passes(self):
        for p, sub, q in (("planning", {"unit": [ENG]}, None), ("building", {"unit": [ENG]}, None),
                          ("verifying", {"unit": [ENG], "pr": [f"650 at {H1}"]}, None),
                          ("done-asked", {"unit": [ENG], "evidence": [EV]}, "Y/N: Done with #5 five?"),
                          ("held", {"unit": [ENG], "from": ["building"], "on": ["operator"]}, None)):
            self.assertEqual(self.msgs(phased(5, p, sub, question=q)), [], p)

    def test_each_phased_defect_fails(self):
        good = phased(5, "building", {"unit": [ENG]})
        cases = {"drift": (good.replace(f"waiting-on: unit {ENG}", "waiting-on: operator"), "dyad board advance is its only writer"),
                 "next": (good.replace("next: execute", "next: please execute"), "'next' is"),
                 "unknown": (good.replace("phase: building", "phase: brewing"), "not one of"),
                 "no-pr": (phased(5, "verifying", {"unit": [ENG]}), "needs sub-key 'pr'"),
                 "no-evidence": (phased(5, "done-ready", {"unit": [ENG]}), "needs sub-key 'evidence'"),
                 "no-from": (phased(5, "held", {"unit": [ENG], "on": ["operator"]}), "needs sub-key 'from'"),
                 "not-owner": (phased(5, "building", {"unit": ["stranger-1"]}), "not among the owners"),
                 "no-question": (phased(5, "plan-asked", {"unit": [ENG]}), "needs its question"),
                 "stray-question": (phased(5, "building", {"unit": [ENG]}, question="Y/N: proceed with #5 as planned?"), "outside an asked phase"),
                 "bad-pr": (phased(5, "verifying", {"unit": [ENG], "pr": ["650 at nothex"]}), "is not `<n> at"),
                 "bad-subkey": (good.replace(f"  unit: {ENG}", f"  unit: {ENG}\n  colour: red"), "unknown sub-key")}
        for label, (text, says) in cases.items():
            got = self.msgs(text)
            self.assertTrue(any(says in m and not m.startswith("warning:") for m in got), (label, got))
        cos = "holder: p\nphase: planning\n  unit: x\n"
        (self.board / "_cos.md").write_text(cos)
        self.assertTrue(any("_cos.md: unknown key 'phase'" in m for m in bd.check_package(self.root)))

    def test_the_ledger_ahead_is_a_warning(self):
        (self.rows / "5.md").write_text(ROW.format(id=5, state="planned"))
        msgs = self.msgs(phased(5, "plan-asked", {"unit": [ENG]}, question="Y/N: proceed with #5 as planned?"))
        self.assertTrue(msgs and all(m.startswith("warning:") for m in msgs), msgs)
        self.assertTrue(any("the ledger is ahead" in m for m in msgs), msgs)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(bd.main([str(self.root)]), 0)                      # a warning, never a failure
        self.assertIn("warn [rule-3]", out.getvalue())
        self.assertEqual(bd.check_entry("5", phased(5, "plan-asked", {"unit": [ENG]}, question="Y/N: proceed with #5 as planned?"),
                                        {5: "planned"}), [])                    # without rows: the row checks are skipped
        msgs = self.msgs(phased(5, "plan-ready", {"unit": [ENG]}))
        self.assertEqual(len(msgs), 1); self.assertIn("still at plan-ready: the ledger is ahead (the automaton catches up)", msgs[0])
        (self.rows / "5.md").write_text(ROW.format(id=5, state="planned").replace(
            "Y plan\n", f"Y plan; 2026-11-04 Y done (merges PR #650 at {H1})\n"))
        for p, sub, says in (("done-ready", {"unit": [ENG], "pr": [f"650 at {H1}"], "evidence": [EV]}, "the automaton catches up"),
                             ("verifying", {"unit": [ENG], "pr": [f"650 at {H1}"]}, "recorded outside done-asked (phase verifying)"),
                             ("building", {"unit": [ENG]}, "on=external merge PR #650")):
            msgs = self.msgs(phased(5, p, sub))
            self.assertTrue(msgs and all(m.startswith("warning:") for m in msgs), (p, msgs))
            self.assertTrue(any(says in m for m in msgs), (p, msgs))

    # compatibility (b): today's entries, which carry no phase, yield what they yield today
    LIVE = {"498": ("holder: program-59cec502\nowner: communicate-17f24597 session_01J9bJr45vegHU9tt315RQ2V\nwaiting-on: operator\n"
                    "next: operator's persona corrections and outline approval in the paired communicate chat; then #503\n"
                    "since: 2026-11-03T16:23Z\nwriter: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", "open"),
            "572": ("holder: orchestrate-d688fecf\nowner: engineer-1537d8fb; orchestrate-d688fecf\nwaiting-on: unit program-59cec502\n"
                    "next: draft 17:40Z is stale on #650's head: #650 rebased to 9bbb5cc8\nsince: 2026-11-04T18:05Z\n"
                    "writer: d688fecf-bbf8-50db-a0b4-26a3971d3761\n", "planned"),
            "575": ("holder: program-59cec502\nowner: program-59cec502; distribute-a603e150; orchestrate-d688fecf\n"
                    "waiting-on: external github-actions\nnext: PR #648 merged by the operator at 15:22Z (1c36a4b1)\n"
                    "since: 2026-11-04T15:23Z\nwriter: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", "planned"),
            "503": ("holder: program-59cec502\nowner: distribute-a603e150 session_0169uQg7HXf2YJowR5n9HfHa; communicate-17f24597 "
                    "session_01J9bJr45vegHU9tt315RQ2V\nwaiting-on: operator\nnext: Pages workflow, site/ skeleton, manifest row and "
                    "season-1 outline after #498's outline is approved; private quotes stay off public remotes until each "
                    "episode's publish question (remedy B)\nsince: 2026-11-03T16:23Z\nwriter: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", "open"),
            "570": ("holder: program-59cec502\nowner: audit-e73be78c; engineer-1537d8fb; counsel-0032b4c0; distribute-a603e150; "
                    "orchestrate-d688fecf\nwaiting-on: unit counsel-0032b4c0\nnext: rows by DoD: #571 hardening (audit), #572 "
                    "automaton (engineer), #573 surface (counsel), #574 attention (counsel: DoD play-book step, then home's backlog "
                    "DoD report); #575 sweep troubleshooting (home); release DoD: the cut after all done and 7 clean sweep days\n"
                    "since: 2026-11-04T02:35Z\nwriter: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", "planned"),
            "573": ("holder: orchestrate-d688fecf\nowner: counsel-0032b4c0; engineer-1537d8fb; orchestrate-d688fecf\nwaiting-on: unit "
                    "engineer-1537d8fb\nnext: fix #651: test_surface S3 stale filter fails 'attended-seats' (alias) once #652 renames "
                    "the key (combined merge red, Rule-12); then orchestrate re-runs the combined check and drafts the Done\n"
                    "since: 2026-11-04T17:58Z\nwriter: d688fecf-bbf8-50db-a0b4-26a3971d3761\n", "open"),
            "574": ("holder: program-59cec502\nowner: counsel-0032b4c0; engineer-1537d8fb\nwaiting-on: operator\nnext: revision 3's "
                    "Rule-3 sentences fold into #585 if planned; PR #646 keeps revision 2's play-book and plan-part work\n"
                    "since: 2026-11-04T17:23Z\nwriter: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", "planned"),
            "584": ("holder: program-59cec502\nowner: counsel-0032b4c0; orchestrate-d688fecf\nwaiting-on: unit counsel-0032b4c0\n"
                    "next: counsel: message-route DMC and Guide citation; its Rule-3 sentence folds into #585\n"
                    "since: 2026-11-04T17:29Z\nwriter: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", "planned"),
            "585": ("holder: program-59cec502\nowner: counsel-0032b4c0; engineer-1537d8fb; orchestrate-d688fecf\nwaiting-on: unit "
                    "counsel-0032b4c0\nnext: counsel: clause map and the new Rule-3 after #641 and #646 land; engineer re-points code "
                    "references; absorbs #574 rev 2/3 and #584 Rule-3 sentences\nsince: 2026-11-04T17:29Z\n"
                    "writer: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", "planned"),
            "586": ("holder: program-59cec502\nowner: engineer-1537d8fb; counsel-0032b4c0; orchestrate-d688fecf\nwaiting-on: unit "
                    "engineer-1537d8fb\nnext: engineer: one agent-zone PR (E1 holder's post adds owner in one commit, E2 dwork batch "
                    "board/post lines validated up front + ring list, tests replaying both errors), files overlap #644/#649; counsel: "
                    "Rule-16 sentence in #585's window; orchestrate: verify, draft Done\nsince: 2026-11-04T17:54Z\n"
                    "writer: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", "planned"),
            "587": ("holder: program-59cec502\nowner: engineer-1537d8fb; counsel-0032b4c0; orchestrate-d688fecf\nwaiting-on: unit "
                    "engineer-1537d8fb\nnext: engineer after #586: PR2 machine (ORCH tables, board advance, X1-X4, X9), PR3 automaton "
                    "X5 combined evidence + X6 head watch + inbox trigger + sweep phase age, PR4 X7 Done skeleton, DoD replay report; "
                    "counsel: Rule-16 board phase/inbox event + play-book section in #585's window; orchestrate: verify, draft Done\n"
                    "since: 2026-11-04T17:54Z\nwriter: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", "planned"),
            "_cos": ("holder: program-59cec502\nqueue: plan-ready 0, done-ready 0\nseats: engineer-1537d8fb session_018L\n"
                     "since: 2026-11-02T16:01Z\npromised: row for running longest test groups first\n"
                     "writer: 59cec502-8c78-5e74-ae6a-66a4f0271c17\n", None)}

    def test_todays_unphased_entries_are_unchanged(self):
        for name, (text, state) in self.LIVE.items():
            if state:
                (self.rows / f"{name}.md").write_text(ROW.format(id=name, state=state))
            (self.board / f"{name}.md").write_text(text)
            self.assertEqual(bd.render(bd.parse(text)[0], bd.keys_for(name)), text, name)   # re-renders byte for byte
        rows = {r.id: r for r in dyadlib.read_rows(self.root)}
        states = {i: r.state for i, r in rows.items()}
        for name, (text, _) in self.LIVE.items():                                # pinned to today's lines (all []), not to itself
            self.assertEqual(bd.check_entry(name, text, states, rows), [], name)
            self.assertEqual(bd.check_entry(name, text, states), [], name)
        self.assertEqual(bd.check_package(self.root), [])


    def test_s3_an_owner_missing_from_the_cos_seat_table_warns(self):
        """#587 S3 replayed: `opened` routed orchestrate while the hand-written `_cos` table omitted it."""
        (self.board / "_cos.md").write_text(bd.render({"holder": HOME, "seats": f"{HOME} (home); {ENG}"}, bd.COS_FIELDS))
        got = self.msgs(phased(5, "building", {"unit": [ENG]}, owner=f"{ENG}; orchestrate-d688fecf"))
        self.assertEqual([m for m in got if "seat table" in m],
                         ["warning: board/5.md: orchestrate-d688fecf owns this entry and is missing from the `_cos` seat "
                          "table — `dyad board set _cos seats=…` adds it (#587 S3)"])
        (self.board / "_cos.md").write_text(bd.render({"holder": HOME, "seats": f"{HOME} (home); {ENG} s; orchestrate-d688fecf"}, bd.COS_FIELDS))
        self.assertEqual([m for m in self.msgs(phased(5, "building", {"unit": [ENG]}, owner=f"{ENG}; orchestrate-d688fecf"))
                          if "seat table" in m], [])
        (self.board / "_cos.md").write_text(bd.render({"holder": HOME}, bd.COS_FIELDS))           # no table: silent
        self.assertEqual([m for m in self.msgs(phased(5, "building", {"unit": [ENG]})) if "seat table" in m], [])


class PhasedQueueTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, True)
        d = self.root / INST / "d-work"
        for sub in ("rows", "plans", "board"):
            (d / sub).mkdir(parents=True)
        for rid in (5, 6, 7, 8):
            (d / "rows" / f"{rid}.md").write_text(ROW.format(id=rid, state="open").replace("2026-11-01 Y plan", "2026-11-01 Y open"))
            (d / "plans" / f"{rid}.md").write_text("# Plan\n")
        (d / "board" / "5.md").write_text(phased(5, "plan-ready", {"unit": [ENG]}))
        (d / "board" / "6.md").write_text(phased(6, "plan-asked", {"unit": [ENG]}, question="Y/N: proceed with #6 as planned?"))
        (d / "board" / "7.md").write_text(phased(7, "done-ready", {"unit": [ENG], "evidence": [EV]}))

    def test_the_phase_counts_and_the_old_clause_keeps_the_unphased(self):
        self.assertEqual(bd.derived_queue(self.root), {"plan-ready": [5, 8], "done-ready": [7]})


class AdvanceTests(unittest.TestCase):
    """`board advance` over a scratch install (the worktree's runner records the answers), a bare origin, a seat whose
    pre-push hook only logs, and a racer clone."""
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST, "DYAD_SESSION": HOME, "CLAUDE_CODE_SESSION_ID": "h-home"})
        e.start(); self.addCleanup(e.stop)
        seed = SCRATCH.copy(False)
        git(seed, "branch", "-M", "main")
        d = seed / INST / "d-work"
        for sub in ("rows", "provenance", "plans"):
            (d / sub).mkdir(parents=True, exist_ok=True)
        for rid, title, state, disposed in ((5, "five", "open", ""), (6, "six", "open", ""), (7, "seven", "planned", "2026-11-01 Y plan")):
            (d / "rows" / f"{rid}.md").write_text(f"id: {rid}\ntitle: {title}\nopened: 2026-11-01\nstate: {state}\ndisposed: {disposed}\nrefs: \n")
            (d / "provenance" / f"{rid}.md").write_text(f"# Provenance #{rid}\n\n## 1 prompt 2026-11-01\n\n```\nopen {title}\n```\n"
                                                        + ("\n## 2 disposition 2026-11-01 Y plan\n\n```\nY\n```\n" if disposed else ""))
        (d / "plans" / "5.md").write_text("# Plan #5\n\nparts: engineer: the verb\n")
        (d / "plans" / "6.md").write_text("# Plan #6\n")
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "ledger: rows")
        top = SCRATCH.mkdtemp()
        self.top, self.origin, self.seat, self.racer, hooks = top, top / "origin.git", top / "seat", top / "racer", top / "hooks"
        git(top, "clone", "-q", "--bare", str(seed), str(self.origin))
        self.log = top / "hook.log"
        hooks.mkdir(); (hooks / "pre-push").write_text(f"#!/bin/sh\n{{ cat; echo --; }} >> '{self.log}'\nexit 0\n")
        (hooks / "pre-push").chmod(0o755)
        for c in (self.seat, self.racer):
            git(top, "clone", "-q", str(self.origin), str(c))
            for k, v in (("user.email", "t@example.com"), ("user.name", "t"), ("core.hooksPath", str(hooks))):
                git(c, "config", k, v)
        self.said = top / "said.txt"; self.said.write_text("Y, as planned\n")
        self.wt = self.seat / ".git" / "dyad-land"

    # ---- helpers
    def seed_board(self, files: dict):
        """Entries (and any other store file) put on origin/main by the racer, past the hook (setup, not an advance)."""
        git(self.racer, "fetch", "-q", "origin"); git(self.racer, "checkout", "-q", "--detach", "origin/main")
        for rel, text in files.items():
            p = self.racer / INST / "d-work" / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
        git(self.racer, "add", "-A"); git(self.racer, *livetest.IDENTITY, "commit", "-qm", "ledger: setup")
        git(self.racer, "push", "-q", "--no-verify", "origin", "HEAD:main")
        git(self.seat, "pull", "-q", "--ff-only", "origin", "main")

    def adv(self, *argv, session=HOME, repo=None):
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, {"DYAD_SESSION": session, "CLAUDE_CODE_SESSION_ID": f"h-{session}"}), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = bd.cli(["advance", *argv], repo or self.seat)
        return rc, out.getvalue(), err.getvalue()

    def main(self):
        return git(self.origin, "rev-parse", "main")

    def show(self, rel, rev="main"):
        r = subprocess.run(["git", "show", f"{rev}:{INST}/d-work/{rel}"], cwd=self.origin, capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None

    def entry(self, rid):
        t = self.show(f"board/{rid}.md")
        return None if t is None else bd.parse(t)[0]

    def box(self, seat):
        r = subprocess.run(["git", "ls-tree", "--name-only", f"main:{INST}/d-work/inbox/{seat}"], cwd=self.origin, capture_output=True, text=True)
        return [bd.parse(self.show(f"inbox/{seat}/{n}"))[0] for n in r.stdout.split() if n.endswith(".md")]

    def files(self, rev):
        return sorted(git(self.origin, "show", "--name-only", "--format=", rev).split())

    def commits(self, before):
        return int(git(self.origin, "rev-list", "--count", f"{before}..main"))

    def guards_pass(self, before, head):
        git(self.seat, "fetch", "-q", "origin"); git(self.seat, "checkout", "-q", "main"); git(self.seat, "merge", "-q", "--ff-only", "origin/main")
        rg, pv = dyadlib.load_guard("agent", "rows"), dyadlib.load_guard("agent", "provenance")
        with unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}):
            fails = [m for m in rg.check_transaction(self.seat, before, head) + pv.check_transaction(self.seat, before, head)
                     if m.startswith("FAIL")]
        self.assertEqual(fails, [])

    def trace(self, rid):
        t = self.seat / INST / "d-work" / "traces" / f"{rid}.md"
        t.parent.mkdir(parents=True, exist_ok=True); t.write_text(f"# Trace #{rid}\n")

    def done_asked(self, rid, prs, question, owner=f"{ENG}; {COU}"):
        return phased(rid, "done-asked", {"unit": [ENG], "pr": prs, "evidence": [EV]} if prs else {"unit": [ENG], "evidence": [EV]},
                      owner=owner, question=question)

    # ---- transitions
    def test_opened_lands_one_commit_with_its_owner_and_relay(self):
        before = self.main()
        rc, out, err = self.adv("5", "opened", "--expect", "none", f"unit={ENG}")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.commits(before), 1)
        f = self.entry(5)
        self.assertEqual((bd.phase_name(f), f["waiting-on"], f["holder"], bd.owners(f)), ("planning", f"unit {ENG}", HOME, [ENG]))
        (msg,) = self.box(ENG)
        self.assertEqual((msg["kind"], msg["body"]), ("relay", "row #5 planning: write plans/5.md; advance plan-landed when it is on main"))
        self.assertIn(f"ring: {ENG}", out)
        self.assertTrue(git(self.origin, "log", "-1", "--format=%s", "main").startswith("ledger: board advance #5 opened (none -> planning)"))
        git(self.seat, "fetch", "-q", "origin")
        self.assertTrue(dyadlib.ledger_only(self.seat, before, self.main()))
        self.assertEqual(bd.check_entry("5", self.show("board/5.md"), {5: "open"}), [])

    def test_s8_opened_adds_a_unit_and_its_relays_need_no_hand_edit(self):
        self.seed_board({"board/6.md": f"holder: {HOME}\nowner: {COU}\nwaiting-on: operator\nnext: decide\nwriter: h1\n"})
        rc, out, err = self.adv("6", "opened", "--expect", "none", f"unit={ENG}")
        self.assertEqual(rc, 0, out + err)
        f = self.entry(6)
        self.assertEqual((bd.owners(f), f["note"]), ([COU, ENG], "decide"))      # adoption: the old next is the note
        rc, out, err = self.adv("6", "plan-landed", "--expect", "planning", session=ENG)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(bd.phase_name(self.entry(6)), "plan-ready")
        self.assertEqual([m["kind"] for m in self.box(HOME)], ["report"])

    def test_plan_landed_without_the_plan_and_two_refusals_land_nothing(self):
        self.seed_board({"board/7.md": phased(7, "planning", {"unit": [ENG]}, owner=ENG)})
        before = self.main()
        rc, _, err = self.adv("7", "plan-landed", "--expect", "planning", session=ENG)
        self.assertEqual(rc, 1); self.assertIn("plans/7.md is not on origin/main", err)
        rc, _, err = self.adv("7", "plan-landed", "--expect", "building", session=ENG)
        self.assertEqual(rc, 1); self.assertIn("not an event from building", err)
        rc, _, err = self.adv("7", "hold", "--expect", "plan-ready", "note=x", "on=operator")
        self.assertEqual(rc, 1); self.assertIn("phase moved: #7 is planning on origin/main, expected plan-ready", err)
        rc, _, err = self.adv("7", "plan-landed", "--expect", "planning", session="stranger-dddddddd")
        self.assertEqual(rc, 1); self.assertIn("a unit event is an owner's or the holder's", err)
        self.assertEqual(self.main(), before)

    def test_asked_over_two_ids_stores_one_batch_question(self):
        self.seed_board({"board/5.md": phased(5, "plan-ready", {"unit": [ENG]}), "board/6.md": phased(6, "plan-ready", {"unit": [ENG]})})
        rc, out, err = self.adv("5", "6", "asked", "--expect", "plan-ready")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(out.splitlines()[0], "Y/N: proceed with #5, #6 as planned?")
        self.assertEqual({self.entry(5)["question"], self.entry(6)["question"]}, {"Y/N: proceed with #5, #6 as planned?"})
        self.assertEqual(self.entry(5)["waiting-on"], "operator")
        self.assertNotIn("ring:", out)

    def test_board_phases_prints_every_event(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(bd.cli(["phases"], self.seat), 0)
        for (f, e), (ts, actor, _) in dyadlib.ORCH_EVENTS.items():
            self.assertIn(f"{f or 'none'} | {e} | {' or '.join(ts)} | {actor} |", out.getvalue())

    # ---- the DoD replays of PR2
    def test_replay_x4_plan_y_is_one_commit(self):
        """S7/S2/S1: the row, its words, the board and the relay in one commit; the automaton has nothing left to do."""
        self.seed_board({"board/5.md": phased(5, "plan-asked", {"unit": [ENG]}, owner=ENG, question="Y/N: proceed with #5 as planned?")})
        before = self.main()
        rc, out, err = self.adv("5", "answered-Y", "--expect", "plan-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        head = self.main()
        self.assertEqual(self.commits(before), 1)
        self.assertIn("state: planned", self.show("rows/5.md")); self.assertRegex(self.show("rows/5.md"), r"disposed: \d{4}-\d{2}-\d{2} Y plan\n")
        self.assertIn("```\nY, as planned\n```", self.show("provenance/5.md"))
        f = self.entry(5)
        self.assertEqual((bd.phase_name(f), f["waiting-on"]), ("building", f"unit {ENG}")); self.assertNotIn("question", f)
        (msg,) = self.box(ENG)
        self.assertEqual((msg["kind"], msg["body"]), ("notice", "row #5 planned; read plans/5.md; yours: the verb"))
        self.assertNotIn("ring:", out)                                           # K2's notice, as before #587
        self.guards_pass(before, head)
        am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
        _, acts = am.plan(self.seat)
        self.assertEqual([a for a in acts if a[1] == 5], [])                     # no K1 flip, no K2 notice, no catch-up
        rc, out, err = self.adv("5", "answered-Y", "--expect", "plan-asked", "--said-file", str(self.said))   # ambiguous re-run
        self.assertEqual(rc, 1); self.assertIn("already landed", err)
        self.assertEqual(self.main(), head)

    def test_replay_x4_done_y_names_the_heads_and_rides_its_trace(self):
        """S7/S9: refused without the trace; with it, one commit holds the trace, the entry, the words, the landing board
        and the notices."""
        q = "Y/N: Done with #7 seven (merges PR #650, #651)?"
        self.seed_board({"board/7.md": self.done_asked(7, [f"650 at {H1}", f"651 at {H2}"], q)})
        before = self.main()
        rc, _, err = self.adv("7", "answered-Y", "--expect", "done-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 1); self.assertIn("run dyad dwork trace 7 --out first", err)
        self.assertEqual(self.main(), before); self.assertEqual(self.commits(before), 0)   # refused in the build, after the fetch
        self.trace(7)
        rc, out, err = self.adv("7", "answered-Y", "--expect", "done-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        head = self.main()
        self.assertEqual(self.commits(before), 1)
        self.assertIn(f"{INST}/d-work/traces/7.md", self.files(head))
        row = self.show("rows/7.md")
        self.assertIn("state: planned", row)
        self.assertRegex(row, rf"Y done \(merges PR #650 at {H1}, PR #651 at {H2}\)\n")
        f = self.entry(7)
        self.assertEqual((bd.phase_name(f), f["waiting-on"]), ("landing", "external merge PR #650, PR #651"))
        self.assertEqual([m["kind"] for m in self.box(ENG) + self.box(COU)], ["notice", "notice"])
        self.assertNotIn("ring:", out)                                           # notices are not rung
        self.guards_pass(before, head)

    def test_replay_binding_refuses_another_id_set(self):
        q = "Y/N: proceed with #5, #6 as planned?"
        self.seed_board({"board/5.md": phased(5, "plan-asked", {"unit": [ENG]}, question=q),
                         "board/6.md": phased(6, "plan-asked", {"unit": [ENG]}, question=q)})
        before = self.main()
        rc, _, err = self.adv("5", "answered-Y", "--expect", "plan-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 1); self.assertIn("the Y binds to the question asked: Y/N: proceed with #5, #6 as planned?", err)
        self.assertEqual(self.main(), before)

    def test_replay_x4_batch_done_writes_one_y_to_both(self):
        q = "Y/N: Done with #5 five, #6 six (merges PR #650, #651)?"
        self.seed_board({"board/5.md": self.done_asked(5, [f"650 at {H1}"], q), "board/6.md": self.done_asked(6, [f"651 at {H2}"], q)})
        self.trace(5); self.trace(6)
        before = self.main()
        rc, out, err = self.adv("5", "6", "answered-Y", "--expect", "done-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.commits(before), 1)
        for rid in (5, 6):
            self.assertRegex(self.show(f"rows/{rid}.md"), rf"Y done \(batch #5,#6, merges PR #650 at {H1}, PR #651 at {H2}\)\n")
            self.assertTrue(self.show(f"provenance/{rid}.md").rstrip().endswith("```\nY, as planned\n```"))
            self.assertEqual(bd.phase_name(self.entry(rid)), "landing")
        self.guards_pass(before, self.main())

    def test_replay_no_pr_done_closes_the_row_and_drops_the_entry(self):
        self.seed_board({"board/7.md": self.done_asked(7, [], "Y/N: Done with #7 seven?")})
        self.trace(7)
        before = self.main()
        rc, out, err = self.adv("7", "answered-Y", "--expect", "done-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.commits(before), 1)
        self.assertIn("state: done", self.show("rows/7.md")); self.assertIsNone(self.entry(7))
        self.assertEqual([m["body"] for m in self.box(ENG)], ["row #7 closed: the Done answer is recorded and the row is done"])
        self.guards_pass(before, self.main())

    def test_replay_answered_n(self):
        self.seed_board({"board/5.md": phased(5, "plan-asked", {"unit": [ENG]}, owner=ENG, question="Y/N: proceed with #5 as planned?"),
                         "board/7.md": self.done_asked(7, [f"650 at {H1}"], "Y/N: Done with #7 seven (merges PR #650)?", owner=ENG)})
        before = self.main()
        rc, out, err = self.adv("5", "answered-N", "--expect", "plan-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        self.assertRegex(self.show("rows/5.md"), r"state: open\ndisposed: \d{4}-\d{2}-\d{2} N plan\n")
        self.assertEqual(bd.phase_name(self.entry(5)), "planning")
        rc, out, err = self.adv("7", "answered-N", "--expect", "done-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        self.assertRegex(self.show("rows/7.md"), r"Y plan; \d{4}-\d{2}-\d{2} N done\n")
        f = self.entry(7)
        self.assertEqual(bd.phase_name(f), "building"); self.assertNotIn("evidence", bd.phase_of(f["phase"])[1])
        self.assertEqual([m["body"] for m in self.box(ENG)][-1], "row #7 building: the Done was refused; read provenance/7.md")
        self.guards_pass(before, self.main())

    def test_a_done_answer_after_a_plan_y_today_is_a_moved_phase_not_already_landed(self):
        """answered_already reads the kind: a plan-Y recorded today with the same words never passes for the Done."""
        self.seed_board({"board/5.md": phased(5, "plan-asked", {"unit": [ENG]}, owner=ENG, question="Y/N: proceed with #5 as planned?")})
        rc, out, err = self.adv("5", "answered-Y", "--expect", "plan-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        self.seed_board({"board/5.md": phased(5, "done-ready", {"unit": [ENG], "evidence": [EV]}, owner=ENG)})
        before = self.main()
        rc, _, err = self.adv("5", "answered-Y", "--expect", "done-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 1)
        self.assertIn("phase moved: #5 is done-ready on origin/main, expected done-asked", err)
        self.assertNotIn("already landed", err)
        self.assertEqual(self.main(), before)

    def test_replay_a_mixed_done_batch_keeps_the_no_pr_row_on_the_board_until_the_merge(self):
        q = "Y/N: Done with #5 five, #6 six (merges PR #650)?"
        self.seed_board({"board/5.md": self.done_asked(5, [f"650 at {H1}"], q), "board/6.md": self.done_asked(6, [], q)})
        self.trace(5); self.trace(6)
        before = self.main()
        rc, out, err = self.adv("5", "6", "answered-Y", "--expect", "done-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.commits(before), 1)
        for rid in (5, 6):
            self.assertIn("state: open", self.show(f"rows/{rid}.md"))           # the state follows the merge
            self.assertRegex(self.show(f"rows/{rid}.md"), rf"Y done \(batch #5,#6, merges PR #650 at {H1}\)\n")
            f = self.entry(rid)
            self.assertEqual((bd.phase_name(f), f["waiting-on"]), ("landing", "external merge PR #650"), rid)
        bodies = [m["body"] for m in self.box(ENG)]
        self.assertFalse([b for b in bodies if "closed" in b], bodies)
        self.assertIn("row #6 landing: the Done answer is recorded on main; the automaton merges PR #650 at " + H1, bodies)
        self.guards_pass(before, self.main())

    def test_replay_a_no_pr_done_closes_its_accreted_rows_under_the_mandate(self):
        self.seed_board({"rows/8.md": "id: 8\ntitle: eight\nopened: 2026-11-01\nstate: open\ndisposed: 2026-11-01 Y plan (mandate #7)\n"
                                      "refs: parent #7\n",
                         "provenance/8.md": "# Provenance #8\n\n## 1 disposition 2026-11-01 Y plan (mandate #7, 2026-11-01)\n\n```\nY\n```\n",
                         "board/7.md": self.done_asked(7, [], "Y/N: Done with #7 seven (accreted #8)?")})
        self.trace(7)
        before = self.main()
        rc, out, err = self.adv("7", "answered-Y", "--expect", "done-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.commits(before), 1)
        self.assertRegex(self.show("rows/7.md"), r"state: done\ndisposed: .*Y done \(accreted #8\)\n")
        self.assertIn("state: done", self.show("rows/8.md"))
        self.assertIn("mandate #7", self.show("provenance/8.md").split("## 2 ")[1])
        self.guards_pass(before, self.main())

    def test_an_adoption_takes_its_unit_from_unit(self):
        self.seed_board({"board/7.md": f"holder: {HOME}\nowner: {COU}\nwaiting-on: operator\nnext: decide\nwriter: h1\n"})
        rc, out, err = self.adv("7", "pr-up", "--expect", "none", "pr=5", f"head={H1}", f"unit={ENG}")
        self.assertEqual(rc, 0, out + err)
        f = self.entry(7)
        self.assertEqual(bd.first(bd.phase_of(f["phase"])[1], "unit"), ENG)
        self.assertIn(ENG, bd.owners(f))
        rc, out, err = self.adv("7", "evidence-failed", "--expect", "verifying", "note=the guard line")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.entry(7)["waiting-on"], f"unit {ENG}")

    def test_a_try_that_runs_no_batch_rings_nobody(self):
        self.seed_board({"board/5.md": phased(5, "plan-ready", {"unit": [ENG]})})
        run, ran = dyadlib.runner_module(), ["stale-seat"]
        build = bd.advance_builder([5], "asked", {}, "plan-ready", None, INST, self.seat, run.DWORK_VALUE_FLAGS,
                                   run.dwork_args, run.words, HOME, ran=ran)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(bd.land_mod().land(self.seat, INST, None, build, "board advance"), 0)
        self.assertEqual(ran, [])

    def race(self, *argv, session):
        """land's push, patched: before the seat's first push, the racer clone fires `argv` (and lands it)."""
        L = bd.land_mod()
        real, fired = L.push, []
        def push(wt, mirror):
            if not fired:
                fired.append(None)                               # the racer's own push passes straight through
                fired[0] = self.adv(*argv, session=session, repo=self.racer)
            return real(wt, mirror)
        return unittest.mock.patch.object(L, "push", push), fired

    def test_replay_x9_a_moved_phase_is_refused_and_nothing_is_pushed(self):
        self.seed_board({"board/5.md": phased(5, "plan-ready", {"unit": [ENG]})})
        patch, fired = self.race("5", "hold", "--expect", "plan-ready", "note=wait for the release", "on=operator", session=HOME)
        with patch:
            rc, out, err = self.adv("5", "asked", "--expect", "plan-ready")
        self.assertEqual(fired[0][0], 0, fired)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("phase moved: #5 is held on origin/main, expected plan-ready", err)
        self.assertEqual(bd.phase_name(self.entry(5)), "held")
        self.assertTrue(git(self.origin, "log", "-1", "--format=%s", "main").startswith("ledger: board advance #5 hold"))

    def test_replay_x9_concurrent_pr_ups_recompute_never_replay(self):
        self.seed_board({"board/5.md": phased(5, "verifying", {"unit": [ENG], "pr": [f"650 at {H1}"]})})
        before = self.main()
        patch, fired = self.race("5", "pr-up", "--expect", "verifying", "pr=651", f"head={H2}", session=ENG)
        with patch:
            rc, out, err = self.adv("5", "pr-up", "--expect", "verifying", "pr=652", f"head={H3}", session=COU)
        self.assertEqual(fired[0][0], 0, fired)
        self.assertEqual(rc, 0, out + err); self.assertIn("main moved", err)
        self.assertEqual(self.commits(before), 2)
        self.assertEqual(bd.pr_list(bd.phase_of(self.entry(5)["phase"])[1]), [(650, H1), (651, H2), (652, H3)])
        reports = [m["body"] for m in self.box(HOME)]
        self.assertEqual(sorted(reports), sorted([f"row #5 verifying: PR #651 at {H2} is up from {ENG}; verify PR #650 at {H1}, PR #651 at {H2}",
                                                  f"row #5 verifying: PR #652 at {H3} is up from {COU}; verify PR #650 at {H1}, PR #651 at {H2}, PR #652 at {H3}"]))

    def test_replay_s7_a_refused_state_line_lands_neither_board_nor_relays(self):
        """Atomicity: the row cannot go planned (blocked on origin), so `dwork state` refuses it in the worktree."""
        self.seed_board({"rows/5.md": "id: 5\ntitle: five\nopened: 2026-11-01\nstate: blocked\ndisposed: \nrefs: 6\n",
                         "board/5.md": phased(5, "plan-asked", {"unit": [ENG]}, owner=ENG, question="Y/N: proceed with #5 as planned?")})
        before = self.main()
        rc, out, err = self.adv("5", "answered-Y", "--expect", "plan-asked", "--said-file", str(self.said))
        self.assertEqual(rc, 1, out + err); self.assertIn("refused it in the worktree", err)
        self.assertEqual(self.main(), before); self.assertEqual(self.box(ENG), [])
        L = bd.land_mod()
        L.prepare(self.seat, self.wt, before)
        self.assertEqual(L.written(self.wt), [])                                  # the next land starts clean

    def test_replay_x2_a_disposition_shaped_note_is_refused_before_any_write(self):
        self.seed_board({"board/5.md": phased(5, "verifying", {"unit": [ENG], "pr": [f"650 at {H1}"]})})
        before = self.main()
        rc, _, err = self.adv("5", "evidence-failed", "--expect", "verifying", "note=Y/N: Done with #5?")
        self.assertEqual(rc, 1); self.assertIn("disposition-shaped", err)
        self.assertEqual(self.main(), before)

    def test_replay_s4_a_co_owners_pr_up_reports_to_the_holder_cc_the_owners(self):
        self.seed_board({"board/5.md": phased(5, "building", {"unit": [ENG]}, owner=f"{ENG}; {COU}; audit-eeeeeeee")})
        before = self.main()
        rc, out, err = self.adv("5", "pr-up", "--expect", "building", "pr=650", f"head={H1}", session=COU)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.commits(before), 1)
        f = self.entry(5)
        self.assertEqual((bd.phase_name(f), f["waiting-on"]), ("verifying", f"unit {HOME}"))
        self.assertEqual([m["kind"] for m in self.box(HOME)], ["report"])
        self.assertEqual([len(self.box(s)) for s in (ENG, "audit-eeeeeeee", COU)], [1, 1, 0])
        self.assertIn(f"ring: {HOME}, {ENG}, audit-eeeeeeee", out)

    def test_set_refuses_derived_keys_on_a_phased_entry(self):
        self.seed_board({"board/5.md": phased(5, "building", {"unit": [ENG]})})
        for kv in ("waiting-on=operator", "next=x", "since=2026-11-04", "phase=planning", "question=Y/N: go?"):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = bd.cli(["set", "5", kv], self.seat)
            self.assertEqual(rc, 1, kv); self.assertIn("written by `dyad board advance`", err.getvalue(), kv)
        for argv in (["set", "5", "note=a free note"], ["set", "5", f"owner={ENG}; {COU}; audit-eeeeeeee"],
                     ["set", "5", "holder=program-ffffffff"], ["set", "5", "--drop"]):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(bd.cli(argv, self.seat), 0, (argv, err.getvalue()))
        out, err = io.StringIO(), io.StringIO()
        self.seed_board({"board/5.md": phased(5, "plan-ready", {"unit": [ENG]})})
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(bd.cli(["set", "5", "holder=program-ffffffff"], self.seat), 0, err.getvalue())
            self.assertEqual(bd.cli(["set", "5", f"owner={COU}"], self.seat), 1)
        self.assertEqual(self.entry(5)["waiting-on"], "unit program-ffffffff")    # re-derived, never typed
        self.assertEqual(bd.check_entry("5", self.show("board/5.md"), {5: "open"}), [])
        self.assertIn("`owner` keeps it", err.getvalue())
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(bd.cli(["set", "6", "phase=planning"], self.seat), 1)
        self.assertIn("a phase is born only by `dyad board advance`", err.getvalue())

    def test_the_automaton_catches_up_a_y_recorded_by_hand(self):
        """A plan-Y recorded with plain `dwork state`: the automaton proposes the catch-up and its run moves the board to
        building with the relay, writing no ledger line; a Done whose entry names another PR set proposes nothing."""
        am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
        self.seed_board({"board/7.md": phased(7, "plan-asked", {"unit": [ENG]}, owner=ENG, question="Y/N: proceed with #7 as planned?"),
                         "rows/6.md": "id: 6\ntitle: six\nopened: 2026-11-01\nstate: planned\n"
                                      f"disposed: 2026-11-01 Y plan; 2026-11-04 Y done (merges PR #650 at {H1})\nrefs: \n",
                         "board/6.md": self.done_asked(6, [f"651 at {H2}"], "Y/N: Done with #6 six (merges PR #651)?")})
        self.seed_board({"rows/7.md": "id: 7\ntitle: seven\nopened: 2026-11-01\nstate: planned\n"   # the answer, recorded by hand
                                      "disposed: 2026-11-01 Y plan; 2026-11-05 Y plan\nrefs: \n"})     # after the asking (S11)
        with unittest.mock.patch.object(am, "corroborate", lambda *a: (True, [])):
            _, acts = am.plan(self.seat)
            self.assertIn(("advance", 7, "answered-Y", "plan-asked"), acts)
            self.assertFalse([a for a in acts if a[0] in ("advance", "board", "notice") and a[1] == 6], acts)
            self.assertFalse([a for a in acts if a[0] in ("board", "notice") and a[1] == 7], acts)
            self.assertIn("catch up #7 answered-Y (recorded on the ledger)", [am.describe(a) for a in acts])
            before = self.main()
            rows_before = self.show("rows/7.md")
            line = am.catch_up(self.seat, 7, "plan-asked")
        self.assertIn("caught up", line)
        f = self.entry(7)
        self.assertEqual((bd.phase_name(f), f["waiting-on"]), ("building", f"unit {ENG}"))
        self.assertEqual(self.show("rows/7.md"), rows_before)                     # no ledger line
        self.assertEqual([(m["from"], m["body"]) for m in self.box(ENG)], [("automaton", "row #7 planned; read plans/7.md")])
        self.assertEqual(self.commits(before), 1)


QSTART = re.compile(r"(?m)^Y/N:")


class DraftTests(unittest.TestCase):
    """`dyad board draft <id>` (#587 X7) over a scratch world: a bare origin and a clone whose row #700 is phased at
    done-ready with two PRs in two zones (agent and infra), two rows accreted under its mandate (one terminal), a plan
    with a DoD section, and its evidence block stored in the clone's evidence store. Each section is asserted, the
    question equals what `asked` would store, a row not at done-ready is refused, `--out` inside the work tree is
    refused, and the clone's `git status` is unchanged by every run."""
    DOD = "## Definition of done\nA report read in one pass:\n1. the `table`.\n```\nnot a fence of ours\n```\n"

    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        top = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, top, True)
        seed, self.origin, self.repo = top / "seed", top / "origin.git", top / "repo"
        seed.mkdir(); git(seed, "init", "-q", "-b", "main")
        d = seed / INST / "d-work"
        for sub in ("rows", "plans", "board"):
            (d / sub).mkdir(parents=True)
        rows = {700: ("the machine", "planned", "2026-11-01 Y plan", "", ""),
                701: ("child one", "open", "2026-11-01 Y plan (mandate #700)", "parent #700", "mode: implicit\n"),
                702: ("child | two", "done", "2026-11-01 Y plan (mandate #700); 2026-11-02 Y done (mandate #700, 2026-11-02)", "parent #700", "mode: implicit\n"),
                703: ("unrelated", "open", "2026-11-01 Y plan (mandate #9)", "parent #700", ""),
                704: ("not ready", "planned", "2026-11-01 Y plan", "", "")}
        for rid, (title, state, disposed, refs, extra) in rows.items():
            (d / "rows" / f"{rid}.md").write_text(f"id: {rid}\ntitle: {title}\nopened: 2026-11-01\nstate: {state}\n"
                                                  f"disposed: {disposed}\nrefs: {refs}\n{extra}")
        (d / "plans" / "700.md").write_text("# Plan #700\n\n## Intent as read\nx\n\n" + self.DOD + "\n## Files touched\ny\n")
        (seed / "preferences-corpus").mkdir()
        (seed / "preferences-corpus" / "PREFERENCES.md").write_text(
            "| key | value | allowed | read by |\n|---|---|---|---|\n| merge-disposition | with-done | `separate` \\| `with-done` | r |\n"
            "| dwork-trace | always | `always` \\| `on-demand` | r |\n")
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "ledger: rows")
        heads = []
        for branch, paths in (("pr-a", ("agent-corpus/notes/a.md",)), ("pr-b", (".github/workflows/b.yml",)),
                              ("pr-c", ("agent-corpus/notes/a b.md", "agent-corpus/notes/é.md"))):
            git(seed, "checkout", "-q", "-b", branch, "main")
            for path in paths:
                (seed / path).parent.mkdir(parents=True, exist_ok=True); (seed / path).write_text("x\n")
            git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", branch)
            heads.append(git(seed, "rev-parse", "HEAD"))
        git(seed, "checkout", "-q", "main")
        self.ha, self.hb, self.hc = heads
        board = d / "board"
        (board / "700.md").write_text(phased(700, "done-ready", {"unit": [ENG], "pr": [f"651 at {self.ha[:12]}", f"652 at {self.hb}"], "evidence": [EV]}))
        (board / "704.md").write_text(phased(704, "verifying", {"unit": [ENG], "pr": [f"653 at {self.ha[:12]}"]}))
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "ledger: board")
        git(top, "clone", "-q", "--bare", str(seed), str(self.origin))
        git(top, "clone", "-q", str(self.origin), str(self.repo))
        git(self.repo, "fetch", "-q", str(seed), "pr-a", "pr-b", "pr-c")   # the PR heads are objects of the clone, as a fetched refs/pull/<n>/head is
        self.pk = dyadlib.runner_module()

    def store_block(self):
        body = [f"head={self.ha}", "tree=" + "1" * 40, "dirty=no", "code=x", "ok   [rule-12] tests pass", "FAIL [guards] agent/x: broken",
                "warn [guards] agent/plans 9.md: never mentions `intent as read` (dyadlib.PLAN_PARTS)"]
        block = body + [self.pk.EVIDENCE_SHA + self.pk.evidence_sha256(body)]
        sha = self.pk.evidence_sha256(body)
        d = Path(git(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / self.pk.EVIDENCE_STORE
        d.mkdir(parents=True, exist_ok=True); (d / f"{sha}.txt").write_text("\n".join(block) + "\n")
        return sha

    def status(self):
        return git(self.repo, "status", "--porcelain", "--untracked-files=all")

    def draft(self, *argv, repo=None):
        out, err = io.StringIO(), io.StringIO()
        before = self.status()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = bd.cli(["draft", *argv], repo or self.repo)
        self.assertEqual(self.status(), before)                              # nothing in the repo changed
        self.assertEqual(self.status(), "")
        return rc, out.getvalue(), err.getvalue()

    def section(self, text, heading):
        parts = text.split("\n## ")
        return next(p for p in parts if p.startswith(heading))

    def test_mandated_includes_terminal_and_accreted_of_does_not(self):
        rows = {r.id: r for r in dyadlib.read_rows(self.repo)}
        self.assertEqual(bd.mandated(700, rows), [701, 702])
        self.assertEqual(bd.accreted_of(700, rows), [701])

    def test_dod_sections_and_fenced(self):
        self.assertEqual(bd.dod_sections("# P\n## Intent\na\n" + self.DOD + "## Next\nb\n## Definition of done, revised\nc\n"),
                         [self.DOD.rstrip("\n"), "## Definition of done, revised\nc"])
        self.assertEqual(bd.dod_sections("# P\n## Intent\na\n"), [])
        f = bd.fenced("a\n```\nb")
        self.assertEqual((f[0], f[-1], f[1:-1]), ("````", "````", [bd.QUOTE + "a", bd.QUOTE + "```", bd.QUOTE + "b"]))

    def test_the_skeleton_of_a_done_ready_row(self):
        sha = self.store_block()
        bd_entry = self.repo / INST / "d-work" / "board" / "700.md"
        bd_entry.write_text(bd_entry.read_text().replace(EV, sha))
        git(self.repo, *livetest.IDENTITY, "commit", "-qam", "ledger: evidence")
        rc, out, err = self.draft("700")
        self.assertEqual((rc, err), (0, ""), err)
        self.assertTrue(out.startswith("# Done #700 the machine: skeleton\n"), out)
        quoted = "\n".join(bd.QUOTE + l for l in self.DOD.rstrip("\n").split("\n"))
        self.assertIn("## Definition of done (quoted from agent-corpus/d-work/plans/700.md)\n\n````\n" + quoted
                      + "\n````\n\n## PRs", out)                                        # verbatim behind the prefix, its own fence kept
        prs = self.section(out, "PRs")
        self.assertIn(f"| #651 | agent | {self.ha[:12]} | 1 |", prs)
        self.assertIn(f"| #652 | infra | {self.hb} | 1 |", prs)
        ev = self.section(out, "Evidence")
        self.assertIn(f"evidence-sha256 `{sha}`, recorded on the phase over PR #651 at {self.ha[:12]}, PR #652 at {self.hb}", ev)
        self.assertIn("counts: ok=1 warn=1 skip=0 fail=1", ev)
        self.assertIn("FAIL [guards] agent/x: broken", ev)
        self.assertIn("not computed by board draft", ev)                                # never computes a baseline
        acc = self.section(out, "Accreted rows")
        self.assertIn("| #701 | open | implicit | 1 | child one |", acc)
        self.assertIn("| #702 (terminal: not in the question) | done | implicit | 2 | child \\| two |", acc)
        self.assertNotIn("#703", acc)                                                   # another mandate's row
        self.assertIn("`agent-corpus/d-work/traces/700.md`: absent (dwork-trace: always; write it with `dyad dwork trace 700 --out`)",
                      self.section(out, "Trace"))
        for head, _ in bd.ORCHESTRATE_SECTIONS:
            self.assertIn(bd.ORCHESTRATE, self.section(out, f"{head} (orchestrate)"))
        last = out.rstrip("\n").splitlines()[-1]
        self.assertEqual(last, "Y/N: Done with #700 the machine (accreted #701, merges PR #651, #652)?")
        rows = {r.id: r for r in dyadlib.read_rows(self.repo)}
        entry = bd.parse(bd_entry.read_text())[0]
        self.assertEqual(last, bd.question("done", [700], {700: entry}, rows, "with-done"))   # what `asked` stores
        self.assertEqual(QSTART.findall(out), ["Y/N:"])

    def test_an_unstored_block_and_a_present_trace(self):
        t = self.repo / INST / "d-work" / "traces" / "700.md"
        t.parent.mkdir(parents=True); t.write_text("# Trace #700\n")
        git(self.repo, "add", "-A"); git(self.repo, *livetest.IDENTITY, "commit", "-qm", "ledger: trace")
        rc, out, _ = self.draft("700")
        self.assertEqual(rc, 0)
        self.assertIn(f"block not stored here; run `dyad check --evidence --show {EV}`", self.section(out, "Evidence"))
        self.assertIn("`agent-corpus/d-work/traces/700.md`: present", self.section(out, "Trace"))

    def test_a_head_not_in_the_clone(self):
        bd_entry = self.repo / INST / "d-work" / "board" / "700.md"
        bd_entry.write_text(bd_entry.read_text().replace(self.hb, "f" * 40))
        git(self.repo, *livetest.IDENTITY, "commit", "-qam", "ledger: moved")
        rc, out, _ = self.draft("700")
        self.assertIn(f"| #652 | ? (head not in this clone: fetch refs/pull/652/head) | {'f' * 40} | ? |", out)

    def test_refusals(self):
        for rid, says in (("704", "#704 is at verifying"), ("703", "#703 is at no board entry"), ("999", "no board entry")):
            rc, out, err = self.draft(rid)
            self.assertEqual((rc, out), (1, ""), rid)
            self.assertEqual(len(err.strip().splitlines()), 1, err)
            self.assertIn(says, err)
        rc, _, err = self.draft("700", "--out", str(self.repo / "draft.md"))
        self.assertEqual(rc, 1); self.assertIn("a worktree or the git dir of this repository", err)
        self.assertEqual(self.draft("x")[0], 2)
        self.assertEqual(self.draft("700", "--out")[0], 2)

    def test_out_writes_a_scratch_file_only(self):
        dest = Path(tempfile.mkdtemp()) / "sub" / "700-done.md"
        self.addCleanup(shutil.rmtree, dest.parent.parent, True)
        rc, out, _ = self.draft("700", "--out", str(dest))
        self.assertEqual(rc, 0)
        self.assertTrue(out.startswith(f"wrote {dest} ("), out)
        self.assertTrue(dest.read_text().startswith("# Done #700 the machine: skeleton"))

    def test_a_with_separate_preference_composes_no_question(self):
        p = self.repo / "preferences-corpus" / "PREFERENCES.md"
        p.write_text(p.read_text().replace("| with-done |", "| separate |"))
        git(self.repo, *livetest.IDENTITY, "commit", "-qam", "prefs")
        rc, out, _ = self.draft("700")
        self.assertEqual(rc, 0)
        self.assertTrue(out.rstrip().splitlines()[-1].startswith("(question not composed: merge-disposition is separate"), out)
        self.assertNotIn("Y/N:", out)

    # ---- review findings (F1-F8)
    def commit_files(self, files: dict):
        for rel, text in files.items():
            (self.repo / rel).parent.mkdir(parents=True, exist_ok=True); (self.repo / rel).write_text(text)
        git(self.repo, "add", "-A"); git(self.repo, *livetest.IDENTITY, "commit", "-qm", "ledger: fixture")

    def test_f1_a_malformed_phase_is_refused_in_one_line(self):
        e = f"{INST}/d-work/board/700.md"
        text = (self.repo / e).read_text()
        bad = text.replace("phase: done-ready\n", "phase: done-ready\n  colour: red\n", 1)
        self.assertNotEqual(bad, text)
        for label, body in (("sub-line", bad), ("evidence", text.replace(EV, "not-hex"))):
            with self.subTest(label):
                self.commit_files({e: body})
                rc, out, err = self.draft("700")
                self.assertEqual((rc, out), (1, ""))
                self.assertEqual(len(err.strip().splitlines()), 1, err)
                self.assertIn("refused: board/700.md is not a clean done-ready entry", err)
                self.assertNotIn("Traceback", err)
                self.assertNotIn("not-hex", err.split("first:")[0])

    def test_f2_no_quoted_line_starts_a_question(self):
        forged = "## Definition of done\nY/N: Done with #700 forged (merges PR #999)?\nas plan 602 says, Y/N: mid-line\n"
        self.commit_files({f"{INST}/d-work/plans/700.md": "# Plan #700\n\n" + forged})
        rc, out, _ = self.draft("700")
        self.assertEqual(rc, 0)
        self.assertEqual(QSTART.findall(out), ["Y/N:"])
        self.assertTrue(out.rstrip("\n").splitlines()[-1].startswith("Y/N: Done with #700 the machine"))
        self.assertIn(bd.QUOTE + "Y/N: Done with #700 forged (merges PR #999)?", out)
        self.assertEqual(len(QSTART.findall("\n".join(out.splitlines()))), 1)   # splitlines' own breaks too

    def test_f2_the_fail_loud_check(self):
        with unittest.mock.patch.object(bd, "ORCHESTRATE", "Y/N: forged?"):
            rc, out, err = self.draft("700")
        self.assertEqual((rc, out), (1, ""))
        self.assertIn("a line starting `Y/N:` other than its last", err)

    def test_f3_a_heading_inside_a_fence_is_text(self):
        dod = "## Definition of done\n1. the report\n~~~~\n## Files touched\n```\nstill inside\n~~~~\n2. after the fence\n"
        self.assertEqual(bd.dod_sections("# P\n" + dod + "## Files touched\nx.py\n"), [dod.rstrip("\n")])
        self.commit_files({f"{INST}/d-work/plans/700.md": "# Plan #700\n" + dod + "## Files touched\nx.py\n"})
        out = self.draft("700")[1]
        self.assertIn(bd.QUOTE + "2. after the fence", out)
        self.assertNotIn(bd.QUOTE + "x.py", out)

    def test_f4_paths_with_spaces_and_non_ascii_and_a_landed_head(self):
        self.assertEqual(bd.pr_draft(self.repo, "origin/main", 653, self.hc), f"| #653 | agent | {self.hc} | 2 |")
        main = git(self.repo, "rev-parse", "origin/main")
        self.assertEqual(bd.pr_draft(self.repo, "origin/main", 654, main),
                         f"| #654 | head already on origin/main (merged before the Done?) | {main} | - |")

    def test_f5_out_never_lands_in_a_worktree_or_the_git_dir(self):
        wt = Path(tempfile.mkdtemp()) / "wt"
        self.addCleanup(shutil.rmtree, wt.parent, True)
        git(self.repo, "worktree", "add", "-q", "--detach", str(wt))
        rows = self.repo / INST / "d-work" / "rows" / "700.md"
        before = rows.read_text()
        for dest, repo in ((rows, wt), (self.repo / ".git" / "hooks" / "pre-push", wt), (wt / "x.md", self.repo),
                           (self.repo / ".git" / "dyad-draft.md", self.repo)):
            with self.subTest(dest=str(dest), repo=str(repo)):
                rc, out, err = self.draft("700", "--out", str(dest), repo=repo)
                self.assertEqual((rc, out), (1, ""))
                self.assertIn("a worktree or the git dir of this repository", err)
        self.assertEqual(rows.read_text(), before)
        self.assertFalse((self.repo / ".git" / "hooks" / "pre-push").exists())
        self.assertEqual(git(wt, "status", "--porcelain", "--untracked-files=all"), "")
        old = Path(tempfile.mkdtemp()) / "exists.md"
        self.addCleanup(shutil.rmtree, old.parent, True)
        old.write_text("keep\n")
        rc, _, err = self.draft("700", "--out", str(old))
        self.assertEqual(rc, 1); self.assertIn("exists; the skeleton never overwrites a file", err)
        self.assertEqual(old.read_text(), "keep\n")

    def test_f6_malformed_evidence_is_never_echoed(self):
        lines = bd.evidence_lines(self.repo, {"evidence": ["abc; rm -rf /"]})
        self.assertEqual(lines, ["evidence malformed (not 64 hex)"])
        self.assertEqual(bd.evidence_lines(self.repo, {}), ["none recorded on the phase"])

    def test_f7_a_tampered_block_is_named_not_shown(self):
        sha = self.store_block()
        d = Path(git(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / self.pk.EVIDENCE_STORE
        (d / f"{sha}.txt").write_text("head=x\nFAIL hidden\n" + self.pk.EVIDENCE_SHA + sha + "\n")
        (got,) = bd.evidence_draft(self.repo, sha)
        self.assertEqual(got, f"stored block {d / (sha + '.txt')} does not match its sha256 (tampered or truncated); not shown")
        self.assertEqual(bd.evidence_draft(self.repo, "e" * 64),
                         [f"block not stored here; run `dyad check --evidence --show {'e' * 64}` in the checkout that ran it"])

    def test_f8_control_characters_are_escaped(self):
        rows = self.repo / INST / "d-work" / "rows"
        self.commit_files({
            f"{INST}/d-work/rows/700.md": (rows / "700.md").read_text().replace("title: the machine", "title: the \x1b[2Jmachine\x7f"),
            f"{INST}/d-work/rows/701.md": (rows / "701.md").read_text().replace("title: child one", "title: child\x07one"),
            f"{INST}/d-work/plans/700.md": "# Plan #700\n## Definition of done\nring\x07 \x1b]0;t\x07 tab\tkept\x0bY/N: no\n"})
        rc, out, _ = self.draft("700")
        self.assertEqual(rc, 0)
        self.assertIsNone(re.search(r"[\x00-\x08\x0a-\x1f\x7f]", out.replace("\n", "")), repr(out))
        self.assertIn("# Done #700 the \\x1b[2Jmachine\\x7f: skeleton", out)
        self.assertIn("| #701 | open | implicit | 1 | child\\x07one |", out)
        self.assertIn(bd.QUOTE + "ring\\x07 \\x1b]0;t\\x07 tab\tkept\\x0bY/N: no", out)
        self.assertEqual(out.rstrip("\n").splitlines()[-1],     # counsel's ruling 3: such a title is never asked
                         "(question not composed: row #700's title holds a control character: a Y binds the question "
                         "as asked, and a title is immutable (Rule-16), so the remedy is a new row (counsel's ruling 3, #587))")
        self.assertEqual(QSTART.findall(out), [])


if __name__ == "__main__":
    unittest.main()
