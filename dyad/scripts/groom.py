#!/usr/bin/env python3
"""The backlog grooming report (core script; d-work #625; the play-book `dyad/playbooks/backlog-groom.md` runs it as
its run-book's one step, `dyad/runbooks/backlog-groom.md` `report`). Kernel: Python 3.12+, git.
`dyad board groom` prints the facts a grooming run reads, one block per backlog row, then the release state:

  #<id>[-<slug>] [backlog, <age>] <title>   the row, labelled as `dwork-slug` says (#622), its age from `opened`
    refs:      each `#N` its `refs` names, with that row's state
    adjacency: the board anchor (a row with a board entry, not terminal) nearest the row, by the TF-IDF weighting
               `hygiene.tfidf` and `hygiene.cosine` give the backlog ranking, and its cosine; no threshold
    promised:  the `_cos` files whose `promised` names the row
    roots:     the craft roots the row's plan file names (`dyad/` is dyad-operator, `crafts/<c>/` is c)
    hygiene … / candidate: …   the lines `hygiene.hygiene` returns that name the row, verbatim, never recomputed
                               (Rule-13; plan #625 F5)
    read:      the row's last reading on the home's `_cos` (`read` lines: `#<id> <date> <outcome> — <ground>`), or
               `never`; a `holds` run held `hygiene-stale-days` or more is marked `unwanted-candidate` (#697); the
               blocks come unread or stale first, oldest by `opened`, after a `read this run:` line (five, or a tenth)
  stale work: the work-in-flight W2 and W3 lines (`hygiene.inflight`), verbatim, for the stale open or planned rows
  releases:  per craft its last release tag and its live VERSION, then the bundle's, as the release run-book's
             `changes` step reads them
  last grooming: the last event of this run-book's `report` step, or none

It prints facts and never a judgement: the class, the size, the retirement ground and the release target are the
home's, by the criteria the play-book cites (`retirement-candidate`, `altitude`, `promotion`, `release-plan`).
Read-only: it writes nothing.
  groom.py            (reached as `dyad board groom`)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("groom.py: Python 3.12+ required")
import datetime, re, subprocess, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

USAGE = "usage: dyad board groom"
RUNBOOK, STEP = "backlog-groom", "report"     # the run-book whose last `report` event is the last grooming
REF = re.compile(r"#(\d+)")
ROOT_PATH = re.compile(r"(?<![\w./-])(dyad|crafts/[a-z][a-z0-9-]*)/")
NAMED = re.compile(r"#(\d+)\b")               # the rows a hygiene or candidate line names


def hygiene():
    return dyadlib.load_module(dyadlib.PKG / "scripts" / "hygiene.py", "hygiene")


def git(root: Path, *a: str) -> str:
    r = subprocess.run(["git", *a], cwd=root, capture_output=True, text=True, env=dyadlib.git_env(), timeout=300)
    return r.stdout if r.returncode == 0 else ""


def roots_of(plan: str) -> list[str]:
    """The crafts whose roots `plan` names by path, in first-seen order: `dyad/` is the core craft."""
    out = []
    for m in ROOT_PATH.finditer(plan):
        c = dyadlib.CORE_CRAFT if m.group(1) == "dyad" else m.group(1).split("/", 1)[1]
        if c not in out:
            out.append(c)
    return out


def lines_by_row(lines: list[str], ids: set[int]) -> dict[int, list[str]]:
    """{row id: the lines of `lines` that name it}, for the ids in `ids`, each line kept verbatim and in order."""
    out: dict[int, list[str]] = {i: [] for i in ids}
    for line in lines:
        for i in dict.fromkeys(int(n) for n in NAMED.findall(line)):
            if i in out:
                out[i].append(line)
    return out


def adjacency(rows, texts: dict[int, str], backlog: list, anchors: list[int]) -> dict[int, tuple[float, int] | None]:
    """{backlog id: (cosine, anchor id) of its nearest anchor, or None when no anchor shares a token}."""
    hy = hygiene()
    vec, norm = hy.tfidf({r.id: texts.get(r.id, r.title) for r in rows})
    out = {}
    for r in backlog:
        got = [(hy.cosine(vec, norm, r.id, a), a) for a in anchors if a != r.id and a in vec]
        best = max((g for g in got if g[0] >= 0.005), key=lambda g: (g[0], -g[1]), default=None)
        out[r.id] = best
    return out


def releases(root: Path) -> list[str]:
    """One line per craft with a VERSION: its last release tag and its live VERSION; then the bundle's."""
    out = []
    crafts = [(dyadlib.CORE_CRAFT, root / "dyad")] + sorted(
        (p.name, p) for p in (root / "crafts").glob("*") if p.is_dir() and (p / "VERSION").is_file())
    for name, r in crafts:
        if not (r / "VERSION").is_file():
            continue
        tag = next(iter(git(root, "tag", "-l", f"{name}-v[0-9]*", "--sort=-v:refname").split()), "")
        out.append(f"  {name}: last tag {tag or 'none'} (VERSION {(r / 'VERSION').read_text().strip()})")
    tag = next(iter(git(root, "tag", "-l", "v[0-9]*", "--sort=-v:refname").split()), "")
    m = re.search(r"(?m)^version: *(\S+)", (root / "BUNDLE.md").read_text()) if (root / "BUNDLE.md").is_file() else None
    out.append(f"  bundle: last tag {tag or 'none'} (BUNDLE.md {m.group(1) if m else 'absent'})")
    return out


