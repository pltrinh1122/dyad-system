#!/usr/bin/env python3
"""Inbox guard and CLI (entity `message`, agent corpus; Rule-16 owns the store beside the rows, Rule-3 what a message
may carry; placed per Rule-11 property 1; d-work #536, cos mode P2). Kernel: Python 3.12+, git.

Seats reported to the cos by `send_message`, which is addressed to a session id. After a hop the report went to the old
session, and a terminal holder could receive none at all (#546's simulator: S5, S6, S18, S26). The inbox puts the report
on `main`, addressed by seat name, so a hop changes nothing for the sender:

  <instance>/d-work/inbox/<seat>/<UTC-stamp>-<from-seat>-<n>.md     one file per message, never edited
  <instance>/d-work/inbox/<seat>/<UTC-stamp>-<from-seat>-<n>.read   its read marker, written by the reader

A message is `key: value` lines, the body continuing on lines that start with two spaces (`board.parse`'s form, so it
stays verbatim). The keys are `from`, `to`, `row`, `kind` (`report` | `relay` | `ack` | `notice`), `sent`, `body` and
`writer`. The poster writes `writer`, the harness session, as `board set` does (Rule-16's writer pattern, #350). A
marker holds `read`, `reader` and `writer`. Reading leaves a marker and never deletes, so history is git's and nothing
is lost.

**Information, never authority.** A body shaped like a disposition is refused, by the CLI before it lands and by the
guard after: a `Y/N:` counter-prompt line, or a ledger entry such as `2026-11-02 Y done (…)` or `Y plan (…)`. Authority
is read in the ledger (rows, provenance) and nowhere else. A report names the row; it does not quote the entry.

  dyad inbox post <seat> --row <id> --kind <kind> [--cc <seat>]... (<body> | --body-file <path>)
                          from this seat (`DYAD_SESSION`): one message, landed ledger-only through land's loop, and
                          the same message in each `--cc` seat's box in the same land (#572 K6; never a relay); a
                          `relay` lands only when `board/<id>.md` on origin/main names <seat> among its owners and
                          this session wrote it last (write-ahead, #552) — or, from the entry's holder, adds <seat>
                          to its owners in the same commit (#586 E1)
  dyad inbox read          this seat's unread messages on a freshly fetched origin/main, printed in order, each under
                          its name (the file's stem); prints only and writes nothing (#587 S10: reports were marked read
                          unseen, #568, #571)
  dyad inbox read <message>...
                          marks exactly the named messages of this seat's box read, in one ledger-only land: each one's
                          `.read` marker and the reader's presence refresh (#567); refused, before any write, for a name
                          that is no message of this box (another seat's box named), a message already read, or a name
                          given twice. For a message whose row has a phased board entry the land fires the machine's
                          `read` event (`dyadlib.ORCH_NO_EFFECT`), which changes nothing on the entry and writes no board
                          file: reading is an event, never a side effect of printing
  dyad inbox list [<seat>] read-only, from the working tree: every message of the box, unread first marked `*`

`send_message` becomes an optional doorbell ("inbox: 1 new"), never the carrier. `dyad board resume` and
`dyad session touch` print this seat's unread count.

The check:
- package (`check_package`): each box is a path-shaped seat; each file is `<stamp>-<from>-<n>.md` or `.read`; a message
  has its keys, its `to` is its box, its `from` its name's, its `kind` one of four, its `sent` a UTC time, its `row` a
  row (Rule-20) and its body not disposition-shaped; a marker has its message and its box's seat as `reader`.
- transaction (`check_transaction`): each non-merge commit only adds files under `inbox/`; a message or marker modified
  or deleted fails (append-only).

  inbox.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("inbox.py: Python 3.12+ required")
import datetime, os, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "message", "agent", True
NAME, OWNER = "inbox message", "Rule-16"
INBOX_REL = "d-work/inbox"
FIELDS = ("from", "to", "row", "kind", "sent", "body", "writer")
REQUIRED = ("from", "to", "row", "kind", "sent", "body")
MARK_FIELDS = ("read", "reader", "writer")
KINDS = ("report", "relay", "ack", "notice")
CLI_FLAGS = dyadlib.cli_forms("inbox")   # #592 R-a: {verb: its dyadlib.CLI form}, the one home of the flags this parser reads (dyad/tests/test_cli.py)
(CC,) = CLI_FLAGS["post"].repeat
POST_VALUES = tuple(f for f in CLI_FLAGS["post"].value_flags if f != CC)
SEAT = re.compile(r"[A-Za-z0-9._-]{1,80}")
NAME_RE = re.compile(r"(?P<stamp>\d{8}T\d{6}Z)-(?P<sender>[A-Za-z0-9._-]+)-(?P<n>\d+)\.(?P<ext>md|read)")
STAMP = "%Y%m%dT%H%M%SZ"
DISPOSITION = re.compile(r"(?m)^\s*Y/N:|\b\d{4}-\d{2}-\d{2} [YN] (?:plan|done|release|backlog)\b|\bY (?:plan|done|release) \(")
USAGE = ("usage: dyad inbox post <seat> --row <id> --kind report|relay|ack|notice [--cc <seat>]... (<body> | --body-file <path>) | "
         "dyad inbox read [<message>...] | dyad inbox list [<seat>]")

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("required-are-fields", lambda: set(REQUIRED) <= set(FIELDS) and "writer" in FIELDS),
    ("four-kinds", lambda: KINDS == ("report", "relay", "ack", "notice")),
    ("disposition-shapes-refused", lambda: all(DISPOSITION.search(b) for b in
        ("Y/N: Done with #5?", "x\n  Y/N: proceed?", "2026-11-02 Y done (merges PR #1 at abc)", "Y plan (mandate #5)"))),
    ("information-passes", lambda: not any(DISPOSITION.search(b) for b in
        ("merged PR #591 onto main as 4157033", "the Done-Y for #546 is recorded on main", "row #536 is planned"))),
    ("names-parse", lambda: bool(NAME_RE.fullmatch("20261102T174400Z-engineer-1537d8fb-1.md"))
                            and NAME_RE.fullmatch("20261102T174400Z-engineer-1537d8fb-1.md")["sender"] == "engineer-1537d8fb"),
    ("store-under-d-work", lambda: INBOX_REL.startswith("d-work/")),
]


class Refused(Exception):
    pass


def board():
    return dyadlib.load_guard("agent", "board")


def sessions():
    return dyadlib.load_guard("agent", "sessions")


def store(root: Path | None = None) -> Path:
    return dyadlib.instance(root) / INBOX_REL


def box(root: Path, seat: str) -> Path:
    return store(root) / seat


def messages(root: Path, seat: str) -> list[tuple[Path, dict[str, str], bool]]:
    """(path, fields, read) for every message of `seat`'s box, oldest first."""
    d = box(root, seat)
    if not d.is_dir():
        return []
    return [(p, board().parse(p.read_text(errors="replace"))[0], p.with_suffix(".read").exists())
            for p in sorted(d.glob("*.md"))]


