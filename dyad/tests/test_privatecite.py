"""Private-citation fence tests (dyad/scripts/privatecite.py, d-work #518): remote normalization (https, ssh, scp, `.git`,
credentials, case); the lists (absent -> one skip line, a malformed hash -> fail-closed, comments carry nothing); the
shapes (each citation form; fenced, blockquote and long-quote bodies; `NEAR`); and `check_push` over a scratch git repo
pushing to a bare remote: public + private citation + fenced body refused, the same without a body passing, a citation to
an undeclared repo passing, a non-public remote passing, an unknown URL and an unreadable commit refused, a quoted body in
the commit message refused, and only commits the remote lacks judged. Fixture repo names only (`acme/secret`); no real
private name appears here, plain or hashed."""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / "scripts"))
import privatecite as pc

SECRET, OPEN = "acme/secret", "acme/open"
FENCED = "```\nthe private text, quoted\n```\n"

def git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True).stdout.strip()

class NormalizeTests(unittest.TestCase):
    def test_forms_agree(self):
        want = "github.com/acme/site"
        for u in ("https://github.com/acme/site", "https://github.com/acme/site.git", "https://github.com/acme/site/",
                  "http://user:tok@GitHub.com/Acme/Site.git", "ssh://git@github.com/acme/site.git",
                  "git@github.com:acme/site.git", "github.com/acme/site"):
            with self.subTest(u=u):
                self.assertEqual(pc.normalize_remote(u), want)
    def test_local_path_kept(self):
        self.assertEqual(pc.normalize_remote("/tmp/x/remote.git/"), "/tmp/x/remote")
    def test_other_repo_differs(self):
        self.assertNotEqual(pc.normalize_remote("git@github.com:acme/site-scratch"), "github.com/acme/site")
    def test_hash_is_lowercased(self):
        self.assertEqual(pc.repo_hash("ACME/Secret.git"), pc.repo_hash(SECRET))

class ShapeTests(unittest.TestCase):
    P = {pc.repo_hash(SECRET)}
    def lines(self, text, start=1):
        return list(enumerate(text.splitlines(), start))
    def test_each_citation_form_beside_a_fence(self):
        sha = "a" * 40
        for cite in (f"repo:{SECRET}@{sha}:docs/x.md", f"commit:{SECRET}@{sha}", f"repo: {SECRET}",
                     f"see {SECRET}@abc1234", f"https://github.com/{SECRET}/blob/main/x", f"git@github.com:{SECRET}.git"):
            with self.subTest(cite=cite):
                self.assertTrue(pc.findings(self.lines(cite + "\n" + FENCED), self.P))
    def test_no_quoted_body_passes(self):
        self.assertEqual(pc.findings(self.lines(f"[^1]: repo:{SECRET}@{'a' * 40}:x.md\nplain prose\n"), self.P), [])
    def test_bare_mention_is_no_citation(self):
        self.assertEqual(pc.findings(self.lines(f"the {SECRET} repo\n" + FENCED), self.P), [])
    def test_longer_name_is_not_the_private_one(self):
        self.assertEqual(pc.findings(self.lines(f"https://github.com/{SECRET}-two\n" + FENCED), self.P), [])
    def test_blockquote_and_long_quote_are_bodies(self):
        self.assertTrue(pc.findings(self.lines(f"repo: {SECRET}\n> they wrote this\n"), self.P))
        long = '"' + "x" * pc.LONG_QUOTE + '"'
        self.assertTrue(pc.findings(self.lines(f"repo: {SECRET} {long}\n"), self.P))
        short = '"' + "x" * (pc.LONG_QUOTE - 1) + '"'
        self.assertEqual(pc.findings(self.lines(f"repo: {SECRET} {short}\n"), self.P), [])
    def test_near_bounds_beside(self):
        far = f"repo: {SECRET}\n" + "prose\n" * pc.NEAR + "> quoted\n"
        self.assertEqual(pc.findings(self.lines(far), self.P), [])
        near = f"repo: {SECRET}\n" + "prose\n" * (pc.NEAR - 1) + "> quoted\n"
        self.assertTrue(pc.findings(self.lines(near), self.P))
    def test_fence_state_resets_at_a_gap(self):
        added = [(1, "```"), (2, "body"), (40, f"repo: {SECRET}")]
        self.assertEqual(pc.quoted_lines(added), {1, 2})
        self.assertEqual(pc.findings(added, self.P), [])
    def test_parse_diff_numbers_added_lines(self):
        diff = "+++ b/a.md\n@@ -0,0 +5,2 @@\n+one\n+two\n+++ /dev/null\n@@ -1 +0,0 @@\n-gone\n"
        self.assertEqual(pc.parse_diff(diff), {"a.md": [(5, "one"), (6, "two")]})

