"""`scripts/audits.py` tests (d-work #619): each audit check the automaton sweep runs (`sweep_audit`), on a scratch repo
— the readings, the warnings, and the two run-book entries."""
import contextlib, io, os, shutil, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dyadlib
au = dyadlib.load_module(dyadlib.PKG / "scripts" / "audits.py", "audits")

ROW = "| {d} | #{i} | what | cause | consequence |\n"
LOG = "| date | d-work | what | cause | consequence |\n|---|---|---|---|---|\n"


class Scratch(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "agent-corpus"}); e.start(); self.addCleanup(e.stop)
        self.git("init", "-q", "-b", "main")
        self.write({"code.txt": "x\n"}); self.commit("base")
    def git(self, *a) -> str:
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.d), *a], check=True,
                              capture_output=True, text=True).stdout.strip()
    def write(self, files: dict[str, str | None]):
        for rel, text in files.items():
            p = self.d / rel
            if text is None:
                p.unlink()
            else:
                p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
    def commit(self, msg: str, files: dict[str, str | None] | None = None) -> str:
        self.write(files or {}); self.git("add", "-A"); self.git("commit", "-qm", msg, "--allow-empty")
        return self.git("rev-parse", "HEAD")
    def audits(self, name: str) -> str:
        return f"agent-corpus/audits/{name}"


class WatermarkTests(Scratch):
    def live(self):
        (line,) = au.watermark(self.d)
        return line.split("audit watermark: ", 1)[1].split("; ")[0], line.rsplit(": ", 1)[1]
    def test_the_watermark_prunes_dated_records_and_the_ledger_and_counts_everything_else(self):
        """Plan #223 A1, kept: the record an audit commits never changes the tree it hashes; #619 Q1: nor does the
        ledger, so ledger churn alone never reopens the audit."""
        self.commit("log", {self.audits("INCIDENTS.md"): LOG + ROW.format(d="2026-10-05", i=1)})
        base, verdict = self.live(); self.assertEqual(verdict, "first exercise")
        self.commit("record", {self.audits("2026-10-05-audit.md"): f"**Audited:** {base} · covered through abc, 2026-10-05\n"})
        self.assertEqual(self.live(), (base, "unchanged"))
        self.commit("dated", {self.audits("2026-10-06-sweep.md"): "another dated record\n"})
        self.assertEqual(self.live(), (base, "unchanged"))
        self.commit("ledger", {"agent-corpus/d-work/rows/1.md": "id: 1\n"})
        self.assertEqual(self.live(), (base, "unchanged"))
        self.commit("incident", {self.audits("INCIDENTS.md"): LOG + ROW.format(d="2026-10-05", i=1) + ROW.format(d="2026-10-06", i=2)})
        tree, verdict = self.live()
        self.assertEqual(verdict, "changed"); self.assertNotEqual(tree, base)
        self.assertRegex(tree, r"^tree [0-9a-f]{64} · python \S+ · git \S+$")


