"""`dyad bootstrap [--check]` (scripts/bootstrap.py; d-work #474, child C1 of mandate #473) and the clone test `check
--evidence` shares with it. Every case runs over a scratch world: a seed repo carrying `dyad/hooks/`, a `BUNDLE.md` with
a `dyad-operator` row and two commits, the first tagged `dyad-operator-v0.1.0`; a bare `origin` cloned from it; and a
checkout cloned from that origin over `file://` with `--depth 1` (a local path ignores `--depth`), so it is shallow and
holds no tag. Nothing reaches the real repo's origin. The cases: `--check` reports all three steps as `warn` and
changes nothing; a run sets the hooks path, unshallows and fetches the tags (`changed`), and a second run is all `ok`;
a full clone missing its tags fetches them only when `BUNDLE.md` names a core release; a clone with no core row is
never fetched for (its origin removed, a fetch would warn); a fetch that fails is a `warn` line and exit 0; misuse is
exit 2, through the runner too; `clone_problems` names a shallow history first and a missing expected tag; and
`check --evidence` refuses a shallow or tagless clone with one `FAIL [evidence]` line, running nothing."""
import contextlib, io, subprocess, sys, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); import dyadlib, livetest

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
TAG = "dyad-operator-v0.1.0"
BUNDLE = "# Bundle\n\nversion: 0.2.0\n\n| component | version |\n|-----------|---------|\n| dyad-operator | 0.1.0 |\n"


def bootstrap():
    return dyadlib.load_module(PKG / "scripts" / "bootstrap.py", "bootstrap")


def git(d, *a):
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=dyadlib.git_env())
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)} in {d}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class World(unittest.TestCase):
    def setUp(self):
        self.bs = bootstrap()
        self.top = SCRATCH.mkdtemp()

    def make_origin(self, bundle=BUNDLE):
        seed = self.top / "seed"; seed.mkdir()
        git(seed, "init", "-q", "-b", "main")
        (seed / "dyad" / "hooks").mkdir(parents=True); (seed / "dyad" / "hooks" / "pre-commit").write_text("#!/bin/sh\n")
        if bundle is not None:
            (seed / "BUNDLE.md").write_text(bundle)
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "one")
        git(seed, *livetest.IDENTITY, "tag", "-a", TAG, "-m", TAG)
        (seed / "two.txt").write_text("two\n"); git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "two")
        self.origin = self.top / "origin.git"
        git(self.top, "clone", "-q", "--bare", str(seed), str(self.origin))
        return self.origin

    def shallow(self, bundle=BUNDLE):
        self.make_origin(bundle)
        work = self.top / "shallow"
        git(self.top, "clone", "-q", "--depth", "1", self.origin.as_uri(), str(work))
        return work

    def full(self, bundle=BUNDLE):
        self.make_origin(bundle)
        work = self.top / "full"
        git(self.top, "clone", "-q", str(self.origin), str(work))
        git(work, "tag", "-d", TAG)
        return work

    def run_main(self, work, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = self.bs.main(list(argv), work)
        return rc, out.getvalue().splitlines(), err.getvalue()

    def state(self, work):
        hooks = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=work, capture_output=True, text=True,
                               env=dyadlib.git_env()).stdout.strip()
        return hooks, git(work, "rev-parse", "--is-shallow-repository"), git(work, "tag", "-l")


