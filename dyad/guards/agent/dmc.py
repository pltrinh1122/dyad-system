#!/usr/bin/env python3
"""Decision-making-criterion guard (entity `dmc`, agent corpus; Rule-12 owns the check — a recurring decision
the dyad states in prose carries a mechanical one — placed per Rule-11 property 1; plan #507). Kernel: Python 3.12+.
A DMC record is a JSON-LD file `<container>/dmc/<identifier>.jsonld`, its form `dyad/dmc/schema.md`, its
context the core's `dyad/dmc/context.jsonld`. Three containers: the core (`dyad/dmc/`, container
`dyad-operator`), every Tended craft (`crafts/<craft>/dmc/`, container `<craft>`) and the instance
(`<instance>/dmc/` and `<host path>/dmc/`, container `instance`; #626). Per record it fails on: a JSON parse error; a missing required key;
an `@context` other than the core context's; an `@type` lacking `DefinedTermSet` or `dyad:DecisionCriterion`;
an `@id` other than `urn:dyad:dmc:<container>/<identifier>`, an `identifier` other than the file stem, an
`isPartOf` other than the container's urn; `dyad:inputs` not a non-empty list of strings; fewer than two
outcomes, an outcome lacking `@type DefinedTerm` or a non-empty `termCode`/`name`/`dyad:when`/`dyad:then`, a
termCode used twice; a `dyad:judgedBy` whose `dyad:kind` is not mechanical|inference|declared|similarity or whose
`dyad:implementation` is neither null nor an existing path; a `dyad:home` or `dyad:alsoIn` path that does not
exist; an outcome name absent from the home file (case-insensitive, whitespace runs collapsed), for a record
homed in a Rule, a craft rule or any other non-procedure file; a date,
version, commit sha or email outside the path fields and `dyad:owner`; an `@id` declared twice. Paths are
relative to the craft root (`dyad/`, `crafts/<craft>/`) for core and craft records and to the repo root for
instance records; `../` may reach another craft but never leave the repo. A path into a craft this system
has not installed (`../crafts/<x>/…` with no `crafts/<x>/`) warns instead of failing (Rule-20 property 2's
severity for an absent store). No record anywhere, or no `dmc/` directory, passes: the summary says so.
The master rule (#626 C0): a record whose `dyad:home` is a play-book or run-book (a file directly under `playbooks/` or
`runbooks/`) is the master of its decision, and its home cites it as `dmc:<identifier>` at the step that applies it.
Each such record fails when its home does not cite it and when the home names every one of its outcomes (a
restatement); C0's per-home phase-in, under which a home citing no record kept the index form and warned, ended with
the last child of #626 (the hard flip). Every `dmc:<id>` in a play-book or run-book of the core or a craft, or in a run-book of the instance's store
(`DYAD_RUNBOOKS`, default `<host path>/runbooks`), names a record, or fails.
Inference, stated: whether a criterion's outcomes are right, whether its home states it, and whether
`dyad:kind` describes how the decision is really made.
  dmc.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("dmc.py: Python 3.12+ required")
import json, os, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib

ENTITY, CORPUS, TRANSACTION = "dmc", "agent", False
CLERICAL_READS = ()   # d-work #564: the ledger/events paths (instance-relative) its state check reads —
                          # the DMC stores of the core, the crafts and the instance (`<instance>/dmc/`), none under the ledger or the events; on a clerical push touching none, the gate leaves it to the sweep
NAME, OWNER = "decision-making criterion", "Rule-12"
FIELDS = ("@context", "@id", "@type", "identifier", "name", "description", "dyad:decides", "dyad:inputs",
          "hasDefinedTerm", "dyad:precedence", "dyad:default", "dyad:tunables", "dyad:judgedBy", "isPartOf", "dyad:home",
          "dyad:alsoIn", "dyad:comparators", "dyad:owner")               # every key of a record, schema.md order
OPTIONAL = ("dyad:precedence", "dyad:default", "dyad:tunables", "dyad:alsoIn", "dyad:comparators")
REQUIRED = tuple(f for f in FIELDS if f not in OPTIONAL)
TYPES = ("DefinedTermSet", "dyad:DecisionCriterion")
OUTCOME_KEYS = ("termCode", "name", "dyad:when", "dyad:then")
KINDS = ("mechanical", "inference", "declared", "similarity")   # similarity: derived over a frozen comparator set (#642)
SIMILARITY = "similarity"
COMPARATOR_KEYS = ("dyad:set", "dyad:sha256", "dyad:threshold", "dyad:margin", "dyad:agreement", "dyad:bar")   # #642
SHA256 = re.compile(r"[0-9a-f]{64}")
RATIFYING = re.compile(r"\b(ratif\w*|dispos\w*|plan-Y|done-Y|merges?|merged|releases?|released|destructive|archiv\w*)\b", re.I)
                                                    # a consequence a similarity outcome may never carry (#642 A5)
PATH_KEYS = ("dyad:home", "dyad:alsoIn", "dyad:implementation")   # path-valued: exempt from the forbidden scan
TUNABLE_KEYS = ("dyad:preference", "dyad:defaultValue", "dyad:allowed", "dyad:readBy")   # one tunable (#590)
TUNABLE_PATH = "dyad:readBy"                                       # path-valued, inside a tunable
PREF_KEY = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")            # a preference key's shape
TEMPLATE = ("templates", "PREFERENCES.md")                         # the core's preference template, under the package
FORBIDDEN_EXEMPT = PATH_KEYS + ("dyad:owner", TUNABLE_PATH, "dyad:set")
CONTEXT = ["https://schema.org", {"dyad": "urn:dyad:term:"}]   # what dyad/dmc/context.jsonld holds
CONTEXT_FILE, STORE, CORE_CONTAINER, INSTANCE_CONTAINER = "context.jsonld", "dmc", "dyad-operator", "instance"
MASTER_DIRS = ("playbooks", "runbooks")   # #626 C0: a record homed in a file of one of these is the decision's master
CITE = re.compile(r"(?<![\w:/-])dmc:([a-z0-9][a-z0-9-]*)")   # a home's citation `dmc:<identifier>`; never a urn's `…:dmc:<container>`
FORBIDDEN = (("date", re.compile(r"\d{4}-\d{2}-\d{2}")),
             ("version", re.compile(r"\bv?\d+\.\d+\.\d+\b")),
             ("commit", re.compile(r"\b[0-9a-f]{40}\b")),
             ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")))
INVARIANTS = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("fields-distinct", lambda: len(set(FIELDS)) == len(FIELDS)),
    ("optional-are-fields", lambda: set(OPTIONAL) <= set(FIELDS) and len(REQUIRED) == len(FIELDS) - len(OPTIONAL) == 13),
    ("path-keys-are-record-keys", lambda: set(PATH_KEYS) - {"dyad:implementation"} <= set(FIELDS)),
    ("owner-required", lambda: "dyad:owner" in REQUIRED and "dyad:owner" in FORBIDDEN_EXEMPT),
    ("tunables-optional", lambda: "dyad:tunables" in OPTIONAL and TUNABLE_PATH in TUNABLE_KEYS and TUNABLE_PATH in FORBIDDEN_EXEMPT),
    ("pref-key-shape", lambda: bool(PREF_KEY.fullmatch("hygiene-stale-days")) and not PREF_KEY.fullmatch("Hygiene_days")),
    ("kinds-are-four", lambda: KINDS == ("mechanical", "inference", "declared", "similarity") and SIMILARITY in KINDS),
    ("comparators-optional", lambda: "dyad:comparators" in OPTIONAL and len(set(COMPARATOR_KEYS)) == len(COMPARATOR_KEYS)),
    ("ratifying-catches-a-merge-and-spares-a-finding", lambda: bool(RATIFYING.search("the named merge may be executed"))
                                                                and not RATIFYING.search("listed as a finding for the home")),
    ("context-is-schema-org-plus-dyad", lambda: CONTEXT[0] == "https://schema.org" and CONTEXT[1] == {"dyad": "urn:dyad:term:"}),
    ("forbidden-patterns-catch-their-kind", lambda: [bool(r.search(s)) for (_, r), s in zip(FORBIDDEN, (
        "on 2026-01-02", "at v1.2.3", "a" * 40, "x@y.org"))] == [True] * 4),
    ("cite-reads-a-citation-not-a-urn", lambda: CITE.findall("step 3: `dmc:release-plan`; urn:dyad:dmc:dyad-operator/x")
                                                == ["release-plan"]),
    ("master-dirs-are-the-procedures", lambda: MASTER_DIRS == ("playbooks", "runbooks")),
    ("forbidden-patterns-spare-a-rule-name", lambda: not any(r.search("Rule-11 sysadmin:host-mutation") for _, r in FORBIDDEN)),
]
TREE_INVARIANTS = [   # reads the package tree: the runner's pass, never at import
    ("context-file-is-the-context", lambda: json.loads((dyadlib.PKG / STORE / CONTEXT_FILE).read_text()).get("@context") == CONTEXT),
]

def stores(root: Path, pkg: Path = dyadlib.PKG) -> list[tuple[str, Path, Path]]:
    """[(container, dmc dir, path base)] for every container whose `dmc/` directory exists: the core, each craft, the
    instance, and the host path's `<host path>/dmc/` (#626: a record homed in a host run-book sits in the host's zone,
    Rule-1), which is the instance's container too, its paths relative to the repo root. An unreadable host path, or
    one whose store is the instance's own, adds nothing."""
    out = [(CORE_CONTAINER, pkg / STORE, pkg)]
    out += [(d.parent.name, d, d.parent) for d in dyadlib.craft_glob(STORE, pkg)]
    out.append((INSTANCE_CONTAINER, dyadlib.instance(root) / STORE, root))
    try:
        host = Path(root) / dyadlib.host_path(root) / STORE
    except ValueError:
        host = None
    if host is not None and os.path.normpath(host) != os.path.normpath(out[-1][1]):
        out.append((INSTANCE_CONTAINER, host, root))
    return [(c, d, b) for c, d, b in out if d.is_dir()]

