"""posts.py (the channels craft's guard, entity `post`; d-work #682): the absent checkout, each template parsing to its
field list, a well-formed store, each failing shape (missing field, wrong format, unknown kind, id or channel off its
path, a channel with no entry, a sender off its path or no member, an unresolved reply, over the size limit, a policy
slot of no allowed value, a member entry naming another system), an unknown field kept, the fence (a credential, a
private name by hash, a disposition shape), append-only against the clone's origin, and the invariants."""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
CRAFT = Path(__file__).resolve().parents[2]
posts = dyadlib.load_guard_file(CRAFT / "guards" / "posts.py")
pc = dyadlib.load_module(dyadlib.PKG / "scripts" / "privatecite.py", "privatecite")
CHANNEL = ("id: release\ncreator: up:home\nowner: up\nsources: up's releases\nadmission: open\nposting: members\n"
           "monitor: session-start\nlimits: 4 KiB, 10 per hour\ndecision-rights: none\n\nReleases.\n")
MEMBER = "system: {s}\nunits: home\nbound-repository: private\nplay-book: 0.1.0\n\nA system.\n"

def message(mid="m1", channel="release", sender="up:home", kind="fact", body="A tag was cut.", **extra) -> str:
    head = {"format": "dyad-channels/1", "id": mid, "channel": channel, "kind": kind, "from": sender,
            "sent": "2026-11-11T00:00:00Z", **extra}
    return "".join(f"{k}: {v}\n" for k, v in head.items()) + "\n" + body + "\n"

