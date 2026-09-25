#!/usr/bin/env python3
"""countersign projector (crafts/countersign/rules/schema.md; crafts/sysarch/rules/projection.md; d-work #156).
Kernel: Python 3.12+, stdlib only (no pydantic, no jsonschema: Rules 13/14 need no manifest row).

Projects this dyad system's stores onto the Countersign core schema (`../templates/countersign-core.json`)
as one instance document, by the mapping contract and derivation rules of `../rules/schema.md`:
  - every d-work row (`dyadlib.read_rows`) is an Act — mode `explicit`, processor the agent (D1);
  - its plan file (Rule-15) and every other counter-question a disposition answers is a Proposal (D2);
  - every `disposed` entry is a Countersignature, its text verbatim from the provenance record
    (`agent/provenance` guard's `parse`) when the record's disposition count matches the row (Rule-7
    property 5), else the ledger entry itself, marked in the profile (D3);
  - the preference `ledger-pr-merge: agent` is a Mandate (D4, preferences guard's `parse`);
  - every release tag (`git for-each-ref refs/tags`) is a Release (D5); no git or no tags: none;
  - every run-book event (`runbook.all_events`) is an Event of one Act per run-book instance (D6);
  - an intake origin in a row's refs (`<system>-<id>`, Rule-3 Intake) and every incident
    (`<instance>/audits/INCIDENTS.md`) is an Escalation (D7);
  - every act's Initiation (`../rules/interaction.md`, imperative I6) is derived into its `profile` — a `prompt`
    entry of its provenance record, an intake origin in its refs, or an opening disposition (D8) — and `interaction`
    reports the acts where none is found, as warnings: I6 is checked, never gated (interaction.md, Checks).
Never hand-drawn: every instance comes from a parser the data's owning Rule provides. Deterministic: sorted
keys, arrays sorted by id (numeric parts compared as numbers), no clock. Output: one JSON document, written to
<instance>/projections/countersign.json (generated, never tracked). `validate` is the stdlib subset of JSON
Schema the schema file uses; `check` adds what a schema cannot say (references resolve, a signer is human,
the processor's kind follows the mode); `interaction` adds the I6 warnings (I1 and I7 are `check`'s).
  project_countersign.py            write the projection, print per-entity counts and the I6 line; exit 1 if it does
                                    not check (I6 warnings never change the exit code)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("project_countersign.py: Python 3.12+ required")
import hashlib, json, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/<craft>/projectors/ -> dyad/scripts (crafts/sysarch/rules/projection.md p2)
import dyadlib
import runbook

SCHEMA_VERSION = "0.2.0"
SYSTEM = "dyad-system"                                          # the profile name this projection declares
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "templates" / "countersign-core.json"
ENTITIES = ("parties", "acts", "proposals", "countersignatures", "mandates", "releases", "events", "escalations")
MODES = ("explicit", "implicit", "automatic")                   # #153 survivor: modes of an act
PARTY_KINDS = ("human", "agent", "executor")
ANSWERS = ("yes", "no", "amend")
BASES = ("per-act", "mandate", "release")
TIMINGS = ("before", "after")
PROCESSOR_KIND = {"explicit": "agent", "implicit": "agent", "automatic": "executor"}   # #153 A5: who processes each mode
EDGES = {("explicit", "implicit"): "delegate", ("explicit", "automatic"): "codify", ("implicit", "automatic"): "codify",
         ("automatic", "explicit"): "escalate", ("implicit", "explicit"): "escalate"}   # the only mode changes (#153)
PARTIES = (("agent", "agent"), ("operator", "human"))           # (id, kind): dyad-system's two parties; no executor act exists here (F3)
DERIVED_MODE, DERIVED_PROCESSOR, SIGNER = "explicit", "agent", "operator"   # D1: every dyad-system act, by construction
ANSWER_OF = {"Y": "yes", "N": "no"}                             # a bare disposal; `amend` is never derived here (text opens a new d-work, Rule-3)
MANDATES = (("ledger-pr-merge", "agent", "merge of a PR whose whole diff is ledger-only (the d-work store)"),)   # D4: (key, value that grants, event class)
LEGACY_CORE_VERSIONS = ("0.3.1", "0.3.2", "0.4.0")              # unprefixed tags cut before #196: core-only, never retagged (Rule-11 provenance)
NOT_SYSTEMS = ("parent",)                                       # `parent-<n>` in refs names a parent row, not an origin system
INITIATION_KINDS = ("prompt", "signal", "release-trigger")      # interaction.md I6: the only three origins of an act
OPENING_WORDS = ("backlog", "intake", "opened")               # D8: the first word of a first disposition that opened the row (Rule-3: backlog is opened by a disposition)
INITIATION_SOURCES = {"provenance": "prompt", "opening-disposition": "prompt", "intake": "signal"}   # D8: where dyad-system records an initiation -> its kind
UNDERIVABLE = "underivable"                                     # D8: a run-book act (D6): an event records no d-work, so no initiation store reaches it

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("entities-are-eight", lambda: len(ENTITIES) == 8 and len(set(ENTITIES)) == 8),
    ("modes-are-three", lambda: MODES == ("explicit", "implicit", "automatic")),
    ("processor-kind-covers-modes", lambda: set(PROCESSOR_KIND) == set(MODES) and set(PROCESSOR_KIND.values()) <= set(PARTY_KINDS)),
    ("only-automatic-is-executor", lambda: [m for m, k in PROCESSOR_KIND.items() if k == "executor"] == ["automatic"]),
    ("edges-change-mode", lambda: all(a != b and a in MODES and b in MODES for a, b in EDGES)),
    ("edges-are-delegate-codify-escalate", lambda: set(EDGES.values()) == {"delegate", "codify", "escalate"}),
    ("enums-distinct", lambda: all(len(set(e)) == len(e) > 0 for e in (PARTY_KINDS, ANSWERS, BASES, TIMINGS))),
    ("parties-have-a-human", lambda: all(k in PARTY_KINDS for _, k in PARTIES) and any(k == "human" for _, k in PARTIES)),
    ("derived-act-is-explicit-agent", lambda: DERIVED_MODE in MODES and dict(PARTIES).get(DERIVED_PROCESSOR) == PROCESSOR_KIND[DERIVED_MODE]),
    ("signer-is-human", lambda: dict(PARTIES).get(SIGNER) == "human"),
    ("answer-of-maps-to-answers", lambda: set(ANSWER_OF.values()) <= set(ANSWERS)),
    ("mandate-keys-distinct", lambda: len({k for k, _, _ in MANDATES}) == len(MANDATES)),
    ("initiation-kinds-are-three", lambda: INITIATION_KINDS == ("prompt", "signal", "release-trigger")),
    ("initiation-sources-map-to-kinds", lambda: len(INITIATION_SOURCES) > 0 and set(INITIATION_SOURCES.values()) <= set(INITIATION_KINDS) and UNDERIVABLE not in INITIATION_SOURCES),
    ("opening-words-distinct", lambda: len(set(OPENING_WORDS)) == len(OPENING_WORDS) > 0),
]

_ENTRY = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(Y|N)\b\s*(.*)$")
_WORD = re.compile(r"[a-z]+")
_ORIGIN = re.compile(r"^([a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*)-(\d+)$")
_TAG = re.compile(r"^(?:([a-z][a-z0-9-]*)-)?v(\d+\.\d+\.\d+)$")
_DWORK = re.compile(r"d-work #(\d+)")
_ROW_ID = re.compile(r"#?(\d+)")

def _natkey(s: str) -> list:
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", s)]

def _sorted(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda d: _natkey(d.get("id", d.get("name", ""))))

def _rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix() if p.is_relative_to(root) else p.as_posix()

def _git(root: Path, *args: str) -> str:
    """stdout of one read-only git command in `root`; "" when git or the repository is absent (a fixture)."""
    try:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, env=dyadlib.git_env(), timeout=120)
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout if r.returncode == 0 else ""

def _tag_token(tag: str) -> re.Pattern:
    return re.compile(r"(?<![\w.-])" + re.escape(tag) + r"(?![\w-]|\.\d)")

# ---- collect: parse the stores (never hand-drawn)
def collect(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    """The core-schema instance document of the system at `root`."""
    root = Path(root)
    prov = dyadlib.load_guard("agent", "provenance", pkg)
    prefs = dyadlib.load_guard("preferences", "preferences", pkg)
    inst = dyadlib.instance(root)
    doc = {"schema_version": SCHEMA_VERSION, "system": SYSTEM, **{e: [] for e in ENTITIES}}
    doc["parties"] = [{"id": pid, "kind": kind} for pid, kind in PARTIES]
    acts, proposals, sigs = doc["acts"], {}, doc["countersignatures"]
    for r in dyadlib.read_rows(root):
        aid = f"act-{r.id}"
        refs = [t for t in re.split(r"[\s,]+", r.refs) if t]
        entries = prov.dispositions(r.disposed)
        rec = prov.store(root) / f"{r.id}.md"
        parsed = prov.parse(rec.read_text(errors="ignore")) if rec.exists() else []
        texts = [e["text"] for e in parsed if e["kind"] == "disposition"]
        acts.append({"id": aid, "title": r.title, "mode": DERIVED_MODE, "processor": DERIVED_PROCESSOR, "state": r.state, "refs": refs,
                     "profile": {"initiation": _initiation(parsed, refs, entries, rec.exists())}})
        plan = inst / "d-work" / "plans" / f"{r.id}.md"
        if plan.exists():
            proposals[f"proposal-{r.id}-plan"] = _proposal(r.id, "plan", root, plan)
        verbatim = len(texts) == len(entries)
        for i, entry in enumerate(entries):
            m = _ENTRY.match(entry)
            date, yn, rest = (m.group(1), m.group(2), m.group(3)) if m else ("", "", entry)
            w = _WORD.match(rest.lower())
            word = w.group(0) if w else "other"
            pid = f"proposal-{r.id}-{word}"
            if pid not in proposals:
                proposals[pid] = _proposal(r.id, word, root, plan if word == "plan" and plan.exists() else None)
            sigs.append({"id": f"countersignature-{r.id}-{i + 1}", "subject": pid, "signer": SIGNER,
                         "answer": ANSWER_OF.get(yn, "no"), "basis": "per-act", "text": texts[i] if verbatim else entry,
                         "bound_hash": None, "at": date,
                         "profile": {"text_source": "provenance" if verbatim else "ledger", "ledger_entry": entry}})
        for tok in refs:
            o = _ORIGIN.match(tok)
            if o and o.group(1) not in NOT_SYSTEMS:
                doc["escalations"].append({"id": f"escalation-intake-{r.id}-{tok}", "from": f"ext:{tok}",
                                           "reason": f"intake: origin {tok} named in the row's refs (Rule-3 Intake)",
                                           "opens": aid, "profile": {"source": "intake"}})
    doc["proposals"] = list(proposals.values())
    doc["mandates"] = _mandates(root, prefs, sigs)
    doc["releases"] = _releases(root, sigs)
    _events(root, doc)
    doc["escalations"] += _incidents(inst, {a["id"] for a in acts})
    for e in ENTITIES:
        doc[e] = _sorted(doc[e])
    return doc

def _initiation(parsed: list[dict], refs: list[str], entries: list[str], has_record: bool) -> dict:
    """D8 (interaction.md): where this system records the act's Initiation, in this order — a `prompt` entry of the
    provenance record (Rule-7), an intake origin in refs (Rule-3 Intake: a signal the Operator's `Y` admitted), or a
    first disposition whose word opens the row (`Y backlog`, `Y intake`: opened by a disposition, Rule-3). `kind` None
    when none is found; `missing` then says what was looked for, so the I6 warning names it."""
    n = next((e["n"] for e in parsed if e["kind"] == "prompt"), None)
    if n is not None:
        return {"kind": INITIATION_SOURCES["provenance"], "source": "provenance", "entry": int(n)}
    origin = next((t for t in refs if (o := _ORIGIN.match(t)) and o.group(1) not in NOT_SYSTEMS), None)
    if origin:
        return {"kind": INITIATION_SOURCES["intake"], "source": "intake", "origin": origin}
    m = _ENTRY.match(entries[0]) if entries else None
    w = _WORD.search(m.group(3).lower()) if m else None
    if w and w.group(0) in OPENING_WORDS:
        return {"kind": INITIATION_SOURCES["opening-disposition"], "source": "opening-disposition", "entry": entries[0]}
    return {"kind": None, "source": None, "missing": "no prompt entry in the provenance record" if has_record else "no provenance record"}

def _proposal(rid: int, word: str, root: Path, body: Path | None) -> dict:
    return {"id": f"proposal-{rid}-{word}", "act": f"act-{rid}", "author": DERIVED_PROCESSOR,
            "body_ref": _rel(root, body) if body else None,
            "artifact_hash": ("sha256:" + hashlib.sha256(body.read_bytes()).hexdigest()) if body else None}

def _mandates(root: Path, prefs, sigs: list[dict]) -> list[dict]:
    """D4: a preference whose value grants standing authority for one class of act is a Mandate. Its
    countersignature is the last `yes` of the d-work that introduced the key (the oldest commit touching
    it, `git log -S`, citing `d-work #N`); None when that cannot be resolved (no git, a fixture)."""
    path = prefs.preferences_path(root)
    if not path.exists():
        return []
    _, rows = prefs.parse(path.read_text())
    values = {r[0].strip("` "): r[1].strip("` ") for r in rows if len(r) >= 2}
    out = []
    for key, grant, event_class in MANDATES:
        if values.get(key) != grant:
            continue
        subjects = _git(root, "log", "--reverse", "--format=%s", "-S", key, "--", _rel(root, path)).splitlines()
        origin = next((m.group(1) for s in subjects if (m := _DWORK.search(s))), None)
        sig = None
        if origin:
            mine = [s for s in sigs if s["id"].startswith(f"countersignature-{origin}-") and s["answer"] == "yes"]
            done = [s for s in mine if s["subject"].endswith("-done")]
            sig = (done or mine or [None])[-1]
        out.append({"id": f"mandate-{key}", "scope": {"event_class": event_class, "plan_template": None, "budget": None,
                                                      "rights": [f"{key}: {grant}"]},
                    "countersignature": sig["id"] if sig else None,
                    "profile": {"preference": key, "value": grant, "origin": f"d-work #{origin}" if origin else None}})
    return out

def _releases(root: Path, sigs: list[dict]) -> list[dict]:
    """D5: every tag shaped `vX.Y.Z` (the bundle, or the core before #196) or `<craft>-vX.Y.Z` (Rule-11 p4, p7).
    Its countersignature is the first recorded disposition naming the tag; None when none does (a release
    `Y` is asked in chat and, unless a row's entry names it, leaves no store record — F2)."""
    out = []
    for line in _git(root, "for-each-ref", "refs/tags", "--format=%(refname:short)\t%(objectname)\t%(*objectname)").splitlines():
        tag, _, rest = line.partition("\t")
        obj, _, peeled = rest.partition("\t")
        m = _TAG.match(tag)
        if not m:
            continue
        craft, ver = m.group(1), m.group(2)
        ref = ("dyad" if ver in LEGACY_CORE_VERSIONS else "BUNDLE.md") if craft is None else ("dyad" if craft == "dyad-operator" else f"crafts/{craft}")
        pat = _tag_token(tag)
        sig = next((s for s in sigs if pat.search(s["text"]) or pat.search(s["profile"]["ledger_entry"])), None)
        out.append({"id": f"release-{tag}", "definition_ref": ref, "version": ver, "hash": f"git:{peeled or obj}",
                    "countersignature": sig["id"] if sig else None, "profile": {"tag": tag}})
    return out

def _events(root: Path, doc: dict) -> None:
    """D6: one Act per run-book instance that has events (the run-book is its definition; no d-work id is
    recorded on an event), one Event per recorded execution, `seq` its position in the append-only file."""
    for name, events in sorted(runbook.all_events(root).items()):
        if not events:
            continue
        slug = re.sub(r"[^a-z0-9.-]+", "-", name.lower()).strip("-") or "runbook"
        aid = f"act-runbook-{slug}"
        doc["acts"].append({"id": aid, "title": f"run-book {name}", "mode": DERIVED_MODE, "processor": DERIVED_PROCESSOR,
                            "state": "recorded", "refs": [f"{runbook.runbooks_rel()}/{name}.md"],
                            "profile": {"initiation": {"kind": None, "source": UNDERIVABLE}}})
        for seq, e in enumerate(events):
            payload = {k: e[k] for k in ("id", "name", "cmd", "class", "role", "exit", "postcondition") if k in e}
            doc["events"].append({"id": f"event-{slug}-{seq}", "act": aid, "seq": seq, "payload": payload, "at": str(e.get("ts", ""))})

def _incidents(inst: Path, act_ids: set[str]) -> list[dict]:
    """D7: every incident row (Rule-3) returns the unexpected to the Operator: from its d-work's act, opening none."""
    f = inst / "audits" / "INCIDENTS.md"
    if not f.exists():
        return []
    text = f.read_text(errors="ignore")
    header = dyadlib.table_header(text)
    col = {h: i for i, h in enumerate(header)}
    if not {"date", "d-work", "what"} <= set(col):
        return []
    out, seen = [], set()
    for row in dyadlib.table_rows(text):
        if len(row) < len(header):
            continue
        date, dw, what = row[col["date"]], row[col["d-work"]], row[col["what"]]
        m = _ROW_ID.match(dw)
        src = f"act-{m.group(1)}" if m and f"act-{m.group(1)}" in act_ids else f"ext:{dw}"
        base = "escalation-incident-" + hashlib.sha256(f"{date}|{dw}|{what}".encode()).hexdigest()[:12]
        eid, k = base, 1
        while eid in seen:
            k += 1; eid = f"{base}-{k}"
        seen.add(eid)
        out.append({"id": eid, "from": src, "reason": f"incident: {what}", "opens": None, "profile": {"source": "incident", "date": date}})
    return out

# ---- validate: the stdlib subset of JSON Schema the schema file uses
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())

_TYPES = {"object": dict, "array": list, "string": str, "null": type(None), "boolean": bool}

def _is(v, t: str) -> bool:
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, _TYPES[t]) and not (t != "boolean" and isinstance(v, bool))

def validate(inst, sch: dict, root: dict | None = None, where: str = "$") -> list[str]:
    """Errors of `inst` against `sch`: `$ref` (local `#/$defs/`), `type`, `enum`, `const`, `required`,
    `properties`, `additionalProperties: false`, `items`, `pattern`, `minimum` — exactly what
    `countersign-core.json` uses. A keyword outside this set is an error, never silently ignored."""
    root = sch if root is None else root
    known = {"$schema", "$id", "$defs", "$ref", "title", "description", "type", "enum", "const", "required",
             "properties", "additionalProperties", "items", "pattern", "minimum"}
    unknown = set(sch) - known
    if unknown:
        return [f"{where}: schema keyword(s) {sorted(unknown)} not supported by this validator"]
    if "$ref" in sch:
        node = root
        for part in sch["$ref"].removeprefix("#/").split("/"):
            node = node[part]
        return validate(inst, node, root, where)
    errs = []
    if "type" in sch:
        types = sch["type"] if isinstance(sch["type"], list) else [sch["type"]]
        if not any(_is(inst, t) for t in types):
            return [f"{where}: {type(inst).__name__} is not {'|'.join(types)}"]
    if "const" in sch and inst != sch["const"]:
        errs.append(f"{where}: {inst!r} is not {sch['const']!r}")
    if "enum" in sch and inst not in sch["enum"]:
        errs.append(f"{where}: {inst!r} not in {sch['enum']}")
    if "pattern" in sch and isinstance(inst, str) and not re.search(sch["pattern"], inst):
        errs.append(f"{where}: {inst!r} does not match {sch['pattern']}")
    if "minimum" in sch and _is(inst, "number") and inst < sch["minimum"]:
        errs.append(f"{where}: {inst} < {sch['minimum']}")
    if isinstance(inst, dict):
        for k in sch.get("required", []):
            if k not in inst:
                errs.append(f"{where}: missing '{k}'")
        props = sch.get("properties", {})
        for k, v in inst.items():
            if k in props:
                errs += validate(v, props[k], root, f"{where}.{k}")
            elif sch.get("additionalProperties") is False:
                errs.append(f"{where}: unexpected '{k}'")
    if isinstance(inst, list) and "items" in sch:
        for i, v in enumerate(inst):
            errs += validate(v, sch["items"], root, f"{where}[{i}]")
    return errs

def check(doc: dict, sch: dict | None = None) -> list[str]:
    """The schema, then what it cannot say: ids unique; every reference resolves to an instance of the right
    entity; an act's processor has the kind its mode requires (#153 A5); a proposal's author is an agent; a
    countersignature's signer is human; an escalation opens an explicit act."""
    errs = validate(doc, sch if sch is not None else schema())
    if errs:
        return errs
    ids = [d["id"] for e in ENTITIES for d in doc[e]]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        errs.append(f"duplicate ids: {dup[:5]}")
    by = {e: {d["id"]: d for d in doc[e]} for e in ENTITIES}
    kind = {p["id"]: p["kind"] for p in doc["parties"]}
    for a in doc["acts"]:
        if kind.get(a["processor"]) != PROCESSOR_KIND[a["mode"]]:
            errs.append(f"{a['id']}: processor {a['processor']} ({kind.get(a['processor'])}) is not the {PROCESSOR_KIND[a['mode']]} a {a['mode']} act requires")
    for p in doc["proposals"]:
        if p["act"] not in by["acts"]:
            errs.append(f"{p['id']}: act {p['act']} unresolved")
        if kind.get(p["author"]) != "agent":
            errs.append(f"{p['id']}: author {p['author']} is not an agent")
    for s in doc["countersignatures"]:
        if s["subject"] not in by["proposals"] and s["subject"] not in by["escalations"]:
            errs.append(f"{s['id']}: subject {s['subject']} unresolved")
        if kind.get(s["signer"]) != "human":
            errs.append(f"{s['id']}: signer {s['signer']} is not human")
    for e in ("mandates", "releases"):
        for d in doc[e]:
            if d["countersignature"] is not None and d["countersignature"] not in by["countersignatures"]:
                errs.append(f"{d['id']}: countersignature {d['countersignature']} unresolved")
    for ev in doc["events"]:
        if ev["act"] not in by["acts"]:
            errs.append(f"{ev['id']}: act {ev['act']} unresolved")
    for x in doc["escalations"]:
        if not x["from"].startswith("ext:") and x["from"] not in by["acts"]:
            errs.append(f"{x['id']}: from {x['from']} unresolved")
        if x["opens"] is not None and by["acts"].get(x["opens"], {}).get("mode") != "explicit":
            errs.append(f"{x['id']}: opens {x['opens']}, not an explicit act")
    return errs

# ---- interaction: the imperatives a projection can check (../rules/interaction.md, Checks)
def interaction(doc: dict) -> dict:
    """I6 over the document: every act's `profile.initiation` (D8). Returns {"initiated": n, "underivable": [ids],
    "uninitiated": [(id, missing)]}. An act with no profile, or no initiation in it, counts as uninitiated — a
    projection from another system that does not derive D8 is reported, never silently passed. Warnings only:
    I6 is checked, never gated (interaction.md) — dyad-system rows predate the store that would carry the prompt."""
    out = {"initiated": 0, "underivable": [], "uninitiated": []}
    for a in doc["acts"]:
        ini = (a.get("profile") or {}).get("initiation") or {}
        if ini.get("kind") in INITIATION_KINDS:
            out["initiated"] += 1
        elif ini.get("source") == UNDERIVABLE:
            out["underivable"].append(a["id"])
        else:
            out["uninitiated"].append((a["id"], ini.get("missing", "no initiation derived")))
    return out

def interaction_line(i: dict) -> str:
    """One line for the I6 result: `ok` when every derivable act is initiated, else `warn` with the count and the first ids."""
    head = f"I6 initiated={i['initiated']} uninitiated={len(i['uninitiated'])} underivable={len(i['underivable'])}"
    if not i["uninitiated"]:
        return f"ok   [project] countersign: {head}"
    first = ", ".join(f"{aid} ({why})" for aid, why in i["uninitiated"][:3])
    return f"warn [project] countersign: {head} — first: {first}"

# ---- render and main
def render(doc: dict) -> str:
    """Byte-identical for the same document: sorted keys, arrays already sorted by collect, no clock."""
    return json.dumps(doc, sort_keys=True, indent=1, ensure_ascii=False) + "\n"

def counts(doc: dict) -> str:
    return " ".join(f"{e}={len(doc[e])}" for e in ENTITIES)

def main() -> int:
    root = dyadlib.repo_root()
    doc = collect(root, dyadlib.PKG)
    problems = check(doc)
    out = dyadlib.instance(root) / "projections" / "countersign.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    text = render(doc)
    out.write_text(text)
    for p in problems:
        print(f"FAIL [project] countersign: {p}", file=sys.stderr)
    print(f"{'ok  ' if not problems else 'FAIL'} [project] countersign: {counts(doc)} -> {out} ({len(text.encode())} bytes)")
    print(interaction_line(interaction(doc)))
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
