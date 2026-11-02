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

  dyad inbox post <seat> --row <id> --kind <kind> (<body> | --body-file <path>)
                          from this seat (`DYAD_SESSION`): one message, landed ledger-only through land's loop
  dyad inbox read [--all]  this seat's unread messages on a freshly fetched origin/main, printed in order and marked
                          read in one ledger-only land; `--all` prints the read ones too
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
SEAT = re.compile(r"[A-Za-z0-9._-]{1,80}")
NAME_RE = re.compile(r"(?P<stamp>\d{8}T\d{6}Z)-(?P<sender>[A-Za-z0-9._-]+)-(?P<n>\d+)\.(?P<ext>md|read)")
STAMP = "%Y%m%dT%H%M%SZ"
DISPOSITION = re.compile(r"(?m)^\s*Y/N:|\b\d{4}-\d{2}-\d{2} [YN] (?:plan|done|release|backlog)\b|\bY (?:plan|done|release) \(")
USAGE = ("usage: dyad inbox post <seat> --row <id> --kind report|relay|ack|notice (<body> | --body-file <path>) | "
         "dyad inbox read [--all] | dyad inbox list [<seat>]")

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


def post_builder(to: str, row: int, kind: str, body: str, sender: str, inst: str):
    me = sessions().writer()
    def build(wt: Path):
        if row not in {r.id for r in dyadlib.read_rows(wt)}:
            raise Refused(f"no row #{row} on origin/main")
        t = now()
        stamp = t.strftime(STAMP)
        d = wt / inst / INBOX_REL / to
        n = 1 + len(list(d.glob(f"{stamp}-{sender}-*.md"))) if d.is_dir() else 1
        path = d / f"{stamp}-{sender}-{n}.md"
        fields = {"from": sender, "to": to, "row": str(row), "kind": kind,
                  "sent": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "body": body, "writer": me}
        d.mkdir(parents=True, exist_ok=True)
        path.write_text(board().render(fields, FIELDS))
        return [path.relative_to(wt).as_posix()], f"ledger: inbox {to} ({kind}, row {row})", f"posted {path.name} to {to}"
    return build


def parse_post(a: list[str]) -> tuple[str, int, str, str]:
    if not a or not SEAT.fullmatch(a[0]):
        raise Refused(USAGE)
    to, rest, vals, words = a[0], a[1:], {}, []
    i = 0
    while i < len(rest):
        if rest[i] in ("--row", "--kind", "--body-file") and i + 1 < len(rest):
            vals[rest[i]] = rest[i + 1]; i += 2
        else:
            words.append(rest[i]); i += 1
    if "--row" not in vals or not vals["--row"].isdigit() or vals.get("--kind") not in KINDS:
        raise Refused(USAGE)
    if ("--body-file" in vals) == bool(words) or len(words) > 1:
        raise Refused("give the body as one argument or as --body-file, not both and not neither")
    body = Path(vals["--body-file"]).read_text() if "--body-file" in vals else words[0]
    body = body.rstrip("\n")
    if not body.strip():
        raise Refused("an empty body")
    if disposition_shaped(body):
        raise Refused("the body is disposition-shaped (a `Y/N:` line or a ledger entry): a message carries information, "
                      "never authority — name the row instead (#536)")
    return to, int(vals["--row"]), vals["--kind"], body


def post(repo: Path, to: str, row: int, kind: str, body: str) -> int:
    inst = dyadlib.instance_rel(repo)
    if inst is None:
        raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree")
    return land().land(repo, inst, None, post_builder(to, row, kind, body, this_seat(), inst), "inbox post")


def render_message(p: Path, f: dict[str, str], read: bool) -> list[str]:
    first, *rest = (f.get("body") or "").split("\n")
    head = f"{'  ' if read else '* '}{p.stem}  row #{f.get('row', '?')} {f.get('kind', '?')} from {f.get('from', '?')} at {f.get('sent', '?')}"
    return [head, f"    {first}"] + [f"    {r}" for r in rest]


class Nothing(Exception):
    pass


def read_builder(seat: str, show_all: bool, inst: str, got: list):
    me = sessions().writer()
    def build(wt: Path):
        got.clear()
        ms = messages(wt, seat)
        new = [(p, f) for p, f, r in ms if not r]
        got.extend((p.name, f, r) for p, f, r in ms if show_all or not r)
        if not new:
            raise Nothing()
        t = now().strftime("%Y-%m-%dT%H:%M:%SZ")
        for p, _ in new:
            p.with_suffix(".read").write_text(board().render({"read": t, "reader": seat, "writer": me}, MARK_FIELDS))
        out = [l for p, f, r in ms if show_all or not r for l in render_message(p, f, r)]
        return ([p.with_suffix(".read").relative_to(wt).as_posix() for p, _ in new],
                f"ledger: inbox {seat} read ({len(new)})", "\n".join(out + [f"inbox {seat}: {len(new)} marked read"]))
    return build


def read(repo: Path, show_all: bool = False) -> list[dict[str, str]]:
    """This seat's messages (unread, or all), marked read in one land; the messages as parsed, oldest first."""
    seat, inst = this_seat(), dyadlib.instance_rel(repo)
    if inst is None:
        raise Refused("the instance (DYAD_INSTANCE) lies outside this work tree")
    got: list = []
    try:
        land().land(repo, inst, None, read_builder(seat, show_all, inst, got), "inbox read")
    except Nothing:
        for name, f, r in got:
            print("\n".join(render_message(Path(name), f, r)))
        print(f"inbox {seat}: 0 unread")
    return [f for _, f, _ in got]


def cli(a: list[str], repo: Path | None = None) -> int:
    repo = Path(repo or dyadlib.repo_root())
    L = land()
    try:
        if a and a[0] in ("-h", "--help"):
            print(__doc__); return 0
        if a and a[0] == "post":
            return post(repo, *parse_post(a[1:]))
        if a and a[0] == "read" and a[1:] in ([], ["--all"]):
            read(repo, a[1:] == ["--all"]); return 0
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