class PushTests(unittest.TestCase):
    """A scratch repo with a bare remote; `check_push` called as the pre-push path calls it."""
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.bare = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.d, True); self.addCleanup(shutil.rmtree, self.bare, True)
        git(self.bare, "init", "-q", "--bare")
        git(self.d, "init", "-q", "-b", "main"); git(self.d, "remote", "add", "origin", str(self.bare))
        self.commit("README.md", "# r\n", "root")
        git(self.d, "push", "-q", "origin", "main")
        self.inst = self.d / "agent-corpus"; self.inst.mkdir()
        self.env = mock.patch.dict(os.environ, {"DYAD_INSTANCE": str(self.inst)}); self.env.start(); self.addCleanup(self.env.stop)
    def commit(self, path, text, msg="c"):
        (self.d / path).write_text(text)
        git(self.d, "add", path); git(self.d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", msg)
        return git(self.d, "rev-parse", "HEAD")
    def lists(self, public=None, private=(SECRET,)):
        (self.inst / pc.PUBLIC).write_text("# public\n" + (public or f"{self.bare}.git/") + "\n")
        (self.inst / pc.PRIVATE).write_text("# hashes\n" + "".join(pc.repo_hash(r) + "\n" for r in private))
    def push(self, sha, url=None):
        lines = [f"refs/heads/main {sha} refs/heads/main {git(self.d, 'rev-parse', 'origin/main')}"]
        return pc.check_push(self.d, "origin", str(self.bare) if url is None else url, lines)
    def test_refused_with_fenced_body(self):
        self.lists(); sha = self.commit("ep.md", f"[^1]: repo:{SECRET}@{'b' * 40}:notes.md\n\n" + FENCED)
        refusals, _ = self.push(sha)
        self.assertTrue(any("ep.md:1 cites a private repo" in r for r in refusals), refusals)
        self.assertNotIn(SECRET, "\n".join(refusals))                   # the hash prefix is named, never the repo
        self.assertIn("there is no override", refusals[-1])
    def test_provenance_record_warns_and_is_not_refused(self):
        # plan #520 revision 2, option (d): the Operator's own words land verbatim (Rule-7); the fence names them
        prov = self.inst / "d-work" / "provenance"; prov.mkdir(parents=True)
        rel = prov.relative_to(self.d).as_posix()
        self.lists(); sha = self.commit(f"{rel}/9.md", f"## 1 prompt 2026-10-28\n\n```\nsee https://github.com/{SECRET}\n```\n")
        refusals, info = self.push(sha)
        self.assertEqual(refusals, [])
        self.assertTrue(any(l.startswith("warn [private-cite]") and f"{rel}/9.md:" in l for l in info), info)
        self.assertNotIn(SECRET, "\n".join(info))
    def test_provenance_exemption_does_not_cover_other_files(self):
        prov = self.inst / "d-work" / "provenance"; prov.mkdir(parents=True)
        self.lists(); sha = self.commit("prov-like.md",
                                        f"```\nsee https://github.com/{SECRET}\n```\n")
        refusals, _ = self.push(sha)
        self.assertTrue(refusals)
    def test_passes_without_quoted_body(self):
        self.lists(); sha = self.commit("ep.md", f"[^1]: repo:{SECRET}@{'b' * 40}:notes.md\n")
        refusals, info = self.push(sha)
        self.assertEqual(refusals, []); self.assertIn("ok   [private-cite] 1 commit(s)", info[0])
    def test_passes_citing_a_repo_not_private(self):
        self.lists(); sha = self.commit("ep.md", f"repo:{OPEN}@{'b' * 40}:x.md\n" + FENCED)
        self.assertEqual(self.push(sha)[0], [])
    def test_passes_to_a_remote_not_public(self):
        self.lists(public="github.com/acme/site"); sha = self.commit("ep.md", f"repo: {SECRET}\n" + FENCED)
        refusals, info = self.push(sha)
        self.assertEqual(refusals, []); self.assertIn("is not a declared public remote", info[0])
    def test_ssh_form_of_a_public_url_is_judged(self):
        self.lists(public="https://github.com/acme/site.git"); sha = self.commit("ep.md", f"repo: {SECRET}\n" + FENCED)
        self.assertTrue(self.push(sha, url="git@github.com:acme/site")[0])
    def test_message_is_scanned(self):
        self.lists(); sha = self.commit("ep.md", "plain\n", msg=f"cite repo: {SECRET}\n\n> their words\n")
        self.assertTrue(any(pc.MESSAGE in r for r in self.push(sha)[0]))
    def test_no_lists_skips_once(self):
        sha = self.commit("ep.md", f"repo: {SECRET}\n" + FENCED)
        refusals, info = self.push(sha)
        self.assertEqual(refusals, []); self.assertEqual(len(info), 1); self.assertTrue(info[0].startswith("skip [private-cite]"))
    def test_malformed_hash_fails_closed(self):
        self.lists(); (self.inst / pc.PRIVATE).write_text(SECRET + "\n")
        refusals, _ = self.push(self.commit("ep.md", "x\n"))
        self.assertTrue(refusals and "fail-closed" in refusals[0])
    def test_unknown_url_fails_closed(self):
        self.lists(); sha = self.commit("ep.md", "x\n")
        self.assertIn("fail-closed", self.push(sha, url="")[0][0])
    def test_unreadable_commit_fails_closed(self):
        self.lists(); sha = self.commit("ep.md", "x\n")
        with mock.patch.object(pc, "leaving", return_value=(["f" * 40], [])):
            refusals, _ = self.push(sha)
        self.assertTrue(any("git cannot read commit" in r and "fail-closed" in r for r in refusals), refusals)
    def test_only_commits_the_remote_lacks(self):
        self.lists(public="github.com/acme/elsewhere")
        old = self.commit("old.md", f"repo: {SECRET}\n" + FENCED); git(self.d, "push", "-q", "origin", "main")
        self.lists(); new = self.commit("new.md", "x\n")
        self.assertEqual(pc.leaving(self.d, [f"refs/heads/main {new} refs/heads/main {old}"], "origin")[0], [new])
        self.assertEqual(self.push(new)[0], [])

if __name__ == "__main__":
    unittest.main()
