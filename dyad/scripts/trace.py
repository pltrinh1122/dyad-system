#!/usr/bin/env python3
"""d-work trace (core script; Rule-3 owns the trace's place in the completion evidence, the play-book
`dyad/playbooks/dwork-trace.md` its format and reading; d-work #213, format agreed in plan #212). Kernel:
Python 3.12+, stdlib.
A **d-work trace** places every second of one d-work, from its first anchored Operator prompt to its Done-`Y`
(before one, to the transcript's last record: the completion reply's preview), in exactly one bucket — the Operator's wait, the Agent's inference, or a mechanical kind — and
adds its timeline, counts and bottleneck line. Its inputs, all read in place and never copied:
- the row, its provenance record and its plan file (`<instance>/d-work/{rows,provenance,plans}/<id>.md`);
- git: the commits that cite `d-work #<id>` or touch those three files, and the merges on the first-parent
  line of HEAD that landed them;
- harness transcripts (JSON lines; Claude Code's layout, the kernel row of Rule-14 property 2): `--transcript
  <path>` (repeatable), else the newest one in the harness's `projects/<slug>/` directory under the home
  directory, the slug being the working tree's path with every non-alphanumeric character a `-`.
A transcript is optional (Rule-14: another CLI inferencing agent keeps none in this layout): without one the
trace holds the git and ledger timeline and says the buckets are absent. A trace never prints transcript
text — only timestamps, durations, tool names and numbers derived from it (Rule-7 property 2).
Anchoring: each provenance entry's fenced text is matched to an Operator message (whitespace-normalized;
equal, or contained when the entry is at least SHORT characters long), in record order, each after the
previous anchor. A disposition is anchored only to a message that answers a `Y/N:` line naming `#<id>`; a
prompt that matches more than one message is ambiguous. An unmatched or ambiguous entry is reported under
Limits and never guessed.
The store `<instance>/d-work/traces/<id>.md` (written by `--out`, in the Done ledger commit; plan #213 revision 2)
is checked by `check_store`: one `<id>.md` per existing row, headed `# Trace #<id> — <title>`, its five sections.
  trace.py <id> [--transcript <path>]... [--out]     (reached as `dyad dwork trace`)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("trace.py: Python 3.12+ required")
import datetime, json, re, statistics, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

# The buckets, in report order. Every second of the window is in exactly one (the sweep's priority, below).
BUCKETS = ("operator", "idle", "inference", "suite", "guards", "github", "git/local", "subagent", "background", "other")
PARTITIONS = {"operator": ("operator", "idle"),
              "agent": ("inference", "suite", "guards", "github", "git/local", "subagent", "background", "other")}
MECHANICAL = ("suite", "guards", "github", "git/local", "subagent", "other")   # a tool's kind; overlapping calls take the first
PRIORITY = ("operator", "idle", "background") + MECHANICAL           # uncovered time is inference
MEANING = {
    "operator": "a reply ending in a `Y/N:` line, to the Operator's next message",
    "idle": "a reply with no `Y/N:` line, to the Operator's next message",
    "inference": "a tool result or message, to the Agent's next tool call or reply (wall gap)",
    "suite": "a Bash call running the push gate, `check --evidence` or `--tests` whose result shows a test run (`Ran N tests`)",
    "guards": "a `git push` whose gate ran guards only (a ledger-only or empty range: no `Ran N tests` in its result)",
    "github": "a GitHub tool call, or a Bash `gh api` call",
    "git/local": "any other Bash call",
    "subagent": "an Agent, Task or Workflow call, launch to result",
    "background": "a finished turn, to the notification of a background task",
    "other": "any other tool call (Read, Edit, Write, Grep, …)"}
SUITE_TOKENS = ("git push", "check --evidence", "--tests")
SUITE_RAN = re.compile(r"\bRan \d+ tests?\b")     # a result that ran a suite; only this flag is kept, never the text
SUBAGENT_TOOLS = ("Agent", "Task", "Workflow")
HARNESS_PREFIXES = ("<task-notification", "<local-command", "<command-", "<system-reminder", "Caveat:")
LEDGER_HEAD = "ledger-"                    # a ledger PR's head branch (Rule-3 Ledger: clerical commits)
SHORT = 20                                 # an entry shorter than this matches only an equal message
LONG_GAP_S = 15 * 60                       # an agent-side segment this long is flagged (restart, sleep, lost turn)
TRACES_REL = "d-work/traces"               # the trace store, under the instance location (Rule-11 property 3; #213 rev. 2)
AGENT_SIDE = re.compile(r"^\*\*Agent-side:\*\* (\d+) s", re.M)
HEADER = re.compile(r"^# Trace #(\d+) — \S")
SECTIONS = ("Timeline", "Buckets", "Counts", "Bottleneck", "Limits")   # a trace's parts, in order (the store check)
DONE = re.compile(r"\bdone\b", re.I)       # a disposition note naming the Done-`Y` (Rule-3 Ledger: `Y done …`)

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("bucket-names-unique", lambda: len(set(BUCKETS)) == len(BUCKETS)),
    ("every-bucket-in-exactly-one-partition", lambda: sorted(b for p in PARTITIONS.values() for b in p) == sorted(BUCKETS)),
    ("priority-covers-every-bucket-but-inference", lambda: sorted(PRIORITY + ("inference",)) == sorted(BUCKETS)),
    ("mechanical-kinds-are-agent-side", lambda: set(MECHANICAL) <= set(PARTITIONS["agent"])),
    ("every-bucket-has-a-meaning", lambda: set(MEANING) == set(BUCKETS)),
    ("sections-are-the-five-parts", lambda: SECTIONS == ("Timeline", "Buckets", "Counts", "Bottleneck", "Limits")),
    ("traces-in-the-d-work-store", lambda: TRACES_REL.startswith("d-work/")),
    ("header-names-the-d-work", lambda: bool(HEADER.match("# Trace #1 — t")) and not HEADER.match("# Trace 1")),
]

# ---- time
def ms(ts: str) -> int | None:
    """An ISO-8601 timestamp as epoch milliseconds, or None."""
    try:
        d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return int(d.timestamp() * 1000)

def utc(t: int) -> str:
    return datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def secs(t: int) -> str:
    s = round(t / 1000)
    return f"{s // 3600}h{s % 3600 // 60:02d}m{s % 60:02d}s" if s >= 3600 else f"{s // 60}m{s % 60:02d}s" if s >= 60 else f"{s}s"

def norm(s: str) -> str:
    return " ".join((s or "").split())

# ---- transcripts
def slug(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))

def default_transcripts(root: Path) -> list[Path]:
    """The newest transcript of the working tree's project directory, else of the main worktree's; [] if none."""
    trees = [root]
    try:
        common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root,
                                capture_output=True, text=True, env=dyadlib.git_env(), timeout=30).stdout.strip()
        if common:
            trees.append(Path(common).parent)
    except (OSError, subprocess.SubprocessError):
        pass
    base = Path.home() / ".claude" / "projects"
    for t in trees:
        d = base / slug(t)
        files = sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime) if d.is_dir() else []
        if files:
            return [files[-1]]
    return []

def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""

def _yn(text: str) -> set[int] | None:
    """The ids a reply's last non-blank line names when it is a `Y/N:` counter-prompt, else None."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines or not lines[-1].lstrip("*_`> ").startswith("Y/N:"):
        return None
    return {int(i) for i in re.findall(r"#(\d+)", lines[-1])}