def records(root: Path, pkg: Path = dyadlib.PKG) -> list[tuple[str, Path, Path]]:
    """[(container, record file, path base)], the context file excluded."""
    return [(c, p, b) for c, d, b in stores(root, pkg) for p in sorted(d.glob("*.jsonld")) if p.name != CONTEXT_FILE]

def urn_part_of(container: str) -> str:
    return "urn:dyad:instance" if container == INSTANCE_CONTAINER else f"urn:dyad:craft:{container}"

def _strings(v, exempt: bool = False):
    """Every string value of a record outside the exempt keys (keys themselves are never scanned)."""
    if isinstance(v, str):
        yield v
    elif isinstance(v, list):
        for x in v:
            yield from _strings(x)
    elif isinstance(v, dict):
        for k, x in v.items():
            if k not in FORBIDDEN_EXEMPT:
                yield from _strings(x)

def resolve(rel: str, base: Path, root: Path, pkg: Path) -> tuple[str, Path | None, str]:
    """('ok'|'fail'|'warn', resolved path or None, reason). Inside the repo and existing → ok; outside the repo →
    fail; inside an absent craft's directory → warn; otherwise absent → fail."""
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        return "fail", None, "is not a relative path"
    p = Path(os.path.normpath(base / rel)); r = Path(os.path.normpath(root))
    if not p.is_relative_to(r):
        return "fail", None, "resolves outside the repo"
    if p.exists():
        return "ok", p, ""
    cd = Path(os.path.normpath(dyadlib.crafts_dir(pkg)))
    if p.is_relative_to(cd) and p != cd and not (cd / p.relative_to(cd).parts[0]).is_dir():
        return "warn", None, f"names craft {p.relative_to(cd).parts[0]}, absent here (Rule-20 property 2)"
    return "fail", None, "does not exist"