def unread(root: Path, seat: str | None) -> int:
    return sum(1 for _, _, r in messages(root, seat) if not r) if seat else 0


def disposition_shaped(body: str) -> bool:
    return bool(DISPOSITION.search(body))


# ---- the check
def check_message(p: Path, text: str, rows: set[int]) -> list[str]:
    where = f"inbox/{p.parent.name}/{p.name}"
    m = NAME_RE.fullmatch(p.name)
    f, problems = board().parse(text)
    msgs = [f"{where}: {x}" for x in problems]
    msgs += [f"{where}: unknown key {k!r} (keys: {', '.join(FIELDS)})" for k in f if k not in FIELDS]
    msgs += [f"{where}: '{k}' missing" for k in REQUIRED if not f.get(k)]
    if f.get("to") and f["to"] != p.parent.name:
        msgs.append(f"{where}: 'to' is {f['to']!r}, not its box {p.parent.name!r}")
    if m and f.get("from") and f["from"] != m["sender"]:
        msgs.append(f"{where}: 'from' is {f['from']!r}, not its name's {m['sender']!r}")
    if f.get("kind") and f["kind"] not in KINDS:
        msgs.append(f"{where}: 'kind' {f['kind']!r} is not one of {', '.join(KINDS)}")
    if f.get("sent"):
        try:
            datetime.datetime.fromisoformat(f["sent"])
        except ValueError:
            msgs.append(f"{where}: 'sent' is not an ISO-8601 time ({f['sent']!r})")
    if f.get("row"):
        if not f["row"].isdigit():
            msgs.append(f"{where}: 'row' is not a row id ({f['row']!r})")
        elif int(f["row"]) not in rows:
            msgs.append(f"{where}: no row #{f['row']} (Rule-20: an unresolved reference)")
    if disposition_shaped(f.get("body", "")):
        msgs.append(f"{where}: the body is disposition-shaped (a `Y/N:` line or a ledger entry): a message carries "
                    f"information, never authority — name the row instead (#536)")
    return msgs


