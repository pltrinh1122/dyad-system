"""channels.py (the channels craft's verbs; d-work #682): the sender, the monitor slot (session-start always due, an
interval due once it passes, doubling after an empty read up to its ceiling and resetting on news), `read` printing
only what is new and keeping its marker under the git common dir, `post` refusing a draft the guard fails and writing
a passing one on its own branch of the clone without pushing, an existing id refused, `breach` naming only other
systems' findings, and the usage errors."""
import datetime as dt, io, json, os, shutil, subprocess, sys, tempfile, unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))
import dyadlib
CRAFT = Path(__file__).resolve().parents[1]
ch = dyadlib.load_module(CRAFT / "scripts" / "channels.py", "channels_script")
_tp = dyadlib.load_module(CRAFT / "tests" / "guards" / "test_posts.py", "channels_test_posts")
CHANNEL, MEMBER, message = _tp.CHANNEL, _tp.MEMBER, _tp.message
AT = dt.datetime(2026, 11, 11, 12, 0, tzinfo=dt.timezone.utc)
GIT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

def run(f, *a, **kw):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = f(*a, **kw)
    return rc, out.getvalue() + err.getvalue()

class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root, self.base = self.tmp / "up", self.tmp / "clone"
        (self.root / "agent-corpus").mkdir(parents=True)
        (self.base / "registry" / "channels").mkdir(parents=True); (self.base / "registry" / "members").mkdir()
        (self.base / "registry" / "channels" / "release.md").write_text(CHANNEL)
        for s in ("up", "down"):
            (self.base / "registry" / "members" / f"{s}.md").write_text(MEMBER.format(s=s))
        env = {k: v for k, v in os.environ.items() if k not in ("DYAD_INSTANCE",)}
        p = mock.patch.dict(os.environ, {**env, **GIT, "DYAD_CHANNELS": str(self.base), "DYAD_SYSTEM": "up",
                                          "DYAD_SESSION": "home"}, clear=True)
        p.start(); self.addCleanup(p.stop)
        for d in (self.root, self.base):
            subprocess.run(["git", "init", "-q", "-b", "main", str(d)], check=True)
        subprocess.run(["git", "-C", str(self.base), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.base), "commit", "-q", "-m", "seed"], check=True)

    def put(self, text, system="up", mid="m1"):
        d = self.base / "channels" / "release" / system; d.mkdir(parents=True, exist_ok=True)
        (d / f"{mid}.md").write_text(text)

class Sender(Fixture):
    def test_sender_is_system_and_unit(self):
        self.assertEqual(ch.sender(self.root), "up:home")
        os.environ.pop("DYAD_SYSTEM")
        self.assertEqual(ch.sender(self.root), "up:home")       # the checkout's directory name

class Monitor(unittest.TestCase):
    def test_session_start_always_due(self):
        self.assertTrue(ch.due({"monitor": "session-start"}, {"last": AT.isoformat()}, AT))
        self.assertIsNone(ch.next_interval({"monitor": "session-start"}, {}, False))

    def test_interval_backs_off_and_resets(self):
        c = {"monitor": "interval 2-8"}
        self.assertTrue(ch.due(c, {}, AT))
        mark = {"last": AT.isoformat(), "interval": 2}
        self.assertFalse(ch.due(c, mark, AT + dt.timedelta(minutes=1)))
        self.assertTrue(ch.due(c, mark, AT + dt.timedelta(minutes=2)))
        self.assertEqual(ch.next_interval(c, mark, False), 4)
        self.assertEqual(ch.next_interval(c, {"interval": 8}, False), 8)
        self.assertEqual(ch.next_interval(c, {"interval": 8}, True), 2)

class Read(Fixture):
    def test_read_prints_new_once_and_marks_outside_trees(self):
        self.put(message(body="Tag one."))
        rc, out = run(ch.cmd_read, self.root, [], at=AT)
        self.assertEqual(rc, 0); self.assertIn("Tag one.", out); self.assertIn("1 new message(s)", out)
        rc, out = run(ch.cmd_read, self.root, [], at=AT)
        self.assertNotIn("Tag one.", out); self.assertIn("0 new message(s)", out)
        mp = ch.marker_path(self.root)
        self.assertTrue(mp.is_file()); self.assertIn(".git", mp.parts)
        self.assertIn("channels/release/up/m1.md", json.loads(mp.read_text())["release"]["seen"])

    def test_read_skips_a_channel_not_due(self):
        (self.base / "registry" / "channels" / "release.md").write_text(CHANNEL.replace("session-start", "interval 5-10"))
        run(ch.cmd_read, self.root, [], at=AT)
        rc, out = run(ch.cmd_read, self.root, [], at=AT + dt.timedelta(minutes=1))
        self.assertIn("skip release", out)

    def test_read_without_checkout_skips(self):
        os.environ["DYAD_CHANNELS"] = str(self.tmp / "none")
        rc, out = run(ch.cmd_read, self.root, [])
        self.assertEqual(rc, 0); self.assertIn("warning: skip read", out)

class Post(Fixture):
    def body(self, text):
        p = self.tmp / "body.txt"; p.write_text(text); return str(p)

    def test_post_writes_on_branch_and_pushes_nothing(self):
        rc, out = run(ch.cmd_post, self.root, ["release", "fact", "v1", self.body("Tag v1 is out."), "refs=abc"], at=AT)
        self.assertEqual(rc, 0, out); self.assertIn("nothing pushed", out); self.assertIn("from: up:home", out)
        branch = subprocess.run(["git", "-C", str(self.base), "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
        self.assertEqual(branch, "post/v1")
        self.assertIn("refs: abc", (self.base / "channels" / "release" / "up" / "v1.md").read_text())

    def test_post_refused_by_fence_writes_nothing(self):
        rc, out = run(ch.cmd_post, self.root, ["release", "fact", "v2", self.body("Y/N: release it?")], at=AT)
        self.assertEqual(rc, 1); self.assertIn("refused: nothing written", out)
        self.assertFalse((self.base / "channels" / "release" / "up" / "v2.md").exists())

    def test_post_refuses_unknown_kind_and_existing_id(self):
        rc, out = run(ch.cmd_post, self.root, ["release", "order", "v3", self.body("x")], at=AT)
        self.assertEqual(rc, 1); self.assertIn("kind 'order'", out)
        self.put(message(mid="v4"), mid="v4")
        rc, out = run(ch.cmd_post, self.root, ["release", "fact", "v4", self.body("x")], at=AT)
        self.assertEqual(rc, 1); self.assertIn("never edited", out)

class Breach(Fixture):
    def test_breach_names_other_systems_only(self):
        self.put(message(mid="d1", sender="down:home", body="Y/N: do it?"), system="down", mid="d1")
        self.put(message(mid="u1", body="Y/N: mine?"), mid="u1")
        rc, out = run(ch.cmd_breach, self.root, [])
        self.assertEqual(rc, 0); self.assertIn("channels/release/down/d1.md", out)
        self.assertNotIn("up/u1.md", out); self.assertIn("1 finding(s)", out)

class Usage(Fixture):
    def test_usage_errors(self):
        self.assertEqual(run(ch.main, [])[0], 2)
        self.assertEqual(run(ch.cmd_post, self.root, ["release"])[0], 2)
        self.assertEqual(run(ch.cmd_read, self.root, ["x"])[0], 2)
        self.assertEqual(run(ch.cmd_subscribe, self.root, [])[0], 2)

if __name__ == "__main__":
    unittest.main()