def last_grooming(root: Path) -> str:
    rb = dyadlib.load_module(dyadlib.PKG / "scripts" / "runbook.py", "runbook")
    ev = rb.last_event(rb.events_path(root, RUNBOOK), STEP)
    return f"{ev.get('id', '?')} at {ev.get('ts', '?')}" if ev else "none"


GROOM_HYGIENE_COUNT = 5   # dmc:groom-trigger G4's fixed count, never a preference


def groom_due(root: Path, hygiene: int | None = None) -> list[str]:
    """The mechanical half of `dmc:groom-trigger` (#695): `G2` when a release tag was created after the last grooming
    event (every tag when there is none), and `G4` when `hygiene` — the hygiene lines `dyad board resume` printed, when
    the caller counted them — reaches the fixed count of five, and `G5` when an old backlog row has gone 90 days unread
    (`uncovered`, #697). G1 (a prompt) and G3 (promotion found nothing) are the
    home's, and so is the floor (nothing changed since the last grooming)."""
    rb = dyadlib.load_module(dyadlib.PKG / "scripts" / "runbook.py", "runbook")
    ev = rb.last_event(rb.events_path(root, RUNBOOK), STEP)
    since = (ev or {}).get("ts") or ""
    out = []
    tags = git(root, "for-each-ref", "--format=%(creatordate:iso-strict) %(refname:short)", "refs/tags").splitlines()
    try:
        t0 = datetime.datetime.fromisoformat(since.replace("Z", "+00:00")) if since else None
    except ValueError:
        t0 = None
    for line in tags:
        when, _, name = line.partition(" ")
        try:
            t = datetime.datetime.fromisoformat(when)
        except ValueError:
            continue
        if re.fullmatch(r"(?:[a-z][a-z0-9-]*-)?v\d+\.\d+\.\d+", name) and (t0 is None or t > t0):
            out.append("G2")
            break
    if hygiene is not None and hygiene >= GROOM_HYGIENE_COUNT:
        out.append("G4")
    if uncovered(root):
        out.append("G5")
    return out


def uncovered(root: Path, base: str = "HEAD") -> list[int]:
    """`dmc:groom-trigger` G5 (#697 G3): the backlog rows older than GROOM_COVERAGE_DAYS by `opened` whose last reading is
    absent or older than that, so a backlog the reading has not covered in 90 days makes a run due."""
    bd = dyadlib.load_guard("agent", "board")
    inst = dyadlib.instance_rel(root) or "agent-corpus"
    try:   # no row store or board on `base` yet (a fresh instance, a fixture): nothing to cover
        rows = dyadlib.read_rows(root, at=base)
        cos_rel = f"{inst}/d-work/board/_cos.md"
        cos = bd.parse(dyadlib.show_many(root, base, [cos_rel]).get(cos_rel, ""))[0]
    except (OSError, ValueError, subprocess.CalledProcessError):
        return []
    read = readings(cos.get("read", ""))
    today = datetime.date.fromisoformat(dyadlib.utc_date())
    def days(d: str) -> int:
        try:
            return (today - datetime.date.fromisoformat(d)).days
        except ValueError:
            return 0
    return [r.id for r in rows if r.state == "backlog" and days(r.opened) > GROOM_COVERAGE_DAYS
            and (r.id not in read or days(read[r.id]["date"]) > GROOM_COVERAGE_DAYS)]