class BootstrapTests(World):
    def test_check_reports_and_changes_nothing(self):
        work = self.shallow()
        before = self.state(work)
        self.assertEqual(before, ("", "true", ""))
        rc, lines, _ = self.run_main(work, "--check")
        self.assertEqual(rc, 0)
        self.assertEqual([l.split()[0] for l in lines], ["warn", "warn", "warn"], lines)
        self.assertEqual([l.split()[2] for l in lines], ["hooksPath:", "history:", "tags:"], lines)
        self.assertEqual(self.state(work), before)

    def test_run_repairs_then_a_second_run_is_all_ok(self):
        work = self.shallow()
        rc, lines, _ = self.run_main(work)
        self.assertEqual(rc, 0)
        self.assertEqual([l.split()[0] for l in lines], ["changed", "changed", "ok"], lines)   # the unshallow brought the tags
        self.assertEqual(self.state(work), ("dyad/hooks", "false", TAG))
        rc, lines, _ = self.run_main(work)
        self.assertEqual((rc, [l.split()[0] for l in lines]), (0, ["ok", "ok", "ok"]), lines)
        rc, lines, _ = self.run_main(work, "--check")
        self.assertEqual((rc, [l.split()[0] for l in lines]), (0, ["ok", "ok", "ok"]), lines)
        self.assertEqual(self.bs.clone_problems(work), [])

    def test_full_clone_without_its_tags_fetches_them(self):
        work = self.full()
        git(work, "config", "core.hooksPath", "dyad/hooks")
        rc, lines, _ = self.run_main(work)
        self.assertEqual([l.split()[0] for l in lines], ["ok", "ok", "changed"], lines)
        self.assertEqual(git(work, "tag", "-l"), TAG)

    def test_no_core_row_expects_no_tag_and_fetches_nothing(self):
        work = self.full(bundle=None)
        git(work, "remote", "remove", "origin")   # a fetch would print warn: proves none is attempted
        rc, lines, _ = self.run_main(work)
        self.assertEqual(rc, 0)
        self.assertEqual(lines[2], f"ok   [bootstrap] tags: no {self.bs.CORE_TAGS} tag, none expected "
                                   f"(BUNDLE.md names no dyad-operator row)")
        self.assertEqual(self.bs.clone_problems(work), [])

    def test_a_failed_fetch_is_a_warn_line_and_exit_0(self):
        work = self.shallow()
        git(work, "remote", "set-url", "origin", (self.top / "gone.git").as_uri())
        rc, lines, _ = self.run_main(work)
        self.assertEqual(rc, 0)
        self.assertEqual([l.split()[0] for l in lines], ["changed", "warn", "warn"], lines)
        self.assertIn("failed", lines[1])
        self.assertEqual(git(work, "rev-parse", "--is-shallow-repository"), "true")

    def test_misuse_is_exit_2(self):
        rc, lines, err = self.run_main(self.top, "--bogus")
        self.assertEqual((rc, lines), (2, []))
        self.assertIn("usage: dyad bootstrap [--check]", err)
        r = subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "bootstrap", "--bogus"],
                           capture_output=True, text=True, env=dyadlib.git_env())   # dispatched by the runner; nothing run
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_clone_problems_names_shallow_first_then_the_missing_tag(self):
        work = self.shallow()
        probs = self.bs.clone_problems(work)
        self.assertEqual(len(probs), 2, probs)
        self.assertTrue(probs[0].startswith("shallow clone: run ./dyad/bin/dyad bootstrap"), probs)
        self.assertTrue(probs[1].startswith(f"no {self.bs.CORE_TAGS} tag while BUNDLE.md names dyad-operator 0.1.0"), probs)

    def test_expected_core_release_reads_the_bundle_row(self):
        self.assertIsNone(self.bs.expected_core_release(self.top))   # no BUNDLE.md
        (self.top / "BUNDLE.md").write_text("# Bundle\n\nversion: 0.2.0\n\n| component | version |\n|---|---|\n| sysarch | 0.3.0 |\n")
        self.assertIsNone(self.bs.expected_core_release(self.top))   # no core row
        (self.top / "BUNDLE.md").write_text(BUNDLE)
        self.assertEqual(self.bs.expected_core_release(self.top), "0.1.0")


class EvidenceRefusalTests(World):
    """`check --evidence` refuses an unfit clone with one line before anything runs (d-work #474)."""
    def evidence(self, work):
        import importlib.util
        spec = importlib.util.spec_from_file_location("package", PKG / "scripts" / "package.py")
        pkg = importlib.util.module_from_spec(spec); spec.loader.exec_module(pkg)
        pkg.REPO = work
        buf = io.StringIO()
        boom = lambda *a, **k: self.fail("evidence ran a check on an unfit clone")
        with unittest.mock.patch.object(pkg, "cmd_check", boom), unittest.mock.patch.object(pkg, "cmd_guards", boom), \
             contextlib.redirect_stdout(buf):
            rc = pkg.cmd_evidence()
        return rc, buf.getvalue().splitlines()

    def test_shallow_clone_is_refused_in_one_line(self):
        rc, lines = self.evidence(self.shallow())
        self.assertEqual(rc, 2)
        self.assertEqual(lines, ["FAIL [evidence] shallow clone: run ./dyad/bin/dyad bootstrap (git fetch --unshallow --tags)"])

    def test_tagless_clone_where_a_core_release_is_expected_is_refused_in_one_line(self):
        rc, lines = self.evidence(self.full())
        self.assertEqual(rc, 2)
        self.assertEqual(len(lines), 1, lines)
        self.assertRegex(lines[0], r"^FAIL \[evidence\] no dyad-operator-v\* tag while BUNDLE\.md names dyad-operator 0\.1\.0: "
                                   r"run \./dyad/bin/dyad bootstrap \(git fetch --tags\)$")


if __name__ == "__main__":
    unittest.main()