def _collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()

def is_master_home(home: Path | None) -> bool:
    """#626 C0: True when `home` is a play-book or run-book (a file directly under a `playbooks/` or `runbooks/`
    directory): a record homed there is the master of its decision. A record homed in an Agent Rule or a craft rule
    is not, and its home stays the master (plan #626 A1)."""
    return home is not None and home.parent.name in MASTER_DIRS

def citations(text: str) -> list[str]:
    """The identifiers `text` cites as `dmc:<identifier>`, in order, each once."""
    return list(dict.fromkeys(CITE.findall(text)))

def host_runbooks(root: Path) -> Path | None:
    """The instance's run-book store (Rule-19 property 1): `DYAD_RUNBOOKS`, else `<host path>/runbooks`, as
    `runbook.runbooks_rel` reads it; None when the host path is unreadable."""
    try:
        rel = os.environ.get("DYAD_RUNBOOKS") or f"{dyadlib.host_path(root)}/runbooks"
    except ValueError:
        return None
    return Path(root) / rel.rstrip("/")

def procedure_files(pkg: Path = dyadlib.PKG, root: Path | None = None) -> list[Path]:
    """Every play-book and run-book of the core and of each Tended craft, and with `root` every run-book of the
    instance's store (`host_runbooks`): the files whose citations must resolve (#626 C0, #639)."""
    roots = [pkg] + [d.parent for d in dyadlib.craft_glob("VERSION", pkg)]
    files = {f for r in roots for m in MASTER_DIRS for f in (r / m).glob("*.md")}
    if root is not None and (h := host_runbooks(root)) is not None and h.is_dir():
        files |= {f for f in h.glob("*.md") if f.stem.lower() != "readme"}
    return sorted(files)