class RegistryTests(Scratch):
    def reg(self, text):
        with unittest.mock.patch.object(au, "registry_text", lambda root: text):
            return au.registry(self.d)
    def test_registry_reads_same_grew_shrank_or_first(self):
        text = "corpus entity\nagent rows\nagent board\n"
        import hashlib
        h = hashlib.sha256(text.encode()).hexdigest()[:16]
        self.assertEqual(self.reg(text), [f"reading: audit fences: registry 3 lines, sha256 {h}; none: first exercise"])
        self.commit("r", {self.audits("2026-10-05-audit.md"): f"**Fences:** registry 3 lines, sha256 {h} · hooksPath dyad/hooks\n"})
        self.assertTrue(self.reg(text)[0].endswith("2026-10-05-audit.md: same"))
        self.assertTrue(self.reg(text + "agent x\n")[0].endswith(": grew"))
        self.assertTrue(self.reg("corpus entity\n")[0].endswith(": shrank"))
        self.assertTrue(self.reg("corpus entity\nagent rows\nagent other\n")[0].endswith(": changed"))
        self.assertEqual(self.reg(None), ["reading: audit fences: registry not read (`check --list` failed)"])

    def test_a_guard_that_left_the_registry_is_named_against_its_own_tag(self):
        self.commit("guards", {"dyad/guards/agent/a.py": "", "dyad/guards/agent/b.py": "", "dyad/guards/agent/_h.py": "",
                               "crafts/c/guards/x.py": "", "crafts/c/VERSION": "0.1.0\n", "crafts/gone/guards/y.py": ""})
        self.git("tag", "dyad-operator-v1.0.0"); self.git("tag", "c-v0.1.0"); self.git("tag", "gone-v0.1.0")
        self.assertEqual(au.guards_left(self.d), [])
        self.commit("drop", {"dyad/guards/agent/b.py": None, "crafts/c/guards/x.py": None, "crafts/gone/guards/y.py": None})
        self.assertEqual(au.guards_left(self.d), [
            "finding: audit fences: guard agent/b is in dyad-operator-v1.0.0 and not in the registry",
            "finding: audit fences: guard c/x is in c-v0.1.0 and not in the registry"])   # `gone` left the tree: skipped
        self.git("tag", "-d", "dyad-operator-v1.0.0")
        self.assertIn("reading: audit fences: no core release tag reachable from main; the guards that left are not read",
                      au.guards_left(self.d))


class DriftTests(Scratch):
    def test_rules_edited_after_the_newest_rule_sweep_record(self):
        self.commit("rules", {"dyad/rules/RULE-1.md": "a\n"})
        self.assertEqual(au.rule_drift(self.d),
                         ["finding: audit drift: dyad/rules/ changed after the newest Rule-5 sweep record (none)"])
        self.commit("other sweep", {self.audits("2026-09-18-sysadmin-sweep.md"): "x\n"})   # a craft's sweep is no Rule-5 record (F3)
        self.assertIn("(none)", au.rule_drift(self.d)[0])
        self.commit("sweep", {self.audits("2026-10-01-rule-sweep.md"): "x\n"})
        self.assertEqual(au.rule_drift(self.d), [])
        self.commit("edit", {"dyad/rules/RULE-1.md": "b\n"})
        self.assertEqual(au.rule_drift(self.d),
                         ["finding: audit drift: dyad/rules/ changed after the newest Rule-5 sweep record (2026-10-01-rule-sweep.md)"])


