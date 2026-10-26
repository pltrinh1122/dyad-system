"""`dyad release [--scan]` (scripts/release.py; d-work #470, born `.github/released.py` by #461). Every case runs over a
scratch world — a seed repo carrying `dyad/VERSION`, `BUNDLE.md` and one row, a bare `origin`, and a checkout of `main`
cloned from it — with `gh` replaced by a shim on PATH that logs its argv and answers `api …/releases/tags/<tag>` from a
file (`release create` adds the tag to it), so nothing reaches GitHub or the real origin. The cases: entry parsing (a
good entry read, a `Y release` without `at` ignored, a malformed one refused); `--scan` with nothing pending prints
`pending: none` and appends `pending=false`, with one pending entry `pending=true`, and writes nothing; the push filter
reads only the entries `BEFORE` lacks; a cut not on main and a tag != VERSION at the cut are refused, the latter with
its worktree removed; a tag at the cut with its Release is skipped (`already`), a tag elsewhere refused; a sha256 that
differs from the recorded one is refused with no tag made (the build stubbed); a dispatch naming no entry fails. Over a
real core install (`livetest.ScratchInstalls`): one entry is published end to end — the cut's own builder, the tag
pushed to the bare origin, `gh release create` with the archive and its `.release.json` — and a second run is
`already`; and `./dyad/bin/dyad release --scan` in a fresh install prints `pending: none`, appends `pending=false` and
exits 0 (plan #469's red `scan` job, inverted)."""
import contextlib, hashlib, io, json, os, subprocess, sys, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts")); import dyadlib, livetest

SCRATCH = livetest.ScratchInstalls()
tearDownModule = SCRATCH.cleanup
INST = "agent-corpus"
REPO = "o/r"
ROW = "id: {id}\ntitle: release\nopened: 2026-10-01\nstate: open\ndisposed: {disposed}\nrefs: \n"
DIGEST = "ab" * 32
GH_SHIM = """#!/bin/sh
printf '%s\\n' "$*" >> "$GH_LOG"
if [ "$1" = api ]; then
  t=${2##*/}
  if [ -f "$GH_RELEASES" ] && grep -qxF "$t" "$GH_RELEASES"; then echo '{}'; exit 0; fi
  echo 'gh: Not Found (HTTP 404)' >&2; exit 1
fi
if [ "$1" = release ] && [ "$2" = create ]; then echo "$3" >> "$GH_RELEASES"; exit 0; fi
exit 3
"""


def release():
    return dyadlib.load_module(PKG / "scripts" / "release.py", "release")


def git(d, *a):
    r = subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, env=dyadlib.git_env())
    if r.returncode:
        raise RuntimeError(f"git {' '.join(a)} in {d}: {r.stdout}{r.stderr}")
    return r.stdout.strip()


def entry(tag, sha, digest=DIGEST):
    return f"2026-10-26 Y release {tag} at {sha} (archive {digest})"


