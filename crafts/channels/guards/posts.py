#!/usr/bin/env python3
"""Post guard (entity `post`, corpus `craft`; the channels craft's guard — its rules `crafts/channels/rules/`; placed
per `crafts/sysarch/rules/guards.md` under `crafts/channels/guards/`; d-work #682). Kernel: Python 3.12+.
Reads a checkout of a channels repository named by the instance file `<instance>/channels.local.txt` (`clone: <path>`,
relative to the repo root or absolute, and `system: <name>`; absent: one `warning: skip` line) and fails what
the protocol's records cannot hold (the canonical message format `dyad-channels/1`, `../templates/message.md`):
- a channel record (`registry/channels/<channel>.md`) lacking a required slot, or a policy slot of no allowed value;
- a member record (`registry/members/<system>.md`) lacking a required slot, or naming another system than its file;
- a message (`channels/<channel>/<system>/<id>.md`) lacking a required field, of a `kind` the format does not list,
  whose `id`, `channel` or `from` system disagrees with its path, whose sender is no member, whose `in-reply-to`
  names no message, or that is larger than its channel's limit;
- a message the clone's `origin` main line holds, edited or deleted in the checkout (append-only);
- the world-facing fence on every record (`check_text`): a credential shape (the core provenance guard's
  `FAIL_SHAPES`), an `owner/repo` whose sha256 the instance lists as private (`<instance>/private_repos.local.txt`,
  read by `dyad/scripts/privatecite.py`, #518), and a disposition-shaped line (the core inbox's `DISPOSITION`).
An unknown field is kept and never refused (the format's generality, plan #682 revision 3). `check_text` is the
function the `post` step calls before it writes a draft into the clone, so the fence holds before any push.
Left to inference, stated: whether a post's claims are its sender's own, and whether a proposal is one (M4, M7).
  posts.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("posts.py: Python 3.12+ required")
import re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/channels/guards/ -> dyad/scripts
import dyadlib

ENTITY, CORPUS, TRANSACTION = "post", "craft", False
NAME, OWNER = "post (a channels message or registry record)", "crafts/channels/rules/channels.md"
FORMAT = "dyad-channels/1"                                                 # the canonical message format's version
FIELDS = ("format", "id", "channel", "kind", "from", "sent")               # a message's required fields
OPTIONAL = ("holder", "in-reply-to", "refs")                               # named optional fields; any other is kept
KINDS = ("fact", "proposal", "reported-disposition", "question", "reply")  # every class of the member play-book's S1
CHANNEL_FIELDS = ("id", "creator", "owner", "sources", "admission", "posting", "monitor", "limits", "decision-rights")
MEMBER_FIELDS = ("system", "units", "bound-repository", "play-book")
POLICY = {"admission": re.compile(r"open"), "posting": re.compile(r"members|named( [\w.-]+:[\w.-]+)+"),
          "monitor": re.compile(r"session-start|interval \d+-\d+"), "limits": re.compile(r"\d+ KiB, \d+ per hour"),
          "decision-rights": re.compile(r"none")}
LOCAL, REGISTRY, STORE = "channels.local.txt", "registry", "channels"   # the instance file (Rule-11 p1: instance data)
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
_SENDER = re.compile(r"([A-Za-z0-9][\w.-]*):([A-Za-z0-9][\w.-]*)")      # `<system>:<unit>`, never a session
_REPO = re.compile(r"(?<![\w.-])([A-Za-z0-9][\w.-]*/[A-Za-z0-9][\w.-]*)(?![\w/-])")
_INTERVAL = re.compile(r"interval (\d+)-(\d+)")
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("fields-open-with-format", lambda: FIELDS[0] == "format" and len(set(FIELDS + OPTIONAL)) == len(FIELDS + OPTIONAL)),
    ("kinds-are-five", lambda: len(set(KINDS)) == 5 and "reported-disposition" in KINDS),
    ("policy-slots-are-channel-fields", lambda: set(POLICY) <= set(CHANNEL_FIELDS)),
    ("session-start-is-a-monitor-value", lambda: bool(POLICY["monitor"].fullmatch("session-start"))
     and bool(POLICY["monitor"].fullmatch("interval 2-64"))),
    ("sender-is-system-and-unit", lambda: bool(_SENDER.fullmatch("dyad-system:engineer")) and not _SENDER.fullmatch("engineer")),
]
dyadlib.enforce(INVARIANTS, __name__)

def local(root: Path | None = None) -> dict[str, str]:
    """The instance file's `key: value` lines (`clone`, `system`), or {} when it is absent."""
    p = dyadlib.instance(root or dyadlib.repo_root()) / LOCAL
    return parse(p.read_text(errors="replace") + "\n\n")[0] if p.is_file() else {}

