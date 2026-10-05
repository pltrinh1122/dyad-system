"""d-work trace tests (dyad/scripts/trace.py, #213): a fixture instance (a temporary git repository holding one
row, its provenance record and plan file) and fixture transcripts written here — never a real session's.
Anchoring is exact and in order, a disposition answers only a `Y/N:` naming its id, the buckets sum to the
window to the millisecond, overlapping tool calls and a background launch are counted once, the no-transcript
path degrades to the git and ledger timeline, an unmatched or ambiguous entry is reported and never guessed,
the window runs through the Done-`Y` (to the Done question in a preview, before one), `--out` writes
`<instance>/d-work/traces/<id>.md`, the store is well-formed, and no transcript text reaches the output."""
import datetime, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
tr = dyadlib.load_module(PKG / "scripts" / "trace.py", "dyad_trace")   # by path: `trace` is also a stdlib module

PROMPT = "please trace the widget pipeline end to end"
SECRET = "SECRET-TRANSCRIPT-WORDS"        # only ever inside the fixture transcript: must never reach a trace
T0 = datetime.datetime(2026, 10, 5, 10, 0, 0, tzinfo=datetime.timezone.utc)

def ts(s: float) -> str:
    return (T0 + datetime.timedelta(seconds=s)).isoformat().replace("+00:00", "Z")

def user(s, text, uid, origin="human"):
    return {"type": "user", "timestamp": ts(s), "uuid": uid, "sessionId": "s1", "origin": {"kind": origin},
            "message": {"role": "user", "content": text}}