class World(unittest.TestCase):
    """A scratch world and the shim; `self.work` is the checkout of main the verb runs in."""

    def setUp(self):
        self.top = SCRATCH.mkdtemp()
        bin_, self.log, self.releases = self.top / "bin", self.top / "gh.log", self.top / "releases"
        bin_.mkdir(); (bin_ / "gh").write_text(GH_SHIM); (bin_ / "gh").chmod(0o755)
        self.out_file = self.top / "github_output"
        e = unittest.mock.patch.dict(os.environ, {
            "DYAD_INSTANCE": INST, "PATH": f"{bin_}{os.pathsep}{os.environ.get('PATH', '')}", "GH_LOG": str(self.log),
            "GH_RELEASES": str(self.releases), "GITHUB_REPOSITORY": REPO, "GITHUB_OUTPUT": str(self.out_file)})
        e.start(); self.addCleanup(e.stop)
        for k in ("BEFORE", "ONLY", "GATE", "GITHUB_STEP_SUMMARY"):
            os.environ.pop(k, None)
        self.rel = release()

    def make_world(self, version="0.1.0", bundle="0.2.0"):
        seed = self.top / "seed"; seed.mkdir()
        git(seed, "init", "-q", "-b", "main")
        (seed / "dyad").mkdir(); (seed / "dyad" / "VERSION").write_text(version + "\n")
        (seed / "BUNDLE.md").write_text(f"# Bundle\n\nversion: {bundle}\n")
        self.write_row(seed, 1, "2026-10-01 Y plan")
        git(seed, "add", "-A"); git(seed, *livetest.IDENTITY, "commit", "-qm", "cut")
        self.cut = git(seed, "rev-parse", "HEAD")
        self.origin, self.work = self.top / "origin.git", self.top / "work"
        git(self.top, "clone", "-q", "--bare", str(seed), str(self.origin))
        git(self.top, "clone", "-q", str(self.origin), str(self.work))
        for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
            git(self.work, "config", k, v)

    def write_row(self, d, rid, disposed):
        rows = Path(d) / INST / "d-work" / "rows"; rows.mkdir(parents=True, exist_ok=True)
        (rows / f"{rid}.md").write_text(ROW.format(id=rid, disposed=disposed))

    def record(self, *entries, rid=1):
        """The row's disposed entries, committed on main as the cos's ledger commit would be; returns the new head."""
        self.write_row(self.work, rid, "; ".join(("2026-10-01 Y plan",) + entries))
        git(self.work, "add", "-A"); git(self.work, "commit", "-qm", f"ledger: #{rid}")
        return git(self.work, "rev-parse", "HEAD")

    def run_verb(self, *a):
        o = io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(io.StringIO()):
            rc = self.rel.main(list(a), self.work)
        return rc, o.getvalue()

    def outcomes(self, out):
        return [json.loads(l) for l in out.splitlines() if l.startswith("{")]

    def gh_calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []

    def tags(self, d=None):
        return git(d or self.work, "tag", "--list").split()


class EntryTests(World):
    def test_a_good_entry_is_read(self):
        self.assertEqual(self.rel.parse_entry(entry("dyad-operator-v0.1.0", "abc1234")), ("dyad-operator-v0.1.0", "abc1234", DIGEST))

    def test_a_release_without_at_and_other_dispositions_are_not_read(self):
        self.assertIsNone(self.rel.parse_entry("2026-09-01 Y release v0.3.0"))   # predates the service
        self.assertIsNone(self.rel.parse_entry("2026-10-01 Y plan"))
        self.assertIsNone(self.rel.parse_entry(""))

    def test_a_malformed_entry_comes_back_empty_and_is_refused(self):
        self.assertEqual(self.rel.parse_entry("2026-10-26 Y release v0.2.0 at nothex (archive 12)"), ("v0.2.0", "", ""))
        self.make_world()
        self.record("2026-09-01 Y release v0.1.9", "2026-10-26 Y release v0.2.0 at nothex (archive 12)")
        rc, out = self.run_verb()
        self.assertEqual(rc, 1)
        [o] = self.outcomes(out)
        self.assertEqual((o["tag"], o["outcome"]), ("v0.2.0", "refused"))
        self.assertIn("1 release entries", out)
        self.assertEqual(self.gh_calls(), [])


