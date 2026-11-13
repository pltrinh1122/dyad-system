#!/usr/bin/env python3
"""Backlog hygiene for the automaton's sweep (d-work #565). Kernel: Python 3.12+, git.

The structural findings an automaton can make about the backlog, and a similarity ranking for the home's review. It
finds and ranks; it judges nothing (plan #565: the semantic problems are the home's). Read from one commit of `main`:

  I1 untouched        a backlog row no commit has touched (its row, plan or provenance file) in `hygiene-stale-days`
  I2 malformed title  an empty title, or one shaped like a flag (it starts with `-`)
  I4 orphaned         a backlog child whose `refs: parent #N` names a terminal row
  I12 worked          a commit on a fetched `origin` branch cites `d-work #N` for a backlog row
  ranking             TF-IDF cosine over each backlog row's title and plan text against every row, siblings under one
                      parent skipped and tokens in more than HYGIENE_MAX_DF of rows dropped; the top pairs at or above
                      `hygiene-similar` (at most `hygiene-top`), listed as candidates and never as findings

Work in flight (d-work #569), `inflight W…` lines, each read from records alone (plan #569's falsification) and
worded from fixed record times, never a computed age, so a finding told once is not new again until its record moves:

  W1  relay unread        a `relay` with no `.read` marker, sent over `inflight-unread-hours` ago (told to home only, A2)
  W2  planned row quiet   a planned row the board says waits on a unit, with no citing commit, PR update, board write
                          or plan-`Y` in `inflight-planned-quiet-days` (A3: rows waiting on the operator are not counted)
  W3  open, no plan       an open row with no plan file, opened over `inflight-unplanned-hours` ago; a child (`refs: parent
                          #N`) or a row under a mandate is exempt (A4, Rule-15)
  W4  orphan PR           an open PR citing no `d-work #N` of a live row (prs.py's parse, A5)
  W5  orphan branch       an origin branch whose tip is not on main, with no open PR and no commit citing a live row (A6)
  W6  stale PR head       an open PR on a live row whose head commit is over `inflight-pr-still-days` old
  W7a unit not in table   a unit a live board entry names that its cabinet's `_cos` `seats` does not
  W7b unit stale          a live entry waiting on a unit whose presence file is stale; skipped with one line until the
                          presence store holds a fresh file (gated on #567, A7)
  W7c retired form        a live entry whose `waiting-on` still holds the removed `seat <name>` (#604): W2, W7a and W7b
                          read `unit <name>` only, so the entry is named here with the board guard's refusal, never skipped
  W8  promise kept listed a `promised` entry of a board file listed over `inflight-promise-days` (its age: git history, A8)
  W9  operator wait       a live row waiting on the operator: with no question, once; with a question older than
                          `inflight-question-hours` (A9)
  W10' report after board an owner's report on a row, to home, newer than the row's board `since` (A10)
  W11 phase age           a phased board entry (#587) whose `since` is older than its phase's threshold:
                          `done-ready` the tunable `inflight-done-ready-hours` (#587 S9: a drafted Done held 13 h), every
                          other phase INFLIGHT_W11_HOURS (an asked phase 24 h, every other 3 days): plan #587 F5's one
                          rule, "phase older than N", worded from the entry's `since` alone

A ring owed (#587 X8: a relay posted by home to a unit, unread) is W1: every unread `relay` is one, whoever sent it,
and a `report` or `notice` home posts never rings (`land.ring_list` rings every kind but `notice`, and the machine's
relays to a unit are all of kind `relay`). W1's threshold is 4 h, not X8's hour: the sweep runs twice a day, so a
lower threshold would tell nothing sooner.

Per cabinet (#594): each entry is read with its own cabinet's `_cos[-<operator>]` file — W7a against that file's
`seats`, W8 over every `_cos` file, W10' in that cabinet's holder's box — and `inflight_cabinets` returns each line
with the cabinet it concerns (a row's entry's, `program` for a row with none and for a line about no row), so the
sweep tells each cabinet's home its own lines.

The hosting's open PRs (W4–W6) are read by the caller with `GITHUB_TOKEN`; without them those kinds print one skip line.
Clustering waits for typed refs (plan #569 decision 3).

Called only by `dyad automaton sweep` (scripts/automaton.py), which only the scheduled sweep runs. It is not a guard,
so the runner's discovery never picks it up and neither `check`, `check --evidence`, `check --corroborate`, the
pre-push gate nor CI runs it (plan #565, Placement). Every line it returns is information: no disposition shape
(TREE_INVARIANTS), so the inbox carries it as a notice.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("hygiene.py: Python 3.12+ required")
import re, subprocess
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib
import similar                       # #642: tokens, tfidf and cosine have one implementation, similar.py
from similar import tokens, cosine   # noqa: F401 (re-exported: intent.py and groom.py read them through hygiene)

# The operator-tunable thresholds (d-work #590): each a preference key, read at use time by `dyadlib.tunable`, whose
# default has one home, its DMC record's `dyad:defaultValue` (dmc/backlog-hygiene.jsonld, dmc/work-in-flight.jsonld).
TUNABLES = {
    "I1": "hygiene-stale-days",            # I1: untouched this long (days)
    "similar": "hygiene-similar",          # ranking: the lowest cosine listed
    "top": "hygiene-top",                  # ranking: at most this many pairs
    "W1": "inflight-unread-hours",         # W1: a relay unread this long (minimum ages: the sweep runs every 12 hours, A11)
    "W2": "inflight-planned-quiet-days",   # W2: a planned row quiet this long
    "W3": "inflight-unplanned-hours",      # W3: an open row with no plan this long
    "W6": "inflight-pr-still-days",        # W6: an open PR's head unchanged this long
    "W8": "inflight-promise-days",         # W8: a promise listed this long
    "W9": "inflight-question-hours",       # W9: a recorded question to the operator this old
    "W11": "inflight-done-ready-hours",    # W11: a phased entry in done-ready this long (#587 S9)
}
HYGIENE_MAX_DF = 0.20          # ranking: a token in more than this share of rows is boilerplate, dropped (an engineering constant)
PARENT = re.compile(r"\bparent #(\d+)")
CITE = re.compile(r"\bd-work #(\d+)\b")
ROW_REF = re.compile(r"\brow #(\d+)")          # the row an `inflight` line is about (#594: its cabinet's home is told)
INFLIGHT_W11_HOURS = {          # W11 (#587 F5): a phased entry in this phase longer than this; asked phases 24 h
    "planning": 72, "intent-asked": 24, "plan-ready": 72, "plan-asked": 24, "building": 72, "verifying": 72,
    "done-asked": 24, "landing": 72, "held": 72}
INFLIGHT_W11_TUNED = {"done-ready": "W11"}   # #587 S9: the phases whose threshold is a tunable (a TUNABLES key), never a constant
INFLIGHT_KINDS = ("W1", "W2", "W3", "W4", "W5", "W6", "W7a", "W7b", "W7c", "W8", "W9", "W10'", "W11")

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("max-df-in-range", lambda: 0 < HYGIENE_MAX_DF < 1),
    ("tunable-keys-distinct", lambda: len(set(TUNABLES.values())) == len(TUNABLES) == 10 and len(set(INFLIGHT_KINDS)) == 13),
    ("w11-covers-every-phase", lambda: set(INFLIGHT_W11_HOURS) | set(INFLIGHT_W11_TUNED) == set(dyadlib.ORCH_PHASES)
                                       and not set(INFLIGHT_W11_HOURS) & set(INFLIGHT_W11_TUNED)
                                       and set(INFLIGHT_W11_TUNED.values()) <= set(TUNABLES)
                                       and all(h > 0 for h in INFLIGHT_W11_HOURS.values())
                                       and all(INFLIGHT_W11_HOURS[p] == 24 for p in dyadlib.ORCH_ASKED)),
]
TREE_INVARIANTS = [   # loads a guard or reads the DMC store, so never at import
    ("tunables-are-the-records", lambda: set(TUNABLES.values()) == dyadlib.tunables_read_by("scripts/hygiene.py")),   # #590: one home
    ("lines-are-information", lambda: not any(dyadlib.load_guard("agent", "inbox").DISPOSITION.search(l) for l in (
        "hygiene I1 untouched: backlog row #1 (a title), no commit in 31 days",
        "hygiene I4 orphaned: backlog row #2's parent #1 is done",
        "hygiene I12 worked: backlog row #3 is cited by abc on origin/x",
        "candidate: #4 and #5 similar (0.40): a / b",
        "inflight W1 relay unread: row #6's relay to engineer-1 sent 2026-11-03T10:00:00Z has no read marker",
        "inflight W9 operator wait: row #7 waits on the operator with no question recorded",
        "inflight W11 phase age: row #8 in done-asked since 2026-11-03T10:00Z"))),
]


def git(repo: Path, *a: str) -> str:
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, env=dyadlib.git_env(), timeout=300)
    return r.stdout if r.returncode == 0 else ""


MEANINGFUL = r"^(state|disposed):"   # #697: a row edit that moves it (git's -G), never a slug or a format write

def last_touched(repo: Path, base: str, inst: str) -> dict[int, int]:
    """{row id: unix time of the newest commit on `base` that meaningfully touched the row}: one changing a row file's
    `state` or `disposed` line (its birth included), or touching its plan or provenance file. A bulk write that changes
    only rows' `slug` or format — the slug backfill 5dce3019 — no longer resets I1 (#697). Two git calls, run at once,
    so `dyad board resume` pays one call's time; a commit moving one row's state and another's slug together counts
    for both, which only makes a row look fresher, never staler."""
    from concurrent.futures import ThreadPoolExecutor
    calls = (["log", "--format=@%ct", "--name-only", f"-G{MEANINGFUL}", base, "--", f"{inst}/d-work/rows"],
             ["log", "--format=@%ct", "--name-only", base, "--", f"{inst}/d-work/plans", f"{inst}/d-work/provenance"])
    with ThreadPoolExecutor(2) as pool:
        logs = list(pool.map(lambda a: git(repo, *a), calls))
    out = {}
    for text in logs:
        when = 0
        for line in text.splitlines():
            if line.startswith("@"):
                when = int(line[1:]); continue
            m = re.search(r"/(\d+)\.md$", line)
            if m:
                out[int(m.group(1))] = max(out.get(int(m.group(1)), 0), when)   # newest first per log: max is the newest
    return out


def cited_on_branches(repo: Path) -> dict[int, tuple[str, str]]:
    """{row id: (commit, branch)} for `d-work #N` cited by a commit on a fetched `origin/*` branch other than main."""
    out = {}
    # #617: one `git log --source` over every origin branch, not one log per branch (511 branches took 20 s); each
    # commit is named with the ref git reached it from, and the newest citing commit wins
    for block in git(repo, "log", "--source", "--format=%H%x00%S%x00%B%x01", "--remotes=origin",
                     "--exclude=refs/remotes/origin/HEAD", "--not", "origin/main").split("\x01"):
        sha, _, rest = block.strip().partition("\x00")
        ref, _, body = rest.partition("\x00")
        ref = ref.removeprefix("refs/remotes/")
        if not sha or ref in ("origin/main", "origin/HEAD", "origin"):
            continue
        for n in CITE.findall(body):
            out.setdefault(int(n), (sha[:12], ref))
    return out


def tfidf(docs: dict) -> tuple[dict, dict]:
    """({key: {token: weight}}, {key: norm}) of `docs` ({key: text}): `similar.tfidf` with HYGIENE_MAX_DF, the one
    weighting `ranking` and `intent.candidates` (#615) read; the implementation is `similar.py`'s (#642)."""
    return similar.tfidf(docs, HYGIENE_MAX_DF)


def ranking(rows, texts: dict[int, str], backlog: list, root: Path | None = None) -> list[tuple[float, int, int]]:
    """[(cosine, a, b)], best first: each backlog row against every row, by TF-IDF over `texts`, siblings skipped; at
    most `hygiene-top` pairs at or above `hygiene-similar`, both read from `root`'s preferences."""
    similar, top = dyadlib.tunable(TUNABLES["similar"], root), dyadlib.tunable(TUNABLES["top"], root)
    vec, norm = tfidf({r.id: texts.get(r.id, r.title) for r in rows})
    parent = {r.id: (PARENT.search(r.refs or "") or [None, None])[1] for r in rows}
    seen, out = set(), []
    for r in backlog:
        for o in rows:
            if o.id == r.id or (min(o.id, r.id), max(o.id, r.id)) in seen or not norm[r.id] or not norm[o.id]:
                continue
            if parent[r.id] and parent[r.id] == parent[o.id]:
                continue                                    # siblings share their parent's boilerplate (A5)
            seen.add((min(o.id, r.id), max(o.id, r.id)))
            cos = cosine(vec, norm, r.id, o.id)
            if cos >= similar:
                out.append((cos, min(o.id, r.id), max(o.id, r.id)))
    return sorted(out, key=lambda x: (-x[0], x[1], x[2]))[:top]


def hygiene(repo: Path, base: str, now: float, prefs: Path | None = None) -> tuple[list[str], list[str]]:
    """(findings, candidates) for the backlog on `base`: `hygiene I…` lines, and `candidate:` ranking lines."""
    inst = dyadlib.instance_rel(repo) or "agent-corpus"
    rows = dyadlib.read_rows(repo, at=base)
    byid = {r.id: r for r in rows}
    backlog = [r for r in rows if r.state == "backlog"]
    touched, cited = last_touched(repo, base, inst), cited_on_branches(repo)
    stale_days = dyadlib.tunable(TUNABLES["I1"], prefs or repo)   # `prefs`: the sweep's worktree at `base` (#590)
    findings = []
    for r in backlog:
        days = (now - touched[r.id]) / 86400 if r.id in touched else None
        if days is not None and days > stale_days:
            findings.append(f"hygiene I1 untouched: backlog row #{r.id} ({r.title[:60]}), no commit in {int(days)} days")
        if not r.title.strip() or r.title.lstrip().startswith("-"):
            findings.append(f"hygiene I2 malformed title: backlog row #{r.id} has the title {r.title[:40]!r}")
        p = PARENT.search(r.refs or "")
        if p and int(p.group(1)) in byid and byid[int(p.group(1))].state in dyadlib.TERMINAL_STATES:
            findings.append(f"hygiene I4 orphaned: backlog row #{r.id}'s parent #{p.group(1)} is {byid[int(p.group(1))].state}")
        if r.id in cited:
            sha, ref = cited[r.id]
            findings.append(f"hygiene I12 worked: backlog row #{r.id} is cited by {sha} on {ref}")
    plans = dyadlib.show_many(repo, base, [f"{inst}/d-work/plans/{r.id}.md" for r in backlog])   # one process (#617)
    texts = {r.id: r.title + "\n" + plans.get(f"{inst}/d-work/plans/{r.id}.md", "") for r in backlog}
    malformed = {r.id for r in backlog if not r.title.strip() or r.title.lstrip().startswith("-")}
    ranked = [r for r in rows if r.id not in malformed]          # an I2 row has no title to compare: a finding already
    candidates = [f"candidate: #{a} and #{b} similar ({c:.2f}): {byid[a].title[:50]} / {byid[b].title[:50]}"
                  for c, a, b in ranking(ranked, texts, [r for r in backlog if r.id not in malformed], prefs or repo)]
    return findings, candidates


# ---- work in flight (d-work #569)
def _when(v: str):
    """A record time (`2026-11-03T10:00Z`, an ISO stamp, or a date) as an aware datetime; None when unreadable."""
    import datetime
    v = (v or "").strip()
    try:
        d = datetime.datetime.fromisoformat(v)
    except ValueError:
        try:
            d = datetime.datetime.combine(datetime.date.fromisoformat(v[:10]), datetime.time())
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)


