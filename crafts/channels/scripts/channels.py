#!/usr/bin/env python3
"""Channels verbs (the channels craft's script; its run-book `crafts/channels/runbooks/channels.md`, run as
`dyad runbook run channels:channels <step>`; d-work #682). Kernel: Python 3.12+, Git.
A Tended craft adds no row to the core's `dyadlib.CLI` table, so its verbs are run-book steps (`cabinet:session-tidy`,
#640). Each reads or writes the channels checkout the instance file `<instance>/channels.local.txt` names (`clone:`);
none pushes:
- `subscribe <url>`: clone the channels repository into that `clone:` path, or fetch it when the clone exists;
- `read`: fetch when a remote exists, then print each message new since this unit's last read, honouring each
  channel's `monitor` slot — `session-start` reads at every run, `interval <min>-<max>` reads once the current interval
  has passed, doubling it after an empty read up to `max` and resetting it to `min` on news (W1). The marker is
  `<git common dir of this checkout>/dyad-channels/<unit>.json`, never in either tree;
- `post <channel> <kind> <id> <body-file> [key=value …]`: build the record, run the guard's checks on it (shape and
  the fence, `posts.check_text`), print it whole, write it on a branch `post/<id>` of the clone with one commit, and
  print the push and the pull request to open; it pushes nothing;
- `breach [<system>]`: run the guard's checks over the messages received (all, or one sender system's) and print each
  finding with the line an incident row needs; it detects and records nothing itself (K1–K4: safety on the receiver,
  never retaliation).
The sender is `<system>:<unit>`: the system the same file's `system:` names, else this checkout's directory name;
the unit `DYAD_SESSION`. Exit 0 ok, 1 refused or a guard failure, 2 a usage error.
  channels.py subscribe <url> | read | post <channel> <kind> <id> <body-file> [k=v …] | breach [<system>]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("channels.py: Python 3.12+ required")
import datetime as dt, json, os, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/channels/scripts/ -> dyad/scripts
import dyadlib
posts = dyadlib.load_guard_file(Path(__file__).resolve().parents[1] / "guards" / "posts.py")

MARKERS = "dyad-channels"
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("marker-dir-is-not-tracked-name", lambda: MARKERS.startswith("dyad-") and "/" not in MARKERS),
]
dyadlib.enforce(INVARIANTS, __name__)

def git(base: Path, *a: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(base), *a], capture_output=True, text=True, check=check)

def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)

def sender(root: Path) -> str:
    system = posts.local(root).get("system") or dyadlib.repo_root(root).name
    return f"{system}:{os.environ.get('DYAD_SESSION') or 'unknown'}"

def marker_path(root: Path) -> Path:
    common = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    return Path(common) / MARKERS / f"{os.environ.get('DYAD_SESSION') or 'unknown'}.json"

def load_marker(p: Path) -> dict:
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}

def due(ch: dict[str, str], mark: dict, at: dt.datetime) -> bool:
    """Whether a channel is read on this run (its `monitor` slot)."""
    m = re.fullmatch(r"interval (\d+)-(\d+)", ch.get("monitor", "session-start"))
    if not m or "last" not in mark:
        return True
    return (at - dt.datetime.fromisoformat(mark["last"])).total_seconds() >= 60 * mark.get("interval", int(m[1]))

def next_interval(ch: dict[str, str], mark: dict, news: bool) -> int | None:
    m = re.fullmatch(r"interval (\d+)-(\d+)", ch.get("monitor", "session-start"))
    if not m:
        return None
    lo, hi = int(m[1]), int(m[2])
    return lo if news else min(hi, max(lo, 2 * mark.get("interval", lo)))

def checkout(root: Path) -> Path | None:
    base = posts.store(root)
    if base is None:
        print(f"channels: name the channels clone as `clone:` in <instance>/{posts.LOCAL}", file=sys.stderr)
    return base

def cmd_subscribe(root: Path, a: list[str]) -> int:
    if len(a) != 1:
        print("usage: channels.py subscribe <url>", file=sys.stderr); return 2
    if (base := checkout(root)) is None:
        return 2
    r = (git(base, "fetch", "--quiet", check=False) if (base / ".git").exists()
         else subprocess.run(["git", "clone", "--quiet", a[0], str(base)], capture_output=True, text=True))
    print(r.stderr.strip() or f"ok   subscribed: {base} ({posts.summary(root)})")
    return 0 if r.returncode == 0 else 1

def cmd_read(root: Path, a: list[str], at: dt.datetime | None = None) -> int:
    if a:
        print("usage: channels.py read", file=sys.stderr); return 2
    if (base := checkout(root)) is None or not base.is_dir():
        print(f"warning: skip read: no channels checkout at {base}"); return 0
    at = at or now()
    if (base / ".git").exists() and git(base, "remote", check=False).stdout.strip():
        git(base, "pull", "--ff-only", "--quiet", check=False)
    mp = marker_path(root)
    marks, chans, count = load_marker(mp), posts.channels(base), 0
    for name, ch in chans.items():
        mark = marks.get(name, {})
        if not due(ch, mark, at):
            print(f"skip {name}: monitor {ch.get('monitor')}, next read after {mark.get('interval')} min from {mark['last']}")
            continue
        seen = set(mark.get("seen", []))
        new = [p for p in posts.messages(base) if p.parts[-3] == name and p.relative_to(base).as_posix() not in seen]
        for p in new:
            head, body = posts.parse(p.read_text(errors="replace"))
            print(f"--- {p.relative_to(base).as_posix()} ({head.get('kind')}, from {head.get('from')}, sent {head.get('sent')})")
            print(body.rstrip())
        marks[name] = {"last": at.isoformat(), "seen": sorted(seen | {p.relative_to(base).as_posix() for p in new})}
        if (iv := next_interval(ch, mark, bool(new))) is not None:
            marks[name]["interval"] = iv
        count += len(new)
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(marks, indent=1, sort_keys=True) + "\n")
    print(f"ok   read: {count} new message(s) over {len(chans)} channel(s)")
    return 0

def record(root: Path, channel: str, kind: str, mid: str, body: str, extra: dict[str, str], at: dt.datetime) -> str:
    head = {"format": posts.FORMAT, "id": mid, "channel": channel, "kind": kind, "from": sender(root),
            "sent": at.strftime("%Y-%m-%dT%H:%M:%SZ"), **extra}
    return "".join(f"{k}: {v}\n" for k, v in head.items()) + "\n" + body.rstrip() + "\n"

def cmd_post(root: Path, a: list[str], at: dt.datetime | None = None) -> int:
    if len(a) < 4 or any("=" not in x for x in a[4:]):
        print("usage: channels.py post <channel> <kind> <id> <body-file> [key=value …]", file=sys.stderr); return 2
    channel, kind, mid, body_file = a[:4]
    extra = dict(x.split("=", 1) for x in a[4:])
    if (base := checkout(root)) is None or not base.is_dir():
        print(f"channels: no channels checkout; run the subscribe step first", file=sys.stderr); return 2
    text = record(root, channel, kind, mid, Path(body_file).read_text(), extra, at or now())
    system = sender(root).split(":")[0]
    path = base / posts.STORE / channel / system / f"{mid}.md"
    ids = {p.stem for p in posts.messages(base)}
    msgs = posts.check_message(base, path, text, posts.channels(base), posts.members(base), ids | {mid})
    msgs += posts.check_text(text, root, path.relative_to(base).as_posix())
    if path.exists():
        msgs.append(f"{path.relative_to(base).as_posix()}: exists; a message is never edited (append-only)")
    print(text, end="")
    if msgs:
        for m in msgs:
            print(f"FAIL {m}")
        print("refused: nothing written"); return 1
    branch = f"post/{mid}"
    if git(base, "switch", "--quiet", "-c", branch, check=False).returncode:
        print(f"refused: branch {branch} exists in the clone; nothing written"); return 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    git(base, "add", "--", str(path))
    git(base, "commit", "--quiet", "-m", f"{channel}: {kind} {mid} from {sender(root)}")
    print(f"ok   written on branch {branch} of {base}; nothing pushed")
    print(f"next: git -C {base} push -u origin {branch}, then open its pull request to the channels repository")
    return 0

def cmd_breach(root: Path, a: list[str]) -> int:
    if len(a) > 1:
        print("usage: channels.py breach [<system>]", file=sys.stderr); return 2
    if (base := checkout(root)) is None or not base.is_dir():
        print(f"warning: skip breach: no channels checkout at {base}"); return 0
    mine = sender(root).split(":")[0]
    found = [m for m in posts.check_package(root) if not m.startswith("warning:")]
    found = [m for m in found if m.startswith(f"{posts.STORE}/") and m.split("/")[2] != mine
             and (not a or m.split("/")[2] == a[0])]
    for m in found:
        print(f"breach {m}")
    print(f"ok   breach: {len(found)} finding(s); each is an incident row the agent records (Rule-3), "
          "and no reply, block or reversal is made from here (never retaliate)")
    return 0

STEPS = {"subscribe": cmd_subscribe, "read": cmd_read, "post": cmd_post, "breach": cmd_breach}

def main(a: list[str]) -> int:
    if not a or a[0] not in STEPS:
        print(__doc__.rsplit("\n", 2)[-2].strip(), file=sys.stderr); return 2
    return STEPS[a[0]](dyadlib.repo_root(), a[1:])

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