def tool_kind(name: str, inp: dict) -> str:
    if name in SUBAGENT_TOOLS:
        return "subagent"
    if "github" in name.lower():
        return "github"
    if name == "Bash":
        cmd = str(inp.get("command", ""))
        if any(t in cmd for t in SUITE_TOKENS):
            return "suite"
        return "github" if re.search(r"\bgh api\b", cmd) else "git/local"
    return "other"

def load(paths: list[Path]) -> tuple[list[dict], list[str]]:
    """Main-thread records of every transcript, time-sorted, as derived dicts; text is kept only on an
    Operator message, for anchoring, and never leaves this module. Returns (records, problems)."""
    recs, seen, problems = [], set(), []
    for p in paths:
        try:
            fh = open(p, encoding="utf-8", errors="replace")
        except OSError as e:
            problems.append(f"transcript {p.name} unreadable: {type(e).__name__}"); continue
        bad = 0
        with fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except ValueError:
                    bad += 1; continue
                if not isinstance(o, dict) or o.get("isSidechain"):
                    continue
                uid = o.get("uuid")
                if uid and uid in seen:
                    continue
                seen.add(uid)
                recs.extend(_derive(o))
        if bad:
            problems.append(f"transcript {p.name}: {bad} line(s) not JSON, skipped")
    recs.sort(key=lambda r: (r["ts"], r["seq"]))
    ran = {r["tool"]: r.get("ran") for r in recs if r["kind"] == "tool_result" and r.get("tool")}
    for r in recs:   # a push gate that ran no suite is a guards-only gate (ledger-only or empty range, Rule-12 p2)
        if r["kind"] == "tool_use" and r.get("tkind") == "suite" and r.get("tool") in ran and not ran[r["tool"]]:
            r["tkind"] = "guards"
    return recs, problems