def check_marker(p: Path, text: str) -> list[str]:
    where = f"inbox/{p.parent.name}/{p.name}"
    f, problems = board().parse(text)
    msgs = [f"{where}: {x}" for x in problems]
    msgs += [f"{where}: unknown key {k!r} (keys: {', '.join(MARK_FIELDS)})" for k in f if k not in MARK_FIELDS]
    if not p.with_suffix(".md").exists():
        msgs.append(f"{where}: a read marker with no message")
    if f.get("reader") != p.parent.name:
        msgs.append(f"{where}: 'reader' is {f.get('reader')!r}, not its box {p.parent.name!r}")
    return msgs


def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    d = store(root)
    if not d.is_dir():
        return []
    rows = {r.id for r in dyadlib.read_rows(root)}
    msgs = []
    for p in sorted(d.iterdir()):
        if not p.is_dir() or not SEAT.fullmatch(p.name):
            msgs.append(f"inbox/{p.name}: not a seat's box (a directory named by a path-shaped seat)")
            continue
        for q in sorted(p.iterdir()):
            if not NAME_RE.fullmatch(q.name):
                msgs.append(f"inbox/{p.name}/{q.name}: not `<stamp>-<from-seat>-<n>.md` or `.read`")
            elif q.suffix == ".md":
                msgs += check_message(q, q.read_text(errors="replace"), rows)
            else:
                msgs += check_marker(q, q.read_text(errors="replace"))
    return msgs


def check_transaction(root: Path, base: str, head: str) -> list[str]:
    """Append-only: no non-merge commit of `base..head` modifies or deletes a file under the inbox."""
    inst = dyadlib.instance_rel(root)
    commits = dyadlib.range_commits(root, base, head)
    if not inst or not commits:
        return []
    prefix, msgs = f"{inst}/{INBOX_REL}/", []
    for c in commits:
        r = subprocess.run(["git", "diff-tree", "--root", "--no-commit-id", "-r", "--no-renames", "--name-status", c],
                           cwd=root, capture_output=True, text=True, env=dyadlib.git_env(), timeout=120)
        for line in r.stdout.splitlines():
            status, _, path = line.partition("\t")
            if path.startswith(prefix) and status != "A":
                msgs.append(f"{c[:12]}: {path} is {'deleted' if status == 'D' else 'modified'}; the inbox is append-only "
                            f"(a message is never edited, a read is a marker beside it, #536)")
    return msgs


def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    d = store(root or dyadlib.repo_root())
    boxes = [p for p in d.iterdir() if p.is_dir()] if d.is_dir() else []
    return f"{sum(len(list(b.glob('*.md'))) for b in boxes)} message(s) in {len(boxes)} box(es)"


def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    d = store(root); rel = d.relative_to(root) if d.is_relative_to(root) else d
    return {"store": f"{rel}/<seat>/<stamp>-<from-seat>-<n>.md (and .read)",
            "parser": "`board.parse` (key: value lines, two-space continuations)",
            "observed": sum(len(list(b.glob("*.md"))) for b in d.iterdir() if b.is_dir()) if d.is_dir() else 0,
            "note": "one file per message, addressed by seat, append-only; information, never authority",
            "fields": [(f, "text", "", f in REQUIRED, "", "inbox.FIELDS") for f in FIELDS]}


# ---- the CLI
def this_seat() -> str:
    seat = os.environ.get("DYAD_SESSION", "")
    if not SEAT.fullmatch(seat):
        raise Refused("DYAD_SESSION names no seat: the inbox is addressed by seat")
    return seat


def land():
    return dyadlib.load_module(dyadlib.PKG / "scripts" / "land.py", "land")


def now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def write_ahead_problem(wt: Path, inst: str, row: int, to: str, me: str) -> str | None:
    """The write-ahead fence on a relay (d-work #552, mode A): None when `board/<row>.md` on origin/main names `to`
    among its owners and this session wrote it last; else why not. A dispatch then cannot precede its board entry."""
    path = wt / inst / board().BOARD_REL / f"{row}.md"
    if not path.is_file():
        return (f"a relay needs its board entry first (write-ahead, #552): board/{row}.md is not on origin/main — "
                f"`dyad board set {row} owner=\"{to} <session>\" waiting-on=\"seat {to}\" next=…`")
    f = board().parse(path.read_text(errors="replace"))[0]
    if to not in board().owners(f):
        return (f"a relay needs its board entry first (write-ahead, #552): board/{row}.md names owner(s) "
                f"{', '.join(board().owners(f)) or 'none'}, not {to}")
    if f.get("writer") != me:
        return (f"a relay needs its board entry first (write-ahead, #552): board/{row}.md was last written by "
                f"{f.get('writer') or 'nobody recorded'}, not this session ({me})")
    return None


