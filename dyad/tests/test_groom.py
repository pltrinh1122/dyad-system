"""The backlog grooming report (scripts/groom.py, `dyad board groom`, d-work #625), over a scratch repo:
- the hygiene and candidate lines it prints are exactly `hygiene.hygiene`'s, verbatim, each under every backlog row it
  names (plan #625 F5: imported, never recomputed);
- a row's refs with their states, its nearest board anchor, the `_cos` files promising it and its plan's craft roots;
- the release lines name each craft's last tag and live VERSION, then the bundle's;
- the last grooming is the run-book's last `report` event;
- rows are labelled under `dwork-slug: on`; any argument is refused; it writes nothing."""
import contextlib, io, json, os, shutil, subprocess, sys, tempfile, time, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
groom = dyadlib.load_module(PKG / "scripts" / "groom.py", "groom")
hy = dyadlib.load_module(PKG / "scripts" / "hygiene.py", "hygiene")
INST = "agent-corpus"
ROW = "id: {id}\ntitle: {title}\nopened: 2026-09-01\nstate: {state}\ndisposed: {disposed}\nrefs: {refs}\n{slug}"
OLD = "2026-09-01T00:00:00Z"


def git(d, *a, date=None):
    env = {**dyadlib.git_env(), **({"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date} if date else {})}
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=env)
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class GroomTests(unittest.TestCase):
    def setUp(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": INST}); e.start(); self.addCleanup(e.stop)
        os.environ.pop("DYAD_RUNBOOKS", None)
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        git(self.d, "init", "-q", "-b", "main")
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            git(self.d, "config", k, v)
        (self.d / "dyad").mkdir(); (self.d / "dyad" / "VERSION").write_text("1.2.0\n")
        (self.d / "crafts" / "pottery").mkdir(parents=True); (self.d / "crafts" / "pottery" / "VERSION").write_text("0.3.0\n")
        (self.d / "BUNDLE.md").write_text("# bundle\nversion: 1.4.0\n")
        git(self.d, "add", "-A"); git(self.d, "commit", "-qm", "tree")

    def put(self, rel, text):
        p = self.d / INST / "d-work" / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)

    def row(self, id, title, state="backlog", refs="", plan=None, date=None, slug=""):
        self.put(f"rows/{id}.md", ROW.format(id=id, title=title, state=state, refs=refs, slug=f"slug: {slug}\n" if slug else "",
                                             disposed="2026-09-01 Y backlog" if state == "backlog" else "2026-09-01 Y plan"))
        if plan:
            self.put(f"plans/{id}.md", plan)
        git(self.d, "add", "-A"); git(self.d, "commit", "-qm", f"ledger: #{id}", date=date)

    def report(self):
        return groom.report(self.d, "HEAD", time.time())

    def block(self, lines, rid):
        i = next(n for n, l in enumerate(lines) if l.startswith(f"#{rid} ") or l.startswith(f"#{rid}-"))
        j = next((n for n in range(i + 1, len(lines)) if not lines[n].startswith("  ")), len(lines))
        return lines[i:j]

    def test_hygiene_lines_are_hygienes_verbatim(self):
        self.row(1, "a parent long done", state="done")
        self.row(2, "an old backlog row about widgets", date=OLD)
        self.row(5, "a child of a done parent", refs="parent #1")
        for i, t in enumerate(["sweep the archive tags against their release entries",
                               "reconcile release tags against the archive entries", "an unrelated row about fonts",
                               "a second unrelated row about colours", "a third unrelated row about spacing",
                               "a fourth unrelated row about margins", "a fifth unrelated row about borders"], 11):
            self.row(i, t)
        findings, candidates = hy.hygiene(self.d, "HEAD", time.time())
        self.assertTrue(findings and candidates)                    # the fixture exercises both kinds
        lines = self.report()
        printed = {l[2:] for l in lines if l.startswith(("  hygiene ", "  candidate: "))}
        self.assertEqual(printed, set(findings) | set(candidates))
        backlog = {r.id for r in dyadlib.read_rows(self.d, at="HEAD") if r.state == "backlog"}
        for line in candidates:                                      # under every backlog row a candidate names
            for rid in {int(n) for n in groom.NAMED.findall(line)} & backlog:
                self.assertIn(f"  {line}", self.block(lines, rid))

    def test_refs_anchor_promise_and_roots(self):
        self.row(30, "the release tag sweep is planned", state="planned")
        self.row(31, "an unrelated planned row about fonts", state="planned")
        self.row(32, "sweep every release tag", refs="#30, parent #99",
                 plan="Files touched: dyad/scripts/release.py, crafts/pottery/rules/glaze.md\n")
        self.row(33, "a row with a plan naming no root", plan="nothing here\n")
        self.row(34, "a row with no plan")
        for i, t in enumerate(["colours", "spacing", "margins", "borders", "kerning", "leading", "gutters"], 35):
            self.row(i, f"filler about {t}", state="done")          # so `release` and `tag` stay under HYGIENE_MAX_DF
        self.put("board/30.md", "holder: program-1\nnext: build\n")
        self.put("board/_cos.md", "holder: program-1\npromised: #33 after #30\n")
        git(self.d, "add", "-A"); git(self.d, "commit", "-qm", "ledger: board")
        lines = self.report()
        self.assertIn("1 board anchor(s)", lines[0])
        b32 = self.block(lines, 32)
        self.assertEqual(b32[0], "#32 [backlog, " + b32[0].split("[backlog, ")[1].split("]")[0] + "] sweep every release tag")
        self.assertIn("  refs: #30 planned, #99 no such row", b32)
        self.assertTrue(any(l.startswith("  adjacency: #30 ") for l in b32), b32)
        self.assertIn("  promised: none", b32)
        self.assertIn("  roots: dyad-operator, pottery", b32)
        b33 = self.block(lines, 33)
        self.assertIn("  promised: _cos", b33)
        self.assertIn("  roots: none named", b33)
        self.assertIn("  refs: none", b33)
        self.assertIn("  roots: no plan file", self.block(lines, 34))
        self.assertFalse(any(l.startswith(("#30 ", "#31 ")) for l in lines))     # only backlog rows get a block

    def test_releases_and_last_grooming(self):
        self.row(40, "a backlog row")
        git(self.d, "tag", "dyad-operator-v1.1.0"); git(self.d, "tag", "dyad-operator-v1.0.9"); git(self.d, "tag", "v1.3.0")
        lines = self.report()
        i = lines.index("releases:")
        self.assertEqual(lines[i + 1:i + 4], ["  dyad-operator: last tag dyad-operator-v1.1.0 (VERSION 1.2.0)",
                                              "  pottery: last tag none (VERSION 0.3.0)",
                                              "  bundle: last tag v1.3.0 (BUNDLE.md 1.4.0)"])
        self.assertEqual(lines[-1], "last grooming: none")
        ev = self.d / "workstation-corpus" / "runbooks" / "events" / "backlog-groom.jsonl"
        ev.parent.mkdir(parents=True)
        ev.write_text(json.dumps({"id": "backlog-groom-20261107T230000Z-report", "ts": "2026-11-07T23:00:00Z",
                                  "name": "report"}) + "\n")
        self.assertEqual(self.report()[-1], "last grooming: backlog-groom-20261107T230000Z-report at 2026-11-07T23:00:00Z")

    def grooming_at(self, ts):
        ev = self.d / "workstation-corpus" / "runbooks" / "events" / "backlog-groom.jsonl"
        ev.parent.mkdir(parents=True, exist_ok=True)
        ev.write_text(json.dumps({"id": "backlog-groom-report", "ts": ts, "name": "report"}) + "\n")

    def test_groom_due_g2_on_a_tag_after_the_last_grooming(self):
        self.assertEqual(groom.groom_due(self.d), [])                        # no tag, no event: nothing due
        git(self.d, "tag", "dyad-operator-v1.2.0")
        self.assertEqual(groom.groom_due(self.d), ["G2"])                    # a tag and no grooming yet
        self.grooming_at("2099-01-01T00:00:00Z")
        self.assertEqual(groom.groom_due(self.d), [])                        # the tag predates the last grooming
        self.grooming_at("2020-01-01T00:00:00Z")
        self.assertEqual(groom.groom_due(self.d), ["G2"])                    # the tag is newer than it
        git(self.d, "tag", "not-a-release")
        self.grooming_at("2099-01-01T00:00:00Z")
        self.assertEqual(groom.groom_due(self.d), [])                        # a tag of no release form never counts

    def test_groom_due_g4_at_five_hygiene_lines(self):
        self.assertEqual(groom.groom_due(self.d, hygiene=4), [])
        self.assertEqual(groom.groom_due(self.d, hygiene=5), ["G4"])
        self.assertEqual(groom.groom_due(self.d, hygiene=None), [])

    def test_labels_under_dwork_slug_on(self):
        self.row(50, "the anchor row", state="planned", slug="the-anchor")
        self.row(51, "a backlog row naming the anchor row", refs="#50", slug="named-row")
        with unittest.mock.patch.object(dyadlib, "slugs_on", return_value=True):
            lines = self.report()
        b = self.block(lines, 51)
        self.assertTrue(b[0].startswith("#51-named-row [backlog, "), b[0])
        self.assertIn("  refs: #50-the-anchor planned", b)

    def test_main_refuses_an_argument_and_writes_nothing(self):
        self.row(60, "a backlog row")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(groom.main(["x"], self.d), 1)
        self.assertIn("refused: usage: dyad board groom", err.getvalue())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(groom.main([], self.d), 0)
        self.assertTrue(out.getvalue().startswith("groom report: 1 backlog row(s) on "))
        self.assertEqual(git(self.d, "status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