def _flat(c) -> str:
    """A tool result's text, for the one suite-ran test above; never stored."""
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(b.get("text", "") for b in c if isinstance(b, dict))
    return ""

_SEQ = [0]
def _rec(kind: str, ts: int, session: str | None, **kw) -> dict:
    _SEQ[0] += 1
    return {"kind": kind, "ts": ts, "seq": _SEQ[0], "session": session, **kw}

def _derive(o: dict) -> list[dict]:
    t, typ, sess = ms(o.get("timestamp", "")), o.get("type"), o.get("sessionId")
    if t is None:
        return []
    msg = o.get("message") if isinstance(o.get("message"), dict) else {}
    if typ == "attachment":
        a = o.get("attachment") if isinstance(o.get("attachment"), dict) else {}
        if a.get("type") != "queued_command" or not isinstance(a.get("prompt"), str):
            return []
        origin = (a.get("origin") or {}).get("kind")
        if origin == "human" or a.get("commandMode") == "prompt":
            return [_rec("operator", ms(a.get("timestamp", "")) or t, sess, text=a["prompt"], queued=True)]
        return [_rec("notify", t, sess)]
    if typ == "user":
        content = msg.get("content")
        if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return [_rec("tool_result", t, sess, tool=b.get("tool_use_id"), ran=bool(SUITE_RAN.search(_flat(b.get("content")))))
                    for b in content if isinstance(b, dict) and b.get("type") == "tool_result"]
        if o.get("isMeta"):
            return []
        text, origin = _text(content), (o.get("origin") or {}).get("kind") if isinstance(o.get("origin"), dict) else None
        if origin not in (None, "human") or (origin is None and text.lstrip().startswith(HARNESS_PREFIXES)):
            return [_rec("notify", t, sess)]
        return [_rec("operator", t, sess, text=text, queued=False)]
    if typ == "assistant":
        out, usage = [], msg.get("usage") if isinstance(msg.get("usage"), dict) else {}
        for b in msg.get("content") or []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                inp = b.get("input") if isinstance(b.get("input"), dict) else {}
                name = str(b.get("name", ""))
                out.append(_rec("tool_use", t, sess, tool=b.get("id"), name=name, tkind=tool_kind(name, inp),
                                background=bool(inp.get("run_in_background")),
                                pr=("ledger" if str(inp.get("head", "")).startswith(LEDGER_HEAD) else "work")
                                if "create_pull_request" in name else None,
                                merge="merge_pull_request" in name))
            elif b.get("type") == "text":
                out.append(_rec("text", t, sess, yn=_yn(b.get("text", ""))))
            else:
                out.append(_rec("thinking", t, sess))
        if out:
            out[-1]["msg_id"], out[-1]["out_tokens"] = msg.get("id"), int(usage.get("output_tokens") or 0)
        return out
    return []

# ---- ledger and git
def provenance(rid: int, root: Path) -> list[dict]:
    p = dyadlib.instance(root) / "d-work" / "provenance" / f"{rid}.md"
    return dyadlib.load_guard("agent", "provenance").parse(p.read_text(encoding="utf-8")) if p.is_file() else []

def _git(root: Path, *a: str) -> str:
    try:
        r = subprocess.run(["git", *a], cwd=root, capture_output=True, text=True, env=dyadlib.git_env(), timeout=120)
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout if r.returncode == 0 else ""