def tunable_keys(d) -> list[str]:
    """The preference keys a record's `dyad:tunables` names, malformed entries skipped."""
    t = d.get("dyad:tunables") if isinstance(d, dict) else None
    return [x["dyad:preference"] for x in t if isinstance(x, dict) and isinstance(x.get("dyad:preference"), str)] \
        if isinstance(t, list) else []

def tunable_problems(t, base: Path, root: Path, pkg: Path, bad, warn) -> list[str]:
    """`dyad:tunables` (#590): a non-empty list of objects, each holding TUNABLE_KEYS as non-empty strings, its
    preference a key-shaped name used once in the record, its `dyad:readBy` a path resolved as `dyad:home` is."""
    if not (isinstance(t, list) and t):
        bad("dyad:tunables is not a non-empty list"); return []
    keys = []
    for i, x in enumerate(t):
        if not isinstance(x, dict):
            bad(f"dyad:tunables[{i}] is not an object"); continue
        for k in TUNABLE_KEYS:
            if not (isinstance(x.get(k), str) and x[k].strip()):
                bad(f"dyad:tunables[{i}] {k} is not a non-empty string")
        pk = x.get("dyad:preference")
        if isinstance(pk, str) and pk.strip():
            if not PREF_KEY.fullmatch(pk):
                bad(f"dyad:tunables[{i}] dyad:preference {pk!r} is not a preference key (lowercase, hyphenated)")
            keys.append(pk)
        rb = x.get(TUNABLE_PATH)
        if isinstance(rb, str) and rb.strip():
            st, _, why = resolve(rb, base, root, pkg)
            if st != "ok":
                (warn if st == "warn" else bad)(f"dyad:tunables[{i}] dyad:readBy {rb!r} {why}")
    for k in sorted({k for k in keys if keys.count(k) > 1}):
        bad(f"dyad:tunables names preference {k!r} twice")
    return keys

