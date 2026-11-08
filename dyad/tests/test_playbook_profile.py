"""`dyad playbook profile <name>` (scripts/playbook_profile.py, d-work #642), over a scratch tree: steps by section and
numbered item with their words, `dmc:` citations and `dyad` commands; each cited record's words and kind; the run total
(play-book, run-book, records); the median trace seconds of rows whose plan names the play-book, with the limit; an
unknown or malformed name refused; nothing written. Plus the live d-work play-book profiles without error."""
import contextlib, io, json, os, shutil, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
pp = dyadlib.load_module(PKG / "scripts" / "playbook_profile.py", "playbook_profile_under_test")

PLAYBOOK = ("# Play-book: kiln\n\nIntro words here.\n\n## Trigger\nWhen fired.\n\n## Steps\n"
            "1. **Load** — apply `dmc:kiln-class` with `dyad board resume`.\n   more load words\n"
            "2. **Fire** — `dmc:kiln-class` then `dmc:kiln-temp`.\n\n## Question\nAsk once.\n")
TRACE = ("# Trace\n\n## Buckets\n\n| bucket | partition | seconds | share | what |\n|---|---|---|---|---|\n"
         "| operator | operator | 100 | x | y |\n| inference | agent | {inf} | x | y |\n| suite | agent | {suite} | x | y |\n"
         "| guards | agent | 5 | x | y |\n| background | agent | 999 | x | y |\n")


class ProfileTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus"}); e.start(); self.addCleanup(e.stop)
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, True)
        c = self.root / "crafts" / "pottery"
        (c / "playbooks").mkdir(parents=True); (c / "runbooks").mkdir(); (c / "dmc").mkdir()
        (c / "VERSION").write_text("0.1.0\n")
        (c / "playbooks" / "kiln.md").write_text(PLAYBOOK)
        (c / "runbooks" / "kiln.md").write_text("# Run-book: kiln\none two three\n")
        for ident, kind in (("kiln-class", "inference"), ("kiln-temp", "mechanical")):
            (c / "dmc" / f"{ident}.jsonld").write_text(json.dumps({"identifier": ident, "dyad:judgedBy": {"dyad:kind": kind}}))
        store = self.root / "agent-corpus" / "d-work"; (store / "plans").mkdir(parents=True); (store / "traces").mkdir()
        for rid, inf, suite, names in ((1, 10, 20, True), (2, 30, 40, True), (3, 999, 999, False)):
            (store / "plans" / f"{rid}.md").write_text("runs crafts/pottery/playbooks/kiln.md\n" if names else "other\n")
            (store / "traces" / f"{rid}.md").write_text(TRACE.format(inf=inf, suite=suite))
        recs = {"kiln-class": c / "dmc" / "kiln-class.jsonld", "kiln-temp": c / "dmc" / "kiln-temp.jsonld"}
        p = unittest.mock.patch.object(pp, "records", return_value=recs); p.start(); self.addCleanup(p.stop)

    def test_steps_records_total_and_time(self):
        out = pp.profile(self.root, "kiln")
        self.assertEqual(out[0], f"play-book kiln: crafts/pottery/playbooks/kiln.md, {pp.words(PLAYBOOK)} words; "
                                 "run-book pottery/runbooks/kiln.md, 6 words")
        self.assertIn("  step Steps 1 Load: 12 words; dmc: kiln-class; commands: `dyad board resume`", out)
        self.assertIn("  step Steps 2 Fire: 6 words; dmc: kiln-class, kiln-temp; commands: -", out)
        self.assertIn("  step Trigger -: 2 words; dmc: -; commands: -", out)
        self.assertIn("  dmc:kiln-class inference, 5 words", out); self.assertIn("  dmc:kiln-temp mechanical, 5 words", out)
        self.assertIn(f"run total: {pp.words(PLAYBOOK) + 6 + 10} words (the play-book, its run-book and the 2 record(s) it cites)", out)
        self.assertEqual(out[-1], "time: 2 trace(s) of rows whose plan names crafts/pottery/playbooks/kiln.md (#1, #2): "
                                  f"median inference 20 s, mechanical 35 s; {pp.LIMIT}")    # mechanical = suite + guards

    def test_trace_seconds_read_the_buckets(self):
        self.assertEqual(pp.trace_seconds(TRACE.format(inf=7, suite=3)), (7, 8))
        self.assertIsNone(pp.trace_seconds("## Buckets\n\nAbsent: no window.\n"))

    def test_refusals_and_nothing_written(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(pp.main([], self.root), 1)
            self.assertEqual(pp.main(["Bad_Name"], self.root), 1)
            self.assertEqual(pp.main(["no-such"], self.root), 1)
        self.assertIn("refused: no play-book no-such", err.getvalue())
        before = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(pp.main(["kiln"], self.root), 0)
        self.assertEqual(sorted(p.relative_to(self.root) for p in self.root.rglob("*")), before)


class LiveProfileTests(unittest.TestCase):
    def test_the_d_work_playbook_profiles(self):
        out = pp.profile(dyadlib.repo_root(), "d-work")
        self.assertTrue(out[0].startswith("play-book d-work: dyad/playbooks/d-work.md, "))
        self.assertTrue(any(l.startswith("  dmc:") for l in out))
        self.assertTrue(out[-1].startswith("time: ") and out[-1].endswith(pp.LIMIT))


if __name__ == "__main__":
    unittest.main()