def git_events(rid: int, root: Path) -> tuple[list[dict], list[dict]]:
    """(commits, merges) of the d-work: non-merge commits citing `d-work #<id>` or touching its row, plan or
    provenance file; and the first-parent merges of HEAD whose second parent landed any of them."""
    rel = dyadlib.instance_rel(root)
    fmt = "--format=%H%x1f%aI%x1f%s"
    lines = _git(root, "log", "--no-merges", fmt, "-E", f"--grep=d-work #{rid}([^0-9]|$)").splitlines()
    if rel:
        lines += _git(root, "log", "--no-merges", fmt, "--", *(f"{rel}/d-work/{d}/{rid}.md" for d in ("rows", "plans", "provenance"))).splitlines()
    commits, seen = [], set()
    for l in lines:
        sha, date, subj = (l.split("\x1f") + ["", ""])[:3]
        if sha and sha not in seen and ms(date) is not None:
            seen.add(sha)
            paths = dyadlib.commit_paths(root, sha) or []
            ledger = bool(rel) and bool(paths) and all(p.startswith(f"{rel}/d-work/") for p in paths)
            commits.append({"sha": sha, "ts": ms(date), "subject": subj, "ledger": ledger})
    commits.sort(key=lambda c: c["ts"])
    merges = []
    if commits:
        since = utc(commits[0]["ts"] - 86_400_000).replace(" ", "T") + "Z"
        for l in _git(root, "log", "--merges", "--first-parent", f"--since={since}", "--format=%H%x1f%aI%x1f%P%x1f%s").splitlines():
            sha, date, parents, subj = (l.split("\x1f") + ["", "", ""])[:4]
            ps = parents.split()
            if len(ps) < 2 or ms(date) is None:
                continue
            landed = set(_git(root, "rev-list", f"{ps[0]}..{ps[1]}").split()) & seen
            if landed:
                led = all(c["ledger"] for c in commits if c["sha"] in landed)
                merges.append({"sha": sha, "ts": ms(date), "subject": subj, "ledger": led, "landed": len(landed)})
        merges.sort(key=lambda m: m["ts"])
    return commits, merges

# ---- anchoring
def _matches(entry_text: str, msg_text: str) -> bool:
    e, m = norm(entry_text), norm(msg_text)
    return bool(e) and (e == m or (len(e) >= SHORT and e in m))

def anchor(entries: list[dict], recs: list[dict], rid: int) -> list[dict]:
    """One result per entry, in order: {n, kind, note, date, ts|None, status, asked_ts}. Status is `anchored`,
    `unmatched` or `ambiguous`; only an anchored entry carries a timestamp."""
    ops, last_any = [], None
    for r in recs:                                       # each Operator message with the reply it answers
        if r["kind"] == "operator":
            ans = last_any if last_any is not None and last_any["kind"] == "text" and last_any.get("yn") is not None else None
            ops.append((r, ans))
        last_any = r
    out, pos = [], 0
    for e in entries:
        res = {"n": e["n"], "kind": e["kind"], "note": e["note"], "date": e["date"], "ts": None, "status": "unmatched", "asked_ts": None}
        cands = [(i, m, ans) for i, (m, ans) in enumerate(ops) if i >= pos and _matches(e["text"], m["text"])]
        if e["kind"] == "disposition":
            cands = [c for c in cands if c[2] is not None and rid in c[2]["yn"]]
            dated = [c for c in cands if utc(c[1]["ts"])[:10] == e["date"]]
            cands = dated or cands
            cands = cands[:1]                            # dispositions are taken in sequence (plan #213, attack 4)
        if len(cands) > 1:
            res["status"] = "ambiguous"
        elif cands:
            i, m, ans = cands[0]
            res.update(ts=m["ts"], status="anchored", asked_ts=ans["ts"] if ans else None)
            pos = i + 1
        out.append(res)
    return out