READ_LINE = re.compile(r"^#(?P<id>\d+) (?P<date>\d{4}-\d{2}-\d{2}) (?P<outcome>[a-z-]+) — (?P<ground>.+)$")   # #697
READ_ADDED = re.compile(r"^\+(?:read: |  )(#\d+ \d{4}-\d{2}-\d{2} [a-z-]+ — .+)$")
GROOM_READ_MIN, GROOM_READ_SHARE, GROOM_COVERAGE_DAYS = 5, 10, 90   # dmc:backlog-staleness's numbers, never preferences


def readings(cos_value: str) -> dict[int, dict[str, str]]:
    """{row id: {date, outcome, ground}} from the home's `read` lines (`#<id> <YYYY-MM-DD> <outcome> — <ground>`), the
    last line per row kept; a malformed line is skipped (#697: a reading is the home's, recorded on its `_cos`)."""
    out = {}
    for line in filter(None, (l.strip() for l in (cos_value or "").splitlines())):
        if m := READ_LINE.match(line):
            out[int(m["id"])] = {"date": m["date"], "outcome": m["outcome"], "ground": m["ground"]}
    return out


def holds_since(root: Path, base: str, inst: str) -> dict[int, str]:
    """{row id: the date of the first `holds` reading in the row's latest unbroken run of `holds`}, read from the history
    of the home's `_cos.md` (each reading overwrites the last, so git keeps the run): one git call (#697 G1)."""
    seq: dict[int, list[tuple[str, str]]] = {}
    for line in git(root, "log", "--reverse", "-p", "--unified=0", "--format=@%h", base, "--",
                    f"{inst}/d-work/board/_cos.md").splitlines():
        if (m := READ_ADDED.match(line)) and (r := READ_LINE.match(m.group(1))):
            seq.setdefault(int(r["id"]), []).append((r["date"], r["outcome"]))
    out = {}
    for rid, rs in seq.items():
        since = None
        for date, outcome in rs:
            since = (since or date) if outcome == "holds" else None
        if since:
            out[rid] = since
    return out