class Store(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.base = self.root / "clone"
        (self.base / "registry" / "channels").mkdir(parents=True); (self.base / "registry" / "members").mkdir()
        (self.base / "registry" / "channels" / "release.md").write_text(CHANNEL)
        for s in ("up", "down"):
            (self.base / "registry" / "members" / f"{s}.md").write_text(MEMBER.format(s=s))
        (self.root / "agent-corpus").mkdir()
        env = {k: v for k, v in os.environ.items() if k != "DYAD_INSTANCE"}
        p = mock.patch.dict(os.environ, {**env, posts.ENV: str(self.base)}, clear=True); p.start(); self.addCleanup(p.stop)

    def put(self, text, channel="release", system="up", mid="m1"):
        d = self.base / "channels" / channel / system; d.mkdir(parents=True, exist_ok=True)
        (d / f"{mid}.md").write_text(text)

    def fails(self):
        return [m for m in posts.check_package(self.root) if not m.startswith("warning:")]

class Absent(unittest.TestCase):
    def test_no_checkout_skips(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(posts.ENV, None)
            msgs = posts.check_package(Path(tempfile.gettempdir()))
        self.assertEqual(len(msgs), 1); self.assertTrue(msgs[0].startswith("warning: skip posts"))

class Templates(unittest.TestCase):
    def test_message_template_fields(self):
        head, _ = posts.parse((CRAFT / "templates" / "message.md").read_text())
        self.assertEqual(tuple(head), posts.FIELDS + posts.OPTIONAL)
    def test_channel_template_fields(self):
        head, _ = posts.parse((CRAFT / "templates" / "channel.md").read_text())
        self.assertEqual(tuple(head), posts.CHANNEL_FIELDS)
    def test_member_template_fields(self):
        head, _ = posts.parse((CRAFT / "templates" / "member.md").read_text())
        self.assertEqual(tuple(head), posts.MEMBER_FIELDS)

class Shapes(Store):
    def test_good_store_passes_and_unknown_field_kept(self):
        self.put(message(extra_field="kept"))
        self.put(message(mid="r1", sender="down:home", kind="reply", **{"in-reply-to": "m1"}), system="down", mid="r1")
        self.assertEqual(self.fails(), [])
        self.assertIn("1 channel(s), 2 member(s), 2 message(s)", posts.summary(self.root))

    def test_missing_field(self):
        self.put(message().replace("sent: 2026-11-11T00:00:00Z\n", ""))
        self.assertTrue(any("lacks `sent:`" in m for m in self.fails()))

    def test_wrong_format_and_kind(self):
        self.put(message(kind="order").replace("dyad-channels/1", "dyad-channels/9"))
        f = self.fails()
        self.assertTrue(any("format" in m for m in f)); self.assertTrue(any("kind 'order'" in m for m in f))

    def test_id_and_channel_off_path(self):
        self.put(message(mid="other", channel="issue"), mid="m1")
        f = self.fails()
        self.assertTrue(any("id 'other'" in m for m in f)); self.assertTrue(any("channel 'issue'" in m for m in f))

    def test_channel_without_entry(self):
        self.put(message(channel="issue"), channel="issue")
        self.assertTrue(any("no registry entry" in m for m in self.fails()))

    def test_sender_off_path_or_not_member(self):
        self.put(message(sender="down:home"))
        self.assertTrue(any("not its own system's path" in m for m in self.fails()))
        shutil.rmtree(self.base / "channels")
        self.put(message(sender="stranger:home"), system="stranger")
        self.assertTrue(any("no member entry" in m for m in self.fails()))

    def test_sender_not_system_and_unit(self):
        self.put(message(sender="home"))
        self.assertTrue(any("is not `<system>:<unit>`" in m for m in self.fails()))

    def test_unresolved_reply(self):
        self.put(message(kind="reply", **{"in-reply-to": "nowhere"}))
        self.assertTrue(any("names no message" in m for m in self.fails()))

    def test_size_limit(self):
        self.put(message(body="x" * 5000))
        self.assertTrue(any("over its channel's limit of 4096" in m for m in self.fails()))

    def test_policy_slot_value(self):
        (self.base / "registry" / "channels" / "release.md").write_text(CHANNEL.replace("session-start", "hourly"))
        self.assertTrue(any("monitor 'hourly' is no allowed value" in m for m in self.fails()))
        (self.base / "registry" / "channels" / "release.md").write_text(CHANNEL.replace("session-start", "interval 64-2"))
        self.assertTrue(any("floor 64 is above its ceiling 2" in m for m in self.fails()))

    def test_member_names_another_system(self):
        (self.base / "registry" / "members" / "down.md").write_text(MEMBER.format(s="up"))
        self.assertTrue(any("is not the file's name" in m for m in self.fails()))

class Fence(Store):
    def test_credential_refused(self):
        self.put(message(body="token ghp_" + "a" * 36))
        self.assertTrue(any("GitHub token shape" in m for m in self.fails()))

    def test_private_name_refused_by_hash(self):
        (self.root / "agent-corpus" / pc.PRIVATE).write_text(pc.repo_hash("someone/hidden-repo") + "\n")
        self.put(message(body="see someone/hidden-repo for the fix"))
        f = self.fails()
        self.assertTrue(any("lists as private" in m for m in f))
        self.assertFalse(any("hidden-repo" in m for m in f))           # the name itself is never printed

    def test_public_name_passes(self):
        (self.root / "agent-corpus" / pc.PRIVATE).write_text(pc.repo_hash("someone/hidden-repo") + "\n")
        self.put(message(body="see someone/open-repo"))
        self.assertEqual(self.fails(), [])

    def test_disposition_shape_refused(self):
        self.put(message(body="Y/N: merge it?"))
        self.assertTrue(any("disposition-shaped" in m for m in self.fails()))

    def test_check_text_is_the_draft_check(self):
        self.assertEqual(posts.check_text(message(), self.root), [])
        self.assertTrue(posts.check_text(message(body="Y/N: go?"), self.root))

class AppendOnly(Store):
    def git(self, *a, cwd=None):
        return subprocess.run(["git", "-C", str(cwd or self.base), *a], capture_output=True, text=True, check=True)

    def test_edit_after_landing_fails(self):
        self.put(message())
        g = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        with mock.patch.dict(os.environ, g):
            self.git("init", "-q", "-b", "main"); self.git("add", "."); self.git("commit", "-q", "-m", "seed")
            self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.assertEqual(posts.append_only(self.base), [])
        self.put(message(body="changed"))
        self.assertTrue(any("edited after it landed" in m for m in posts.append_only(self.base)))
        (self.base / "channels" / "release" / "up" / "m1.md").unlink()
        self.assertTrue(any("deleted after it landed" in m for m in posts.append_only(self.base)))

class Invariants(unittest.TestCase):
    def test_invariants_hold(self):
        self.assertEqual([n for n, f in posts.INVARIANTS if not f()], [])

if __name__ == "__main__":
    unittest.main()