# ---- buckets
def intervals(recs: list[dict], start: int, end: int) -> tuple[list[tuple[int, int, str]], list[dict]]:
    """(labelled intervals, background launches) over [start, end]: operator and idle waits, background waits,
    and every foreground tool call by its kind. Uncovered time is inference."""
    out, bg = [], []
    results = {}
    for r in recs:
        if r["kind"] == "tool_result" and r.get("tool") and r["tool"] not in results:
            results[r["tool"]] = r["ts"]
    for r in recs:
        if r["kind"] == "tool_use" and start <= r["ts"] <= end:
            done = results.get(r.get("tool"))
            if r["background"]:
                bg.append({"ts": r["ts"], "name": r["name"], "tkind": r["tkind"]})
            if done is not None and done > r["ts"]:
                out.append((r["ts"], done, r["tkind"]))
    prev = None
    for r in recs:
        if prev is not None and prev["kind"] == "text" and r["kind"] in ("operator", "notify") and r["ts"] > prev["ts"]:
            label = "background" if r["kind"] == "notify" else "operator" if prev.get("yn") is not None else "idle"
            out.append((prev["ts"], r["ts"], label))
        prev = r
    return [(max(a, start), min(b, end), lab) for a, b, lab in out if b > start and a < end], bg

def buckets(ivs: list[tuple[int, int, str]], start: int, end: int) -> tuple[dict[str, int], list[tuple[int, int, str]]]:
    """Milliseconds per bucket over [start, end] by a sweep: each instant takes the first label of PRIORITY
    covering it, else inference, so the buckets sum to the window exactly. Also returns the segments."""
    edges = sorted({start, end} | {a for a, _, _ in ivs} | {b for _, b, _ in ivs})
    events: dict[int, list[tuple[int, str]]] = {}
    for a, b, lab in ivs:
        events.setdefault(a, []).append((1, lab)); events.setdefault(b, []).append((-1, lab))
    active = {b: 0 for b in BUCKETS}
    out, segs = {b: 0 for b in BUCKETS}, []
    for i, t in enumerate(edges):
        for d, lab in events.get(t, []):
            active[lab] += d
        if i + 1 < len(edges) and t >= start and edges[i + 1] <= end:
            lab = next((p for p in PRIORITY if active[p] > 0), "inference")
            out[lab] += edges[i + 1] - t
            if segs and segs[-1][2] == lab and segs[-1][1] == t:
                segs[-1] = (segs[-1][0], edges[i + 1], lab)
            else:
                segs.append((t, edges[i + 1], lab))
    return out, segs

def turns_naming_others(recs: list[dict], rid: int, start: int, end: int) -> tuple[list[tuple[int, set]], list[int]]:
    """(shared, others): turns in the window ending in a `Y/N:` line that names #rid with other ids (shared, with
    the ids), and turns whose `Y/N:` names only other ids (their milliseconds)."""
    shared, others, turn_start = [], [], start
    for r in recs:
        if r["kind"] in ("operator", "notify"):
            turn_start = max(r["ts"], start)
        elif r["kind"] == "text" and r.get("yn") is not None and start <= r["ts"] <= end and r["ts"] > turn_start:
            if rid in r["yn"] and len(r["yn"]) > 1:
                shared.append((r["ts"] - turn_start, r["yn"]))
            elif r["yn"] and rid not in r["yn"]:
                others.append(r["ts"] - turn_start)
    return shared, others

# ---- report
def median_agent_side(root: Path, rid: int) -> tuple[float | None, int]:
    d = dyadlib.instance(root) / TRACES_REL
    vals = []
    for p in sorted(d.glob("*.md")) if d.is_dir() else []:
        if p.stem != str(rid) and (m := AGENT_SIDE.search(p.read_text(encoding="utf-8", errors="replace"))):
            vals.append(int(m.group(1)))
    return (statistics.median(vals) if vals else None), len(vals)