def read_count(backlog: int) -> int:
    """How many backlog rows one run reads: five, or a tenth of the backlog, whichever is more (#697 G3)."""
    return max(GROOM_READ_MIN, -(-backlog // GROOM_READ_SHARE))


def read_label(rid: int, reading, since: str | None, stale_days: int, today: datetime.date) -> str:
    """The block's `read:` line: the last reading, or `never`; a `holds` held `stale_days` or more since its run began is
    marked `unwanted-candidate` (mechanical, #697 G1)."""
    if not reading:
        return "  read: never"
    line = f"  read: {reading['date']} {reading['outcome']} — {reading['ground']}"
    if reading["outcome"] == "holds" and since:
        try:
            held = (datetime.date.fromisoformat(reading["date"]) - datetime.date.fromisoformat(since)).days
        except ValueError:
            held = 0
        if held >= stale_days:
            line += f" (holds since {since}: unwanted-candidate)"
    return line


def fresh(reading, stale_days: int, today: datetime.date) -> bool:
    """A reading younger than `stale_days`: the run does not read the row again (#697)."""
    try:
        return bool(reading) and (today - datetime.date.fromisoformat(reading["date"])).days < stale_days
    except ValueError:
        return False


def age(opened: str, today: datetime.date) -> str:
    try:
        return f"{(today - datetime.date.fromisoformat(opened)).days}d"
    except ValueError:
        return "?"


def report(root: Path, base: str = "HEAD", now: float | None = None) -> list[str]:
    """The report's lines for the backlog on `base` of `root`."""
    hy = hygiene()
    inst = dyadlib.instance_rel(root) or "agent-corpus"
    rows = dyadlib.read_rows(root, at=base)
    byid = {r.id: r for r in rows}
    backlog = [r for r in rows if r.state == "backlog"]
    findings, candidates = hy.hygiene(root, base, time.time() if now is None else now)
    named = lines_by_row(findings + candidates, {r.id for r in backlog})
    boards = hy._board_files(root, base, inst)
    bd = dyadlib.load_guard("agent", "board")
    anchors = sorted(int(n) for n in boards if n.isdigit() and int(n) in byid
                     and byid[int(n)].state not in dyadlib.TERMINAL_STATES)
    cos = {n: f for n, f in boards.items() if bd.is_cos(n)}
    plans = dyadlib.show_many(root, base, [f"{inst}/d-work/plans/{r.id}.md" for r in rows])
    texts = {r.id: r.title + "\n" + plans.get(f"{inst}/d-work/plans/{r.id}.md", "") for r in rows}
    near = adjacency(rows, texts, backlog, anchors)
    on = dyadlib.slugs_on(root)
    lab = lambda i: dyadlib.row_label(i, byid, on)
    today = datetime.date.fromisoformat(dyadlib.utc_date())
    head = git(root, "rev-parse", "--short=12", base).strip() or base
    out = [f"groom report: {len(backlog)} backlog row(s) on {head}; {len(anchors)} board anchor(s) "
           f"(read-only: facts, never a judgement; the classes are the home's, by the play-book's criteria)"]
    stale_days = dyadlib.tunable(hy.TUNABLES["I1"], root)
    read = readings(cos.get("_cos", {}).get("read", ""))
    since = holds_since(root, base, inst) if read else {}
    unread = [r for r in backlog if not fresh(read.get(r.id), stale_days, today)]
    k = read_count(len(backlog))
    out.append(f"read this run: {min(k, len(unread))} of {len(unread)} unread or stale (five, or a tenth of the backlog; "
               f"oldest by opened first, as the blocks below)")
    order = lambda r: (fresh(read.get(r.id), stale_days, today), r.opened, r.id)   # #697: the oldest unread first
    for r in sorted(backlog, key=order):
        refs = list(dict.fromkeys(int(n) for n in REF.findall(r.refs or "")))
        plan = plans.get(f"{inst}/d-work/plans/{r.id}.md")
        promised = [n for n, f in cos.items() if re.search(rf"#{r.id}\b", f.get("promised", ""))]
        out.append(f"{lab(r.id)} [backlog, {age(r.opened, today)}] {r.title}")
        out.append("  refs: " + (", ".join(f"{lab(i)} {byid[i].state if i in byid else 'no such row'}" for i in refs) or "none"))
        out.append("  adjacency: " + (f"{lab(near[r.id][1])} {near[r.id][0]:.2f}" if near[r.id] else "none"))
        out.append("  promised: " + (", ".join(promised) or "none"))
        out.append("  roots: " + ((", ".join(roots_of(plan)) or "none named") if plan is not None else "no plan file"))
        out.append(read_label(r.id, read.get(r.id), since.get(r.id), stale_days, today))
        out.extend(f"  {line}" for line in named[r.id])
    stale = [l for l in hy.inflight(root, base, time.time() if now is None else now, None)
             if l.startswith(("inflight W2 ", "inflight W3 "))]   # #697 G4: verbatim, never recomputed
    out.append("stale work:" + ("" if stale else " none"))
    out.extend(f"  {l}" for l in stale)
    out.append("releases:")
    out.extend(releases(root))
    out.append(f"last grooming: {last_grooming(root)}")
    return out


def main(argv=None, root: Path | None = None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if a:
        print(f"refused: {USAGE}", file=sys.stderr); return 1
    print("\n".join(report(root or dyadlib.repo_root())))
    return 0


INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("roots-read-core-and-craft", lambda: roots_of("touches dyad/scripts/x.py, crafts/sysadmin/rules/a.md and dyad/b")
                                         == [dyadlib.CORE_CRAFT, "sysadmin"]),
    ("roots-skip-a-path-inside-another", lambda: roots_of("see agent-corpus/dyad/x and ../dyad/y") == []),
    ("lines-keep-every-named-row", lambda: lines_by_row(["candidate: #1 and #2 similar (0.40): a / b"], {1, 2, 3})
                                           == {1: ["candidate: #1 and #2 similar (0.40): a / b"],
                                               2: ["candidate: #1 and #2 similar (0.40): a / b"], 3: []}),
]
dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import

if __name__ == "__main__":
    sys.exit(main())