def result(s, tool, uid, content=SECRET):
    return {"type": "user", "timestamp": ts(s), "uuid": uid, "sessionId": "s1",
            "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool, "content": content}]}}

def tool(s, tid, name, uid, msg, out=10, **inp):
    return {"type": "assistant", "timestamp": ts(s), "uuid": uid, "sessionId": "s1",
            "message": {"id": msg, "role": "assistant", "content": [{"type": "tool_use", "id": tid, "name": name, "input": inp}],
                        "usage": {"output_tokens": out}}}

def text(s, body, uid, msg, out=10):
    return {"type": "assistant", "timestamp": ts(s), "uuid": uid, "sessionId": "s1",
            "message": {"id": msg, "role": "assistant", "content": [{"type": "text", "text": body}], "usage": {"output_tokens": out}}}

def transcript() -> list[dict]:
    """Window 0 → 230 s: operator 80→200 (120 s), suite 10→70 (60 s), git/local 5→7 and the background launch
    210→211 (3 s), github 212→215 with a Read 212→214 inside it (3 s, counted once), inference the rest (44 s)."""
    return [
        text(-120, f"{SECRET}\nY/N: proceed with #6 as planned?", "d0", "m0"),
        user(-100, "Y", "d1"),                                          # a `Y` for another d-work: never #7's anchor
        user(0, f"  {PROMPT}\n", "u0"),
        tool(5, "a1", "Bash", "u1", "m1", command="ls"),
        result(7, "a1", "u2"),
        tool(10, "a2", "Bash", "u3", "m2", command="dyad/bin/dyad check --evidence"),
        result(70, "a2", "u4", content=f"Ran 5 tests OK\n{SECRET}"),
        text(80, f"{SECRET}\nY/N: proceed with #7 as planned?", "u5", "m3", out=100),
        user(200, "Y", "u6"),
        tool(210, "a3", "Bash", "u7", "m4", command="sleep 60", run_in_background=True),
        result(211, "a3", "u8"),
        tool(212, "a4", "mcp__github__create_pull_request", "u9", "m5", head="work-7"),
        tool(212, "a5", "Read", "u10", "m6", file_path="x"),
        result(214, "a5", "u11"),
        result(215, "a4", "u12"),
        text(230, f"{SECRET}\nY/N: Done with #7 widget (merges PR #1)?", "u13", "m7"),
        user(400, "Y", "u14"),
    ]

def record(entries) -> str:
    out = "# Provenance #7\n"
    for n, (kind, date, note, body) in enumerate(entries, 1):
        out += f"\n## {n} {kind} {date}{' ' + note if note else ''}\n\n```\n{body}\n```\n"
    return out

ENTRIES = [("prompt", "2026-10-05", "", PROMPT), ("disposition", "2026-10-05", "Y plan", "Y"),
           ("disposition", "2026-10-05", "Y done merges PR #1", "Y")]

def git(root, *a):
    subprocess.run(["git", *a], cwd=root, check=True, capture_output=True, env=dyadlib.git_env())

def fixture(entries=ENTRIES, lines=None):
    """(root, transcript path): a git repository with row 7, its record and plan, one ledger commit and one
    work commit citing `d-work #7`; and the transcript, in the scratch directory and never in the repo."""
    root = Path(tempfile.mkdtemp())
    git(root, "init", "-q"); git(root, "config", "user.email", "t@example.org"); git(root, "config", "user.name", "t")
    dw = root / "agent-corpus" / "d-work"
    for d in ("rows", "plans", "provenance"):
        (dw / d).mkdir(parents=True)
    (dw / "rows" / "7.md").write_text("id: 7\ntitle: widget\nopened: 2026-10-05\nstate: planned\ndisposed: 2026-10-05 Y plan\nrefs: \n")
    (dw / "plans" / "7.md").write_text("# Plan #7\n")
    (dw / "provenance" / "7.md").write_text(record(entries))
    git(root, "add", "-A"); git(root, "commit", "-qm", "ledger: open #7")
    (root / "code.py").write_text("x = 1\n")
    git(root, "add", "-A"); git(root, "commit", "-qm", "the widget (d-work #7)")
    tdir = Path(tempfile.mkdtemp())
    path = tdir / "session.jsonl"
    path.write_text("".join(json.dumps(o) + "\n" for o in (transcript() if lines is None else lines)) + "not json\n")
    return root, path

class TraceTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("DYAD_INSTANCE", None)

    def test_anchoring_is_exact_and_in_order(self):
        root, path = fixture()
        recs, problems = tr.load([path])
        self.assertEqual(problems, ["transcript session.jsonl: 1 line(s) not JSON, skipped"])
        got = tr.anchor(tr.provenance(7, root), recs, 7)
        self.assertEqual([a["status"] for a in got], ["anchored"] * 3)
        self.assertEqual([a["ts"] for a in got], [tr.ms(ts(s)) for s in (0, 200, 400)])   # never the `Y` at -100 (#6's)
        self.assertEqual([a["asked_ts"] for a in got], [None, tr.ms(ts(80)), tr.ms(ts(230))])

    def test_buckets_sum_to_the_window_and_overlap_counts_once(self):
        root, path = fixture()
        recs, _ = tr.load([path])
        start, end = tr.ms(ts(0)), tr.ms(ts(230))
        ivs, bg = tr.intervals(recs, start, end)
        got, _ = tr.buckets(ivs, start, end)
        self.assertEqual(sum(got.values()), end - start)
        self.assertEqual({b: v // 1000 for b, v in got.items() if v},
                         {"operator": 120, "suite": 60, "git/local": 3, "github": 3, "inference": 44})
        self.assertEqual(got["other"], 0)                                 # the Read inside the GitHub call: counted once
        self.assertEqual([b["name"] for b in bg], ["Bash"])              # the background launch is listed

    def test_a_push_that_ran_no_suite_is_a_guards_only_gate(self):
        """A ledger-only or empty range runs guards only (Rule-12 p2): its push is `guards`, never `suite`."""
        lines = [tool(0, "p1", "Bash", "g0", "n0", command="git push -u origin ledger-7"),
                 result(8, "p1", "g1", content="ok   [guards] agent/rows"),
                 tool(10, "p2", "Bash", "g2", "n1", command="git push -u origin work-7"),
                 result(110, "p2", "g3", content="     [Rule-12] dyad/tests: Ran 585 tests OK")]
        path = Path(tempfile.mkdtemp()) / "t.jsonl"
        path.write_text("".join(json.dumps(l) + "\n" for l in lines))
        recs, _ = tr.load([path])
        self.assertEqual([r["tkind"] for r in recs if r["kind"] == "tool_use"], ["guards", "suite"])

    def test_report_window_counts_and_no_transcript_text(self):
        root, path = fixture()
        out = tr.trace(7, root, [path])
        self.assertIn("Window: 2026-10-05 10:00:00 → 2026-10-05 10:06:40 UTC, 6m40s", out)   # through the Done-`Y` (rev. 2)
        self.assertIn("| **total** | | 400 | 100% |", out)
        self.assertIn("| operator | operator | 290 |", out)                 # both waits: plan question, Done question
        self.assertIn("**Agent-side:** 110 s", out)
        self.assertIn("| commits | 2 (1 ledger-only) | git |", out)
        self.assertIn("| PRs created in the window | ledger 0, work 1 | transcript |", out)
        self.assertIn("| output tokens | 160 | transcript |", out)             # m1..m7 inside the window, one usage each
        self.assertIn("— after the window (clerical tail)", out)
        self.assertIn("(3 entries, 3 anchored)", out)
        for leak in (SECRET, PROMPT, "check --evidence\"", "sleep 60"):
            self.assertNotIn(leak, out)

    def test_no_transcript_gives_git_and_ledger_only(self):
        root, _ = fixture()
        out = tr.trace(7, root, [])
        self.assertIn("transcript: none found.", out)
        self.assertIn("Absent: no transcript.", out)
        self.assertIn("the widget (d-work #7)", out)
        self.assertIn("| tool calls, tokens, PRs created | absent | no transcript window |", out)

    def test_unmatched_and_ambiguous_entries_are_reported_never_guessed(self):
        entries = ENTRIES[:1] + [("prompt", "2026-10-05", "", "words the Operator never sent in this session")] + ENTRIES[1:]
        root, path = fixture(entries)
        out = tr.trace(7, root, [path])
        self.assertIn("provenance entry 2 (prompt 2026-10-05) unmatched in the transcript: not used as an anchor, never guessed", out)
        lines = transcript()
        lines.insert(3, user(1, PROMPT, "dup"))                          # the same prompt twice: ambiguous
        root, path = fixture(lines=lines)
        got = tr.anchor(tr.provenance(7, root), tr.load([path])[0], 7)
        self.assertEqual(got[0]["status"], "ambiguous"); self.assertIsNone(got[0]["ts"])

    def test_before_the_done_y_the_trace_is_a_preview(self):
        lines = transcript()[:-1]                                         # the Done question asked, not yet answered
        root, path = fixture(ENTRIES[:2], lines=lines)
        out = tr.trace(7, root, [path])
        self.assertIn("preview: the d-work has no Done disposition yet", out)
        self.assertIn("Window: 2026-10-05 10:00:00 → 2026-10-05 10:03:50 UTC, 3m50s", out)   # prompt → Done question
        self.assertIn("— after the window |", out)                         # not a clerical tail: no Done-`Y` yet

    def test_an_unanchored_done_ends_at_the_last_event(self):
        root, path = fixture(lines=transcript()[:-1])                    # the record holds a Done the transcript lacks
        out = tr.trace(7, root, [path])
        self.assertIn("the Done disposition is not anchored", out)
        self.assertIn("provenance entry 3 (disposition 2026-10-05 Y done merges PR #1) unmatched", out)

    def test_out_writes_the_instance_trace_file(self):
        root, path = fixture()
        from io import StringIO
        from contextlib import redirect_stdout
        with redirect_stdout(StringIO()) as buf:
            self.assertEqual(tr.main(["7", "--transcript", str(path), "--out"], root=root), 0)
        dest = root / "agent-corpus" / "d-work" / "traces" / "7.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(buf.getvalue().strip(), "wrote agent-corpus/d-work/traces/7.md")
        self.assertEqual(tr.check_store(root), [])                       # what --out writes is well-formed
        self.assertTrue(dest.read_text().startswith("# Trace #7 — widget"))
        other = dest.with_name("8.md"); other.write_text("**Agent-side:** 50 s (x)\n")
        self.assertEqual(tr.median_agent_side(root, 7), (50, 1))         # the Compare step's median, this trace excluded

    def test_store_well_formedness(self):
        root, path = fixture()
        self.assertEqual(tr.check_store(root), [])                       # an absent store passes (nothing traced yet)
        store = root / "agent-corpus" / "d-work" / "traces"; store.mkdir()
        good = tr.trace(7, root, [path])
        (store / "7.md").write_text(good)
        self.assertEqual(tr.check_store(root), [])
        (store / "9.md").write_text(good.replace("# Trace #7", "# Trace #9", 1))     # no row #9
        (store / "notes.md").write_text("x\n")                                         # not `<id>.md`
        (store / "7.md").write_text(good.replace("# Trace #7", "# Trace #8", 1).replace("## Counts", "## Tallies"))
        msgs = tr.check_store(root)
        self.assertEqual(len(msgs), 4, msgs)
        self.assertTrue(any("9.md: no row #9" in m for m in msgs))
        self.assertTrue(any("notes.md: not `<id>.md`" in m for m in msgs))
        self.assertTrue(any("7.md: first line is not `# Trace #7" in m for m in msgs))
        self.assertTrue(any("7.md: sections" in m for m in msgs))

class LiveTests(unittest.TestCase):
    def test_live_trace_store_is_well_formed(self):
        os.environ.pop("DYAD_INSTANCE", None)
        msgs = tr.check_store(dyadlib.repo_root())
        self.assertEqual(msgs, [], msgs)

    def test_refusals(self):
        root, path = fixture()
        for argv in (["7", "--transcript"], ["7", "--bogus"], ["7", "--transcript", str(path) + ".missing"], []):
            with self.assertRaises(SystemExit):
                tr.main(argv, root=root)

if __name__ == "__main__":
    unittest.main()
