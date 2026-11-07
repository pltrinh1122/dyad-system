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

    def test_only_the_bundle_takes_latest(self):
        """#465: a core or craft Release is created `--latest=false`; a bundle keeps gh's default, so it stays Latest."""
        self.make_world()
        tags = {"dyad-operator-v0.1.0": "core", "sysadmin-v0.3.0": "craft", "v0.2.0": "bundle"}
        self.record(*(entry(t, self.cut) for t in tags))
        def stub(ctx, tag, sha, tmp):   # the build stubbed: each kind's archive, its digest the recorded one
            (tmp / "out").mkdir(); a = tmp / "out" / f"{tag}.tar.gz"; a.write_bytes(b"x")
            return tags[tag], DIGEST, [str(a)]
        with unittest.mock.patch.object(self.rel, "build", stub):
            rc, out = self.run_verb()
        self.assertEqual((rc, [o["outcome"] for o in self.outcomes(out)]), (0, ["released"] * 3), out)
        creates = {c.split()[2]: c.split() for c in self.gh_calls() if c.startswith("release create")}
        self.assertEqual(set(creates), set(tags))
        for t in ("dyad-operator-v0.1.0", "sysadmin-v0.3.0"):
            self.assertIn("--latest=false", creates[t], t)
        self.assertFalse([a for a in creates["v0.2.0"] if a.startswith("--latest")], creates["v0.2.0"])

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


def ready_line(tag, sha, digest=DIGEST):
    return f"2026-11-01 release-ready {tag} at {sha} (archive {digest})"


class GateTests(World):
    """#545: under RELEASE_APPROVAL=tap the service reads the Agent's `release-ready` lines only; with the gate off it
    reads the recorded `Y release` as before."""
    def test_each_gate_reads_its_own_kind(self):
        sha = "a" * 40
        y, r = entry("dyad-operator-v0.1.0", sha), ready_line("dyad-operator-v0.1.0", sha)
        self.assertEqual(self.rel.parse_entry(y), ("dyad-operator-v0.1.0", sha, DIGEST))
        self.assertIsNone(self.rel.parse_entry(r))
        self.assertEqual(self.rel.parse_entry(r, "tap"), ("dyad-operator-v0.1.0", sha, DIGEST))
        self.assertIsNone(self.rel.parse_entry(y, "tap"))
        self.assertEqual(self.rel.parse_entry("2026-11-01 release-ready v0.2.0 at abc", "tap"), ("v0.2.0", "", ""))

    def test_scan_under_tap_sees_a_ready_line_and_not_a_y_release(self):
        self.make_world()
        self.record(entry("dyad-operator-v0.1.0", self.cut))
        os.environ["GATE"] = "tap"
        self.assertEqual(self.run_verb("--scan"), (0, "pending: none\n"))
        self.record(entry("dyad-operator-v0.1.0", self.cut), ready_line("dyad-operator-v0.1.0", self.cut))
        self.assertEqual(self.run_verb("--scan"), (0, "pending: dyad-operator-v0.1.0\n"))
        os.environ["GATE"] = "ledger"
        self.assertEqual(self.run_verb("--scan"), (0, "pending: dyad-operator-v0.1.0\n"))   # the Y release, read as before

    def test_an_unknown_gate_is_refused(self):
        self.make_world()
        os.environ["GATE"] = "maybe"
        with self.assertRaises(SystemExit):
            self.rel.context(self.work)