class HardeningTests(Scratch):
    INDEX = "**Ledger:** `agent-corpus/audits/INCIDENTS.md` · **covered through:** {n} rows, latest {d}\n"
    def test_the_survey_says_first_exercise_no_op_or_delta(self):
        self.commit("log", {self.audits("INCIDENTS.md"): LOG + ROW.format(d="2026-10-05", i=1) + ROW.format(d="2026-10-06", i=1)})
        lines, outcome = au.hardening(self.d)
        self.assertEqual(outcome, "first exercise")
        self.assertEqual(lines, ["reading: hardening: live 2 rows, latest 2026-10-06; no index audit names INCIDENTS.md: first exercise"])
        self.commit("ix", {self.audits("2026-10-07-incident-failure-modes.md"): self.INDEX.format(n=2, d="2026-10-06")})
        self.assertEqual(au.hardening(self.d), (["reading: hardening: live 2 rows, latest 2026-10-06; "
                                                 "2026-10-07-incident-failure-modes.md: 2 rows, latest 2026-10-06"], "no-op"))
        self.commit("more", {self.audits("INCIDENTS.md"): LOG + ROW.format(d="2026-10-05", i=1) + ROW.format(d="2026-10-06", i=1)
                             + ROW.format(d="2026-10-08", i=3)})
        lines, outcome = au.hardening(self.d)
        self.assertEqual((outcome, lines[0]), ("delta", "finding: hardening: INCIDENTS.md holds rows past the watermark of "
                                                        "2026-10-07-incident-failure-modes.md"))
        (sizing,) = au.incidents(self.d)
        self.assertEqual(sizing, "reading: incidents: 3 rows, latest 2026-10-08; per month 2026-10 3; 1 d-works carry two or more rows")
        other = self.d / "elsewhere" / "LOG.md"
        self.commit("other", {"elsewhere/LOG.md": LOG + ROW.format(d="2026-10-05", i=1)})
        self.assertEqual(au.hardening(self.d, other)[1], "first exercise")    # the parameter, never the default's index

    def test_the_index_fence_rows_and_fences_resolve_or_are_named(self):
        legacy = ("| mode | incidents | closed by | fence, row or impossibility |\n|---|---|---|---|\n"
                  "| 01 | 3 | row (proposed) | R-g |\n| 02 | 1 | row (proposed) | R-g |\n| 03 | 1 | row (proposed) | #5 |\n"
                  "| 04 | 2 | fenced | `x.py` |\n")
        self.commit("ix", {self.audits("2026-10-07-incident-failure-modes.md"): legacy, "agent-corpus/d-work/rows/5.md": "id: 5\n"})
        self.assertEqual(au.index_fences(self.d, set()), [
            "finding: hardening: 2026-10-07-incident-failure-modes.md modes 01, 02 name fence row R-g, which is no ledger row",
            "finding: hardening: 2026-10-07-incident-failure-modes.md has no fence column; the closed modes' fences are not read"])
        seam = ("| mode | exit | fence row | fence |\n|---|---|---|---|\n| 01 | 2 | #7 | — |\n| 02 | 2 | #5 | — |\n"
                "| 03 | 1 | — | `dyad/m.py:CHECK`, `dyad/m.py:gone`, `agent/rows`, `nope/x`, `dyad/m.py` |\n| 04 | 3 | — | — |\n")
        self.commit("new", {self.audits("2026-11-01-incident-failure-modes.md"): seam, "dyad/m.py": "CHECK = 1\ndef f(): pass\n"})
        self.assertEqual(au.index_fences(self.d, {"agent/rows"}), [
            "finding: hardening: 2026-11-01-incident-failure-modes.md mode 01 names fence row #7, which is no ledger row",
            "finding: hardening: 2026-11-01-incident-failure-modes.md mode 03 names fence dyad/m.py:gone, which does not resolve",
            "finding: hardening: 2026-11-01-incident-failure-modes.md mode 03 names fence nope/x, which does not resolve"])
        self.assertTrue(au.resolves(self.d, "dyad/m.py:f", set()))
        self.commit("bare", {self.audits("2026-11-02-incident-failure-modes.md"): "no table here\n"})
        self.assertEqual(au.index_fences(self.d, set()), ["finding: hardening: 2026-11-02-incident-failure-modes.md has no "
                                                          "mode table; its fence rows and fences are not read"])


class RecordTests(Scratch):
    def run_(self, *a):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = au.main(list(a), self.d)
        return rc, out.getvalue(), err.getvalue()
    def test_the_newest_records_two_lines(self):
        self.assertEqual(au.record_lines(self.d), [])
        self.assertEqual(self.run_("record")[0], 1)                                  # no record: nothing to read back
        self.commit("r", {self.audits("2026-10-05-audit.md"): "**Audited:** tree t\n",
                          self.audits("2026-10-04-audit.md"): "**Audited:** tree t\n**Fences:** registry 1 lines, sha256 0\n"})
        self.assertEqual(au.record_lines(self.d), ["finding: audit record: 2026-10-05-audit.md lacks its **Fences:** line"])
        rc, out, _ = self.run_("record")
        self.assertEqual(rc, 1); self.assertIn("**Audited:** tree t", out)
        self.assertEqual(self.run_("record", self.audits("2026-10-04-audit.md"))[0], 0)
        self.assertEqual(self.run_("bogus")[0], 2)
    def test_hardening_entry_prints_its_verdict(self):
        self.commit("log", {self.audits("INCIDENTS.md"): LOG + ROW.format(d="2026-10-05", i=1)})
        rc, out, _ = self.run_("hardening")
        self.assertEqual(rc, 0); self.assertTrue(out.rstrip().endswith("verdict: first exercise"), out)