def store(root: Path | None = None) -> Path | None:
    """The channels checkout the instance file's `clone:` names, or None; a relative path reads from `root`."""
    v = local(root).get("clone")
    if not v:
        return None
    p = Path(v)
    return p if p.is_absolute() else (root or dyadlib.repo_root()) / p

def parse(text: str) -> tuple[dict[str, str], str]:
    """(header, body): the leading `key: value` lines up to the first blank line, then everything after it."""
    head, _, body = text.partition("\n\n")
    out = {}
    for line in head.splitlines():
        k, sep, v = line.partition(":")
        if sep and k.strip() and not k.startswith(" "):
            out[k.strip()] = v.strip()
    return out, body

def private_hashes(root: Path) -> set[str]:
    pc = dyadlib.load_module(dyadlib.PKG / "scripts" / "privatecite.py", "privatecite")
    return pc.read_lists(root)[1] or set()

def check_text(text: str, root: Path, where: str = "draft", private: set[str] | None = None) -> list[str]:
    """The world-facing fence on one record's whole text (plan #682, rules/fence.md): credentials, private names by
    hash, and disposition-shaped lines. [] when it may be shown to every member."""
    prov = dyadlib.load_guard("agent", "provenance")
    pc = dyadlib.load_module(dyadlib.PKG / "scripts" / "privatecite.py", "privatecite")
    private = private_hashes(root) if private is None else private
    msgs = [f"{where}: holds a {name} shape; a channel is public (fence)" for name, pat in prov.FAIL_SHAPES if pat.search(text)]
    msgs += [f"{where}: names a repository the instance lists as private (sha256 {pc.repo_hash(r)[:12]}…); a channel is public (fence)"
             for r in sorted({m[1].removesuffix(".git") for m in _REPO.finditer(text)}) if pc.repo_hash(r) in private]
    if dyadlib.load_guard("agent", "inbox").DISPOSITION.search(text):
        msgs.append(f"{where}: holds a disposition-shaped line; a message reports a disposition as a fact and never asks or gives one (M1, M8)")
    return msgs

def channels(base: Path) -> dict[str, dict[str, str]]:
    d = base / REGISTRY / "channels"
    return {p.stem: parse(p.read_text(errors="replace"))[0] for p in sorted(d.glob("*.md"))} if d.is_dir() else {}

def members(base: Path) -> dict[str, dict[str, str]]:
    d = base / REGISTRY / "members"
    return {p.stem: parse(p.read_text(errors="replace"))[0] for p in sorted(d.glob("*.md"))} if d.is_dir() else {}

def messages(base: Path) -> list[Path]:
    d = base / STORE
    return sorted(d.glob("*/*/*.md")) if d.is_dir() else []

def limit_bytes(ch: dict[str, str]) -> int | None:
    m = re.match(r"(\d+) KiB", ch.get("limits", ""))
    return int(m[1]) * 1024 if m else None

def check_message(base: Path, path: Path, text: str, chans: dict, mems: dict, ids: set[str]) -> list[str]:
    where = path.relative_to(base).as_posix()
    head, _ = parse(text)
    msgs = [f"{where}: lacks `{k}:` (templates/message.md)" for k in FIELDS if not head.get(k)]
    if head.get("format") and head["format"] != FORMAT:
        msgs.append(f"{where}: format {head['format']!r} is not {FORMAT}")
    if head.get("kind") and head["kind"] not in KINDS:
        msgs.append(f"{where}: kind {head['kind']!r} is none of {', '.join(KINDS)}")
    channel, system = path.parts[-3], path.parts[-2]
    if head.get("id") and (head["id"] != path.stem or not _ID.fullmatch(head["id"])):
        msgs.append(f"{where}: id {head['id']!r} is not the file's name, or not 1–80 of [A-Za-z0-9._-]")
    if head.get("channel") and head["channel"] != channel:
        msgs.append(f"{where}: channel {head['channel']!r} is not the directory {channel!r}")
    if channel not in chans:
        msgs.append(f"{where}: channel {channel!r} has no registry entry (G1)")
    sender = _SENDER.fullmatch(head.get("from", ""))
    if head.get("from") and not sender:
        msgs.append(f"{where}: from {head['from']!r} is not `<system>:<unit>` (G5)")
    elif sender and sender[1] != system:
        msgs.append(f"{where}: from {head['from']!r} writes under {system}/, not its own system's path (G8)")
    elif sender and sender[1] not in mems:
        msgs.append(f"{where}: sender system {sender[1]!r} has no member entry (G2)")
    if head.get("in-reply-to") and head["in-reply-to"] not in ids:
        msgs.append(f"{where}: in-reply-to {head['in-reply-to']!r} names no message (M6)")
    if (cap := limit_bytes(chans.get(channel, {}))) and len(text.encode()) > cap:
        msgs.append(f"{where}: {len(text.encode())} bytes, over its channel's limit of {cap} (L5)")
    return msgs