class ReadyTests(World):
    """#545: `dyad release ready` writes the release-ready line only after C2's fence: every root the tag carries is,
    at the cut, the tree it holds at a head the row's operative Done-`Y` names, and the archive built at the cut has the
    given sha256. The build is stubbed (a worktree at the cut and a fixed digest); the fence and the write are real."""
    def setUp(self):
        super().setUp()
        self.make_world()
        git(self.work, "checkout", "-q", "-b", "pr")
        (self.work / "dyad" / "x.py").write_text("x\n"); git(self.work, "add", "-A"); git(self.work, "commit", "-qm", "pr")
        self.head = git(self.work, "rev-parse", "HEAD")
        git(self.work, "checkout", "-q", "main")
        self.done = f"2026-11-01 Y done (merges PR #9 at {self.head}, releases dyad-operator-v0.1.0, v0.2.0)"
        self.record(self.done)
        git(self.work, "merge", "-q", "--no-ff", "-m", "merge", self.head)
        self.cut_sha = git(self.work, "rev-parse", "HEAD")
        rel = self.rel
        def stub_build(ctx, tag, sha, tmp):
            (tmp / "out").mkdir(exist_ok=True)
            git(ctx.root, "worktree", "add", "-q", "--detach", str(tmp / "tree"), sha)
            return "core", DIGEST, []
        p = unittest.mock.patch.object(rel, "build", stub_build); p.start(); self.addCleanup(p.stop)

    def run_ready(self, *a):
        o, e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            rc = self.rel.main(["ready", *a], self.work)
        return rc, o.getvalue(), e.getvalue()

    def row(self):
        return (self.work / INST / "d-work" / "rows" / "1.md").read_text()

    def test_the_fence_passes_and_the_line_is_written_once(self):
        rc, out, err = self.run_ready("1", "dyad-operator-v0.1.0", "--at", self.cut_sha, "--archive", DIGEST)
        self.assertEqual(rc, 0, err)
        self.assertIn(f"release-ready dyad-operator-v0.1.0 at {self.cut_sha} (archive {DIGEST})", self.row())
        rows = dyadlib.load_guard("agent", "rows")
        self.assertTrue(rows.operative_done(dyadlib.parse_row_file(self.row()).disposed))   # the Y done stays operative
        rc, out, _ = self.run_ready("1", "dyad-operator-v0.1.0", "--at", self.cut_sha, "--archive", DIGEST)
        self.assertEqual(rc, 0); self.assertTrue(out.startswith("already:"), out)
        self.assertEqual(self.row().count("release-ready"), 1)

    def test_the_line_keeps_the_rows_slug(self):
        """#622: `ready` rebuilds the row with every field, so a row slug survives the release-ready line."""
        p = self.work / INST / "d-work" / "rows" / "1.md"; p.write_text(p.read_text() + "slug: release-1.1.0\n")
        git(self.work, "commit", "-qam", "slug")
        rc, _, err = self.run_ready("1", "dyad-operator-v0.1.0", "--at", self.cut_sha, "--archive", DIGEST)
        self.assertEqual(rc, 0, err)
        self.assertEqual(dyadlib.parse_row_file(self.row()).slug, "release-1.1.0"); self.assertIn("release-ready", self.row())

    def test_the_line_carries_the_utc_date(self):
        # #592 R-b: the release-ready entry is dated UTC's day, whatever the host's local one
        with livetest.off_utc() as (utc, local):
            self.assertNotEqual(utc, local)
            rc, _, err = self.run_ready("1", "dyad-operator-v0.1.0", "--at", self.cut_sha, "--archive", DIGEST)
        self.assertEqual(rc, 0, err)
        self.assertIn(f"; {utc} release-ready dyad-operator-v0.1.0 at {self.cut_sha}", self.row())
        self.assertNotIn(f"{local} release-ready", self.row())

    def test_a_root_changed_after_the_verified_head_is_refused(self):
        (self.work / "dyad" / "late.py").write_text("late\n"); git(self.work, "add", "-A"); git(self.work, "commit", "-qm", "late")
        cut = git(self.work, "rev-parse", "HEAD")
        rc, _, err = self.run_ready("1", "dyad-operator-v0.1.0", "--at", cut, "--archive", DIGEST)
        self.assertEqual(rc, 1); self.assertIn("C2's fence: dyad at the cut", err)
        self.assertNotIn("release-ready", self.row())

    def test_a_ledger_commit_after_the_head_does_not_trip_the_fence(self):
        self.record(self.done, "2026-11-01 Y plan (noise)")
        cut = git(self.work, "rev-parse", "HEAD")
        self.record(self.done)   # the Done entry last again
        self.assertEqual(self.run_ready("1", "dyad-operator-v0.1.0", "--at", cut, "--archive", DIGEST)[0], 0)

    def test_a_different_archive_digest_is_refused(self):
        rc, _, err = self.run_ready("1", "dyad-operator-v0.1.0", "--at", self.cut_sha, "--archive", "cd" * 32)
        self.assertEqual(rc, 1); self.assertIn(f"has sha256 {DIGEST}, not {'cd' * 32}", err)

    def test_no_operative_y_done_is_refused(self):
        self.record(self.done, "2026-11-01 N hold")
        rc, _, err = self.run_ready("1", "dyad-operator-v0.1.0", "--at", self.cut_sha, "--archive", DIGEST)
        self.assertEqual(rc, 1); self.assertIn("last disposition is no Y done", err)

    def test_a_tag_the_y_done_does_not_name_is_refused(self):
        """Rule-2 Binding: the Done question under the gate names its tags (`releases <tag>`); a tag it did not name is
        not ratified by it."""
        rc, _, err = self.run_ready("1", "sysadmin-v0.1.0", "--at", self.cut_sha, "--archive", DIGEST)
        self.assertEqual(rc, 1); self.assertIn("names no `releases … sysadmin-v0.1.0`", err)
        self.record(f"2026-11-01 Y done (merges PR #9 at {self.head})")       # no `releases` clause at all
        rc, _, err = self.run_ready("1", "dyad-operator-v0.1.0", "--at", self.cut_sha, "--archive", DIGEST)
        self.assertEqual(rc, 1); self.assertIn("names no `releases … dyad-operator-v0.1.0`", err)

    def test_a_short_cut_and_misuse(self):
        rc, _, err = self.run_ready("1", "dyad-operator-v0.1.0", "--at", self.cut_sha[:12], "--archive", DIGEST)
        self.assertEqual(rc, 1); self.assertIn("full sha", err)
        self.assertEqual(self.run_ready("1", "dyad-operator-v0.1.0")[0], 2)

    def test_roots_of_each_kind(self):
        tree = self.work
        (tree / "crafts" / "a").mkdir(parents=True); (tree / "crafts" / "a" / "VERSION").write_text("0.1.0\n")
        self.assertEqual(self.rel.roots_of("a-v0.1.0", tree), ["crafts/a"])
        self.assertEqual(self.rel.roots_of("dyad-operator-v0.1.0", tree), ["dyad"])          # crafts/a declares nothing
        self.assertEqual(self.rel.roots_of("v0.2.0", tree), ["BUNDLE.md", "dyad", "crafts/a"])


if __name__ == "__main__":
    unittest.main()
