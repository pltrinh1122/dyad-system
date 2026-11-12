"""channels.py (the channels craft's verbs; d-work #682): the sender, the monitor slot (session-start always due, an
interval due once it passes, doubling after an empty read up to its ceiling and resetting on news), `read` printing
only what is new and keeping its marker under the git common dir, `post` refusing a draft the guard fails and writing
a passing one on its own branch of the clone without pushing, an existing id refused, `breach` naming only other
systems' findings, and the usage errors; a whole message posted byte for byte (the v1.3.0 bytes, sha256 cf30bcb7),
refused when it names another id or system or carries extra fields, a bare body still wrapped, and the two
postconditions as commands (d-work #688)."""
import datetime as dt, hashlib, io, json, os, shutil, subprocess, sys, tempfile, unittest
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
        self.local = self.root / "agent-corpus" / "channels.local.txt"
        self.local.write_text(f"clone: {self.base}\nsystem: up\n")
        env = {k: v for k, v in os.environ.items() if k not in ("DYAD_INSTANCE",)}
        p = mock.patch.dict(os.environ, {**env, **GIT, "DYAD_SESSION": "home"}, clear=True)
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
        self.local.write_text(f"clone: {self.base}\n")
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
        self.local.write_text(f"clone: {self.tmp / 'none'}\n")
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

V130 = CRAFT / "tests" / "data" / "v1.3.0.md"     # the v1.3.0 post as approved: sha256 cf30bcb7 (d-work #688)
V130_SHA = "cf30bcb7256e13c7f6fb15b322d179863a1e2c017717bf31b9a77b2da09d1ae6"

class WholeMessage(Fixture):
    def setUp(self):
        super().setUp()
        (self.base / "registry" / "members" / "dyad-system.md").write_text(MEMBER.format(s="dyad-system"))
        self.local.write_text(f"clone: {self.base}\nsystem: dyad-system\n")
        subprocess.run(["git", "-C", str(self.base), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.base), "commit", "-q", "-m", "member"], check=True)

    def test_whole_message_is_kept_byte_for_byte(self):
        self.assertEqual(hashlib.sha256(V130.read_bytes()).hexdigest(), V130_SHA)
        rc, out = run(ch.cmd_post, self.root, ["release", "fact", "v1.3.0", str(V130)], at=AT)
        self.assertEqual(rc, 0, out)
        written = (self.base / "channels" / "release" / "dyad-system" / "v1.3.0.md").read_bytes()
        self.assertEqual(hashlib.sha256(written).hexdigest(), V130_SHA)
        self.assertEqual(written.count(b"format: dyad-channels/1"), 1)   # one header, never two
        self.assertEqual(ch.cmd_posted(self.root, ["release", "v1.3.0"]), 0)

    def test_whole_message_naming_another_id_is_refused(self):
        rc, out = run(ch.cmd_post, self.root, ["release", "fact", "v9", str(V130)], at=AT)
        self.assertEqual(rc, 1); self.assertIn("the message's id 'v1.3.0' is not the step's 'v9'", out)
        self.assertFalse((self.base / "channels" / "release" / "dyad-system" / "v9.md").exists())

    def test_whole_message_under_another_system_is_refused(self):
        self.local.write_text(f"clone: {self.base}\nsystem: up\n")
        rc, out = run(ch.cmd_post, self.root, ["release", "fact", "v1.3.0", str(V130)], at=AT)
        self.assertEqual(rc, 1); self.assertIn("is not this system's (up)", out)

    def test_whole_message_refuses_extra_fields(self):
        rc, out = run(ch.cmd_post, self.root, ["release", "fact", "v1.3.0", str(V130), "refs=x"], at=AT)
        self.assertEqual(rc, 1); self.assertIn("a whole message carries its own", out)

    def test_bare_body_is_still_wrapped(self):
        p = self.tmp / "bare.txt"; p.write_text("Tag v2 is out.\n")
        rc, out = run(ch.cmd_post, self.root, ["release", "fact", "v2", str(p)], at=AT)
        self.assertEqual(rc, 0, out)
        text = (self.base / "channels" / "release" / "dyad-system" / "v2.md").read_text()
        self.assertTrue(text.startswith("format: dyad-channels/1\nid: v2\n")); self.assertIn("\n\nTag v2 is out.\n", text)

class Postconditions(Fixture):
    def test_subscribed_passes_on_a_clone_of_the_url(self):
        url = "https://example.invalid/channels.git"
        subprocess.run(["git", "-C", str(self.base), "remote", "add", "origin", url], check=True)
        self.assertEqual(ch.cmd_subscribed(self.root, [url]), 0)
        self.assertEqual(ch.cmd_subscribed(self.root, ["https://example.invalid/channels/"]), 0)   # .git and / ignored
        self.assertEqual(ch.cmd_subscribed(self.root, ["https://example.invalid/other"]), 1)

    def test_subscribed_fails_without_a_clone_or_origin(self):
        self.assertEqual(ch.cmd_subscribed(self.root, ["https://example.invalid/channels"]), 1)   # no origin
        self.local.write_text(f"clone: {self.tmp / 'none'}\n")
        self.assertEqual(ch.cmd_subscribed(self.root, ["https://example.invalid/channels"]), 1)

    def test_posted_fails_before_the_post(self):
        self.assertEqual(ch.cmd_posted(self.root, ["release", "v1"]), 1)

    def test_runbook_postconditions_are_commands(self):
        rb = (CRAFT / "runbooks" / "channels.md").read_text()
        self.assertIn('postcondition: dyad/bin/dyad-python crafts/channels/scripts/channels.py subscribed "$URL"', rb)
        self.assertIn('postcondition: dyad/bin/dyad-python crafts/channels/scripts/channels.py posted "$CHANNEL" "$ID"', rb)

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
