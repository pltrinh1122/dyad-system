#!/usr/bin/env python3
"""Backlog hygiene for the automaton's sweep (d-work #565). Kernel: Python 3.12+, git.

The structural findings an automaton can make about the backlog, and a similarity ranking for the home's review. It
finds and ranks; it judges nothing (plan #565: the semantic problems are the home's). Read from one commit of `main`:

  I1 untouched        a backlog row no commit has touched (its row, plan or provenance file) in HYGIENE_STALE_DAYS
  I2 malformed title  an empty title, or one shaped like a flag (it starts with `-`)
  I4 orphaned         a backlog child whose `refs: parent #N` names a terminal row
  I12 worked          a commit on a fetched `origin` branch cites `d-work #N` for a backlog row
  ranking             TF-IDF cosine over each backlog row's title and plan text against every row, siblings under one
                      parent skipped and tokens in more than HYGIENE_MAX_DF of rows dropped; the top pairs at or above
                      HYGIENE_SIMILAR, listed as candidates and never as findings

Called only by `dyad automaton sweep` (scripts/automaton.py), which only the scheduled sweep runs. It is not a guard,
so the runner's discovery never picks it up and neither `check`, `check --evidence`, `check --corroborate`, the
pre-push gate nor CI runs it (plan #565, Placement). Every line it returns is information: no disposition shape
(TREE_INVARIANTS), so the inbox carries it as a notice.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("hygiene.py: Python 3.12+ required")
import math, re, subprocess
from collections import Counter
from pathlib import Path
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

HYGIENE_STALE_DAYS = 30        # I1: untouched this long
HYGIENE_SIMILAR = 0.35         # ranking: the lowest cosine listed
HYGIENE_MAX_DF = 0.20          # ranking: a token in more than this share of rows is boilerplate, dropped
HYGIENE_TOP = 10               # ranking: at most this many pairs
PARENT = re.compile(r"\bparent #(\d+)")
CITE = re.compile(r"\bd-work #(\d+)\b")
TOKEN = re.compile(r"[a-z][a-z0-9]{2,}")

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("thresholds-in-range", lambda: HYGIENE_STALE_DAYS > 0 and 0 < HYGIENE_SIMILAR < 1 and 0 < HYGIENE_MAX_DF < 1 and HYGIENE_TOP > 0),
]
TREE_INVARIANTS = [   # loads a guard, so never at import
    ("lines-are-information", lambda: not any(dyadlib.load_guard("agent", "inbox").DISPOSITION.search(l) for l in (
        "hygiene I1 untouched: backlog row #1 (a title), no commit in 31 days",
        "hygiene I4 orphaned: backlog row #2's parent #1 is done",
        "hygiene I12 worked: backlog row #3 is cited by abc on origin/x",
        "candidate: #4 and #5 similar (0.40): a / b"))),
]


def git(repo: Path, *a: str) -> str:
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, env=dyadlib.git_env(), timeout=300)
    return r.stdout if r.returncode == 0 else ""


def last_touched(repo: Path, base: str, inst: str) -> dict[int, int]:
    """{row id: unix time of the newest commit on `base` touching its row, plan or provenance file}, in one git call."""
    out, when = {}, 0
    for line in git(repo, "log", "--format=@%ct", "--name-only", base, "--",
                    f"{inst}/d-work/rows", f"{inst}/d-work/plans", f"{inst}/d-work/provenance").splitlines():
        if line.startswith("@"):
            when = int(line[1:]); continue
        m = re.search(r"/(\d+)\.md$", line)
        if m:
            out.setdefault(int(m.group(1)), when)          # log is newest first: the first time seen is the newest
    return out


def cited_on_branches(repo: Path) -> dict[int, tuple[str, str]]:
    """{row id: (commit, branch)} for `d-work #N` cited by a commit on a fetched `origin/*` branch other than main."""
    out = {}
    for ref in git(repo, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin").split():
        if ref in ("origin/main", "origin/HEAD", "origin"):
            continue
        for block in git(repo, "log", "--format=%H%x00%B%x01", f"origin/main..{ref}").split("\x01"):
            sha, _, body = block.strip().partition("\x00")
            for n in CITE.findall(body):
                out.setdefault(int(n), (sha[:12], ref))
    return out


def tokens(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def ranking(rows, texts: dict[int, str], backlog: list) -> list[tuple[float, int, int]]:
    """[(cosine, a, b)], best first: each backlog row against every row, by TF-IDF over `texts`, siblings skipped."""
    docs = {r.id: Counter(tokens(texts.get(r.id, r.title))) for r in rows}
    n = max(len(docs), 1)
    df = Counter(t for d in docs.values() for t in d)
    idf = {t: math.log(n / c) for t, c in df.items() if c / n <= HYGIENE_MAX_DF}
    vec = {i: {t: c * idf[t] for t, c in d.items() if t in idf} for i, d in docs.items()}
    norm = {i: math.sqrt(sum(v * v for v in w.values())) for i, w in vec.items()}
    parent = {r.id: (PARENT.search(r.refs or "") or [None, None])[1] for r in rows}
    seen, out = set(), []
    for r in backlog:
        for o in rows:
            if o.id == r.id or (min(o.id, r.id), max(o.id, r.id)) in seen or not norm[r.id] or not norm[o.id]:
                continue
            if parent[r.id] and parent[r.id] == parent[o.id]:
                continue                                    # siblings share their parent's boilerplate (A5)
            seen.add((min(o.id, r.id), max(o.id, r.id)))
            cos = sum(v * vec[o.id].get(t, 0.0) for t, v in vec[r.id].items()) / (norm[r.id] * norm[o.id])
            if cos >= HYGIENE_SIMILAR:
                out.append((cos, min(o.id, r.id), max(o.id, r.id)))
    return sorted(out, key=lambda x: (-x[0], x[1], x[2]))[:HYGIENE_TOP]


def hygiene(repo: Path, base: str, now: float) -> tuple[list[str], list[str]]:
    """(findings, candidates) for the backlog on `base`: `hygiene I…` lines, and `candidate:` ranking lines."""
    inst = dyadlib.instance_rel(repo) or "agent-corpus"
    rows = dyadlib.read_rows(repo, at=base)
    byid = {r.id: r for r in rows}
    backlog = [r for r in rows if r.state == "backlog"]
    touched, cited = last_touched(repo, base, inst), cited_on_branches(repo)
    findings = []
    for r in backlog:
        days = (now - touched[r.id]) / 86400 if r.id in touched else None
        if days is not None and days > HYGIENE_STALE_DAYS:
            findings.append(f"hygiene I1 untouched: backlog row #{r.id} ({r.title[:60]}), no commit in {int(days)} days")
        if not r.title.strip() or r.title.lstrip().startswith("-"):
            findings.append(f"hygiene I2 malformed title: backlog row #{r.id} has the title {r.title[:40]!r}")
        p = PARENT.search(r.refs or "")
        if p and int(p.group(1)) in byid and byid[int(p.group(1))].state in dyadlib.TERMINAL_STATES:
            findings.append(f"hygiene I4 orphaned: backlog row #{r.id}'s parent #{p.group(1)} is {byid[int(p.group(1))].state}")
        if r.id in cited:
            sha, ref = cited[r.id]
            findings.append(f"hygiene I12 worked: backlog row #{r.id} is cited by {sha} on {ref}")
    texts = {}
    for r in backlog:
        texts[r.id] = r.title + "\n" + git(repo, "show", f"{base}:{inst}/d-work/plans/{r.id}.md")
    malformed = {r.id for r in backlog if not r.title.strip() or r.title.lstrip().startswith("-")}
    ranked = [r for r in rows if r.id not in malformed]          # an I2 row has no title to compare: a finding already
    candidates = [f"candidate: #{a} and #{b} similar ({c:.2f}): {byid[a].title[:50]} / {byid[b].title[:50]}"
                  for c, a, b in ranking(ranked, texts, [r for r in backlog if r.id not in malformed])]
    return findings, candidates


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import