def comparator_problems(d: dict, kind, terms: list, base: Path, root: Path, pkg: Path, bad, warn) -> None:
    """#642: a `similarity` record carries `dyad:comparators` ({COMPARATOR_KEYS}), and only such a record does. It fails
    when the set's file is missing or no comparator set (`similar.load`), its sha256 differs, its labels are not the
    record's outcome names, the threshold or margin names no preference of the record's `dyad:tunables`, the agreement
    or bar is no number in [0, 1], the agreement is below the bar, or an outcome's `dyad:then` names a ratification
    event or a destructive act (A5: a disposition is never derived)."""
    c = d.get("dyad:comparators")
    if kind != SIMILARITY:
        bad(f"dyad:comparators on a record of kind {kind!r}: only a similarity record carries one"); return
    if not isinstance(c, dict):
        bad("a similarity record carries dyad:comparators, an object of " + ", ".join(COMPARATOR_KEYS)); return
    missing = [k for k in COMPARATOR_KEYS if k not in c]
    if missing:
        bad(f"dyad:comparators lacks {', '.join(missing)}"); return
    names = {o.get("name") for o in terms if isinstance(o, dict)}
    for o in terms:
        if isinstance(o, dict) and isinstance(o.get("dyad:then"), str) and (m := RATIFYING.search(o["dyad:then"])):
            bad(f"similarity outcome {o.get('termCode')!r} names {m.group(0)!r} in its consequence: a ratification event "
                f"or a destructive act is never derived by similarity (#642 A5)")
    st, path, why = resolve(c["dyad:set"], base, root, pkg)
    if st != "ok":
        (warn if st == "warn" else bad)(f"dyad:comparators dyad:set {c['dyad:set']!r} {why}")
    else:
        import similar
        try:
            cset = similar.load(path)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
            bad(f"dyad:comparators dyad:set {c['dyad:set']!r}: {e}"); cset = None
        if cset is not None:
            if not (isinstance(c["dyad:sha256"], str) and SHA256.fullmatch(c["dyad:sha256"])):
                bad("dyad:comparators dyad:sha256 is not 64 hex")
            elif cset["sha256"] != c["dyad:sha256"]:
                bad(f"dyad:comparators dyad:sha256 differs from the set's ({cset['sha256'][:12]}…): the set changed "
                    f"since it was measured")
            if similar.labels(cset) != names:
                bad(f"the comparator set's labels {sorted(similar.labels(cset))} are not the record's outcome names {sorted(names)}")
    keys = tunable_keys(d)
    for k in ("dyad:threshold", "dyad:margin"):
        if c[k] not in keys:
            bad(f"dyad:comparators {k} {c[k]!r} names no preference of this record's dyad:tunables")
    nums = {k: c[k] for k in ("dyad:agreement", "dyad:bar")}
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1 for v in nums.values()):
        bad("dyad:comparators dyad:agreement and dyad:bar are numbers in [0, 1]")
    elif nums["dyad:agreement"] < nums["dyad:bar"]:
        bad(f"dyad:comparators agreement {nums['dyad:agreement']} is below its bar {nums['dyad:bar']}: the decision "
            f"returns to inference (#642 A4)")

def template_keys(pkg: Path) -> set[str] | None:
    """The keys of the core's preference template, or None when it is absent."""
    p = pkg.joinpath(*TEMPLATE)
    if not p.is_file():
        return None
    return {dyadlib.plain(r[0]).strip() for r in dyadlib.table_rows(p.read_text()) if r}

