#!/usr/bin/env python3
"""Decision-making-criterion guard (entity `dmc`, agent corpus; Rule-12 owns the check — a recurring decision
the dyad states in prose carries a mechanical one — placed per Rule-11 property 1; plan #507). Kernel: Python 3.12+.
A DMC record is a JSON-LD file `<container>/dmc/<identifier>.jsonld`, its form `dyad/dmc/schema.md`, its
context the core's `dyad/dmc/context.jsonld`. Three containers: the core (`dyad/dmc/`, container
`dyad-operator`), every Tended craft (`crafts/<craft>/dmc/`, container `<craft>`) and the instance
(`<instance>/dmc/`, container `instance`). Per record it fails on: a JSON parse error; a missing required key;
an `@context` other than the core context's; an `@type` lacking `DefinedTermSet` or `dyad:DecisionCriterion`;
an `@id` other than `urn:dyad:dmc:<container>/<identifier>`, an `identifier` other than the file stem, an
`isPartOf` other than the container's urn; `dyad:inputs` not a non-empty list of strings; fewer than two
outcomes, an outcome lacking `@type DefinedTerm` or a non-empty `termCode`/`name`/`dyad:when`/`dyad:then`, a
termCode used twice; a `dyad:judgedBy` whose `dyad:kind` is not mechanical|inference|declared or whose
`dyad:implementation` is neither null nor an existing path; a `dyad:home` or `dyad:alsoIn` path that does not
exist; an outcome name absent from the home file (case-insensitive, whitespace runs collapsed); a date,
version, commit sha or email outside the path fields and `dyad:owner`; an `@id` declared twice. Paths are
relative to the craft root (`dyad/`, `crafts/<craft>/`) for core and craft records and to the repo root for
instance records; `../` may reach another craft but never leave the repo. A path into a craft this system
has not installed (`../crafts/<x>/…` with no `crafts/<x>/`) warns instead of failing (Rule-20 property 2's
severity for an absent store). No record anywhere, or no `dmc/` directory, passes: the summary says so.
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
NAME, OWNER = "decision-making criterion", "Rule-12"
FIELDS = ("@context", "@id", "@type", "identifier", "name", "description", "dyad:decides", "dyad:inputs",
          "hasDefinedTerm", "dyad:precedence", "dyad:default", "dyad:judgedBy", "isPartOf", "dyad:home",
          "dyad:alsoIn", "dyad:owner")                                   # every key of a record, schema.md order
OPTIONAL = ("dyad:precedence", "dyad:default", "dyad:alsoIn")
REQUIRED = tuple(f for f in FIELDS if f not in OPTIONAL)
TYPES = ("DefinedTermSet", "dyad:DecisionCriterion")
OUTCOME_KEYS = ("termCode", "name", "dyad:when", "dyad:then")
KINDS = ("mechanical", "inference", "declared")
PATH_KEYS = ("dyad:home", "dyad:alsoIn", "dyad:implementation")   # path-valued: exempt from the forbidden scan
FORBIDDEN_EXEMPT = PATH_KEYS + ("dyad:owner",)
CONTEXT = ["https://schema.org", {"dyad": "urn:dyad:term:"}]   # what dyad/dmc/context.jsonld holds
CONTEXT_FILE, STORE, CORE_CONTAINER, INSTANCE_CONTAINER = "context.jsonld", "dmc", "dyad-operator", "instance"
FORBIDDEN = (("date", re.compile(r"\d{4}-\d{2}-\d{2}")),
             ("version", re.compile(r"\bv?\d+\.\d+\.\d+\b")),
             ("commit", re.compile(r"\b[0-9a-f]{40}\b")),
             ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")))
INVARIANTS = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("fields-distinct", lambda: len(set(FIELDS)) == len(FIELDS)),
    ("optional-are-fields", lambda: set(OPTIONAL) <= set(FIELDS) and len(REQUIRED) == len(FIELDS) - len(OPTIONAL) == 13),
    ("path-keys-are-record-keys", lambda: set(PATH_KEYS) - {"dyad:implementation"} <= set(FIELDS)),
    ("owner-required", lambda: "dyad:owner" in REQUIRED and "dyad:owner" in FORBIDDEN_EXEMPT),
    ("kinds-are-three", lambda: KINDS == ("mechanical", "inference", "declared")),
    ("context-is-schema-org-plus-dyad", lambda: CONTEXT[0] == "https://schema.org" and CONTEXT[1] == {"dyad": "urn:dyad:term:"}),
    ("forbidden-patterns-catch-their-kind", lambda: [bool(r.search(s)) for (_, r), s in zip(FORBIDDEN, (
        "on 2026-01-02", "at v1.2.3", "a" * 40, "x@y.org"))] == [True] * 4),
    ("forbidden-patterns-spare-a-rule-name", lambda: not any(r.search("Rule-11 sysadmin:host-mutation") for _, r in FORBIDDEN)),
]
TREE_INVARIANTS = [   # reads the package tree: the runner's pass, never at import
    ("context-file-is-the-context", lambda: json.loads((dyadlib.PKG / STORE / CONTEXT_FILE).read_text()).get("@context") == CONTEXT),
]

def stores(root: Path, pkg: Path = dyadlib.PKG) -> list[tuple[str, Path, Path]]:
    """[(container, dmc dir, path base)] for every container whose `dmc/` directory exists: the core, each craft, the instance."""
    out = [(CORE_CONTAINER, pkg / STORE, pkg)]
    out += [(d.parent.name, d, d.parent) for d in dyadlib.craft_glob(STORE, pkg)]
    out.append((INSTANCE_CONTAINER, dyadlib.instance(root) / STORE, root))
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
        text = _collapse(home.read_text(errors="replace"))
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
    msgs, seen = [], {}
    for container, p, base in recs:
        m, rid = check_record(container, p, base, root, pkg, context)
        msgs += m
        if rid is not None:
            seen.setdefault(rid, []).append(p)
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