def holder_adds_owner(wt: Path, inst: str, row: int, to: str, me: str, sender: str) -> str | None:
    """#586 E1: a relay from the board's holder to a unit its entry does not yet name as an owner adds that unit to
    `owner`, writing the entry in the worktree so it lands in the relay's own commit, board first (write-ahead kept by
    construction, #552). Only the holder, and only when this session wrote the entry last; anything else is refused
    as before. Returns the entry's repo-relative path, or None when it does not apply."""
    path = wt / inst / board().BOARD_REL / f"{row}.md"
    if not path.is_file():
        return None
    f = board().parse(path.read_text(errors="replace"))[0]
    if f.get("holder") != sender or f.get("writer") != me or to in board().owners(f):
        return None
    f["owner"] = "; ".join(x for x in (f.get("owner", "").strip(), to) if x)
    path.write_text(board().render(f, board().keys_for(str(row))))
    return path.relative_to(wt).as_posix()


def post_builder(to: str, row: int, kind: str, body: str, sender: str, inst: str, cc=()):
    """One message to `to` and, for each `--cc` seat, the same message in that seat's box (its `to` its own box), all in
    one land (#572 K6: a report sent to home and copied to orchestrate was two posts, two lands)."""
    me = sessions().writer()
    def build(wt: Path):
        r = next((x for x in dyadlib.read_rows(wt) if x.id == row), None)
        if r is None:
            raise Refused(f"no row #{row} on origin/main")
        extra = []
        if kind == "relay":
            why = write_ahead_problem(wt, inst, row, to, me)
            if why and r.state not in dyadlib.TERMINAL_STATES and (added := holder_adds_owner(wt, inst, row, to, me, sender)):
                extra.append(added)                       # #586 E1: the board entry first, in the same commit
                why = write_ahead_problem(wt, inst, row, to, me)
            if why:
                raise Refused(why)
        t = now()
        stamp = t.strftime(STAMP)
        paths = []
        for box in (to, *cc):
            d = wt / inst / INBOX_REL / box
            n = 1 + len(list(d.glob(f"{stamp}-{sender}-*.md"))) if d.is_dir() else 1
            path = d / f"{stamp}-{sender}-{n}.md"
            fields = {"from": sender, "to": box, "row": str(row), "kind": kind,
                      "sent": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "body": body, "writer": me}
            d.mkdir(parents=True, exist_ok=True)
            path.write_text(board().render(fields, FIELDS))
            paths.append(path)
        copies = f" (cc {', '.join(cc)})" if cc else ""
        return (extra + [p.relative_to(wt).as_posix() for p in paths], f"ledger: inbox {to}{copies} ({kind}, row {row})",
                (f"added {to} to board/{row}.md's owners (#586)\n" if extra else "") + f"posted {paths[0].name} to {to}{copies}")
    return build


def parse_post(a: list[str]) -> tuple[str, int, str, str, tuple[str, ...]]:
    if not a or not SEAT.fullmatch(a[0]):
        raise Refused(USAGE)
    to, rest, vals, words, cc = a[0], a[1:], {}, [], []
    i = 0
    while i < len(rest):
        if rest[i] == CC and i + 1 < len(rest):
            if not SEAT.fullmatch(rest[i + 1]) or rest[i + 1] == to or rest[i + 1] in cc:
                raise Refused(f"--cc takes another seat, once each, not {rest[i + 1]!r}")
            cc.append(rest[i + 1]); i += 2
        elif rest[i] in POST_VALUES and i + 1 < len(rest):
            vals[rest[i]] = rest[i + 1]; i += 2
        else:
            words.append(rest[i]); i += 1
    if "--row" not in vals or not vals["--row"].isdigit() or vals.get("--kind") not in KINDS:
        raise Refused(USAGE)
    if ("--body-file" in vals) == bool(words) or len(words) > 1:
        raise Refused("give the body as one argument or as --body-file, not both and not neither")
    try:
        body = Path(vals["--body-file"]).read_text(encoding="utf-8") if "--body-file" in vals else words[0]
    except (OSError, UnicodeDecodeError) as e:
        raise Refused(f"--body-file {vals['--body-file']}: {e}") from None
    body = body.rstrip("\n")
    if not body.strip():
        raise Refused("an empty body")
    if disposition_shaped(body):
        raise Refused("the body is disposition-shaped (a `Y/N:` line or a ledger entry): a message carries information, "
                      "never authority — name the row instead (#536)")
    if cc and vals["--kind"] == "relay":
        raise Refused("a relay goes to the one seat its board entry names (write-ahead, #552); --cc is for a report, "
                      "notice or ack")
    return to, int(vals["--row"]), vals["--kind"], body, tuple(cc)


