#!/usr/bin/env python3
"""Reference guard (entity `reference`, agent corpus; Rule-20 owns the register; placed per Rule-11 property 1).
Kernel: Python 3.12+, stdlib and git.
Every reference from one entity instance to another — a row id in `refs`, a Rule number in a
row, a Rule text or the preference table, a plan file's id and base commit, a Rule's Provenance
pointer, a backticked package or craft path in a Rule (`dyad/…`, `crafts/…`, `.github/workflows/dyad-…`), the frame's `@` imports (and the reverse: every
Rule file imported), a change-log, incident or ops-script `#N`, an ops script's change-log key, a
record's `ledger #N`, a registry module, a run-book event's command name and a change-log row's
`event: <id>` (Rule-19, d-work #150) — is listed once in `REFERENCES` with one resolver and
resolved mechanically: the target *exists*, nothing more (property 3). A kind another guard
already resolves is listed as `guard:<corpus>/<entity>.py` and not re-run (the frame's imports,
kinds 12 and 13, are `guards/agent/frame.py`'s since plan #151); a kind into The World is `world`
and warns once as inference — including a package or Tended craft's own `ledger #N` citations
(`dyad/`, `crafts/*/falsification/rules/`, `crafts/*/rules/`: historical provenance of the
authoring instance, never a receiving instance's to resolve, #177), distinct from an instance
record's own citations (`agent-corpus/`), which stay a real, resolved reference; a target store
that is absent or empty (a fresh install) skips its
kinds with a printed line, never a failure (property 4) — and so does a kind whose parser is a
Tended craft's guard that no installed craft provides (`sysadmin/ops_scripts`, `sysadmin/runbooks`,
`sysadmin/events`; `dyadlib.find_guard`, #155). A `crafts/<name>/…` path resolves against the *craft*,
not the tree (#167): present, the path must exist; absent, one line per craft — `skip` where no
`crafts/REGISTRY.md` exists to judge the name, `warn … unknown craft` where the registry has no such
row, and a failure where it has one (installed, then deleted). The entities projector (crafts/sysarch/rules/projection.md)
draws its relations from the same list (crafts/sysarch/rules/references.md p4).
  references.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("references.py: Python 3.12+ required")
import fnmatch, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dyadlib
vocabulary = dyadlib.load_guard("agent", "vocabulary")
craft_cli = dyadlib.load_module(dyadlib.PKG / "scripts" / "craft.py", "dyad_craft_cli")   # the craft registry's format is craft.py's (Rule-13 p2): read through it, never re-authored
ops_scripts = dyadlib.find_guard("workstation", "ops_scripts")   # the sysadmin craft's guards: None when no craft provides them
runbooks = dyadlib.find_guard("workstation", "runbooks")
events = dyadlib.find_guard("workstation", "events")
GUARD_KINDS = {"changelog.action->ops": ("ops_scripts", ops_scripts), "ops.dwork->row": ("ops_scripts", ops_scripts),
               "ops.changelog->changelog": ("ops_scripts", ops_scripts), "event.command->command": ("runbooks", runbooks),
               "changelog.event->event": ("events", events)}          # kind -> (craft guard entity, module or None)
provenance = dyadlib.load_guard("agent", "provenance")   # core guard: always present

ENTITY, CORPUS, TRANSACTION = "reference", "agent", False
NAME, OWNER = "reference kind (register row)", "Rule-20"
FIELDS = ("kind", "source", "field", "target", "resolver")     # one REFERENCES entry, minus its extractor
NON_GUARD_SOURCES = {"rules", "registry", "cache", "pr", "incident", "craft_rule"}   # register sources that are not a guard's ENTITY: data files, the runner, The World, the incident log (no guard, plan #151), and a Tended craft's own rule text (#177)
WORLD_TARGETS = {"file", "commit", "pr", "component"}           # targets that are not an entity of this surface
CRAFT_ENTITIES = {"changelog", "ops", "command", "event"}        # entities the sysadmin craft's guards declare; absent on a core-only install, when the kinds naming them skip (#155)
table_rows, load_module = dyadlib.table_rows, dyadlib.load_module   # shared parsers (dyadlib owns them since #151)

def generated_patterns(pkg: Path) -> list[str]:
    """`generated:` entries of package_rules.txt (Rule-11 property 6 data); empty when absent."""
    f = pkg / "scripts" / "package_rules.txt"
    if not f.exists():
        return []
    out = []
    for line in f.read_text().splitlines():
        k, _, v = line.strip().partition(":")
        if k.strip() == "generated" and v.strip():
            out.append(v.strip())
    return out

def installed_crafts(pkg: Path) -> set[str]:
    """The Tended crafts installed beside the package, derived from `dyadlib.craft_dirs` and never
    enumerated here (INVARIANTS `craft-set-is-craft-dirs`, `craft-names-not-literal`; #167)."""
    return {p.name for p in dyadlib.craft_dirs(pkg)}

def craft_token(token: str) -> tuple[str | None, str | None]:
    """Classify a `crafts/…` path token: `("craft", <name>)` when its second segment is a craft name
    (the shape `craft.py` `_NAME` allows: lower-case, no dot), `("registry", None)` for a file at the
    crafts root (`crafts/REGISTRY.md`), `(None, None)` for a glob or a `<placeholder>`, which keeps
    the ordinary path/glob resolution."""
    seg = token.removeprefix("crafts/").split("/")[0]
    if not seg or "*" in seg or "<" in seg or ">" in seg:
        return None, None
    if "." in seg:
        return ("registry", None) if seg == "REGISTRY.md" else (None, None)
    return "craft", seg

# ---- token patterns
_RANGE = re.compile(r"#(\d+)\s*[–-]\s*#(\d+)")
_HASH = re.compile(r"#(\d+)\b")
_RULE = re.compile(r"\bRule-(\d+)\b")
_LEDGER = re.compile(r"(?:ledger|d-work) #(\d+)\b")
_MERGE = re.compile(r"\bmerge #(\d+)\b")
_BASE = re.compile(r"(?i)base commit[^:\n]*:\s*([0-9a-f]{7,40})\b")
_PKG_PATH = re.compile(r"`((?:dyad/|crafts/|\.github/workflows/dyad-)[^`]*)`")
_PROVENANCE = re.compile(r"`(\.\./falsification/rules/[^`]+)`")
PRE_LEDGER = "(pre-ledger)"
_CL_KEY = re.compile(r'row "#(\d+) (H\d+)"')
_EVENT = re.compile(r"\bevent:\s*`?([A-Za-z0-9][\w.-]*)`?")

def hash_ids(text: str) -> list[str]:
    """`#N` ids in a field: `#a–#b` / `#a-#b` ranges expand; a `;`-segment starting `PR` is skipped,
    and so is one annotated `(pre-ledger)` — the field itself says its target predates the store."""
    out = []
    for seg in text.split(";"):
        seg = seg.strip()
        if seg.startswith("PR") or PRE_LEDGER in seg:
            continue
        def expand(m):
            a, b = int(m.group(1)), int(m.group(2))
            out.extend(str(i) for i in range(min(a, b), max(a, b) + 1)); return " "
        rest = _RANGE.sub(expand, seg)
        out.extend(_HASH.findall(rest))
    return out

# ---- the corpus a check reads once
class Corpus:
    def __init__(self, root: Path, pkg: Path):
        self.root, self.pkg, self.inst = root, pkg, dyadlib.instance(root)
        self.rows = {r.id for r in dyadlib.read_rows(root)} if dyadlib.rows_dir(root).is_dir() else set()
        self.row_files = {r: dyadlib.rows_dir(root) / f"{r}.md" for r in self.rows}
        self.rules = dyadlib.rule_files(pkg)
        self.rule_text = {n: p.read_text() for n, p in self.rules.items()}
        plans = self.inst / "d-work" / "plans"
        self.plans = sorted((p for p in plans.glob("*.md") if p.stem.isdigit()), key=lambda p: int(p.stem)) if plans.is_dir() else []
        self.provenance = provenance.records(root)          # Rule-21 property 3: the guard is the parser
        frame = pkg / "CLAUDE.md"
        self.frame_lines = [l.strip() for l in frame.read_text().splitlines() if l.startswith("@")] if frame.exists() else []
        prefs = root / "preferences-corpus" / "PREFERENCES.md"
        self.prefs = (dyadlib.table_header(prefs.read_text()), table_rows(prefs.read_text().replace("\\|", "/"))) if prefs.exists() else ([], [])
        cl = root / "workstation-corpus" / "CHANGELOG.md"
        self.changelog = (dyadlib.table_header(cl.read_text()), table_rows(cl.read_text())) if cl.exists() else ([], [])
        inc = self.inst / "audits" / "INCIDENTS.md"
        self.incidents = (dyadlib.table_header(inc.read_text()), table_rows(inc.read_text())) if inc.exists() else ([], [])
        ops = ops_scripts.ops_dir(root) if ops_scripts else None
        self.ops = {p: p.read_text(errors="ignore") for p in sorted(ops.glob("*.sh"))} if ops and ops.is_dir() else {}
        recs = []
        for d in (pkg / "falsification" / "rules", self.inst / "falsification", self.inst / "audits"):
            if d.is_dir():
                recs += sorted(d.glob("*.md"))
        recs += dyadlib.craft_glob("falsification/rules/*.md", pkg)   # a Tended craft's own Rule records: package-shipped too (#177)
        self.records = {p: p.read_text(errors="ignore") for p in recs}
        self.craft_rules = {p: p.read_text(errors="ignore") for p in dyadlib.craft_glob("rules/*.md", pkg)}   # a Tended craft's own rule text (#177); never `workstation-corpus/rules/` (the host's, genuinely instance-side)
        self.runbooks = {n: runbooks.parse(p) for n, p in runbooks.runbooks(root).items()} if runbooks else {}   # {instance: [Command]}
        self.events = events.all_events(root) if events else {}                                              # {instance: [event dict]}
        pk = pkg / "scripts" / "package.py"
        self.registry = dict(getattr(load_module(pk, f"dyad_registry_{abs(hash(str(pk)))}"), "PROJECTORS", {})) if pk.exists() else {}
        self.generated = generated_patterns(pkg)
        crafts = dyadlib.crafts_dir(pkg)
        self.crafts_absent = not crafts.is_dir()                    # a core-only install: `crafts/…` paths a Rule names skip (property 4)
        self.installed_crafts = installed_crafts(pkg)               # the unit of presence is the craft, not the tree (#167)
        reg = crafts / "REGISTRY.md"                                # craft.REGISTRY, relative to the repo root
        self.craft_registry = set(craft_cli.registry_rows(crafts.parent)) if reg.exists() else None   # None: this install has no craft registry
        self._commits: dict[str, bool] | None = None
        try:
            import package
            self._generated_match = package.generated_matches
        except Exception:  # package.py outside a git repo: whole-token match only
            self._generated_match = lambda rel, pats: next((g for g in pats if fnmatch.fnmatch(rel, g)), None)

    def rel(self, p: Path) -> str:
        return str(p.relative_to(self.root)) if p.is_relative_to(self.root) else str(p)

    def commit_known(self, sha: str) -> bool:
        if self._commits is None:  # one `git cat-file --batch-check` for every plan's sha
            shas = sorted({t for _, t in base_commit(self)})
            r = subprocess.run(["git", "cat-file", "--batch-check"], cwd=self.root, input="".join(f"{s}^{{commit}}\n" for s in shas),
                               capture_output=True, text=True)
            self._commits = {s: False for s in shas}
            for line in r.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "commit":
                    for s in shas:
                        if parts[0].startswith(s):
                            self._commits[s] = True
        return self._commits.get(sha, False)

    def craft_state(self, token: str) -> tuple[str, str, str] | None:
        """How a `crafts/…` token resolves on *this* install (property 4, #167). `None` resolves it as a
        path (a present craft, a glob, a registry that is there); otherwise `(severity, key, reason)`:
          skip — the craft is absent and this install has no `crafts/REGISTRY.md` to judge the name by,
                 or the token names the registry itself and it has never been written;
          warn — the craft is absent *and* not in the registry: unknown here (a typo reads the same, so
                 it is stated on every run, never silently skipped);
          FAIL — the registry lists the craft as installed and its tree is gone (installed-then-deleted).
        """
        kind, name = craft_token(token)
        if kind == "registry":
            return None if self.craft_registry is not None else ("skip", "crafts/REGISTRY.md", "crafts/REGISTRY.md absent (no craft installed here)")
        if kind != "craft" or name in self.installed_crafts:
            return None
        if self.craft_registry is None:
            return "skip", name, f"craft {name} absent (Rule-20 property 4)"
        if name in self.craft_registry:
            return "FAIL", name, f"craft {name} is installed per crafts/REGISTRY.md and crafts/{name}/ is missing"
        return "warn", name, f"craft {name} absent and not in crafts/REGISTRY.md (unknown craft: never installed here, or a typo)"

    def store_empty(self, target: str) -> bool:
        """A target store that is absent or holds no instance (property 4)."""
        if target == "row":
            return not self.rows
        if target == "rule":
            return not self.rules
        if target == "changelog":
            return not self.changelog[1]
        if target == "command":
            return not any(self.runbooks.values())
        if target == "event":
            return not any(self.events.values())
        return False

# ---- extractors: each returns [(where, token)]
def rows_refs(c: Corpus):
    return [(f"{c.rel(c.row_files[r])} refs", t) for r in sorted(c.rows) for t in hash_ids(dyadlib.parse_row_file(c.row_files[r].read_text()).refs)]

def rule_tokens(c: Corpus):
    out = []
    for r in sorted(c.rows):
        out += [(f"{c.rel(c.row_files[r])} refs", n) for n in _RULE.findall(dyadlib.parse_row_file(c.row_files[r].read_text()).refs)]
    return out

def pr_tokens(c: Corpus):
    out = []
    for r in sorted(c.rows):
        row = dyadlib.parse_row_file(c.row_files[r].read_text())
        out += [(f"{c.rel(c.row_files[r])} disposed", n) for n in _MERGE.findall(row.disposed)]
        out += [(f"{c.rel(c.row_files[r])} refs", n) for seg in row.refs.split(";") if seg.strip().startswith("PR") for n in _HASH.findall(seg)]
    return out

def plan_id(c: Corpus):
    return [(c.rel(p), p.stem) for p in c.plans]

def provenance_id(c: Corpus):
    return [(c.rel(p), p.stem) for p in c.provenance]

def base_commit(c: Corpus):
    out = []
    for p in c.plans:
        m = _BASE.search(p.read_text())
        if m:
            out.append((f"{c.rel(p)} base commit", m.group(1)))
    return out

def owner_rule(c: Corpus):
    vocab = c.pkg / "vocabulary" / "VOCABULARY.md"
    return [(f"{c.rel(vocab)} '{t}' owner", o) for t, _, o, _ in vocabulary.parse(vocab.read_text())] if vocab.exists() else []

def used_by_rules(c: Corpus):
    vocab = c.pkg / "vocabulary" / "VOCABULARY.md"
    return [(f"{c.rel(vocab)} '{t}' used by", n) for t, _, _, u in vocabulary.parse(vocab.read_text()) for n in u.split()] if vocab.exists() else []

def rule_text_rules(c: Corpus):
    return [(c.rel(c.rules[n]), m) for n in sorted(c.rules) for m in _RULE.findall(c.rule_text[n])]

def rule_text_rows(c: Corpus):
    """Core Rule text lives only under `dyad/rules/` — always package, never instance (there is no
    such thing as an instance-authored numbered Agent Rule); its `ledger #N` / `d-work #N`
    citations are this authoring instance's historical provenance, resolved `world` (#177)."""
    return [(c.rel(c.rules[n]), m) for n in sorted(c.rules) for m in _LEDGER.findall(c.rule_text[n])]

def record_pointer(c: Corpus):
    return [(f"{c.rel(c.rules[n])} Provenance", m) for n in sorted(c.rules) for m in _PROVENANCE.findall(c.rule_text[n])]

def package_paths(c: Corpus):
    """Backticked `dyad/…`, `crafts/…` and `.github/workflows/dyad-…` tokens in Rule text, cut at the first space."""
    return [(c.rel(c.rules[n]), m.split()[0]) for n in sorted(c.rules) for m in _PKG_PATH.findall(c.rule_text[n]) if m.split()]

def frame_imports(c: Corpus):
    """The frame's `@rules/` lines, plus every Rule file (so one not imported fails the reverse check)."""
    out = [(f"{c.rel(c.pkg / 'CLAUDE.md')} @rules/", l[1:]) for l in c.frame_lines if l.startswith("@rules/")]
    seen = {t for _, t in out}
    out += [(c.rel(p), f"rules/{p.name}") for n, p in sorted(c.rules.items()) if f"rules/{p.name}" not in seen]
    return out

def frame_files(c: Corpus):
    return [(f"{c.rel(c.pkg / 'CLAUDE.md')} @", l[1:]) for l in c.frame_lines if not l.startswith("@rules/")]

def preference_rules(c: Corpus):
    header, rows = c.prefs
    i = header.index("read by") if "read by" in header else None
    if i is None:
        return []
    return [(f"preferences-corpus/PREFERENCES.md '{r[0]}' read by", n) for r in rows if len(r) > i for n in _RULE.findall(r[i])]

def _column_ids(c: Corpus, table, where: str, col: str):
    header, rows = table
    i = header.index(col) if col in header else None
    if i is None:
        return []
    return [(f"{where} row {k + 1} {col}", t) for k, r in enumerate(rows) if len(r) > i for t in hash_ids(r[i])]

def changelog_ids(c: Corpus):
    return _column_ids(c, c.changelog, "workstation-corpus/CHANGELOG.md", "d-work")

def incident_ids(c: Corpus):
    return _column_ids(c, c.incidents, c.rel(c.inst / "audits" / "INCIDENTS.md"), "d-work")

def ops_paths(c: Corpus):
    """Ops-script paths named in a change-log action (`<ops dir>/<name>.sh`, ops dir per `DYAD_OPS`)."""
    header, rows = c.changelog
    i = header.index("action") if "action" in header else None
    if i is None:
        return []
    pat = re.compile(re.escape(c.rel(ops_scripts.ops_dir(c.root))) + r"/[\w.-]+\.sh")
    return [(f"workstation-corpus/CHANGELOG.md row {k + 1} action", m) for k, r in enumerate(rows) if len(r) > i for m in pat.findall(r[i])]

def ops_dwork(c: Corpus):
    return [(f"{c.rel(p)} # d-work:", t) for p, text in c.ops.items() for l in text.splitlines() if l.startswith("# d-work:") for t in hash_ids(l)]

def changelog_key(c: Corpus):
    return [(f"{c.rel(p)} # change-log:", f"#{m.group(1)} {m.group(2)}") for p, text in c.ops.items()
            for l in text.splitlines() if l.startswith("# change-log:") for m in [_CL_KEY.search(l)] if m]

def record_ledger(c: Corpus):
    """A falsification record's `ledger #N` citations, instance-authored only: flat, not under a
    `rules/` directory (vocabulary `falsification record`: "a Rule's record lives in `rules/` and
    is package, any other is instance"). A real reference, checked against this install's own row
    store — an instance's own record citing its own missing row is a real bug (#177)."""
    return [(c.rel(p), m) for p, text in c.records.items() if p.parent.name != "rules" for m in _LEDGER.findall(text)]

def record_ledger_world(c: Corpus):
    """A Rule's own falsification record — package (`dyad/falsification/rules/`) or a Tended
    craft's (`crafts/*/falsification/rules/`), under a `rules/` directory: ships with every
    install that carries it. Its `ledger #N` citations are the authoring instance's historical
    provenance, not a reference a receiving instance can or should resolve (#177; Q2, plan #142)."""
    return [(c.rel(p), m) for p, text in c.records.items() if p.parent.name == "rules" for m in _LEDGER.findall(text)]

def craft_rule_ledger(c: Corpus):
    """A Tended craft rule's own text (`crafts/*/rules/*.md`, e.g. `crafts/sysadmin/rules/host-mutation.md`
    citing `d-work #155`): package-shipped with that craft, the same historical-provenance problem
    as a core Rule's — previously unscanned by any kind (#177)."""
    return [(c.rel(p), m) for p, text in c.craft_rules.items() for m in _LEDGER.findall(text)]

def rules_components(c: Corpus):
    f = c.pkg / "guards" / "infra" / "manifest_rules.txt"
    if not f.exists():
        return []
    return [(c.rel(f), l.partition(":")[0].strip()) for l in f.read_text().splitlines() if l.strip() and not l.startswith("#") and ":" in l]

def registry_modules(c: Corpus):
    return [(f"{c.rel(c.pkg / 'scripts' / 'package.py')} PROJECTORS[{s!r}]", m) for s, m in sorted(c.registry.items())]   # m: a repo-relative `crafts/<craft>/projectors/…` path (#160)

def event_commands(c: Corpus):
    """Every event's `name`, keyed by its instance: `<instance>/<name>` names a command of that run-book."""
    d = events.events_dir(c.root)
    return [(f"{c.rel(d / f'{inst}.jsonl')} line {i} name", f"{inst}/{e.get('name', '')}")
            for inst, evs in sorted(c.events.items()) for i, e in enumerate(evs, 1)]

def changelog_events(c: Corpus):
    """`event: <id>` tokens in a change-log outcome cell (Rule-8 Conduct: the event is the row's evidence)."""
    header, rows = c.changelog
    i = header.index("outcome") if "outcome" in header else None
    if i is None:
        return []
    return [(f"workstation-corpus/CHANGELOG.md row {k + 1} outcome", m) for k, r in enumerate(rows) if len(r) > i for m in _EVENT.findall(r[i])]

# ---- resolvers: (corpus, token) -> the target exists
def row_exists(c: Corpus, t: str) -> bool:
    return t.isdigit() and int(t) in c.rows

def rule_exists(c: Corpus, t: str) -> bool:
    return t.isdigit() and int(t) in c.rules

def commit_exists(c: Corpus, t: str) -> bool:
    return c.commit_known(t)

def file_exists(c: Corpus, t: str) -> bool:
    """A Provenance pointer (`../`-relative to rules/), a frame import (relative to the package
    root) or a repo-relative path; the first that exists."""
    return any(b.joinpath(t).exists() for b in (c.pkg / "rules", c.pkg, c.root))

def path_or_glob_exists(c: Corpus, t: str) -> bool:
    """A repo-relative path in the working tree; `<…>` and `*` make it a glob needing one match;
    a token matching a `generated:` pattern (Rule-11 property 6) is accepted unseen."""
    if c._generated_match(t.rstrip("/"), c.generated):
        return True
    if "<" in t or "*" in t:
        pat = re.sub(r"<[^>]*>", "*", t)
        return any(True for _ in c.root.glob(pat))
    return (c.root / t).exists()

def changelog_row_exists(c: Corpus, t: str) -> bool:
    """`#N Hk`: at least one change-log row with d-work `#N` whose action starts `Hk` (re-runs share a key)."""
    header, rows = c.changelog
    if "d-work" not in header or "action" not in header:
        return False
    d, a = header.index("d-work"), header.index("action")
    n, hk = t.split()
    return any(len(r) > max(d, a) and r[d].strip() == n and re.match(rf"{hk}\b", r[a].strip()) for r in rows)

def command_exists(c: Corpus, t: str) -> bool:
    """`<instance>/<name>`: the run-book of that instance holds a command of that name."""
    inst, _, name = t.partition("/")
    return any(cmd.name == name for cmd in c.runbooks.get(inst, []))

def event_exists(c: Corpus, t: str) -> bool:
    return any(e.get("id") == t for evs in c.events.values() for e in evs)

# ---- the register (Rule-20 property 1): one row per reference kind, plan #142 order.
# (kind, source entity key, source field / anchor, extractor, target entity key, resolver)
# resolver: a callable (this guard resolves), "guard:<corpus>/<entity>.py" (an existing guard resolves;
# listed for the projector, never re-checked here), or "world" (unresolvable: listed; warns once as inference).
REFERENCES = [
    ("row.refs->row",             "row",        "refs",          rows_refs,         "row",        row_exists),
    ("row.refs->rule",            "row",        "refs",          rule_tokens,       "rule",       rule_exists),
    ("row.disposed->pr",          "row",        "disposed",      pr_tokens,         "pr",         "world"),
    ("plan.id->row",              "plan",       "<id>",          plan_id,           "row",        row_exists),
    ("plan.base->commit",         "plan",       "base commit",   base_commit,       "commit",     commit_exists),
    ("provenance.id->row",        "provenance", "<id>",          provenance_id,     "row",        row_exists),
    ("term.owner->rule",          "term",       "owner",         owner_rule,        "rule",       "guard:agent/vocabulary.py"),
    ("term.used_by->rule",        "term",       "used by",       used_by_rules,     "rule",       "guard:agent/vocabulary.py"),
    ("rule.text->rule",           "rule",       "text",          rule_text_rules,   "rule",       rule_exists),
    ("rule.text->row",            "rule",       "text",          rule_text_rows,    "row",        "world"),
    ("rule.provenance->record",   "rule",       "Provenance",    record_pointer,    "record",     file_exists),
    ("rule.text->path",           "rule",       "text",          package_paths,     "file",       path_or_glob_exists),
    ("frame.import->rule",        "frame",      "@rules/",       frame_imports,     "rule",       "guard:agent/frame.py"),
    ("frame.import->file",        "frame",      "@",             frame_files,       "file",       "guard:agent/frame.py"),
    ("preference.read_by->rule",  "preference", "read by",       preference_rules,  "rule",       rule_exists),
    ("changelog.dwork->row",      "changelog",  "d-work",        changelog_ids,     "row",        row_exists),
    ("changelog.action->ops",     "changelog",  "action",        ops_paths,         "ops",        file_exists),
    ("incident.dwork->row",       "incident",   "d-work",        incident_ids,      "row",        row_exists),
    ("ops.dwork->row",            "ops",        "d-work:",       ops_dwork,         "row",        row_exists),
    ("ops.changelog->changelog",  "ops",        "change-log:",   changelog_key,     "changelog",  changelog_row_exists),
    ("record.ledger->row",        "record",     "ledger #",      record_ledger,     "row",        row_exists),
    ("rules.component->component","rules",      "component",     rules_components,  "component",  "guard:infra/manifest.py"),
    ("pr.body->row",              "pr",         "body",          None,              "row",        "guard:agent/prs.py"),
    ("registry.module->file",     "registry",   "module",        registry_modules,  "file",       file_exists),
    ("cache.source->path",        "cache",      "source:",       None,              "file",       "world"),
    ("event.command->command",    "event",      "name",          event_commands,    "command",    command_exists),
    ("changelog.event->event",    "changelog",  "outcome",       changelog_events,  "event",      event_exists),
    ("record.ledger->provenance", "record",     "ledger #",      record_ledger_world, "row",      "world"),
    ("craft_rule.text->provenance","craft_rule", "text",          craft_rule_ledger, "row",        "world"),
]

# crafts/syseng/rules/invariants.md: the register's facts, over its rows and the guard registry (package data, not the instance)
def _entity_keys() -> set[str]:
    return {dyadlib.load_guard_file(py).ENTITY for py in dyadlib.guard_files()}

def _resolver_ok(r) -> bool:
    if callable(r):
        import inspect
        return len(inspect.signature(r).parameters) == 2
    if r == "world":
        return True
    return isinstance(r, str) and r.startswith("guard:") and (dyadlib.PKG / "guards" / r.removeprefix("guard:")).is_file()

def _no_craft_name_literal() -> bool:
    """No installed craft's name occurs as a quoted literal in this module: the craft set is derived
    (`installed_crafts` -> `dyadlib.craft_dirs`), never enumerated (#167). A craft named like one of
    this guard's own literals (an entity key such as `row` or `file`) trips it deliberately: the two
    share the namespace of every message printed here."""
    src = Path(__file__).read_text()
    return not any(re.search(rf"""['"]{re.escape(p.name)}['"]""", src) for p in dyadlib.craft_dirs())

INVARIANTS = [
    ("craft-set-is-craft-dirs", lambda: installed_crafts(dyadlib.PKG) == {p.name for p in dyadlib.craft_dirs(dyadlib.PKG)}),
    ("craft-names-not-literal", _no_craft_name_literal),
    ("kinds-unique", lambda: len({r[0] for r in REFERENCES}) == len(REFERENCES)),
    ("sources-are-entity-keys", lambda: {r[1] for r in REFERENCES} <= _entity_keys() | NON_GUARD_SOURCES | CRAFT_ENTITIES),
    ("targets-are-entity-keys-or-world-kinds", lambda: {r[4] for r in REFERENCES} <= _entity_keys() | WORLD_TARGETS | CRAFT_ENTITIES),
    ("craft-entities-are-not-core", lambda: CRAFT_ENTITIES.isdisjoint(dyadlib.load_guard_file(py).ENTITY for py in dyadlib.guard_files() if dyadlib.guard_key(py)[0] == "core")),
    ("resolver-shape", lambda: all(_resolver_ok(r[5]) for r in REFERENCES)),
    ("extractor-present-when-resolved-here", lambda: all(callable(r[3]) for r in REFERENCES if callable(r[5]))),
    # #177: a package/craft Rule's own ledger citations are historical provenance, not a reference
    # a receiving instance can resolve; an instance's own record citing its own missing row stays
    # a real, checked bug. Both halves of that split are register invariants, not just today's data.
    ("package-ledger-kinds-stay-world", lambda: all(r[5] == "world" for r in REFERENCES
                                                     if r[0] in {"rule.text->row", "record.ledger->provenance", "craft_rule.text->provenance"})),
    ("instance-record-ledger-stays-checked", lambda: any(r[0] == "record.ledger->row" and callable(r[5]) for r in REFERENCES)),
]

def check(root: Path, pkg: Path = dyadlib.PKG) -> tuple[int, int, list[str]]:
    """(references resolved, kinds resolved, messages). Messages start `FAIL `, `warn ` or `skip `;
    a kind with a `guard:` resolver is listed only; `world` warns once; an empty target store skips."""
    c = Corpus(root, pkg)
    n_refs, n_kinds, msgs = 0, 0, []
    for kind, _src, _field, extract, target, resolve in REFERENCES:
        if isinstance(resolve, str):
            if resolve == "world":
                n = len(extract(c)) if extract else 0
                msgs.append(f"warn {kind}: {n} reference(s) to {target}; unresolvable (The World), inference")
            continue
        if kind in GUARD_KINDS and GUARD_KINDS[kind][1] is None:
            msgs.append(f"skip {kind}: guard sysadmin/{GUARD_KINDS[kind][0]} absent (no installed craft provides it)")
            continue
        if c.store_empty(target):
            msgs.append(f"skip {kind}: {target} store is empty or absent")
            continue
        n_kinds += 1
        skipped_crafts, absent_crafts = False, {}          # one line per craft, never one per token (#167)
        for where, token in extract(c):
            if target == "file" and token.startswith("crafts/"):
                if c.crafts_absent:
                    if not skipped_crafts:
                        msgs.append(f"skip {kind}: `crafts/…` tokens; no crafts/ tree is installed (a core-only install)"); skipped_crafts = True
                    continue
                state = c.craft_state(token)
                if state and state[0] == "FAIL":           # installed-then-deleted: named per token, like any failure
                    n_refs += 1
                    msgs.append(f"FAIL {kind}: {where} -> {token} does not resolve ({state[2]})")
                    continue
                if state:
                    entry = absent_crafts.setdefault(state[1], [state[0], state[2], 0]); entry[2] += 1
                    continue
            n_refs += 1
            if not resolve(c, token):
                msgs.append(f"FAIL {kind}: {where} -> {token} does not resolve")
        for severity, reason, n in absent_crafts.values():
            msgs.append(f"{severity} {kind}: {reason}; {n} token(s) unresolved here")
    return n_refs, n_kinds, msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """The runner's entry point (S4): `FAIL` lines bare (they fail), `warn` and `skip` lines as
    `warning: ` (they do not)."""
    return [m[5:] if m.startswith("FAIL ") else f"warning: {m}" for m in check(root or dyadlib.repo_root(), pkg)[2]]

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    n, k, _ = check(root or dyadlib.repo_root(), pkg)
    return f"{n} references, {k} kinds resolve"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    ex = REFERENCES[0]
    res = lambda r: r if isinstance(r, str) else f"references.{r.__name__}"
    return {"store": "`dyad/guards/agent/references.py` (`REFERENCES`)", "parser": "`references.REFERENCES` (the register, Rule-20 property 1)", "observed": len(REFERENCES),
            "note": "one row per reference kind; the entities surface draws its relations from this list (Rule-20 property 5); `world` kinds are unresolvable, `guard:` kinds another guard's",
            "fields": [("kind", "text", "`<source>.<field>-><target>`, unique", True, ex[0], "references.FIELDS"),
                       ("source", "enum", "an entity key of this surface", True, ex[1], "references.FIELDS"),
                       ("field", "text", "the source field or store token the value sits in", True, ex[2], "references.FIELDS"),
                       ("target", "enum", "an entity key, `file`, `commit`, `pr`", True, ex[4], "references.FIELDS"),
                       ("resolver", "text", "a function of this guard | `guard:<corpus>/<entity>.py` | `world`", True, res(ex[5]), "references.FIELDS")]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    n, k, msgs = check(root)
    fails = [m for m in msgs if m.startswith("FAIL ")]
    for m in msgs:
        if m.startswith("FAIL "):
            print(f"FAIL [rule-20] {m[5:]}", file=sys.stderr)
        else:
            print(f"{m[:4]} [rule-20] {m[5:]}")
    if not fails:
        print(f"ok   [rule-20] {n} references, {k} kinds resolve")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