class LevelTests(Scratch):
    """#619 Decision 3: L1 to L3's coded halves read the stored report, never re-run it."""
    def report(self, *lines: str) -> str:
        head = self.git("rev-parse", "HEAD")
        d = self.d / ".git" / au.SWEEP_STORE; d.mkdir(exist_ok=True)
        body = "\n".join([*lines, f"sweep of main {head[:12]}: 0 finding(s)", "checks-sha256=c", "report-sha256=r"]) + "\n"
        (d / "r.txt").write_text(body)
        return body
    def levels(self, unit: str, integration: str):
        self.commit("levels", {"workstation-corpus/self-diagnostic-levels.txt": f"unit {unit}\nintegration {integration}\n",
                               unit: "", integration: ""})
    def test_unit_and_integration_class_the_reports_failing_tests_by_the_levels_file(self):
        self.levels("dyad/tests/test_a.py", "dyad/tests/test_b.py")
        self.assertEqual(au.level(self.d, "unit")[1], 2)                               # no report at HEAD
        self.report("reading: suite dyad/tests: Ran 2 tests OK")
        lines, rc = au.level(self.d, "unit")
        self.assertEqual((rc, lines[-3]), (0, "L1 unit: 1 modules, 0 failed"))
        self.assertEqual(lines[-2:], ["checks-sha256=c", "report-sha256=r"])         # the event carries both digests
        self.report("reading: suite dyad/tests: Ran 2 tests FAILED", "finding: FAIL [rule-12] tests failed (dyad/tests):",
                    "finding: ERROR: test_x (dyad.tests.test_b.C.test_x) — boom")
        self.assertEqual(au.level(self.d, "unit")[1], 0)                               # test_b is integration
        lines, rc = au.level(self.d, "integration")
        self.assertEqual(rc, 1)
        self.assertIn("L2 integration: 1 modules, 1 failed: dyad/tests/test_b.py; 1 failing check line(s)", lines)
        self.report()                                                                 # a report whose check ran no suite
        self.assertIn("the report ran no suite", au.level(self.d, "unit")[0][-3])
        self.assertEqual(au.level(self.d, "unit", "nope")[1], 2)
    def test_invariants_read_the_reports_reading(self):
        self.report("reading: invariants 40 ok, 0 FAIL")
        self.assertEqual(au.level(self.d, "invariants")[1], 0)
        self.report("reading: invariants 39 ok, 1 FAIL")
        self.assertEqual(au.level(self.d, "invariants")[1], 1)
        self.report()
        self.assertEqual(au.level(self.d, "invariants")[0][1], "L3 invariants: the report holds no invariant reading")


class AuditTests(Scratch):
    def test_readings_and_a_check_that_raises_is_one_finding(self):
        self.commit("p", {"agent-corpus/d-work/sessions/a.md": "session: a\nseen: 2020-01-01T00:00:00+00:00\n"})
        self.assertEqual(au.presence(self.d), ["reading: presence: 1 files past the stale window"])
        self.assertEqual(au.branches(self.d), ["reading: branches: 0 not merged into main"])
        self.assertEqual(au.levels(self.d), [])                                       # no levels file: no line
        with unittest.mock.patch.object(au, "registry", lambda root: 1 / 0):
            got = au.audit(self.d)
        self.assertIn("finding: audit: registry not read (ZeroDivisionError)", got)
        self.assertTrue(got[0].startswith("reading: audit watermark: "))
        self.assertTrue(all(l.startswith(("reading: ", "finding: ")) for l in got))
    def test_invariants(self):
        self.assertEqual(dyadlib.check_invariants(au), len(au.INVARIANTS))


if __name__ == "__main__":
    unittest.main()