def post_ring(to: str, kind: str, cc=(), sender: str = "") -> list[str]:
    """K-21 (#652): the units an `inbox post` rings — the box and each `--cc` box, in order and once each — unless the
    post is a notice (an information-only copy rings nobody) or the unit is the sender (a self-addressed post rings
    nobody); the rule `land.ring_list` applies to a batch's posts (Rule-3 Batch disposition, `dmc:message-route`)."""
    if kind == "notice":
        return []
    out = []
    for u in (to, *cc):
        if u != sender and u not in out:
            out.append(u)
    return out


def post(repo: Path, to: str, row: int, kind: str, body: str, cc=()) -> int:
    """Land the message; only then, after `land` has printed its `landed <sha> on main` line, print the `ring:` line
    naming the units the session now rings. A refused or unlanded post raises before it, so it rings nobody (K-21,
    #652: the doorbell follows the post that has landed, never one that has not)."""
    inst = dyadlib.instance_rel(repo)
    if inst is None:
        raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree")
    sender = this_seat()
    rc = land().land(repo, inst, None, post_builder(to, row, kind, body, sender, inst, tuple(cc)), "inbox post")
    ring = post_ring(to, kind, cc, sender)
    if rc == 0 and ring:
        print(f"ring: {', '.join(ring)} (a doorbell is the session's act, #586 X4)")
    return rc


def render_message(p: Path, f: dict[str, str], read: bool) -> list[str]:
    first, *rest = (f.get("body") or "").split("\n")
    head = f"{'  ' if read else '* '}{p.stem}  row #{f.get('row', '?')} {f.get('kind', '?')} from {f.get('from', '?')} at {f.get('sent', '?')}"
    return [head, f"    {first}"] + [f"    {r}" for r in rest]


class Nothing(Exception):
    pass


PLANNED_NOTICE = re.compile(r"^row #(\d+) planned\b")   # the automaton's notice (automaton.PLANNED)


def handed_rows(new: list) -> list[str]:
    """#567: the rows the messages being marked read hand this seat — each `relay`'s row, and each `notice` that
    announces a row planned — for `sessions.claim` to gate against the board."""
    out = []
    for _, f in new:
        if f.get("kind") == "relay" or (f.get("kind") == "notice" and PLANNED_NOTICE.match(f.get("body") or "")):
            if (f.get("row") or "").isdigit() and f["row"] not in out:
                out.append(f["row"])
    return out


def show_builder(seat: str, got: list):
    """The print path of `inbox read` (#587 S10): collects this seat's unread messages in land's worktree on a freshly
    fetched origin/main and lands nothing (Nothing, always)."""
    def build(wt: Path):
        got[:] = [(p.name, f, r) for p, f, r in messages(wt, seat) if not r]
        raise Nothing()
    return build


def message_name(name: str, seat: str) -> tuple[str, str]:
    """(box, stem) of a name as `inbox read` prints it — a stem, `<stem>.md`, or `<box>/<stem>` — the box this seat's
    when none is named."""
    box, _, stem = name.rpartition("/")
    stem = stem.removesuffix(".md")
    if (box and not SEAT.fullmatch(box)) or not NAME_RE.fullmatch(stem + ".md"):
        raise Refused(f"{name!r} is not a message name (`<stamp>-<from-seat>-<n>`, as `dyad inbox read` prints it)")
    return box or seat, stem