def check_record(container: str, path: Path, base: Path, root: Path, pkg: Path, context) -> tuple[list[str], str | None]:
    """(messages, @id or None) for one record; bare messages fail, `warning:` ones warn."""
    name = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
    try:
        d = json.loads(path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return [f"{name}: not JSON ({e.msg if hasattr(e, 'msg') else e})"], None
    if not isinstance(d, dict):
        return [f"{name}: not a JSON object"], None
    msgs = []; bad = lambda m: msgs.append(f"{name}: {m}"); warn = lambda m: msgs.append(f"warning: {name}: {m}")
    missing = [k for k in REQUIRED if k not in d]
    if missing:
        bad(f"missing required key(s) {', '.join(missing)} (dyad/dmc/schema.md)")
    if "@context" in d and d["@context"] != context:
        bad("@context differs from dyad/dmc/context.jsonld's")
    t = d.get("@type")
    if "@type" in d and not (isinstance(t, list) and all(x in t for x in TYPES)):
        bad(f"@type must hold {' and '.join(TYPES)}")
    ident = d.get("identifier")
    if "identifier" in d and ident != path.stem:
        bad(f"identifier {ident!r} differs from the file stem {path.stem!r}")
    want_id = f"urn:dyad:dmc:{container}/{path.stem}"
    if "@id" in d and d["@id"] != want_id:
        bad(f"@id {d['@id']!r} is not {want_id!r}")
    if "isPartOf" in d and d["isPartOf"] != urn_part_of(container):
        bad(f"isPartOf {d['isPartOf']!r} is not {urn_part_of(container)!r}")
    for k in ("name", "description", "dyad:decides", "dyad:owner"):
        if k in d and not (isinstance(d[k], str) and d[k].strip()):
            bad(f"{k} is not a non-empty string")
    ins = d.get("dyad:inputs")
    if "dyad:inputs" in d and not (isinstance(ins, list) and ins and all(isinstance(x, str) and x.strip() for x in ins)):
        bad("dyad:inputs is not a non-empty list of strings")
    terms = d.get("hasDefinedTerm"); outcomes = []
    if "hasDefinedTerm" in d:
        if not (isinstance(terms, list) and len(terms) >= 2):
            bad("hasDefinedTerm is not a list of at least two outcomes")
        else:
            codes = []
            for i, o in enumerate(terms):
                if not isinstance(o, dict):
                    bad(f"hasDefinedTerm[{i}] is not an object"); continue
                ot = o.get("@type")
                if not (ot == "DefinedTerm" or (isinstance(ot, list) and "DefinedTerm" in ot)):
                    bad(f"hasDefinedTerm[{i}] @type is not DefinedTerm")
                for k in OUTCOME_KEYS:
                    if not (isinstance(o.get(k), str) and o[k].strip()):
                        bad(f"hasDefinedTerm[{i}] {k} is not a non-empty string")
                if isinstance(o.get("termCode"), str):
                    codes.append(o["termCode"])
                if isinstance(o.get("name"), str) and o["name"].strip():
                    outcomes.append(o["name"])
            for c in sorted({c for c in codes if codes.count(c) > 1}):
                bad(f"termCode {c!r} used twice")
    jb = d.get("dyad:judgedBy")
    if "dyad:judgedBy" in d:
        if not isinstance(jb, dict):
            bad("dyad:judgedBy is not an object")
        else:
            if jb.get("dyad:kind") not in KINDS:
                bad(f"dyad:judgedBy dyad:kind {jb.get('dyad:kind')!r} is not one of {', '.join(KINDS)}")
            if "dyad:implementation" not in jb:
                bad("dyad:judgedBy lacks dyad:implementation (a path, or null)")
            elif jb["dyad:implementation"] is not None:
                st, _, why = resolve(jb["dyad:implementation"], base, root, pkg)
                if st != "ok":
                    (warn if st == "warn" else bad)(f"dyad:implementation {jb['dyad:implementation']!r} {why}")
    kind = jb.get("dyad:kind") if isinstance(jb, dict) else None
    if kind == SIMILARITY or "dyad:comparators" in d:
        comparator_problems(d, kind, terms if isinstance(terms, list) else [], base, root, pkg, bad, warn)
    if "dyad:tunables" in d:
        if container != CORE_CONTAINER:   # one home for a default, the core's: dyadlib.tunable reads no other record (#590)
            bad("dyad:tunables is the core's only (dyad/dmc/): dyadlib.tunable reads no craft or instance record (#590)")
        else:
            tunable_problems(d["dyad:tunables"], base, root, pkg, bad, warn)
    home = None
    if "dyad:home" in d:
        st, home, why = resolve(d["dyad:home"], base, root, pkg)
        if st != "ok":
            (warn if st == "warn" else bad)(f"dyad:home {d['dyad:home']!r} {why}")
    if "dyad:alsoIn" in d:
        also = d["dyad:alsoIn"]
        if not (isinstance(also, list) and all(isinstance(x, str) for x in also)):
            bad("dyad:alsoIn is not a list of paths")
        else:
            for a in also:
                st, _, why = resolve(a, base, root, pkg)
                if st != "ok":
                    (warn if st == "warn" else bad)(f"dyad:alsoIn {a!r} {why}")
    if home is not None and home.is_file() and outcomes:
        raw = home.read_text(errors="replace"); text = _collapse(raw)
        if is_master_home(home):   # #626: the record is the master (the per-home phase-in ended with the hard flip)
            if ident not in citations(raw):
                bad(f"master record not cited: its dyad:home {d['dyad:home']} cites no `dmc:{ident}` (dyad/dmc/schema.md)")
            if all(_collapse(o) in text for o in outcomes):
                bad(f"restated: dyad:home {d['dyad:home']} names every outcome of this master record; the home "
                    f"cites `dmc:{ident}` and restates none of its definitions (dyad/dmc/schema.md)")
        else:
            for o in outcomes:
                if _collapse(o) not in text:
                    bad(f"outcome name {o!r} not found in dyad:home {d['dyad:home']}")
    found = set()
    for s in _strings(d):
        for kind, rx in FORBIDDEN:
            m = rx.search(s)
            if m and (kind, m.group(0)) not in found:
                found.add((kind, m.group(0))); bad(f"forbidden {kind} {m.group(0)!r} (dyad/dmc/schema.md)")
    rid = d.get("@id") if isinstance(d.get("@id"), str) else None
    return msgs, rid

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    recs = records(root, pkg)
    if not recs:
        return []
    ctx_path = pkg / STORE / CONTEXT_FILE
    try:
        context = json.loads(ctx_path.read_text()).get("@context")
    except (OSError, json.JSONDecodeError, AttributeError):
        return [f"{STORE}/{CONTEXT_FILE}: the core context is absent or not JSON; {len(recs)} records cannot be judged"]
    msgs, seen, claims = [], {}, {}
    for container, p, base in recs:
        m, rid = check_record(container, p, base, root, pkg, context)
        msgs += m
        if rid is not None:
            seen.setdefault(rid, []).append(p)
        try:
            for k in dict.fromkeys(tunable_keys(json.loads(p.read_text()))):
                claims.setdefault(k, []).append(p)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    idents = set()
    for container, p, base in recs:
        try:
            d = json.loads(p.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(d, dict) and isinstance(d.get("identifier"), str):
            idents.add(d["identifier"])
    for f in procedure_files(pkg, root):   # #626 C0: every `dmc:<id>` names a record, from C0 on; the host's run-books too (#639)
        name = f.relative_to(root).as_posix() if f.is_relative_to(root) else str(f)
        for c in citations(f.read_text(errors="replace")):
            if c not in idents:
                msgs.append(f"{name}: `dmc:{c}` names no DMC record (dyad/dmc/, crafts/<craft>/dmc/, <instance>/dmc/)")
    tkeys, unseeded = template_keys(pkg), {}
    for k, ps in sorted(claims.items()):
        if len(ps) > 1:
            msgs.append(f"preference {k!r} claimed as a tunable by {len(ps)} records: " + ", ".join(x.name for x in ps))
        elif tkeys is not None and k not in tkeys:
            unseeded.setdefault(ps[0].name, []).append(k)
    for name, ks in sorted(unseeded.items()):   # one line per record: the gap until the keys are seeded (#590)
        msgs.append(f"warning: {name}: {len(ks)} tunable(s) with no row in {'/'.join(TEMPLATE)} yet: {', '.join(ks)}")
    for rid, ps in seen.items():
        if len(ps) > 1:
            msgs.append(f"@id {rid} declared by {len(ps)} records: " + ", ".join(
                (x.relative_to(root).as_posix() if x.is_relative_to(root) else str(x)) for x in ps))
    return msgs

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    recs = records(root or dyadlib.repo_root(), pkg)
    if not recs:
        return "skip: no DMC records (no dmc/*.jsonld in the core, a craft or the instance)"
    by = {}
    for c, *_ in recs:
        by[c] = by.get(c, 0) + 1
    return f"{len(recs)} records (" + ", ".join(f"{c} {n}" for c, n in by.items()) + ")"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    recs = records(root, pkg)
    ex = {}
    if recs:
        try:
            ex = json.loads(recs[0][1].read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            ex = {}
    show = lambda v: v if isinstance(v, str) else json.dumps(v)[:80]
    fields = [(f, "json", "", f in REQUIRED, show(ex.get(f, "")), "dmc.FIELDS") for f in FIELDS]
    return {"store": "dyad/dmc/<id>.jsonld, crafts/<craft>/dmc/<id>.jsonld, <instance>/dmc/<id>.jsonld",
            "parser": "`dmc.check_record` (JSON-LD, schema.org plus the dyad: terms of dyad/dmc/schema.md)",
            "observed": len(recs),
            "note": "one decision-making criterion per record; its outcomes are hasDefinedTerm, its home the file that states it",
            "fields": fields}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        if m.startswith("warning:"): print(f"warn [rule-12] {m.removeprefix('warning:').strip()}")
        else: print(f"FAIL [rule-12] {m}", file=sys.stderr)
    if not fails:
        print(f"ok   [rule-12] {summary(root)}")
    return 1 if fails else 0

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import (crafts/syseng/rules/invariants.md p1)

if __name__ == "__main__":
    sys.exit(main())