class ScanTests(World):
    def test_nothing_pending(self):
        self.make_world()
        rc, out = self.run_verb("--scan")
        self.assertEqual((rc, out), (0, "pending: none\n"))
        self.assertEqual(self.out_file.read_text(), "pending=false\n")
        self.assertEqual(self.gh_calls(), [])

    def test_one_pending_and_nothing_written(self):
        self.make_world()
        self.record(entry("dyad-operator-v0.1.0", self.cut[:7]))
        head = git(self.work, "rev-parse", "HEAD")
        rc, out = self.run_verb("--scan")
        self.assertEqual((rc, out), (0, "pending: dyad-operator-v0.1.0\n"))
        self.assertEqual(self.out_file.read_text(), "pending=true\n")
        self.assertEqual((self.tags(), git(self.work, "status", "--porcelain"), git(self.work, "rev-parse", "HEAD")), ([], "", head))

    def test_the_push_filter_reads_only_the_entries_before_lacks(self):
        self.make_world()
        before = self.record(entry("v0.2.0", self.cut))
        self.record(entry("v0.2.0", self.cut), entry("dyad-operator-v0.1.0", self.cut))
        os.environ["BEFORE"] = before
        self.assertEqual(self.run_verb("--scan"), (0, "pending: dyad-operator-v0.1.0\n"))
        os.environ["BEFORE"] = "0" * 40   # a dispatch: every entry
        self.assertEqual(self.run_verb("--scan"), (0, "pending: v0.2.0 dyad-operator-v0.1.0\n"))

    def test_bad_arguments(self):
        self.make_world()
        self.assertEqual(self.run_verb("--publish")[0], 2)

    def test_entries_without_a_repository_are_refused_not_reported_pending(self):
        """#470: with GITHUB_REPOSITORY unset (a hand run) the Release lookup cannot answer, so the verb refuses
        rather than report every recorded release as pending; a store with no entry still scans green."""
        self.make_world()
        os.environ.pop("GITHUB_REPOSITORY", None)
        self.assertEqual(self.run_verb("--scan"), (0, "pending: none\n"))   # no entry: nothing to look up
        self.record(entry("dyad-operator-v0.1.0", self.cut[:7]))
        self.assertEqual(self.run_verb("--scan")[0], 2)
        self.assertEqual(self.run_verb()[0], 2)
        self.assertEqual(self.gh_calls(), [])


class PublishTests(World):
    def test_a_cut_not_on_main_is_refused(self):
        self.make_world()
        git(self.work, "checkout", "-q", "-b", "side")
        (self.work / "x").write_text("x"); git(self.work, "add", "x"); git(self.work, "commit", "-qm", "side")
        side = git(self.work, "rev-parse", "HEAD"); git(self.work, "checkout", "-q", "main")
        self.record(entry("dyad-operator-v0.1.0", side))
        rc, out = self.run_verb()
        [o] = self.outcomes(out)
        self.assertEqual((rc, o["outcome"]), (1, "refused"))
        self.assertIn("is not a commit on main", o["detail"])

    def test_a_tag_other_than_version_at_the_cut_is_refused(self):
        self.make_world()
        self.record(entry("dyad-operator-v0.9.9", self.cut), entry("v0.9.9", self.cut))
        rc, out = self.run_verb()
        core, bundle = self.outcomes(out)
        self.assertEqual(rc, 1)
        self.assertEqual((core["outcome"], bundle["outcome"]), ("refused", "refused"))
        self.assertIn("!= dyad-operator-v0.1.0", core["detail"]); self.assertIn("!= v0.2.0", bundle["detail"])
        self.assertEqual(self.tags(), [])
        self.assertEqual(len(git(self.work, "worktree", "list").splitlines()), 1, "the build worktree is removed")

    def test_a_tag_at_the_cut_with_its_release_is_skipped(self):
        self.make_world()
        git(self.work, "tag", "-a", "dyad-operator-v0.1.0", self.cut, "-m", "t")
        self.releases.write_text("dyad-operator-v0.1.0\n")
        self.record(entry("dyad-operator-v0.1.0", self.cut))
        self.assertEqual(self.run_verb("--scan"), (0, "pending: none\n"))
        rc, out = self.run_verb()
        [o] = self.outcomes(out)
        self.assertEqual((rc, o["outcome"]), (0, "already"))
        self.assertFalse([c for c in self.gh_calls() if c.startswith("release create")])

    def test_a_tag_elsewhere_is_refused(self):
        self.make_world()
        head = self.record(entry("dyad-operator-v0.1.0", self.cut))
        git(self.work, "tag", "-a", "dyad-operator-v0.1.0", head, "-m", "t")
        rc, out = self.run_verb()
        [o] = self.outcomes(out)
        self.assertEqual((rc, o["outcome"]), (1, "refused"))
        self.assertIn("tags never move", o["detail"])

    def test_a_digest_other_than_recorded_is_refused_and_nothing_tagged(self):
        self.make_world()
        self.record(entry("dyad-operator-v0.1.0", self.cut))
        def stub(ctx, tag, sha, tmp):   # the build stubbed: an archive whose digest is not DIGEST
            (tmp / "out").mkdir(); a = tmp / "out" / "dyad-0.1.0.tar.gz"; a.write_bytes(b"other")
            return "core", hashlib.sha256(b"other").hexdigest(), [str(a)]
        with unittest.mock.patch.object(self.rel, "build", stub):
            rc, out = self.run_verb()
        [o] = self.outcomes(out)
        self.assertEqual((rc, o["outcome"]), (1, "refused"))
        self.assertIn(f"!= recorded {DIGEST}", o["detail"])
        self.assertEqual((self.tags(), self.tags(self.origin)), ([], []))

    def test_a_dispatch_naming_no_entry_fails(self):
        self.make_world()
        os.environ["ONLY"] = "v9.9.9"
        rc, out = self.run_verb()
        self.assertEqual(rc, 1); self.assertIn("no release entry names v9.9.9", out)