def _board_files(repo: Path, base: str, inst: str) -> dict[str, dict[str, str]]:
    bd = dyadlib.load_guard("agent", "board")
    d = f"{inst}/d-work/board"
    names = [n for n in git(repo, "ls-tree", "--name-only", f"{base}:{d}").split() if n.endswith(".md")]
    got = dyadlib.show_many(repo, base, [f"{d}/{n}" for n in names])
    return {n[:-3]: bd.parse(got.get(f"{d}/{n}", ""))[0] for n in names}


def _units(field: str) -> list[str]:
    """The unit a `waiting-on` names (`unit <name>`; `seat <name>` removed in 1.0, #604), as a one-item list, else []."""
    w = field.split()
    return [w[1]] if len(w) >= 2 and w[0] == "unit" else []


def _messages(repo: Path, base: str, inst: str) -> list[dict[str, str]]:
    """Every inbox message on `base`, each with `_box` and `_read` (its `.read` marker exists)."""
    bd = dyadlib.load_guard("agent", "board")
    root = f"{inst}/d-work/inbox/"
    names = git(repo, "ls-tree", "-r", "--name-only", base, root).split()
    marks = {n[:-5] for n in names if n.endswith(".read")}
    got = dyadlib.show_many(repo, base, [n for n in names if n.endswith(".md")])   # one process (#617)
    out = []
    for n in names:
        if n.endswith(".md"):
            f = bd.parse(got.get(n, ""))[0]
            f["_box"], f["_read"] = n[len(root):].split("/")[0], n[:-3] in marks
            out.append(f)
    return out