def landed_ref(base: Path) -> str | None:
    """The clone's view of the shared repository's main line (`origin/HEAD`, else `origin/main`), or None."""
    for ref in ("origin/HEAD", "origin/main"):
        r = subprocess.run(["git", "-C", str(base), "rev-parse", "--verify", "--quiet", ref], capture_output=True, text=True)
        if r.returncode == 0:
            return ref
    return None

def append_only(base: Path) -> list[str]:
    """A message the shared repository already holds is never edited or deleted (G8, the store's append-only rule)."""
    if not (base / ".git").exists() or (ref := landed_ref(base)) is None:
        return []
    r = subprocess.run(["git", "-C", str(base), "diff", "--name-status", "--no-renames", ref, "--", STORE],
                       capture_output=True, text=True)
    return [f"{line.split(chr(9))[-1]}: {'edited' if line[0] == 'M' else 'deleted'} after it landed on {ref}; a message is append-only"
            for line in r.stdout.splitlines() if line[:1] in ("M", "D")]

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    base = store(root)
    if base is None or not base.is_dir():
        return [f"warning: skip posts: no channels checkout (name one as `clone:` in <instance>/{LOCAL})"]
    private, msgs = private_hashes(root), []
    chans, mems = channels(base), members(base)
    for name, ch in chans.items():
        where = f"{REGISTRY}/channels/{name}.md"
        msgs += [f"{where}: lacks `{k}:` (templates/channel.md)" for k in CHANNEL_FIELDS if not ch.get(k)]
        msgs += [f"{where}: {k} {ch[k]!r} is no allowed value (templates/channel.md)" for k, pat in POLICY.items()
                 if ch.get(k) and not pat.fullmatch(ch[k])]
        if (m := _INTERVAL.fullmatch(ch.get("monitor", ""))) and int(m[1]) > int(m[2]):
            msgs.append(f"{where}: monitor floor {m[1]} is above its ceiling {m[2]} (W1)")
    for name, mem in mems.items():
        where = f"{REGISTRY}/members/{name}.md"
        msgs += [f"{where}: lacks `{k}:` (templates/member.md)" for k in MEMBER_FIELDS if not mem.get(k)]
        if mem.get("system") and mem["system"] != name:
            msgs.append(f"{where}: system {mem['system']!r} is not the file's name; each system writes only its own entry (G2)")
    paths = messages(base)
    ids = {p.stem for p in paths}
    for p in paths:
        text = p.read_text(errors="replace")
        msgs += check_message(base, p, text, chans, mems, ids)
    msgs += append_only(base)
    for p in sorted(base.glob(f"{REGISTRY}/*/*.md")) + paths:
        msgs += check_text(p.read_text(errors="replace"), root, p.relative_to(base).as_posix(), private)
    return msgs

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    base = store(root or dyadlib.repo_root())
    if base is None or not base.is_dir():
        return "no channels checkout"
    return f"{len(channels(base))} channel(s), {len(members(base))} member(s), {len(messages(base))} message(s)"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    allowed = {"format": FORMAT, "id": "1-80 of [A-Za-z0-9._-], the file's name", "channel": "its directory",
               "kind": " | ".join(KINDS), "from": "<system>:<unit>", "sent": "an ISO-8601 UTC time"}
    return {"store": f"<clone: of <instance>/{LOCAL}>/channels/<channel>/<system>/<id>.md", "parser": "`posts.parse`",
            "observed": len(messages(store(root))) if store(root) and store(root).is_dir() else 0,
            "note": "unknown fields are kept and never refused; optional: " + ", ".join(OPTIONAL),
            "fields": [(f, "text", allowed[f], True, "", "posts.FIELDS") for f in FIELDS]}

def main(a: list[str]) -> int:
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(m)
    bad = [m for m in msgs if not m.startswith("warning:")]
    print(f"{'FAIL' if bad else 'ok  '} [channels/posts] {summary(root)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