def mark_builder(seat: str, names: list[str], inst: str, got: list, repo: Path | None = None):
    """The marking path of `inbox read <message>…` (#587 S10): on every try, in land's worktree on a freshly fetched
    origin/main, refuse every name that is no unread message of this seat's box before any write; then write each named
    message's marker, fire the machine's `read` on each named row's phased entry (no board write) and refresh the
    reader's presence (#567), all in one ledger-only land."""
    me = sessions().writer()
    def build(wt: Path):
        got.clear()
        mine = {p.stem: (p, f, r) for p, f, r in messages(wt, seat)}
        picked, seen = [], set()
        for name in names:
            box, stem = message_name(name, seat)
            if stem in seen:
                raise Refused(f"{name} is named twice")
            seen.add(stem)
            if box != seat:
                raise Refused(f"{name} is a message of {box}'s box, not this seat's ({seat}): a seat marks only what it read "
                              f"in its own box; nothing marked")
            if stem not in mine:
                d = store(wt)
                other = sorted(b.name for b in d.iterdir() if (b / f"{stem}.md").is_file()) if d.is_dir() else []
                raise Refused(f"{name} is " + (f"a message of {', '.join(other)}'s box, not this seat's ({seat})" if other
                                               else f"no message of {seat}'s box on origin/main")
                              + "; nothing marked")
            p, f, r = mine[stem]
            if r:
                at = board().parse(p.with_suffix(".read").read_text(errors="replace"))[0].get("read", "?")
                raise Refused(f"{name} is already read (its marker says {at}); nothing marked")
            picked.append((p, f))
        rows = {r.id: r for r in dyadlib.read_rows(wt)}
        events = []
        for rid in dict.fromkeys(int(f["row"]) for _, f in picked if (f.get("row") or "").isdigit()):
            try:
                line = board().read_event(wt, inst, rid, rows.get(rid), seat)
            except board().Refused as e:
                raise Refused(str(e)) from None
            if line:
                events.append(line)
        t = now().strftime("%Y-%m-%dT%H:%M:%SZ")
        for p, _ in picked:
            p.with_suffix(".read").write_text(board().render({"read": t, "reader": seat, "writer": me}, MARK_FIELDS))
        got.extend((p.name, f, False) for p, f in picked)
        presence = land().refresh_presence(wt, inst, handed_rows(picked), repo, always=True)   # #567: the read lands the touch with it
        return ([p.with_suffix(".read").relative_to(wt).as_posix() for p, _ in picked] + presence,
                f"ledger: inbox {seat} read ({len(picked)})",
                "\n".join([f"marked read: {p.stem}" for p, _ in picked] + events + [f"inbox {seat}: {len(picked)} marked read"]))
    return build


def read(repo: Path, names: list[str] | tuple = ()) -> list[dict[str, str]]:
    """`inbox read`: with no names, this seat's unread messages printed and nothing written; with names, exactly those
    messages marked read in one land (#587 S10). The messages printed or marked, as parsed, oldest first, each with
    `_name` its name as printed (the file's stem), the word `read <message>` takes."""
    seat, inst = this_seat(), dyadlib.instance_rel(repo)
    if inst is None:
        raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree")
    got: list = []
    if names:
        land().land(repo, inst, None, mark_builder(seat, list(names), inst, got, repo), "inbox read")
        return [{**f, "_name": Path(n).stem} for n, f, _ in got]
    try:
        land().land(repo, inst, None, show_builder(seat, got), "inbox read")
    except Nothing:
        pass
    for name, f, r in got:
        print("\n".join(render_message(Path(name), f, r)))
    print(f"inbox {seat}: {len(got)} unread, none marked" + (" — mark what you have read: `dyad inbox read <message>...`"
                                                             if got else ""))
    return [{**f, "_name": Path(n).stem} for n, f, _ in got]


def cli(a: list[str], repo: Path | None = None) -> int:
    repo = Path(repo or dyadlib.repo_root())
    L = land()
    try:
        if a and a[0] in ("-h", "--help"):
            print(__doc__); return 0
        if a and a[0] == "post":
            return post(repo, *parse_post(a[1:]))
        if a and a[0] == "read":
            if any(x.startswith("-") for x in a[1:]):
                raise Refused(f"{USAGE} (`--all` is removed: `dyad inbox list` shows the read messages, #587 S10)")
            read(repo, a[1:]); return 0
        if a and a[0] == "list" and len(a) <= 2:
            seat = a[1] if len(a) == 2 else this_seat()
            ms = messages(repo, seat)
            for p, f, r in ms:
                print("\n".join(render_message(p, f, r)))
            print(f"inbox {seat}: {len(ms)} message(s), {sum(1 for *_, r in ms if not r)} unread (the working tree; `git pull` first for main's)")
            return 0
        raise Refused(USAGE)
    except (Refused, L.Refused) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2 if str(e) == USAGE else 1


def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(f"FAIL [rule-16] {m}")
    print(f"ok   [rule-16] {summary(root)}")
    return 1 if msgs else 0


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