def _cited_times(repo: Path) -> dict[int, int]:
    """{row id: unix time of the newest commit, on any fetched origin ref, whose message cites `d-work #N`}."""
    out = {}
    for block in git(repo, "log", "--remotes=origin", "--format=%ct%x00%B%x01").split("\x01"):
        ct, _, body = block.strip().partition("\x00")
        if ct.isdigit():
            for n in CITE.findall(body):
                out[int(n)] = max(out.get(int(n), 0), int(ct))
    return out


def _promise_since(repo: Path, base: str, rel: str, text: str, log: dict | None = None) -> int | None:
    """Unix time of the newest commit on `base` that added `text` to `rel`, the start of its listing: the newest commit
    whose patch adds more occurrences of `text` than it removes, as git's pickaxe (`-S`) reads a change of count. `log`
    caches each file's one `git log -p` across promises (#617: one process per file, not one pickaxe per promise)."""
    if log is None or rel not in log:
        commits, cur = [], None
        for line in git(repo, "log", "-p", "--format=@%ct", "--no-color", "--no-ext-diff", base, "--", rel).splitlines():
            if line.startswith("@") and line[1:].isdigit():
                cur = [int(line[1:]), [], []]; commits.append(cur)
            elif cur is not None and line.startswith("+") and not line.startswith("+++"):
                cur[1].append(line[1:])
            elif cur is not None and line.startswith("-") and not line.startswith("---"):
                cur[2].append(line[1:])
        if log is None:
            log = {}
        log[rel] = commits
    for when, added, removed in log[rel]:                 # newest first
        if "\n".join(added).count(text) > "\n".join(removed).count(text):
            return when
    return None


