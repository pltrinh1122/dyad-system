#!/usr/bin/env python3
"""Run-book guard (entity `command`, store zone `workstation`; the sysadmin craft's `server-instances.md`
owns the check, Rule-19's kernel binds existence and health, placed per Rule-11 property 1 — a Tended craft's guard,
`crafts/sysadmin/guards/`, discovered by the core runner as `sysadmin/runbooks`, #155).
Kernel: Python 3.12+, stdlib. The parser of a run-book lives in the core runner (`dyad/scripts/runbook.py`,
so `dyad runbook` works with no craft installed; #155 amendment); this guard imports it and re-exports
its names so `runbooks.parse`, `runbooks.FIELDS` … keep reading as before.

A run-book (`<runbooks>/<instance>.md`; `DYAD_RUNBOOKS`, default `<host>/runbooks` — `<host>` the host path,
preference `host-path`, default `workstation-corpus`, #175 — relative to the git root; instance, the host zone) holds its commands as fenced blocks tagged `dyad-cmd`:
a header of `key: value` lines (FIELDS: name, class, role, undo, postcondition, scope), a blank line,
then the command. Prose stays around the blocks; a bare shell block (```bash, ```sh, ```shell,
```console or untagged) is refused so every command is data the runner executes.

check_package(root): every run-book (the instance's, and the core craft's under `dyad/runbooks/`, #165) parses;
every section of its set — the craft rule's (SECTIONS) unless the file's header declares `# sections: A, B, C`
(`runbook.declared_sections`; a core run-book's sections are its own) — holds at least one command; every
command carries every field, a Rule-8 class (dyadlib.HOST_CLASSES), a role (ROLES),
a unique name; a command whose text names `sudo` or a credential word (CREDENTIAL_WORDS) is role
`operator`; a state-changing command names an undo (reversible) and a postcondition (reversible,
destructive); a run-book that cites no `crafts/*/server*/` or `workstation-corpus/server*/` directory warns.
  runbooks.py [repo-root]           check every run-book (the CLI of `dyad runbook check`)
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("runbooks.py: Python 3.12+ required")
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))  # the core craft's library
import dyadlib
import runbook as _rb                                                   # the core runner: parser and constants

ENTITY, CORPUS, TRANSACTION = "command", "workstation", False
NAME, OWNER = "run-book command", "Rule-19"
# re-exports (the runner owns the parser; this guard owns the check)
FENCE, FIELDS, CLASSES, ROLES, CREDENTIAL_WORDS, NONE, PROSE_FENCES, DEFAULT_RUNBOOKS = (
    _rb.FENCE, _rb.FIELDS, _rb.CLASSES, _rb.ROLES, _rb.CREDENTIAL_WORDS, _rb.NONE, _rb.PROSE_FENCES, _rb.DEFAULT_RUNBOOKS)
CORE_RUNBOOKS = _rb.CORE_RUNBOOKS                                       # the core craft's run-books, checked too (#165)
Command, parse_text, parse, prose_blocks, sections, in_section, needs_operator, counts, declared_sections = (
    _rb.Command, _rb.parse_text, _rb.parse, _rb.prose_blocks, _rb.sections, _rb.in_section, _rb.needs_operator, _rb.counts, _rb.declared_sections)
runbooks_rel, runbooks_dir, runbook_path, runbooks, core_runbooks, all_runbooks = (
    _rb.runbooks_rel, _rb.runbooks_dir, _rb.runbook_path, _rb.runbooks, _rb.core_runbooks, _rb.all_runbooks)
SECTIONS = ("Status/health", "Start", "Stop", "Restart", "Logs", "Backup", "Restore", "Upgrade", "Credential rotation", "Data")
SERVER_GLOBS = ("crafts/*/server*", "<host>/server*")                    # a run-book cites one of these directories (warning otherwise); `<host>` is the host path (#175)
_NAME = re.compile(r"^[a-z][a-z0-9-]*$")
INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("fields-cover-parser-keys", lambda: {"class" if f.name == "cls" else f.name for f in __import__("dataclasses").fields(Command)} >= set(FIELDS)),
    ("classes-are-host-classes", lambda: CLASSES is dyadlib.HOST_CLASSES),
    ("sections-distinct", lambda: len(set(SECTIONS)) == len(SECTIONS) and "Status/health" in SECTIONS),
]

# ---- check
def server_globs(root: Path) -> list[str]:
    """SERVER_GLOBS with `<host>` resolved to the host path of the repo at `root` (dyadlib.host_path, #175)."""
    host = dyadlib.host_path(root)
    return [g.replace("<host>", host) for g in SERVER_GLOBS]

def server_dirs(root: Path) -> list[Path]:
    return sorted(p for g in server_globs(root) for p in root.glob(g) if p.is_dir())

def check_runbook(path: Path, root: Path | None = None) -> list[str]:
    """Failures (and `warning: ` lines) for one run-book, each prefixed by its file name."""
    text = path.read_text()
    name, msgs, cmds = path.name, [], parse_text(text)
    for line, tag in prose_blocks(text):
        msgs.append(f"{name}:{line}: {tag} block is prose; a run-book command is a ```{FENCE} block")
    heads = sections(text)
    declared = declared_sections(text)                       # `# sections:` header: the run-book's own set (a core run-book's, #165)
    for s in declared if declared is not None else SECTIONS:
        if not any(in_section(h, s) for h in heads):
            msgs.append(f"{name}: section `{s}` missing ({'declared in its header' if declared is not None else 'server-instances rule, sysadmin craft'})")
        elif not any(in_section(c.section, s) for c in cmds):
            msgs.append(f"{name}: section `{s}` holds no {FENCE} command")
    seen = set()
    for c in cmds:
        where = f"{name}:{c.line}"
        label = c.name or "(unnamed)"
        for f in FIELDS:
            if not getattr(c, "cls" if f == "class" else f):
                msgs.append(f"{where}: command {label} lacks `{f}:`")
        if not c.cmd:
            msgs.append(f"{where}: command {label} has no command line (blank line, then the command)")
        if c.name and not _NAME.match(c.name):
            msgs.append(f"{where}: name `{c.name}` is not [a-z][a-z0-9-]*")
        if c.name in seen:
            msgs.append(f"{where}: name `{c.name}` defined twice")
        seen.add(c.name)
        if c.cls and c.cls not in CLASSES:
            msgs.append(f"{where}: command {label} class `{c.cls}` is not one of {', '.join(CLASSES)} (Rule-8)")
        if c.role and c.role not in ROLES:
            msgs.append(f"{where}: command {label} role `{c.role}` is not one of {', '.join(ROLES)}")
        w = needs_operator(c.cmd)
        if w and c.role != "operator":
            msgs.append(f"{where}: command {label} names `{w}` but role is `{c.role or ''}`; must be `operator` (Rule-8, Operator-run)")
        if c.cls == "reversible" and c.undo in ("", NONE):
            msgs.append(f"{where}: reversible command {label} names no undo")
        if c.cls in ("reversible", "destructive") and c.postcondition in ("", NONE):
            msgs.append(f"{where}: {c.cls} command {label} names no postcondition")
    if root is not None and declared is None:            # a run-book with its own section set is not a server's
        if not any(f"{p.relative_to(root)}/" in text for p in server_dirs(root)):
            msgs.append(f"warning: {name}: cites no {' or '.join(g + '/' for g in server_globs(root))} directory (no server counterpart)")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    """Every run-book under the runbooks dir of `root`; a missing directory passes (fresh install)."""
    root = root or dyadlib.repo_root()
    msgs = []
    for _, p in sorted(all_runbooks(root).items()):      # the instance's and the core craft's (dyad/runbooks/, #165)
        msgs += check_runbook(p, root)
    return msgs

def summary(root: Path | None = None) -> str:
    b, c = counts(root)
    return f"{b} run-books, {c} commands"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    books = runbooks(root)
    cmds = [(inst, c) for inst, p in sorted(books.items()) for c in parse(p)]
    ex = cmds[0][1] if cmds else None
    d = runbooks_dir(root); rel = d.relative_to(root) if d.is_relative_to(root) else d
    allowed = {"name": "unique per run-book, [a-z][a-z0-9-]*", "class": " | ".join(CLASSES) + " (Rule-8)", "role": " | ".join(ROLES),
               "undo": f"a command, or `{NONE}` (never for reversible)", "postcondition": f"a shell test, or `{NONE}` (never for reversible or destructive)",
               "scope": "the containers, paths and services it may touch"}
    return {"store": f"{rel}/<instance>.md (```{FENCE} blocks)", "parser": "`runbook.parse` (core runner; re-exported as `runbooks.parse`)", "observed": len(cmds),
            "note": f"header, blank line, then the native command line (`cmd`); sections: {', '.join(SECTIONS)}; "
                    f"a command naming {', '.join(CREDENTIAL_WORDS)} is role operator; run by `dyad runbook run`",
            "fields": [(f, "enum" if f in ("class", "role") else "line", allowed.get(f, ""), True,
                        (getattr(ex, "cls" if f == "class" else f) if ex else ""), "runbook.FIELDS") for f in FIELDS]}

def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    fails = [m for m in msgs if not m.startswith("warning: ")]
    for m in msgs:
        if m.startswith("warning: "):
            print(f"warn [rule-19] {m[9:]}")
        else:
            print(f"FAIL [rule-19] {m}", file=sys.stderr)
    if not fails:
        n, k = counts(root)
        print(f"ok   [rule-19] {n} run-book(s), {k} commands")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