class InstallTests(World):
    """Over a real core install: the cut's own builder, end to end; and the entrypoint's `--scan` (plan #469)."""

    def test_an_entry_is_published_end_to_end_then_already(self):
        self.work = SCRATCH.copy(False)
        cut, ver = git(self.work, "rev-parse", "HEAD"), (self.work / "dyad" / "VERSION").read_text().strip()
        probe = self.top / "probe.tar.gz"
        r = subprocess.run([sys.executable, str(self.work / "dyad" / "scripts" / "package.py"), "build", str(probe)],
                           cwd=self.work, capture_output=True, text=True, env=dyadlib.git_env())
        self.assertEqual(r.returncode, 0, r.stderr)
        digest = hashlib.sha256(probe.read_bytes()).hexdigest()
        self.origin = self.top / "origin.git"
        git(self.top, "clone", "-q", "--bare", str(self.work), str(self.origin))
        git(self.work, "remote", "add", "origin", str(self.origin))
        for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
            git(self.work, "config", k, v)
        tag = f"dyad-operator-v{ver}"
        self.record(entry(tag, cut, digest), rid=1)
        rc, out = self.run_verb()
        [o] = self.outcomes(out)
        self.assertEqual((rc, o["outcome"]), (0, "released"), out)
        self.assertEqual(git(self.origin, "rev-parse", f"{tag}^{{commit}}"), cut, "the annotated tag pushed, at the cut")
        [create] = [c for c in self.gh_calls() if c.startswith("release create")]
        self.assertIn(f"dyad-{ver}.tar.gz", create); self.assertIn(f"{tag}.release.json", create)
        self.assertIn(f"--repo {REPO} --verify-tag", create)
        self.assertEqual(git(self.work, "status", "--porcelain"), "")
        self.assertEqual(len(git(self.work, "worktree", "list").splitlines()), 1)
        rc, out = self.run_verb()
        self.assertEqual((rc, self.outcomes(out)[0]["outcome"]), (0, "already"))

    def test_scan_in_a_fresh_install_is_green(self):
        d = SCRATCH.copy(False)
        env = {k: v for k, v in dyadlib.git_env().items() if k not in ("BEFORE", "ONLY", "DYAD_INSTANCE")}
        r = subprocess.run([str(d / "dyad" / "bin" / "dyad"), "release", "--scan"], cwd=d, capture_output=True,
                           text=True, env=env)
        self.assertEqual((r.returncode, r.stdout), (0, "pending: none\n"), r.stderr)
        self.assertEqual(self.out_file.read_text(), "pending=false\n")
        self.assertEqual(self.gh_calls(), [])


if __name__ == "__main__":
    unittest.main()