def inflight(repo: Path, base: str, now: float, pulls: list[dict] | None,
             presence_fresh=None, prefs: Path | None = None) -> list[str]:
    """`inflight W…` lines for the work in flight on `base` (module docstring). `pulls` is the hosting's open PRs as
    [{number, body, title, head_ref, head_sha}], or None when it was not read (W4–W6 then skip with one line).
    `presence_fresh(seat, now)` says whether a seat's presence is fresh; None reads the presence store on `base`.
    The thresholds are read from `prefs`'s preferences (the sweep's worktree at `base`, #590), else `repo`'s."""
    return [line for _, line in inflight_cabinets(repo, base, now, pulls, presence_fresh, prefs)]


def inflight_cabinets(repo: Path, base: str, now: float, pulls: list[dict] | None,
                      presence_fresh=None, prefs: Path | None = None) -> list[tuple[str, str]]:
    """`inflight`'s lines, each as (cabinet, line) (#594): the cabinet of the row the line is about — its board entry's,
    `program` when it has none — and `program` for a line about no row."""
    import datetime
    nowdt = datetime.datetime.fromtimestamp(now, datetime.timezone.utc)
    inst = dyadlib.instance_rel(repo) or "agent-corpus"
    rows = {r.id: r for r in dyadlib.read_rows(repo, at=base)}
    live = {i for i, r in rows.items() if r.state not in dyadlib.TERMINAL_STATES and r.state != "backlog"}
    bd = dyadlib.load_guard("agent", "board")
    boards = _board_files(repo, base, inst)
    coses = {bd.cos_cabinet(n): boards.pop(n) for n in sorted(boards) if bd.is_cos(n)}
    filed = {int(n): bd.entry_cabinet(f) for n, f in boards.items() if n.isdigit()}
    entries = {int(n): f for n, f in boards.items() if n.isdigit() and int(n) in live}
    homes = {c: f.get("holder") for c, f in coses.items()}
    msgs = _messages(repo, base, inst)
    special: dict[str, str] = {}                         # a line tagged from its file, not its text: W7a, every W8
    def cab(row) -> str:
        return filed.get(int(row), bd.SOLO) if str(row).isdigit() else bd.SOLO
    w = {k: dyadlib.tunable(TUNABLES[k], prefs or repo) for k in ("W1", "W2", "W3", "W6", "W8", "W9", "W11")}   # read now, never at import
    out = []
    # W1: a relay no one has read
    for m in msgs:
        sent = _when(m.get("sent", ""))
        if m.get("kind") == "relay" and not m["_read"] and sent and (nowdt - sent).total_seconds() > w["W1"] * 3600:
            out.append(f"inflight W1 relay unread: row #{m.get('row')}'s relay to {m['_box']} sent {m.get('sent')} has no "
                       f"read marker (over {w['W1']}h)")
    # W2: a planned row waiting on a unit, quiet
    cited = _cited_times(repo)
    pr_rows = {}
    for p in pulls or []:
        for n in CITE.findall(f"{p.get('title', '')}\n{p.get('body') or ''}"):
            t = _when(p.get("updated_at", ""))
            if t:
                pr_rows[int(n)] = max(pr_rows.get(int(n), 0), int(t.timestamp()))
    for i, f in sorted(entries.items()):
        r = rows[i]
        if r.state != "planned" or not _units(f.get("waiting-on", "")):
            continue
        plan_y = [e for e in r.disposed.split(";") if " Y plan" in e]
        marks = [cited.get(i, 0), pr_rows.get(i, 0)]
        for v in (f.get("since", ""), plan_y[-1].strip()[:10] if plan_y else ""):
            if (t := _when(v)):
                marks.append(int(t.timestamp()))
        last = max(marks)
        if last and now - last > w["W2"] * 86400:
            stamp = datetime.datetime.fromtimestamp(last, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
            out.append(f"inflight W2 planned row quiet: row #{i} waits on {f['waiting-on']} with nothing since {stamp} "
                       f"(no citing commit, PR update, board write or plan-Y; over {w['W2']} days)")
    # W3: an open row with no plan file
    plans = set(git(repo, "ls-tree", "--name-only", f"{base}:{inst}/d-work/plans").split())
    for i in sorted(live):
        r = rows[i]
        if r.state != "open" or f"{i}.md" in plans or PARENT.search(r.refs or "") or "mandate #" in r.disposed:
            continue
        added = git(repo, "log", "--diff-filter=A", "--format=%ct", base, "--", f"{inst}/d-work/rows/{i}.md").split()
        t = int(added[-1]) if added else int(_when(r.opened).timestamp()) if _when(r.opened) else None
        if t and now - t > w["W3"] * 3600:
            out.append(f"inflight W3 open, no plan: row #{i} ({r.title[:50]}), opened {r.opened}, has no plan file "
                       f"(over {w['W3']}h)")
    # W4, W6: open PRs; W5: branches
    if pulls is None:
        out.append("inflight W4-W6 skipped: the hosting's open PRs were not read (no GITHUB_TOKEN/GITHUB_REPOSITORY)")
    else:
        for p in sorted(pulls, key=lambda p: p["number"]):
            ids = {int(n) for n in CITE.findall(f"{p.get('title', '')}\n{p.get('body') or ''}")}
            ref = f"refs/remotes/origin/{p.get('head_ref', '')}"
            ids |= {int(n) for n in CITE.findall(git(repo, "log", "--format=%B", f"{base}..{ref}"))} if p.get("head_ref") else set()
            on = sorted(ids & live)
            if not on:
                out.append(f"inflight W4 orphan PR: PR #{p['number']} cites no live row"
                           + (f" (cites {', '.join(f'#{n}' for n in sorted(ids))})" if ids else " (cites none)"))
                continue
            ct = git(repo, "log", "-1", "--format=%ct", p.get("head_sha", "")).strip()
            if ct.isdigit() and now - int(ct) > w["W6"] * 86400:
                stamp = datetime.datetime.fromtimestamp(int(ct), datetime.timezone.utc).strftime("%Y-%m-%d")
                out.append(f"inflight W6 stale PR head: PR #{p['number']} on row #{on[0]} has head {p['head_sha'][:12]} "
                           f"of {stamp} (over {w['W6']} days)")
        open_refs = {p.get("head_ref") for p in pulls}
        for ref in git(repo, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin").split():
            name = ref.removeprefix("origin/")
            if name in ("main", "HEAD") or ref == "origin" or name in open_refs:
                continue
            if subprocess.run(["git", "merge-base", "--is-ancestor", ref, base], cwd=repo, env=dyadlib.git_env(),
                              capture_output=True).returncode == 0:
                continue
            ids = {int(n) for n in CITE.findall(git(repo, "log", "--format=%B", f"{base}..{ref}"))}
            if ids & live:
                continue
            tip = git(repo, "log", "-1", "--format=%h %cs", ref).split()
            out.append(f"inflight W5 orphan branch: {name} (tip {tip[0] if tip else '?'} of {tip[1] if len(tip) > 1 else '?'}) "
                       f"is not on main, has no open PR and no commit citing a live row")
    # W7a: a unit the board names that its cabinet's unit table does not
    for c in sorted(set(coses) | {bd.SOLO}):
        table = set(bd.owners({"owner": coses.get(c, {}).get("seats", "").replace("\n", ";")}))
        if table:
            named = {u for i, f in entries.items() if filed.get(i, bd.SOLO) == c
                     for u in bd.owners(f) + _units(f.get("waiting-on", ""))}
            for u in sorted(named - table):
                line = f"inflight W7a unit not in table: {u} is named on the board but not in {bd.cos_name(c)}'s seats"
                out.append(line); special[line] = c
    # W7b: waiting on a unit whose presence is stale, gated on a presence store that holds a fresh file (#567)
    sv = dyadlib.load_guard("agent", "sessions")
    if presence_fresh is None:
        d = f"{inst}/d-work/sessions"
        seen = {n[:-3]: sv.parse(git(repo, "show", f"{base}:{d}/{n}")).get("seen", "")
                for n in git(repo, "ls-tree", "--name-only", f"{base}:{d}").split() if n.endswith(".md")}
        presence_fresh = lambda seat, at: bool(seen.get(seat)) and not sv.is_stale(seen[seat], at)
        gate = any(not sv.is_stale(v, nowdt) for v in seen.values() if v)
    else:
        gate = True
    if not gate:
        out.append("inflight W7b skipped: the presence store holds no fresh file (gated on #567)")
    else:
        for i, f in sorted(entries.items()):
            for u in _units(f.get("waiting-on", "")):
                if not presence_fresh(u, nowdt):
                    out.append(f"inflight W7b unit stale: row #{i} waits on {u}, whose presence file is stale")
    # W7c: the removed `seat <name>` form (#604), which W2/W7a/W7b no longer read, so never skipped without a line
    for i, f in sorted(entries.items()):
        if (refusal := bd.retired_waiting(f.get("waiting-on", ""))):
            out.append(f"inflight W7c retired form: row #{i}'s board entry {refusal}")
    # W8: a promise still listed
    patches: dict = {}                                   # one `git log -p` per board file (#617)
    for name, f in [(bd.cos_name(c), f) for c, f in coses.items()] + [(str(i), f) for i, f in sorted(entries.items())]:
        for promise in [x.strip() for x in f.get("promised", "").replace("\n", ";").split(";") if x.strip()]:
            t = _promise_since(repo, base, f"{inst}/d-work/board/{name}.md", promise, patches)
            if t and now - t > w["W8"] * 86400:
                stamp = datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%d")
                line = (f"inflight W8 promise still listed: board {name} has promised {promise[:80]!r} since {stamp} "
                        f"(over {w['W8']} days)")
                out.append(line)                         # tagged from its file, never by a `row #` in the promise's text
                special[line] = bd.cos_cabinet(name) if bd.is_cos(name) else filed.get(int(name), bd.SOLO)
    # W9: waiting on the operator
    for i, f in sorted(entries.items()):
        if f.get("waiting-on") != "operator":
            continue
        if not f.get("question"):
            out.append(f"inflight W9 operator wait: row #{i} waits on the operator with no question recorded")
        elif (t := _when(f.get("since", ""))) and (nowdt - t).total_seconds() > w["W9"] * 3600:
            out.append(f"inflight W9 operator wait: row #{i}'s question to the operator stands since {f['since']} "
                       f"(over {w['W9']}h)")
    # W10': an owner's report newer than the board
    for i, f in sorted(entries.items()):
        since, owners = _when(f.get("since", "")), set(bd.owners(f))
        late = [m for m in msgs if m["_box"] == homes.get(filed.get(i, bd.SOLO)) and m.get("kind") == "report" and m.get("row") == str(i)
                and m.get("from") in owners and since and (t := _when(m.get("sent", ""))) and t > since]
        if late:
            m = max(late, key=lambda m: m.get("sent", ""))
            out.append(f"inflight W10' report after board: row #{i}'s board since {f.get('since')}, but {m['from']} "
                       f"reported on it at {m.get('sent')}")
    out += phase_age(entries, nowdt, {p: w[k] for p, k in INFLIGHT_W11_TUNED.items()})
    return [(special[line] if line in special else cab(m[1]) if (m := ROW_REF.search(line)) else bd.SOLO, line)
            for line in out]


def phase_age(entries: dict[int, dict[str, str]], nowdt, tuned: dict[str, int | float]) -> list[str]:
    """W11 (#587 F5): `inflight W11 phase age: row #N in <phase> since <since>` for each phased entry whose `since` is
    older than its phase's threshold, `tuned` (the INFLIGHT_W11_TUNED phases' hours, read by the caller at run time)
    over INFLIGHT_W11_HOURS; worded from the record alone, never a computed age, so the line is new
    again only when the entry moves. An unphased entry, an unknown phase or an unreadable `since` says nothing (the
    board guard names a malformed one)."""
    bd = dyadlib.load_guard("agent", "board")
    hours = {**INFLIGHT_W11_HOURS, **tuned}
    out = []
    for i, f in sorted(entries.items()):
        p = bd.phase_name(f)
        t = _when(f.get("since", ""))
        if p in hours and t and (nowdt - t).total_seconds() > hours[p] * 3600:
            out.append(f"inflight W11 phase age: row #{i} in {p} since {f['since']}")
    return out


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import