def check_store(root: Path | None = None) -> list[str]:
    """Well-formedness of the trace store `<instance>/d-work/traces/`: every file is `<id>.md` for an existing row,
    opens with `# Trace #<id> — <title>` naming that same id, and holds the five sections in order. An absent store
    passes (no d-work traced yet, a fresh install)."""
    root = root or dyadlib.repo_root()
    d = dyadlib.instance(root) / TRACES_REL
    if not d.is_dir():
        return []
    ids, msgs = {r.id for r in dyadlib.read_rows(root)}, []
    for p in sorted(d.iterdir()):
        if not (p.suffix == ".md" and p.stem.isdigit()):
            msgs.append(f"{p.name}: not `<id>.md` (the trace store holds one trace per d-work)"); continue
        if int(p.stem) not in ids:
            msgs.append(f"{p.name}: no row #{p.stem}")
        text = p.read_text(encoding="utf-8", errors="replace")
        m = HEADER.match(text)
        if not m or m.group(1) != p.stem:
            msgs.append(f"{p.name}: first line is not `# Trace #{p.stem} — <title>`")
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        if tuple(heads) != SECTIONS:
            msgs.append(f"{p.name}: sections {heads}, not {list(SECTIONS)}")
    return msgs

def trace(rid: int, root: Path, transcripts: list[Path] | None) -> str:
    rows = {r.id: r for r in dyadlib.read_rows(root)}
    if rid not in rows:
        raise SystemExit(f"no row {rid}")
    row, inst = rows[rid], dyadlib.instance(root)
    rel = lambda p: str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
    entries = provenance(rid, root)
    plan = inst / "d-work" / "plans" / f"{rid}.md"
    commits, merges = git_events(rid, root)
    paths = transcripts if transcripts is not None else default_transcripts(root)
    recs, problems = load(paths) if paths else ([], [])
    anchors = anchor(entries, recs, rid) if recs else []
    limits: list[str] = list(problems)
    home = str(Path.home())
    shown = ", ".join("`" + (str(p).replace(home, "~", 1) if str(p).startswith(home) else str(p)) + "`" for p in paths)
    n_anch = sum(a["status"] == "anchored" for a in anchors)
    lines = [f"# Trace #{rid} — {row.title}", "",
             f"Sources: row `{rel(dyadlib.rows_dir(root) / f'{rid}.md')}` (state {row.state}); provenance "
             f"`{rel(inst / 'd-work' / 'provenance' / f'{rid}.md')}` ({len(entries)} entries, {n_anch} anchored); plan "
             f"`{rel(plan)}`{'' if plan.is_file() else ' (absent)'}; git HEAD ({len(commits)} commits, {len(merges)} merges); "
             + (f"transcript {shown} (read in place, never copied; no transcript text below)." if paths else "transcript: none found.")
             + f" Produced by `dyad dwork trace {rid}` (play-book `dyad/playbooks/dwork-trace.md`).", ""]
    # window
    start = end = None
    done_ts, preview = None, False
    anchored = [a for a in anchors if a["status"] == "anchored"]
    if anchored:
        start = min(a["ts"] for a in anchored)
        dones = [a for a in anchored if a["kind"] == "disposition" and DONE.search(a["note"])]
        if dones:                                        # the trace proper: through the Done-`Y` (plan #213 revision 2)
            done_ts = end = dones[-1]["ts"]
        elif not any(e["kind"] == "disposition" and DONE.search(e["note"]) for e in entries):
            preview = True                               # no Done-`Y` yet: the completion reply's preview, to now
            end = max(r["ts"] for r in recs)
            limits.append("preview: the d-work has no Done disposition yet, so the window ends at the transcript's last record "
                          "(the Done question being asked); the trace proper is written at the Done-`Y`")
        else:
            last_rec = max(r["ts"] for r in recs)
            end = min(max([a["ts"] for a in anchored] + [c["ts"] for c in commits if c["ts"] >= start]), last_rec)
            limits.append("the Done disposition is not anchored: the window ends at the d-work's last event, not at the Done-`Y`")
    for a in anchors:
        if a["status"] != "anchored":
            limits.append(f"provenance entry {a['n']} ({a['kind']} {a['date']}{' ' + a['note'] if a['note'] else ''}) "
                          f"{a['status']} in the transcript: not used as an anchor, never guessed")
    if entries and paths and not anchored:
        limits.append("no provenance entry anchored in the transcript (another session's, or a transcript that does not cover this d-work): buckets absent")
    # timeline
    tl: list[tuple[int, str, str]] = []
    for a in anchored:
        tl.append((a["ts"], "Operator", f"{a['kind']} (provenance {a['n']}{', ' + a['note'] if a['note'] else ''})"))
        if a["kind"] == "disposition" and a["asked_ts"]:
            tl.append((a["asked_ts"], "Agent", "counter-prompt asked" + (" (the Done question)" if a["ts"] == done_ts else "")))
    for c in commits:
        tl.append((c["ts"], "Agent", f"commit {c['sha'][:7]}{' (ledger)' if c['ledger'] else ''}: {c['subject'][:90]}"))
    for m in merges:
        tl.append((m["ts"], "Agent", f"merge {m['sha'][:7]}{' (ledger)' if m['ledger'] else ''}: {m['subject'][:90]}"))
    results = {r["tool"]: r["ts"] for r in reversed(recs) if r["kind"] == "tool_result" and r.get("tool")}
    if start is not None:
        for r in recs:
            if r["kind"] == "tool_use" and start <= r["ts"] <= end and r["tkind"] in ("suite", "guards", "github", "subagent"):
                d = results.get(r.get("tool"))
                dur = secs(d - r["ts"]) if d and d > r["ts"] else "no result"
                tl.append((r["ts"], "mechanical", f"{r['tkind']}: {r['name']}{' (background)' if r['background'] else ''}, {dur}"))
    lines += ["## Timeline", "", "| UTC | actor | event |", "|-----|-------|-------|"]
    for t, actor, ev in sorted(tl):
        after = start is not None and end is not None and t > end
        lines.append(f"| {utc(t)} | {actor} | {ev}{' — after the window' + (' (clerical tail)' if done_ts else '') if after else ''} |")
    if not tl:
        lines.append("| — | — | no event found |")
    lines.append("")
    # buckets
    agent_side = None
    lines += ["## Buckets", ""]
    if start is None or end is None or end <= start:
        lines += ["Absent: " + ("no transcript." if not paths else "no window (no anchored provenance entry before a Done question)."), ""]
    else:
        ivs, bg = intervals(recs, start, end)
        got, segs = buckets(ivs, start, end)
        total = end - start
        lines += [f"Window: {utc(start)} → {utc(end)} UTC, {secs(total)} — the first anchored prompt to "
                  + ("the Done-`Y`; its ledger commit and the merge are the clerical tail, not in it." if done_ts
                     else "the transcript's last record (a preview)." if preview else "the last d-work event."), "",
                  "| bucket | partition | seconds | share | what it measures |", "|--------|-----------|---------|-------|------------------|"]
        part = {b: p for p, bs in PARTITIONS.items() for b in bs}
        for b in BUCKETS:
            lines.append(f"| {b} | {part[b]} | {round(got[b] / 1000)} | {100 * got[b] / total:.1f}% | {MEANING[b]} |")
        lines += [f"| **total** | | {round(total / 1000)} | 100% | the window; every second in exactly one bucket |", ""]
        if bg:
            lines += [f"Background launches ({len(bg)}), counted once — their run overlaps the buckets above and is not summed again: "
                      + ", ".join(f"{utc(b['ts'])[11:]} {b['name']} ({b['tkind']})" for b in bg) + ".", ""]
        agent_ms = sum(got[b] for b in PARTITIONS["agent"])
        agent_side = round(agent_ms / 1000)
        long = [(a, b, lab) for a, b, lab in segs if lab in PARTITIONS["agent"] and b - a >= LONG_GAP_S * 1000]
        if long:
            limits.append(f"{len(long)} agent-side segment(s) of {LONG_GAP_S // 60} min or more ({secs(sum(b - a for a, b, _ in long))}): "
                          "a restart, a sleep or a lost turn reads as that bucket — " + ", ".join(f"{utc(a)[11:]} {lab} {secs(b - a)}" for a, b, lab in long))
        sessions = {r["session"] for r in recs if start <= r["ts"] <= end and r["session"]}
        if len(sessions) > 1:
            limits.append(f"{len(sessions)} harness sessions in the window: a restart or resume lies inside it")
        shared, others = turns_naming_others(recs, rid, start, end)
        if shared:
            lines += [f"Shared turns: {len(shared)} turn(s) ending in a `Y/N:` that names #{rid} with other d-works "
                      f"({secs(sum(d for d, _ in shared))}); split evenly, #{rid}'s part is {secs(round(sum(d / len(ids) for d, ids in shared)))}. "
                      "The buckets above hold them whole.", ""]
            limits.append("shared turns are counted whole in the buckets and split evenly only in the line under them (flagged)")
        if others:
            limits.append(f"{len(others)} turn(s) in the window ask only about other d-works ({secs(sum(others))}): interleaved work, counted in the buckets")
    # counts
    in_win = [r for r in recs if start is not None and start <= r["ts"] <= end]
    tools = [r for r in in_win if r["kind"] == "tool_use"]
    tokens = {}
    for r in in_win:
        if r.get("msg_id"):
            tokens[r["msg_id"]] = max(tokens.get(r["msg_id"], 0), r.get("out_tokens", 0))
    lines += ["## Counts", "", "| count | value | source |", "|-------|-------|--------|",
              f"| commits | {len(commits)} ({sum(c['ledger'] for c in commits)} ledger-only) | git |",
              f"| merges (PRs landed) | ledger {sum(m['ledger'] for m in merges)}, work {sum(not m['ledger'] for m in merges)} | git |"]
    if in_win:
        prs = [r["pr"] for r in tools if r.get("pr")]
        bash = [r for r in tools if r["tkind"] == "suite"]
        gates = [r for r in tools if r["tkind"] == "guards"]
        lines += [f"| PRs created in the window | ledger {prs.count('ledger')}, work {prs.count('work')} | transcript |",
                  f"| PRs merged in the window | {sum(bool(r.get('merge')) for r in tools)} | transcript |",
                  f"| full-suite runs (push gate, evidence, `--tests`) | {len(bash)} | transcript |",
                  f"| guards-only push gates | {len(gates)} | transcript |",
                  f"| tool calls | {len(tools)} | transcript |",
                  f"| output tokens | {sum(tokens.values())} | transcript |"]
    else:
        lines.append("| tool calls, tokens, PRs created | absent | no transcript window |")
    lines.append("")
    # bottleneck
    lines += ["## Bottleneck", ""]
    if agent_side is None:
        lines += ["Absent: no buckets.", ""]
    else:
        top = sorted(((got[b], b) for b in BUCKETS if got[b] > 0), reverse=True)[:3]
        lines.append("**Top 3:** " + ", ".join(f"{b} {100 * v / total:.0f}% ({secs(v)})" for v, b in top) + ".")
        med, n = median_agent_side(root, rid)
        lines += [f"**Agent-side:** {agent_side} s ({100 * agent_ms / total:.0f}% of the window; the Operator's wait excluded); "
                  + (f"median of {n} traced d-work(s): {round(med)} s." if med is not None else "no other traced d-work to compare."), ""]
    # limits
    limits += ["inference is a wall-clock gap between transcript records: it includes harness and network latency and overstates the model's own time",
               "the trace stops at the Done-`Y`: the Done ledger commit that carries it and the merge are clerical and appear only as git events after the window"]
    lines += ["## Limits", ""] + [f"- {l}" for l in limits] + [""]
    return "\n".join(lines)

def main(argv=None, root: Path | None = None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    usage = "usage: dyad dwork trace <id> [--transcript <path>]... [--out]"
    ids, paths, out, i = [], [], False, 0
    while i < len(a):
        if a[i] == "--transcript":
            if i + 1 >= len(a):
                sys.exit(f"refused: --transcript needs a path; {usage}")
            paths.append(Path(a[i + 1])); i += 2; continue
        if a[i] == "--out":
            out = True
        elif a[i].isdigit():
            ids.append(int(a[i]))
        else:
            sys.exit(f"refused: {a[i]!r}; {usage}")
        i += 1
    if len(ids) != 1:
        sys.exit(usage)
    missing = [p for p in paths if not p.is_file()]
    if missing:
        sys.exit(f"refused: no transcript at {', '.join(map(str, missing))}")
    root = root or dyadlib.repo_root()
    text = trace(ids[0], root, paths or None)
    if out:
        dest = dyadlib.instance(root) / TRACES_REL / f"{ids[0]}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        print(f"wrote {dest.relative_to(root) if dest.is_relative_to(root) else dest}")
    else:
        print(text)
    return 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1)

if __name__ == "__main__":
    sys.exit(main())
