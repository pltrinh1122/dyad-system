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
Limits and never guessed. An entry is **not verbatim** (#592 R-b, mode 49) when it anchors only after that whitespace
normalisation, or when its turn is in the transcript (a disposition: the reply asking it, on its date; a prompt: an
Operator message on its date answering no `Y/N:`), no other entry anchors that turn, and its words never anchor — never
for an entry noted `relayed via` or `mandate #<id>`, whose words were given in another chat; Limits names its number
and kind, nothing more.
The store `<instance>/d-work/traces/<id>.md` (written by `--out`, in the commit that records the Done-`Y`; plan #213 revision 2, #202)
is checked by `check_store`: one `<id>.md` per existing row, headed `# Trace #<id> — <title>`, its five sections, and
never a preview (#592 R-b): a stored trace holding the preview line (`PREVIEW_MARK`) fails unless the instance's
`<instance>/traces_preview_legacy.local.txt` (`<id>` per line, generated once at PR-b's head) names it, and warns
while the instance keeps no such list. `--out` therefore needs the Done words: the record's own Done entry, or
`--said-file <f>` — the words the `state` line is about to record, read as a Done entry dated UTC today — and
refuses, writing nothing, with neither. `--said-file` is read even when the record already holds a Done (a refused
`N done`, or a `Y done` a changed head voided, Rule-2 Binding), so the window ends at the Done asked again; it is
skipped only when the record's last entry already is those words, recorded today, and no later answer anchors them.
`--said-file` without `--out` is refused: the preview runs to the Done question, before any Done words.
  trace.py <id> [--transcript <path>]... [--out [--said-file <f>]]     (reached as `dyad dwork trace`)
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
def bottleneck_side(bucket: str) -> str:
    """dmc:trace-bottleneck (#641): which side leads, from the bucket on top of a trace's bottleneck line. `operator`
    (operator on top) for the Operator's partition (operator, idle); `inference` (inference on top) for inference;
    `mechanical` (mechanical bucket on top) for every other agent bucket. One trace gives no verdict (the record's
    default): this names the side of one line. ValueError on a name that is no bucket."""
    if bucket not in BUCKETS:
        raise ValueError(f"trace-bottleneck: {bucket!r} is no bucket ({', '.join(BUCKETS)})")
    if bucket in PARTITIONS["operator"]:
        return "operator"
    return "inference" if bucket == "inference" else "mechanical"

MEANING = {
    "operator": "a reply ending in a `Y/N:` line, to the Operator's next message",
    "idle": "a reply with no `Y/N:` line, to the Operator's next message",
    "inference": "a tool result or message, to the Agent's next tool call or reply (wall gap)",
    "suite": "a Bash call whose gate ran Rule-12's suite, by what it ran and never by duration: `check --evidence` or `--tests` always; a `git push` whose pushed range (git) touches anything outside `<instance>/d-work/` with no skip line, or whose result shows `Ran N tests`; a hand-run `unittest` showing `Ran N tests`",
    "guards": "a `git push` whose gate ran guards only: the gate's own `skip [guards] Rule-12 suite:` line, else a ledger-only or empty pushed range (read from git, not from the result text; #216)",
    "github": "a GitHub tool call, or a Bash `gh api` call",
    "git/local": "any other Bash call",
    "subagent": "an Agent, Task or Workflow call, launch to result",
    "background": "a finished turn, to the notification of a background task",
    "other": "any other tool call (Read, Edit, Write, Grep, …)"}
SUITE_TOKENS = ("git push", "check --evidence", "--tests")
SUITE_RAN = re.compile(r"\bRan \d+ tests?\b")     # a result that ran a suite; only this flag is kept, never the text
SUITE_SKIP = re.compile(r"skip \[guards\] Rule-12 suite:")   # the gate's own skip line (`package.py` `suite_memo_clause`, `suite_gate`; #216)
PUSH = re.compile(r"\bgit push\b")                # a push-gate call: its kind is decided by what the gate ran (#216)
HAND_RUN = re.compile(r"\bunittest\b")            # a measure-only run by hand (Rule-12 p2): `suite` only with `Ran N tests` (#216)
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
PLAN = re.compile(r"\bplan\b", re.I)       # a disposition note naming a plan-`Y` (`Y plan …`)
OPENING = re.compile(r"\s*Y (?:open|backlog)\b", re.I)   # a note (or a row's first `disposed` entry) opening the row (#240)
PROCEED = re.compile(r"^Y/N:\s*proceed with\b", re.I)    # the plan counter-prompt's form (Rule-3 Plan)
DONE_ASKED = re.compile(r"^Y/N:\s*Done with\b", re.I)    # the completion counter-prompt's form (Rule-3)
PREVIEW_MARK = "- preview:"                # a Limits line only a preview carries: a stored trace never does (#592 R-b)
PREVIEW_LEGACY = "traces_preview_legacy.local.txt"   # <instance>/: the stored previews before #592, `<id>` per line
ELSEWHERE = re.compile(r"relayed via|\bmandate #\d+")   # a note whose words were given in another chat (Rule-7 p4, #422)
CLI_FLAGS = dyadlib.cli_forms("dwork", ("trace",))   # #592 R-a: {verb: its dyadlib.CLI form}, the one home of the flags this parser reads (dyad/tests/test_cli.py)
(TRANSCRIPT, SAID_FILE), (OUT,) = CLI_FLAGS["trace"].value_flags, CLI_FLAGS["trace"].bare
SAID_NOTE = "Y done (--said-file)"         # the note of the Done entry `--said-file` stands in for (#592 R-b)
TRIGGERS = ("operator", "notify", "compact")    # what wakes a turn: the record kinds that end the previous one (#602)
PR_RUN = re.compile(r"\b(?:pull request|PRs?|pulls?|merges?|merged)\s*#\d+(?:\s*(?:,\s*and|,|and|&)\s*#\d+)*", re.I)   # PR/merge numbers, never rows (#602 F2)
ROW_ID = re.compile(r"#(\d{1,7})(?!\d)")         # bounded: untrusted text never reaches int() unbounded (#602 F3)
MANDATE = re.compile(r"\bmandate #\d+")          # a disposition entry carried from a mandate: no answer given here (#602 F6)

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("bucket-names-unique", lambda: len(set(BUCKETS)) == len(BUCKETS)),
    ("every-bucket-in-exactly-one-partition", lambda: sorted(b for p in PARTITIONS.values() for b in p) == sorted(BUCKETS)),
    ("priority-covers-every-bucket-but-inference", lambda: sorted(PRIORITY + ("inference",)) == sorted(BUCKETS)),
    ("mechanical-kinds-are-agent-side", lambda: set(MECHANICAL) <= set(PARTITIONS["agent"])),
    ("every-bucket-has-a-meaning", lambda: set(MEANING) == set(BUCKETS)),
    ("sections-are-the-five-parts", lambda: SECTIONS == ("Timeline", "Buckets", "Counts", "Bottleneck", "Limits")),
    ("traces-in-the-d-work-store", lambda: TRACES_REL.startswith("d-work/")),
    ("header-names-the-d-work", lambda: bool(HEADER.match("# Trace #1 — t")) and not HEADER.match("# Trace 1")),
    ("preview-legacy-is-instance-local", lambda: PREVIEW_LEGACY.endswith(".local.txt") and "/" not in PREVIEW_LEGACY),
    ("said-note-names-the-done", lambda: bool(DONE.search(SAID_NOTE)) and not OPENING.match(SAID_NOTE)),
    ("none-is-no-trigger", lambda: "none" not in TRIGGERS),
    ("trigger-names-unique", lambda: len(set(TRIGGERS)) == len(TRIGGERS)),
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

def _ids(text: str, rows=None) -> frozenset[int]:
    """The row ids a text names: every `#<n>` of at most seven digits once the runs of PR and merge numbers
    (`merges PR #8, #9`, `PRs #8 and #10`, `merged #9`) are removed, intersected with `rows` when given. Integers
    only, never the text (Rule-7 p2); a longer digit run names nothing and never reaches `int()` (#602 F2, F3)."""
    got = frozenset(int(i) for i in ROW_ID.findall(PR_RUN.sub(" ", text or "")))
    return got if rows is None else got & frozenset(rows)

def _yn(text: str) -> set[int] | None:
    """The ids a reply's last non-blank line names when it is a `Y/N:` counter-prompt, else None (`_ids`: PR
    numbers stripped, the token bounded; #602)."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines or not lines[-1].lstrip("*_`> ").startswith("Y/N:"):
        return None
    return set(_ids(lines[-1]))

def _yn_kind(text: str) -> str | None:
    """`plan` or `done`: which counter-prompt a reply's last `Y/N:` line asks (Rule-3 forms), else None."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    last = lines[-1].lstrip("*_`> ") if lines else ""
    return "plan" if PROCEED.search(last) else "done" if DONE_ASKED.search(last) else None

def _note_kind(note: str) -> str | None:
    """`open`, `plan` or `done`: which counter-prompt a disposition note answers (`Y open …` or `Y backlog …`, the
    question that opens a row, read first since its note may name another row's plan; `Y plan …`; `Y done …`), else
    None (#240)."""
    return "open" if OPENING.match(note) else "done" if DONE.search(note) else "plan" if PLAN.search(note) else None

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

def load(paths: list[Path], commits: list[dict] | None = None) -> tuple[list[dict], list[str]]:
    """Main-thread records of every transcript, time-sorted, as derived dicts; text is kept only on an
    Operator message, for anchoring, and never leaves this module. `commits` (`git_events`'s, each with its
    `ledger` flag) is the range a push's kind is read from (`push_kinds`). Returns (records, problems)."""
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
    push_kinds(recs, commits)
    return recs, problems

def push_kinds(recs: list[dict], commits: list[dict] | None) -> None:
    """d-work #216: the `suite`/`guards` kind of a gate call by **what the gate ran**, never by duration. A
    `git push` is `guards` when its result carries the gate's own skip line (the suite memo or a ledger-only
    range, `SUITE_SKIP`); else `suite` when it shows `Ran N tests` (corroboration only); else by the pushed
    range read from git — the commits between the same session's previous push (its first record, before
    one) and this call: any touching anything outside `<instance>/d-work/` → `suite` (Rule-12 p2: the gate
    runs the suite on such a range), all ledger-only or none → `guards`. A range-booked push is flagged
    `ranged` (a Limits line); a range the timeline did not capture reads as empty. `check --evidence` and
    `--tests` are `suite` always (never skipped). A hand-run `unittest` (`hand`) is `suite` only when its
    result shows `Ran N tests`, else it stays `git/local`."""
    res = {r["tool"]: r for r in recs if r["kind"] == "tool_result" and r.get("tool")}
    first, last_push = {}, {}
    for r in recs:
        first.setdefault(r["session"], r["ts"])
        if r["kind"] != "tool_use":
            continue
        got = res.get(r.get("tool"), {})
        if r.get("push"):
            prev = last_push.get(r["session"], first[r["session"]])
            last_push[r["session"]] = r["ts"]
            if got.get("skipped"):
                r["tkind"] = "guards"
            elif got.get("ran"):
                r["tkind"] = "suite"
            else:
                rng = [c for c in commits or [] if prev <= c["ts"] <= r["ts"]]
                r["tkind"] = "suite" if any(not c["ledger"] for c in rng) else "guards"
                r["ranged"] = True
        elif r.get("hand") and got.get("ran"):
            r["tkind"] = "suite"

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
            return [_rec("operator", ms(a.get("timestamp", "")) or t, sess, text=a["prompt"], queued=True, ids=_ids(a["prompt"]))]
        return [_rec("notify", t, sess, ids=_ids(a["prompt"]))]          # the ids only, never the text (#602)
    if typ == "user":
        content = msg.get("content")
        if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return [_rec("tool_result", t, sess, tool=b.get("tool_use_id"), ran=bool(SUITE_RAN.search(_flat(b.get("content")))),
                         skipped=bool(SUITE_SKIP.search(_flat(b.get("content")))))   # two flags, never the text (#216)
                    for b in content if isinstance(b, dict) and b.get("type") == "tool_result"]
        if o.get("isCompactSummary"):                    # a compaction's summary: never the Operator's (#286)
            return [_rec("compact", t, sess)]
        if o.get("isMeta"):
            return []
        text, origin = _text(content), (o.get("origin") or {}).get("kind") if isinstance(o.get("origin"), dict) else None
        if origin not in (None, "human") or (origin is None and text.lstrip().startswith(HARNESS_PREFIXES)):
            return [_rec("notify", t, sess, ids=_ids(text))]
        return [_rec("operator", t, sess, text=text, queued=False, ids=_ids(text))]
    if typ == "assistant":
        out, usage = [], msg.get("usage") if isinstance(msg.get("usage"), dict) else {}
        for b in msg.get("content") or []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                inp = b.get("input") if isinstance(b.get("input"), dict) else {}
                name = str(b.get("name", ""))
                cmd = str(inp.get("command", "")) if name == "Bash" else ""
                kind = tool_kind(name, inp)
                out.append(_rec("tool_use", t, sess, tool=b.get("id"), name=name, tkind=kind,
                                push=bool(PUSH.search(cmd)), hand=kind == "git/local" and bool(HAND_RUN.search(cmd)),   # #216
                                background=bool(inp.get("run_in_background")),
                                pr=("ledger" if str(inp.get("head", "")).startswith(LEDGER_HEAD) else "work")
                                if "create_pull_request" in name else None,
                                merge="merge_pull_request" in name))
            elif b.get("type") == "text":
                out.append(_rec("text", t, sess, yn=_yn(b.get("text", "")), ynk=_yn_kind(b.get("text", ""))))
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

def _verbatim(entry_text: str, msg_text: str) -> bool:
    """The match `_matches` makes, without its whitespace normalisation (only the ends trimmed): the words as given."""
    e, m = (entry_text or "").strip(), (msg_text or "").strip()
    return bool(e) and (e == m or (len(norm(e)) >= SHORT and e in m))

def anchor(entries: list[dict], recs: list[dict], rid: int, origins: set[int] = frozenset(),
           opened: bool = False) -> list[dict]:
    """One result per entry, in order: {n, kind, note, date, ts|None, status, asked_ts, verbatim}. Status is `anchored`,
    `unmatched` or `ambiguous`; only an anchored entry carries a timestamp. `verbatim` is False for an entry anchored
    only after whitespace normalisation, or unmatched while its turn is there (a disposition: the reply asking it, on
    its date; a prompt: an Operator message on its date, after the previous anchor, answering no `Y/N:`) and no other
    entry anchors that turn, its note naming no other chat (`relayed via`, `mandate #<id>`) — #592 R-b; else None. `origins` are the ids the row refs and
    `opened` says its first `disposed` entry opened it (`Y open`, `Y backlog`): an opening disposition is asked before
    the row exists, so it may anchor to a `Y/N:` reply naming no id or an origin's id (#240)."""
    ops, last_text = [], None
    for r in recs:                                       # each Operator message with the reply it answers: the last
        if r["kind"] == "operator":                      # text since the previous Operator message, across harness
            ans = last_text if last_text is not None and last_text.get("yn") is not None else None   # notices,
            ops.append((r, ans)); last_text = None       # compactions, thinking and tools (#286)
        elif r["kind"] == "text":
            last_text = r
    out, pos, used, turns_of = [], 0, set(), {}
    for e in entries:
        res = {"n": e["n"], "kind": e["kind"], "note": e["note"], "date": e["date"], "ts": None, "status": "unmatched",
               "asked_ts": None, "verbatim": None}
        open_turns = [(i, m, ans) for i, (m, ans) in enumerate(ops) if i >= pos]   # the turns it may be; words not yet read
        cands = [c for c in open_turns if _matches(e["text"], c[1]["text"])]
        if e["kind"] == "disposition":
            want = _note_kind(e["note"])                 # a plan `Y` answers a plan question, a Done `Y` a Done one
            if want == "open" or (opened and str(e["n"]) == "1" and want is None):   # never a plan or Done question
                cands = [c for c in cands if c[2] is not None and c[2].get("ynk") is None
                         and (not c[2]["yn"] or rid in c[2]["yn"] or c[2]["yn"] & set(origins))]
            else:
                cands = [c for c in cands if c[2] is not None and rid in c[2]["yn"]
                         and (want is None or c[2].get("ynk") == want)]
            cands = [c for c in cands if utc(c[1]["ts"])[:10] == e["date"]]   # a wrong date is unmatched, never guessed
            cands = cands[:1]                            # dispositions are taken in sequence (plan #213, attack 4)
            asked = [c for c in open_turns if c[2] is not None and rid in c[2]["yn"] and utc(c[1]["ts"])[:10] == e["date"]
                     and (want in (None, "open") or c[2].get("ynk") == want)]
        else:
            asked = [c for c in open_turns if utc(c[1]["ts"])[:10] == e["date"]]
        if e["kind"] != "disposition":                   # a prompt's turn: an Operator message answering no `Y/N:`
            asked = [c for c in asked if c[2] is None]
        if len(cands) > 1:
            res["status"] = "ambiguous"
        elif cands:
            i, m, ans = cands[0]
            res.update(ts=m["ts"], status="anchored", asked_ts=ans["ts"] if ans else None,
                       verbatim=None if _verbatim(e["text"], m["text"]) else False)
            used.add(i); pos = i + 1
        elif asked and norm(e["text"]) and not ELSEWHERE.search(e["note"] or ""):
            turns_of[len(out)] = {c[0] for c in asked}   # judged once every anchor is known, below
        out.append(res)
    for k, idx in turns_of.items():                      # its turn is there, its words are not (#592 R-b) — a turn
        if idx - used:                                   # another entry anchors is that entry's, never this one's
            out[k]["verbatim"] = False
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
    for i, r in enumerate(recs):                         # a reply's wait: to the next real Operator message across any
        if r["kind"] != "text":                          # notice or compaction; else, when an agent act follows a
            continue                                     # notice unanswered, to the first notice (#286)
        j, first_notify = i + 1, None
        while j < len(recs) and recs[j]["kind"] in ("notify", "compact"):
            if recs[j]["kind"] == "notify" and first_notify is None:
                first_notify = recs[j]
            j += 1
        nxt = recs[j] if j < len(recs) else None
        if nxt is not None and nxt["kind"] == "operator" and nxt["ts"] > r["ts"]:
            out.append((r["ts"], nxt["ts"], "operator" if r.get("yn") is not None else "idle"))
        elif first_notify is not None and first_notify["ts"] > r["ts"]:
            out.append((r["ts"], first_notify["ts"], "background"))
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

def _nexts(recs: list[dict]) -> list[dict | None]:
    """For each record, the next record of the same harness session, or None: several transcripts merge into one
    time-sorted list (`load`), and a reply ends its own session's turn, never another's (#602)."""
    out, after = [None] * len(recs), {}
    for i in range(len(recs) - 1, -1, -1):
        s = recs[i].get("session")
        out[i] = after.get(s)
        after[s] = recs[i]
    return out

def replies(recs: list[dict], start: int, end: int) -> int:
    """Agent replies in [start, end]: text records that end a turn, the next record of the same session being an
    Operator message, a harness notice, a compaction or none. What the Operator was shown, the metric's stand-in
    for what was read (#560 D5; per session, #602)."""
    out = 0
    for r, nxt in zip(recs, _nexts(recs)):
        if r["kind"] == "text" and start <= r["ts"] <= end:
            out += nxt is None or nxt["kind"] in TRIGGERS
    return out

def turns(recs: list[dict], rows) -> list[dict]:
    """The turns of the transcript, each {trigger, ids, replies, ts, by} (#602), read per harness session (records
    of several transcripts interleave by time; each session keeps its own turn and ids). A turn opens at the first
    TRIGGERS record after the previous turn's ending reply (a reply as `replies` reads it), and that record's kind
    is its trigger (F7). An operator or notify record arriving before the turn's first Agent record joins it: the
    kind stays the first trigger's and the ids are the union. One arriving later — a queued notice mid-turn — opens
    nothing and relabels nothing; so does a compaction mid-turn (an auto-compaction inside a tool loop). A
    compaction opens a turn only after an ending reply or in place of a turn not yet started, and that turn
    inherits the ids of the last operator or notify trigger (F8). A reply before any trigger is a `none` turn. Its
    ids, intersected with `rows`: the closing `Y/N:` line's when non-empty (`by` = `yn`), else the trigger's
    (`by` = `trigger`); the Agent's prose never (F1)."""
    rows, out, state = frozenset(rows), [], {}
    for r, nxt in zip(recs, _nexts(recs)):
        k, sess = r["kind"], r.get("session")
        cur, last_ids = state.get(sess, (None, frozenset()))
        if k in TRIGGERS:
            if cur is not None and not cur["ended"] and cur["started"]:
                continue                                          # mid-turn: opens nothing, relabels nothing
            if k != "compact" and cur is not None and not cur["ended"]:
                cur["tids"] = last_ids = cur["tids"] | frozenset(r.get("ids") or ())   # joins the unstarted turn
            else:
                if k != "compact":
                    last_ids = frozenset(r.get("ids") or ())
                cur = {"trigger": k, "tids": last_ids, "ts": r["ts"], "started": False, "ended": False, "yn": None, "replies": 0}
                out.append(cur)
        elif k in ("text", "tool_use", "thinking"):
            if cur is None or cur["ended"]:
                cur = {"trigger": "none", "tids": frozenset(), "ts": r["ts"], "started": False, "ended": False, "yn": None, "replies": 0}
                out.append(cur)
            cur["started"] = True
            if k == "text" and (nxt is None or nxt["kind"] in TRIGGERS):
                cur.update(ended=True, replies=1, ts=r["ts"], yn=r.get("yn"))
        state[sess] = (cur, last_ids)
    res = []
    for t in out:
        yn = frozenset(t["yn"] or ()) & rows
        res.append({"trigger": t["trigger"], "ids": yn or (t["tids"] & rows), "replies": t["replies"], "ts": t["ts"],
                    "by": "yn" if yn else "trigger"})
    return res

def replies_for(tns: list[dict], rid: int, start: int, end: int) -> tuple[int, dict[str, int], int]:
    """(replies, by trigger, attributed by trigger): the replies in [start, end] of the turns naming #rid, split by
    what woke each turn (TRIGGERS, then `none`; the split sums to the replies), and how many of them were named by
    the turn's trigger rather than its `Y/N:` line (#602)."""
    split = {k: 0 for k in TRIGGERS + ("none",)}
    n = by_trigger = 0
    for t in tns:
        if t["replies"] and rid in t["ids"] and start <= t["ts"] <= end:
            n += t["replies"]; split[t["trigger"]] += t["replies"]
            by_trigger += t["replies"] if t["by"] == "trigger" else 0
    return n, split, by_trigger

def answers(entries: list[dict], days: tuple[str, str]) -> int:
    """The row's operator answers in the window: its disposition entries (provenance entries or `anchor`'s results,
    read by key) dated on the window's days, anchored or not, less those noted `mandate #<id>` — words given to
    another row (Rule-7 p4). A `relayed via` entry counts: the Operator gave it (#602 F5, F6)."""
    return sum(e.get("kind") == "disposition" and days[0] <= str(e.get("date", "")) <= days[1]
               and not MANDATE.search(str(e.get("note") or "")) for e in entries)

def window_answers(recs: list[dict], start: int, end: int) -> int:
    """Distinct Operator answers in [start, end]: operator messages answering a `Y/N:` reply (the last text since
    the previous Operator message, as `anchor` pairs them), counted once per timestamp — a batch `Y` once (#602 F5)."""
    seen, last_text = set(), None
    for r in recs:
        if r["kind"] == "operator":
            if last_text is not None and last_text.get("yn") is not None and start <= r["ts"] <= end:
                seen.add(r["ts"])
            last_text = None
        elif r["kind"] == "text":
            last_text = r
    return len(seen)

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

def is_preview(text: str) -> bool:
    """Whether a trace's text is a preview: its Limits carry the preview line (`PREVIEW_MARK`)."""
    return any(l.startswith(PREVIEW_MARK) for l in text.splitlines())

def preview_legacy(root: Path) -> tuple[set[int] | None, list[str]]:
    """The instance's list of stored previews that predate #592 (`<instance>/traces_preview_legacy.local.txt`, `<id>`
    per line, `#` a comment): (ids, problems), ids None when the file is absent."""
    p = dyadlib.instance(root) / PREVIEW_LEGACY
    if not p.is_file():
        return None, []
    ids, problems = set(), []
    for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if not line.isdigit():
            problems.append(f"{PREVIEW_LEGACY}:{n}: not `<id>`"); continue
        if int(line) in ids:
            problems.append(f"{PREVIEW_LEGACY}:{n}: #{line} named twice")
        ids.add(int(line))
    return ids, problems

def check_store(root: Path | None = None) -> list[str]:
    """Well-formedness of the trace store `<instance>/d-work/traces/`: every file is `<id>.md` for an existing row,
    opens with `# Trace #<id> — <title>` naming that same id, and holds the five sections in order. An absent store
    passes (no d-work traced yet, a fresh install). A stored trace is never a preview (#592 R-b): one carrying the
    preview line fails unless `PREVIEW_LEGACY` names it, and warns (`warning:`) while the instance keeps no list."""
    root = root or dyadlib.repo_root()
    d = dyadlib.instance(root) / TRACES_REL
    if not d.is_dir():
        return []
    legacy, problems = preview_legacy(root)
    ids, msgs = {r.id for r in dyadlib.read_rows(root)}, list(problems)
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
        if is_preview(text):
            if legacy is None:
                msgs.append(f"warning: {p.name}: a stored preview (`{PREVIEW_MARK}` under Limits), and this instance has no "
                            f"{PREVIEW_LEGACY} naming the previews stored before #592; a trace is written through the Done-`Y` "
                            f"(`dyad dwork trace {p.stem} --out --said-file <f>`)")
            elif int(p.stem) not in legacy:
                msgs.append(f"{p.name}: a stored preview (`{PREVIEW_MARK}` under Limits): a trace is written through the Done-`Y`, "
                            f"with the Done words (`dyad dwork trace {p.stem} --out --said-file <f>`; #592), and "
                            f"{PREVIEW_LEGACY} does not name it")
    return msgs

def has_done(entries: list[dict]) -> bool:
    """Whether a record holds a Done disposition (`Y done …`)."""
    return any(e["kind"] == "disposition" and DONE.search(e["note"]) for e in entries)

def recorded_done(entries: list[dict], extra: dict) -> bool:
    """Whether the record's last entry already is the Done `extra` stands in for: a Done disposition of its date whose
    words match (`state` ran before `trace`, #592 R-b)."""
    last = entries[-1] if entries else None
    return bool(last and last["kind"] == "disposition" and DONE.search(last["note"] or "")
                and last["date"] == extra["date"] and norm(last["text"]) == norm(extra["text"]))

def said_entry(entries: list[dict], said: str) -> dict:
    """The Done entry `--said-file` stands in for (#592 R-b): the words the `state` line will record, numbered after
    the record's last entry and dated UTC today, as `append_provenance` will write it."""
    return {"n": str(len(entries) + 1), "kind": "disposition", "date": dyadlib.utc_date(), "note": SAID_NOTE, "text": said}

def trace(rid: int, root: Path, transcripts: list[Path] | None, said: str | None = None) -> str:
    rows = {r.id: r for r in dyadlib.read_rows(root)}
    if rid not in rows:
        raise SystemExit(f"no row {rid}")
    row, inst = rows[rid], dyadlib.instance(root)
    rel = lambda p: str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
    entries = provenance(rid, root)
    plan = inst / "d-work" / "plans" / f"{rid}.md"
    commits, merges = git_events(rid, root)
    paths = transcripts if transcripts is not None else default_transcripts(root)
    recs, problems = load(paths, commits) if paths else ([], [])
    first = (row.disposed or "").split(";")[0]
    anchor_all = lambda es: anchor(es, recs, rid, {int(i) for i in re.findall(r"\d+", row.refs or "")} - {rid},
                                   bool(OPENING.match(re.sub(r"^\s*\d{4}-\d{2}-\d{2}", "", first)))) if recs else []
    said_used = said is not None                         # #592 R-b: the window anchored on the Done words to be recorded,
    if said_used:                                        # whatever Done the record already holds (a refused or voided one)
        extra = said_entry(entries, said)
        if recorded_done(entries, extra):                # unless `state` already wrote these words: then they are the
            said_used = bool(recs) and anchor_all(entries + [extra])[-1]["status"] == "anchored"   # record's, unless a
        if said_used:                                    # later answer of their own shows the Done asked again
            entries = entries + [extra]
    anchors = anchor_all(entries)
    limits: list[str] = list(problems)
    if said_used:
        limits.append(f"the Done entry is read from --said-file (entry {entries[-1]['n']}, dated {entries[-1]['date']} UTC): the words "
                      "the Done record is about to carry, not yet in the provenance record")
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
        start = min([a["ts"] for a in anchored] + [a["asked_ts"] for a in anchored    # from the opening question,
                     if a["kind"] == "disposition" and str(a["n"]) == "1" and a["asked_ts"]])   # its wait booked (#240)
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
        if a.get("verbatim") is False:                   # #592 R-b (mode 49): its number and kind only, never its words
            limits.append(f"provenance entry {a['n']} ({a['kind']}) not verbatim: "
                          + ("anchored only after whitespace normalisation" if a["status"] == "anchored"
                             else "its turn is in the transcript and its words never anchor"))
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
    agent_side = agent_ms = sub_ms = None
    lines += ["## Buckets", ""]
    if start is None or end is None or end <= start:
        lines += ["Absent: " + ("no transcript." if not paths else "no window (no anchored provenance entry before a Done question)."), ""]
    else:
        ivs, bg = intervals(recs, start, end)
        got, segs = buckets(ivs, start, end)
        total = end - start
        lines += [f"Window: {utc(start)} → {utc(end)} UTC, {secs(total)} — the first anchored prompt to "
                  + ("the Done-`Y`; its record commit, the merges and the commit that sets `done` are the clerical tail, not in it." if done_ts
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
        sub_ms = got["subagent"]
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
                  f"| full-suite runs (push gate, evidence, `--tests`, a hand-run `unittest` that ran) | {len(bash)} | transcript |",
                  f"| guards-only push gates | {len(gates)} | transcript |",
                  f"| tool calls | {len(tools)} | transcript |",
                  f"| output tokens | {sum(tokens.values())} | transcript |"]
        tns = turns(recs, rows)                          # #602: per row, only the replies of the turns naming it
        n_rep, split, by_trigger = replies_for(tns, rid, start, end)
        days = (utc(start)[:10], utc(end)[:10])         # the ledger's own count, not the transcript's anchors
        n_ans = answers(entries, days)                   # #560 D5: what the Operator reads per decision it makes
        lines.append(f"| replies per disposition | {n_rep / n_ans:.1f} ({n_rep} replies, {n_ans} answers) | transcript |"
                     if n_ans else f"| replies per disposition | no operator answer in the window ({n_rep} replies) | transcript |")
        lines.append("| replies by trigger | " + ", ".join(f"{k} {v}" for k, v in split.items() if k != "none" or v)
                     + " | transcript |")
        n_all = replies(recs, start, end)
        named = {i for t in tns if t["replies"] and start <= t["ts"] <= end for i in t["ids"]}
        summed = sum(replies_for(tns, i, start, end)[0] for i in named)
        lines.append(f"| replies in the window, all rows | {n_all} replies, {window_answers(recs, start, end)} answers, "
                     f"overlap {f'{summed / n_all:.1f}' if n_all else 'n/a'} | transcript |")
        limits.append(f"replies per disposition counts only the replies of the turns naming #{rid} — by the turn's closing "
                      "`Y/N:` line, else by what opened it (an Operator message or a harness notice; a compaction inherits "
                      "the trigger before it), never by the Agent's prose; PR and merge numbers are stripped and ids that "
                      "are no row dropped, but an id a trigger names for another reason still counts. A reply is what the "
                      "Operator was shown (a turn's last text), never what was read: an inference. Its answers are the "
                      "provenance record's dispositions dated on the window's days (a record holds dates, not times), "
                      "anchored or not, less those noted `mandate #<id>`; a turn naming several rows counts whole in each, "
                      "and the window line's overlap is their sum over the window's replies (#560 D5, #602)")
        if by_trigger:
            limits.append(f"{by_trigger} of #{rid}'s {n_rep} replies were attributed by the turn's trigger (no `Y/N:` naming "
                          f"a row): the shared-turn reading (`turns_naming_others`) reads `Y/N:` lines only, so the two read "
                          f"those {by_trigger} turn(s) differently")
        ranged = [r for r in tools if r.get("ranged")]   # #216: pushes booked from the pushed range, not the result text
        if ranged:
            limits.append(f"{len(ranged)} push gate(s) booked from the pushed range read from git (no skip line and no `Ran N tests` "
                          f"in the result — filtered or absent output): {sum(r['tkind'] == 'suite' for r in ranged)} suite, "
                          f"{sum(r['tkind'] == 'guards' for r in ranged)} guards; a range the timeline did not capture reads as guards")
        hand = [r for r in tools if r.get("hand")]
        if hand:
            limits.append(f"{len(hand)} hand-run `unittest` call(s): `suite` only when the result shows `Ran N tests` "
                          f"({sum(r['tkind'] == 'suite' for r in hand)} did), else `git/local` — never by duration")
    else:
        lines.append("| tool calls, tokens, PRs created | absent | no transcript window |")
    if sub_ms is not None:   # d-work #254: the `subagent` bucket over the agent partition, beside the tokens it
        # drafted. 0% on a token-heavy d-work is `delegation: plan-and-execute` not firing for work it covers
        # (Rule-3 Scope, Rule-10's concise-mode clause) — the omission that leaves a turn open to a lost segment.
        lines.append(f"| delegated share | {(100 * sub_ms / agent_ms if agent_ms else 0.0):.1f}% "
                     f"({round(sub_ms / 1000)} s of {agent_side} s agent-side, {sum(tokens.values())} output tokens) "
                     "| transcript |")
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
        # #216: the agent partition as a table under that line (not a sixth section: SECTIONS and the store are untouched),
        # then test execution (suite + guards) against inference — the kinds by what the gate ran, never by duration.
        lines += ["| agent bucket | seconds | share of agent-side |", "|--------------|---------|---------------------|"]
        for b in PARTITIONS["agent"]:
            lines.append(f"| {b} | {round(got[b] / 1000)} | {(100 * got[b] / agent_ms if agent_ms else 0.0):.1f}% |")
        tests_ms, inf_ms = got["suite"] + got["guards"], got["inference"]
        lines += [f"| **suite + guards** | {round(tests_ms / 1000)} | {(100 * tests_ms / agent_ms if agent_ms else 0.0):.1f}% |", "",
                  f"**Test execution:** suite + guards {round(tests_ms / 1000)} s against inference {round(inf_ms / 1000)} s; "
                  f"test execution / inference = {f'{tests_ms / inf_ms:.1f}' if inf_ms else 'n/a'}.", ""]
    # limits
    limits += ["inference is a wall-clock gap between transcript records: it includes harness and network latency and overstates the model's own time",
               "the trace stops at the Done-`Y`: the Done record commit that carries it, the merges and the commit that sets `done` are clerical and appear only as git events after the window"]
    lines += ["## Limits", ""] + [f"- {l}" for l in limits] + [""]
    return "\n".join(lines)

def main(argv=None, root: Path | None = None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    usage = "usage: dyad dwork trace <id> [--transcript <path>]... [--out [--said-file <f>]]"
    ids, paths, out, said_file, i = [], [], False, None, 0
    while i < len(a):
        if a[i] == TRANSCRIPT:
            if i + 1 >= len(a):
                sys.exit(f"refused: --transcript needs a path; {usage}")
            paths.append(Path(a[i + 1])); i += 2; continue
        if a[i] == SAID_FILE:
            if i + 1 >= len(a) or said_file is not None:
                sys.exit(f"refused: --said-file needs one path; {usage}")
            said_file = Path(a[i + 1]); i += 2; continue
        if a[i] == OUT:
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
    said = None
    if said_file is not None:
        if not said_file.is_file():
            sys.exit(f"refused: --said-file {said_file} is not a file (the Operator's Done words, verbatim, Rule-7)")
        said = said_file.read_text(encoding="utf-8").rstrip("\n")
        if not said.strip():
            sys.exit(f"refused: --said-file {said_file} is empty")
        if not out:                                      # the preview runs to the Done question, before any Done words
            sys.exit(f"refused: --said-file needs --out; {usage}")
    if out and said is None and not has_done(provenance(ids[0], root)):
        sys.exit(f"refused: dyad dwork trace {ids[0]} --out: row #{ids[0]}'s provenance record holds no Done disposition and no "
                 f"--said-file was given, so the trace would be a preview, and a stored trace never is (#592 R-b); pass the "
                 f"Operator's Done words: dyad dwork trace {ids[0]} --out --said-file <f>, then record the same file with "
                 f"`dwork state … --said-file <f>`; nothing written")
    text = trace(ids[0], root, paths or None, said)
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
