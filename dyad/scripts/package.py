#!/usr/bin/env python3
"""dyad package tool (Rule-11; runner per S4). Kernel: Python 3.12+.
Entrypoint: dyad/bin/dyad (`dyad <noun> <verb>`, preference cli-pattern, ledger #152); `dyad` below
means `dyad/bin/dyad` from the git root (or python3.12 dyad/scripts/package.py).

  dyad check              the invariant pass (every model module's INVARIANTS, crafts/syseng/rules/invariants.md:
                                `ok   [invariant] <module> (<n>)` or `FAIL [invariant] <module>: <name>`; a
                                FAIL is red but the checks still run), then Rule-11's own check, Rule-12's
                                tests (the core suite, then every crafts/<craft>/tests/ present), then every
                                guard's package check — the guard registry is discovered from
                                dyad/guards/<corpus>/<entity>.py and, for every Tended craft,
                                crafts/<craft>/guards/<entity>.py (crafts/sysarch/rules/guards.md, two roots; #155),
                                never hand-listed
  dyad check --list       print the guard registry: corpus (or craft), entity, module, transaction, root
  dyad check --guards     the guards on the kernel (I2): the invariant pass, every guard's package check, then
                                the transaction guards (TRANSACTION = True: infra/containment,
                                agent/rows, agent/prs, sysadmin/events) over <base>..HEAD, each in its
                                declared transaction mode (a push range: containment checks commits, #166)
  dyad check --pr <base> [<head>]
                                the PR transaction (Rule-1 binds a commit and a PR; a push range is
                                neither): the invariant pass, then every transaction guard's `check_pr`
                                when it declares one — containment's whole-diff `range` mode — else its
                                `check_transaction`. Run before opening a PR; since #168 no hosted job
                                checks a PR's whole diff before it merges
  dyad check --tests [<target>]
                          Rule-12's suites the way the runner runs them (d-work #155): every test root,
                                or one root by path, or one dotted module/class/method — always with
                                DYAD_NO_NESTED_TESTS set, which is what makes it ~39 s and not ~120 s
  dyad check --evidence   the evidence block (Rule-14 property 3): head=, tree=, dirty=,
                                every line `check` and `check --guards` print, then
                                evidence-sha256= of those lines; non-zero if any check fails
  dyad build [out.tar.gz] deterministic archive of the core craft (scripts/distribute.py, the one
                                distribution code path every craft uses; #156)
  dyad install <repo>     idempotent install of the core craft into another repo (same code path)
  dyad bundle check | build [dir]
                                Rule-11 p7 (guards/infra/bundle.py): check BUNDLE.md against the tree's
                                craft VERSIONs (both directions; a missing BUNDLE.md skips), or build every
                                component it names — dyad build / craft.py export per row, one code path,
                                no new mechanism — into [dir] (default .), plus a generated BUNDLE.sha256
  dyad craft new <name> | list | check [<craft>] | export <craft> [out.tar.gz] | install <src> [--force] [--dwork N]
                                Tended crafts (scripts/craft.py, Rule-11 p5): scaffold one (#165), list every crafts/<craft>/
                                with its version and origin, check one or all (guards/craft/crafts.py),
                                export one as <craft>-<version>.tar.gz, install one from an archive or
                                a tree (writes crafts/<craft>/ and its crafts/REGISTRY.md row only)
  dyad ledger             render <instance>/d-work/LEDGER.md from rows/ (Rule-16)
  dyad dwork new <title> [refs] [--backlog] [-d text]
                                allocate the next id, write its row file (state open, or
                                backlog with --backlog; -d records the creating disposition)
  dyad dwork state <id> <state> [-d text] [-r refs]  change state / append disposition
  dyad dwork list [--state <s>] [--craft <c>]
                                rows from the row store (Rule-16), one `#<id> [<state>] <title>`
                                line each, sorted by id; `--craft <c>` keeps only rows whose `refs`
                                carries the bare token `<c>` (row.refs->craft, Rule-20; d-work #22)
                                — a routing tag, not a re-check of the guard's own resolution
  dyad session touch [-r <row>]... [-f <file>]... | list
                                Rule-16 presence (guards/agent/sessions.py): touch refreshes this
                                session's file (DYAD_SESSION env, else a fresh id); no args, the
                                files from this session's own open/planned rows' stored plans;
                                list prints every session's file, flagging one past the stale window
  dyad project <surface> | --list   run a projector discovered under crafts/*/projectors/ (crafts/sysarch/rules/projection.md)
                                / print the registry as `<surface> <craft> <module>`; no craft: one line, exit 2
  dyad runbook check | list <instance> | run <instance> <name> [--as operator|agent] | new <instance>
                                Rule-19 run-books (scripts/runbook.py, the core runner; the check is the
                                sysadmin craft's guard, crafts/sysadmin/guards/runbooks.py): check every
                                run-book (exit 2 when no craft provides the check), list one's commands,
                                execute one command through the one runner — it prints the native
                                command line, tests the postcondition and appends an event to
                                <runbooks>/events/<instance>.jsonl — or seed a run-book from the craft's template
"""
import sys
if sys.version_info < (3, 12):
    sys.exit(f"package.py: Python 3.12+ required (kernel pin), found {sys.version.split()[0]}")
import os, re, subprocess, functools, fnmatch, hashlib
print = functools.partial(print, flush=True)  # CI pipes are block-buffered; a stuck check must be visible
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent          # dyad/
sys.path.insert(0, str(PKG / "scripts")); import dyadlib, distribute, hostadapter
REPO = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=PKG, text=True,
            env={k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}).strip())  # hooks export GIT_DIR (#142)
INSTANCE = os.environ.get("DYAD_INSTANCE", "agent-corpus")
WORKFLOW_PREFIX = "dyad-"
IMPORT_LINE = "@dyad/CLAUDE.md"
def rules():
    """Rule-11 check data: package_rules.txt plus this instance's package_rules.local.txt (dyadlib.package_rules, #192)."""
    return dyadlib.package_rules(PKG, REPO)
TEMPLATES = {"VERSION": f"{INSTANCE}/d-work/VERSION", "rows-README.md": f"{INSTANCE}/d-work/rows/README.md", "INCIDENTS.md": f"{INSTANCE}/audits/INCIDENTS.md",
             "PREFERENCES.md": "preferences-corpus/PREFERENCES.md"}   # the core craft's own hooks (Rule-11 p2, host-side hooks are the core craft's only). The
                                                                       # change log's seed (crafts/sysadmin/templates/CHANGELOG.md) is a Tended craft's — never
                                                                       # here; `dyad craft check`/`install` warn if it is absent, MANIFEST.md `seeds:` (#180)

CORE_ROOTS = ["dyad"]                                  # the core craft's tree (Rule-11 p1)
CORE_HOOKS = distribute.Hooks(templates=TEMPLATES, import_line=IMPORT_LINE, gitignore=True)   # its host-side hooks (p2); gitignore: d-work #179, G9

def bundled_crafts(pkg=None):
    """Every **bundled craft** (Rule-11 property 2, vocabulary): a Tended craft the core release
    carries. A craft declares itself by setting `BUNDLED_WITH_CORE = True` in any one of its own
    guard modules — the craft-shipped contribution shape property 2 already blesses for
    `REFERENCES_CONTRIB` (#101), discovered through `dyadlib.guard_files()`'s craft half. The core
    keeps no list, so a craft removed from the tree takes its own claim with it and nothing here
    needs editing. Returns craft names, sorted."""
    pkg = pkg or dyadlib.PKG
    out = set()
    for py in dyadlib.guard_files(pkg):
        corpus, craft = dyadlib.guard_key(py, pkg)[:2]
        if corpus != "craft" or craft in out:
            continue
        if getattr(dyadlib.load_guard_file(py, pkg), "BUNDLED_WITH_CORE", False):
            out.add(craft)
    return sorted(out)


def release_roots(pkg=None):
    """The roots the core *release* carries: `CORE_ROOTS` plus every bundled craft's tree. Used by
    `build` and `install` only — never by `check`, whose craft/instance scan (property 1) still
    judges the core craft alone, and never by the craft guard, which judges each Tended craft on
    its own. Bundling changes what ships, not what anything is."""
    return CORE_ROOTS + [f"crafts/{c}" for c in bundled_crafts(pkg)]


def core_extra():
    """The `dyad-*` workflow files: the core craft's host-side hooks that ship in its archive (p2)."""
    out = subprocess.check_output(["git", "ls-files", ".github/workflows"], cwd=REPO, text=True).split()
    return [p for p in out if Path(p).name.startswith(WORKFLOW_PREFIX)]

def package_files():
    return distribute.files(REPO, CORE_ROOTS, core_extra())

def tracked_files(repo=None):
    """Every tracked path in the repo (property 6 scans the repository, not only the package)."""
    return subprocess.check_output(["git", "ls-files"], cwd=repo or REPO, text=True).split()

def generated_matches(rel, patterns):
    """The first generated pattern that matches `rel`: the whole path, any single path component,
    or any suffix starting at a component (so `__pycache__/*` matches a nested dir); else None."""
    parts = rel.split("/")
    candidates = [rel] + parts + ["/".join(parts[i:]) for i in range(1, len(parts))]
    for g in patterns:
        if any(fnmatch.fnmatch(c, g) for c in candidates):
            return g
    return None

# ---- checks: each Architecture Rule owns its function; this file only runs them (S4)
def version():
    return (PKG / "VERSION").read_text().strip()

# crafts/syseng/rules/invariants.md: the runner's own facts (over its constants and the package files they name).
INVARIANTS = [
    ("projector-modules-exist-with-main", lambda: all((REPO / rel).is_file() and hasattr(dyadlib.load_module(REPO / rel, f"project_{s.replace('/', '_')}"), "main") for s, rel in PROJECTORS.items())),
    ("templates-exist", lambda: all((PKG / "templates" / t).is_file() for t in TEMPLATES)),
    ("contract-names-distinct", lambda: len(set(CONTRACT)) == len(CONTRACT)),
]

def check_rule_11():
    fails = []
    if not dyadlib.SEMVER.fullmatch(version()):   # one grammar, shared with a Tended craft's own VERSION check (D2, #100)
        fails.append(f"VERSION '{version()}' is not MAJOR.MINOR.PATCH")
    r = rules()
    # the same scan the craft guard runs over crafts/<craft>/ (distribute.instance_state; templates/ exempt, #156)
    fails += distribute.instance_state(REPO, CORE_ROOTS, r, extra=core_extra(), what="the package")
    for t in TEMPLATES:
        if not (PKG / "templates" / t).exists():
            fails.append(f"templates/{t} missing")
    fails += check_generated(REPO, r["generated"])
    return fails

def check_generated(repo, patterns):
    """Property 6: no tracked path in `repo` matches a generated pattern (whole path or any component)."""
    fails = []
    for rel in tracked_files(repo):
        g = generated_matches(rel, patterns)
        if g:
            fails.append(f"{rel}: generated file tracked (pattern '{g}', property 6)")
    return fails

def test_suites():
    """The test roots `unittest discover` runs: the core `dyad/tests/`, then every `crafts/<craft>/tests/` present."""
    return [PKG / "tests"] + dyadlib.craft_glob("tests", PKG)

_SUITE_RAN = False   # d-work #155: the suite runs at most once per process — `cmd_evidence` calls
                     # both `cmd_check` and `cmd_guards`, and without this the evidence block paid
                     # for the whole suite twice (caught by the pre-merge evidence run, #155)

def check_rule_12():
    """Rule-12's kernel: the tests pass — `unittest discover` once per test root (the core's, then every Tended
    craft's; guards/ subdirectories are packages). Which module maps to which test file is the syseng craft's
    guard (`crafts/syseng/guards/tests.py`, `syseng/tests`; #162) — the runner runs, the craft maps."""
    global _SUITE_RAN
    msgs = []
    if os.environ.get("DYAD_NO_NESTED_TESTS"):
        return msgs  # already inside a test run (test_package.py calls `check`); do not recurse
    _SUITE_RAN = True
    for suite in test_suites():
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(suite), "-q"],
                           capture_output=True, text=True, timeout=600,
                           env=suite_env())
        summary = [re.sub(r" in [\d.]+s$", "", l) for l in r.stderr.strip().splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]  # no timing: the evidence block must be deterministic (#138)
        print(f"     [Rule-12] {suite.relative_to(REPO)}: " + " ".join(summary))  # `Ran N tests … OK (skipped=k)`: skips are visible in CI
        if r.returncode != 0:
            msgs.append(f"tests failed ({suite.relative_to(REPO)}):\n" + r.stderr.strip().splitlines()[-1])
    return msgs

def ledger_only_range(base, head):
    """True when every path `base..head` touches lives under `<instance>/d-work/` — a range that
    cannot change a suite's outcome. The prefix, never the file suffix: a `.py` filter would have
    let #137's markdown run-book through, which broke the core suite by falsifying a pinned count
    (d-work #155, plan's revision table). Unknown range → False, so the suite runs."""
    inst = os.environ.get("DYAD_INSTANCE", "agent-corpus")
    try:
        out = subprocess.check_output(["git", "diff", "--name-only", f"{base}..{head}"], cwd=REPO, text=True)
    except subprocess.CalledProcessError:
        return False
    paths = out.split()
    return bool(paths) and all(p.startswith(f"{inst}/d-work/") for p in paths)

def suite_env() -> dict[str, str]:
    """The environment a test child runs in: `DYAD_NO_NESTED_TESTS` set and every `GIT_VARS` dropped.
    A git hook exports an absolute `GIT_DIR` when it runs in a linked worktree; a suite that inherits
    it points every scratch-repo git call at the real repository (#152: `core.bare`, a `feature`
    branch and a tag written into the live repo by the pre-push hook's run)."""
    return {**dyadlib.git_env(), "DYAD_NO_NESTED_TESTS": "1"}

def run_suite(suite, target=None):
    """One `unittest` child, the way `check_rule_12` spawns it — always with `DYAD_NO_NESTED_TESTS`,
    which is what makes it cost 39 s instead of 120 s (the nested scratch installs do not re-run
    their own suites). Returns (rc, summary lines)."""
    argv = ["-m", "unittest", target, "-q"] if target else ["-m", "unittest", "discover", "-s", str(suite), "-q"]
    r = subprocess.run([sys.executable, *argv], capture_output=True, text=True, timeout=600, cwd=REPO,
                       env=suite_env())
    summary = [re.sub(r" in [\d.]+s$", "", l) for l in r.stderr.strip().splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    return r.returncode, summary, r.stderr

def cmd_tests(target=None):
    """Rule-13 property 1: the suites, run the way the runner runs them, as one verb. Without a
    target every root of `test_suites()`; with a directory that root; with anything else a dotted
    module, class or method handed to `unittest`. The point is the environment, not the typing:
    a hand-run without `DYAD_NO_NESTED_TESTS` pays about three times (d-work #154's audit)."""
    global _SUITE_RAN
    rc = 0
    if os.environ.get("DYAD_NO_NESTED_TESTS"):
        return rc       # already inside a test run (a suite invoking `check`); do not recurse
    _SUITE_RAN = True
    if target and not Path(target).is_dir():
        code, summary, err = run_suite(None, target)
        print(f"     [Rule-12] {target}: " + " ".join(summary))
        if code:
            print(err.strip().splitlines()[-1], file=sys.stderr); rc = 1
        return rc
    for suite in ([Path(target)] if target else test_suites()):
        code, summary, err = run_suite(suite)
        print(f"     [Rule-12] {suite.relative_to(REPO) if suite.is_absolute() else suite}: " + " ".join(summary))
        if code:
            print(err.strip().splitlines()[-1], file=sys.stderr); rc = 1
    return rc

# ---- the guard registry (crafts/sysarch/rules/guards.md p4): discovered from dyad/guards/<corpus>/<entity>.py (core) and
# crafts/<craft>/guards/<entity>.py (every Tended craft, #155), never hand-listed. Each module declares
# ENTITY, CORPUS, FIELDS, TRANSACTION, check_package(root) and, when TRANSACTION, check_transaction(root, base, head);
# the runner owns none of their semantics (S4). A core guard's CORPUS equals its directory; a craft
# guard's CORPUS is a zone name (containment.ZONES), the zone of the entity's store.
GUARD_FIELDS = ("corpus", "entity", "module", "transaction", "root")
CONTRACT = dyadlib.CONTRACT   # one definition, shared with the craft guard (dyadlib.contract_problem, #156)

def zone_names():
    try:
        return {z for z, _ in dyadlib.load_guard("infra", "containment", PKG).ZONES}
    except Exception:
        return set()

def registry():
    """[(group, entity, module path relative to the repo, transaction, module or None, problem)] in
    registry order (core root sorted, then each craft root sorted); `group` is the corpus of a core
    guard or the craft name of a craft guard, so the label `<group>/<entity>` is unique. A module that
    fails to load or lacks the contract carries the problem text and no module."""
    out, zones = [], None
    for py in dyadlib.guard_files(PKG):
        root, group, entity = dyadlib.guard_key(py, PKG)
        rel = str(py.relative_to(REPO))
        try:
            mod = dyadlib.load_guard_file(py, PKG)
        except Exception as e:  # a guard that does not import is a failing guard, not a missing one
            out.append((group, entity, rel, False, None, f"does not load: {e}")); continue
        if root == "craft":
            zones = zone_names() if zones is None else zones
        problem = dyadlib.contract_problem(mod, root, group, zones)
        if problem:
            out.append((group, entity, rel, bool(getattr(mod, "TRANSACTION", False)), None, problem)); continue
        out.append((group, entity, rel, bool(mod.TRANSACTION), mod, ""))
    return out

def guard_root(rel: str) -> str:
    return "craft" if rel.startswith("crafts/") else "core"

def guard_check(entry):
    """The package-check callable of one registry entry (a failing one for a broken entry)."""
    corpus, entity, rel, _, mod, problem = entry
    if mod is None:
        return lambda: [f"{rel}: {problem}"]
    return lambda: mod.check_package(REPO)

CHECKS = {"Rule-11": check_rule_11, "Rule-12": check_rule_12}
CHECKS.update({f"{c}/{e}": guard_check(entry) for entry in registry() for c, e in [entry[:2]]})

# ---- the invariant pass (crafts/syseng/rules/invariants.md p1, p4): before any check, over every model module
def invariant_modules():
    """[(label, module, extra invariants)] in pass order: dyadlib, this runner, every guard in registry order
    (each with the four contract invariants appended, dyadlib.contract_invariants), every projector in
    PROJECTORS order, then the run-book runner, the craft CLI and the distribution path. A guard that does not
    load is the registry's failure, not the pass's."""
    out = [("dyadlib", dyadlib, ()), ("package", sys.modules[__name__], ())]
    zones = None
    for group, entity, rel, tx, mod, problem in registry():
        if mod is None:
            continue
        root = guard_root(rel)
        if root == "craft" and zones is None:
            zones = zone_names()
        out.append((f"{group}/{entity}", mod, dyadlib.contract_invariants(mod, root, group, zones)))
    for s, rel in sorted(PROJECTORS.items()):
        label = f"project_{s.replace('/', '_')}"   # `/`-free: distinct from a guard label's own `corpus/entity` shape below
        out.append((label, dyadlib.load_module(REPO / rel, label), ()))
    for name in ("runbook", "craft", "distribute"):
        out.append((name, dyadlib.load_module(PKG / "scripts" / f"{name}.py", name), ()))
    return out

def cmd_invariants():
    """Print one line per module; rc 1 when any invariant is false. Never run at import, never by --list/--help."""
    rc = 0
    for label, mod, extra in invariant_modules():
        try:
            n = dyadlib.check_invariants(mod, extra, label)
            print(f"ok   [invariant] {label} ({n})")
        except dyadlib.InvariantError as e:
            for name in e.failed:
                print(f"FAIL [invariant] {label}: {name}")
            rc = 1
    return rc

def cmd_list():
    print(f"{'corpus':<12} {'entity':<12} {'module':<44} {'transaction':<12} root")
    for corpus, entity, rel, tx, mod, problem in registry():
        print(f"{corpus:<12} {entity:<12} {rel:<44} {'yes' if tx else 'no':<12} {guard_root(rel)}{'  FAIL ' + problem if problem else ''}")
    return int(any(e[5] for e in registry()))

def cmd_guards(base="origin/main"):
    """I2: run every guard locally, the way a push would be judged — each guard's package check,
    then every TRANSACTION guard over base..HEAD. Returns rc."""
    rc = cmd_invariants()
    entries = registry()
    for corpus, entity, rel, tx, mod, problem in entries:
        label = f"{corpus}/{entity}"
        if mod is None:
            print(f"FAIL [guards] {label}: {problem}"); rc = 1; continue
        msgs = mod.check_package(REPO)
        fails = [m for m in msgs if not m.startswith("warning:")]
        for m in msgs:
            if m.startswith("warning:"): print(f"warn [guards] {label} {m.removeprefix('warning:').strip()}")
        if fails:
            for m in fails: print(f"FAIL [guards] {label} {m}")
            rc = 1
        else:
            extra = f" ({mod.summary(REPO)})" if hasattr(mod, "summary") else ""
            print(f"ok   [guards] {label}{extra}")
    try:
        subprocess.check_output(["git", "rev-parse", "--verify", "-q", base], cwd=REPO)
        base_ok = True
    except subprocess.CalledProcessError:
        # d-work #158: the transaction guards need the base ref; the suite below does not, and used
        # to be unreachable here — so a fresh install, a system with no remote, or one whose default
        # branch is not `main` never ran Rule-12's suite at push at all.
        print(f"skip [guards] transaction guards: no {base}"); base_ok = False
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    for corpus, entity, rel, tx, mod, problem in (entries if base_ok else ()):
        if not tx or mod is None:
            continue
        fails = mod.check_transaction(REPO, base, head)
        label, mode = f"{corpus}/{entity}", getattr(mod, "TRANSACTION_MODE", "")   # the guard names its mode (#166); most declare none
        if fails:
            for m in fails: print(f"FAIL [guards] {label} {m.removeprefix('FAIL ')}")
            rc = 1
        else:
            print(f"ok   [guards] {label} transaction{f' [{mode}]' if mode else ''} ({base}..HEAD)")
    # Rule-12's suite, gated (d-work #155): the local gate tested nothing before this, so the Agent
    # ran it by hand 134 times in one session (#154's audit). A ledger-only range cannot change a
    # suite's outcome, so it skips and the push stays at the guards' own ~1.7 s; anything else pays
    # the suite here rather than by hand at three times the price. The guards above are never gated.
    if os.environ.get("DYAD_NO_NESTED_TESTS") or _SUITE_RAN:
        pass            # inside a test run, or `cmd_check` already ran it in this process
    elif base_ok and ledger_only_range(base, head):
        print(f"skip [guards] Rule-12 suite: {base}..HEAD is ledger-only (d-work #155)")
    elif cmd_tests():
        rc = 1
    return int(rc)

def cmd_pr(base=None, head="HEAD"):
    """Rule-1's PR transaction (#166): every transaction guard over `base..head` as a *PR* — its
    `check_pr` when it declares one (infra/containment's whole-diff `range` mode), else the
    `check_transaction` the push path runs. The Agent runs it before opening a PR: since #168
    removed the `pull_request` trigger, no hosted job judges a PR's whole diff before it merges,
    so one zone per PR is conduct plus this command, never a gate. The runner owns no semantics (S4)."""
    if not base:
        print("usage: dyad check --pr <base> [<head>]", file=sys.stderr); return 2
    shas = {}
    for name, ref in (("base", base), ("head", head)):
        try:
            shas[name] = subprocess.check_output(["git", "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"],
                                                 cwd=REPO, text=True, stderr=subprocess.DEVNULL).strip()
        except subprocess.CalledProcessError:
            print(f"refused: {name} {ref!r} does not resolve to a commit", file=sys.stderr); return 2
    rc = cmd_invariants()
    span = f"{shas['base'][:7]}..{shas['head'][:7]}"
    for corpus, entity, rel, tx, mod, problem in registry():
        label = f"{corpus}/{entity}"
        if not tx:
            continue
        if mod is None:
            print(f"FAIL [pr] {label}: {problem}"); rc = 1; continue
        pr = getattr(mod, "check_pr", None)
        mode = getattr(mod, "PR_MODE", "pr") if pr else getattr(mod, "TRANSACTION_MODE", "transaction")
        fails = (pr or mod.check_transaction)(REPO, shas["base"], shas["head"])
        if fails:
            for m in fails: print(f"FAIL [pr] {label} {m.removeprefix('FAIL ')}")
            rc = 1
        else:
            print(f"ok   [pr] {label} {mode} ({span})")
    return int(rc)

def evidence_sha256(lines):
    """Pure: the sha256 of an evidence block's lines, joined by newline (Rule-14 property 3)."""
    import hashlib
    return hashlib.sha256(chr(10).join(lines).encode()).hexdigest()

def cmd_evidence():
    """Rule-14 property 3: the evidence block. Runs `check` and `check --guards` on the exact
    head, prints head/tree/dirty, every line they print, and a sha256 of all preceding lines
    (joined by newline) so the Operator can re-run it on the same head and compare."""
    import io, contextlib
    git = lambda *a: subprocess.check_output(["git", *a], cwd=REPO, text=True).strip()
    lines = [f"head={git('rev-parse', 'HEAD')}", f"tree={git('rev-parse', 'HEAD^{tree}')}",
             f"dirty={'yes' if git('status', '--porcelain') else 'no'}"]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cmd_check() | cmd_guards()
    lines += buf.getvalue().splitlines()
    for l in lines:
        print(l)
    print(f"evidence-sha256={evidence_sha256(lines)}")
    return int(rc)

def cmd_check():
    rc = cmd_invariants()
    for name, fn in CHECKS.items():
        msgs = fn()
        msgs = [m.removeprefix("FAIL ") for m in msgs]
        hard = [m for m in msgs if not m.startswith("warning:")]
        for m in msgs:
            print(f"FAIL [{name}] {m}" if not m.startswith("warning:") else f"warn [{name}] {m.removeprefix('warning:').strip()}")
        if hard:
            rc = 1
        elif not msgs:
            print(f"ok   [{name}]")
    print(f"package: {len(package_files())} files")
    return rc

def cmd_build(out=None):
    """The core craft's export: the one code path (distribute.build; deterministic, p5)."""
    roots = release_roots()
    out = distribute.build(REPO, roots, out or f"dyad-{version()}.tar.gz", extra=core_extra())
    bundled = bundled_crafts()
    print(f"built {out} (version {version()})" + (f"; bundled: {', '.join(bundled)}" if bundled else ""))
    return 0

def cmd_install(target):
    """The core craft's install: the same code path, with the core's hooks (templates, import line; p2).
    `prune=True` (#178): the core is one tree (CORE_ROOTS), so a file the new version dropped (a
    retired Rule, a relocated script) must not survive an upgrade — an unpruned stale file can
    resurrect a retired Rule for the frame guard and reintroduce a superseded test module (#178
    empirical finding: 23 stale files, `agent/frame` FAIL plus 28 test failures, replaying the
    pre-#160 -> current upgrade unpruned). Destination path resolution goes through the host
    adapter (#179), not a bare `.resolve()` call at the site."""
    target = hostadapter.resolve(target)
    bundled = bundled_crafts()
    changed = distribute.install(REPO, target, release_roots(), prune=True, hooks=CORE_HOOKS, extra=core_extra())
    print(f"installed into {target}: {changed} changes" + (f"; bundled: {', '.join(bundled)}" if bundled else "")
          + f"; run: git -C {target} config core.hooksPath dyad/hooks")
    return 0

def cmd_craft(a):
    """Rule-11 p5: the Tended-craft CLI lives in scripts/craft.py; this is dispatch only (S4)."""
    return dyadlib.load_module(PKG / "scripts" / "craft.py", "craft").main(a)

def cmd_bundle(a):
    """Rule-11 p7: `check` runs the bundle guard by hand; `build [dir]` sequences the one
    distribution code path once per BUNDLE.md row (`cmd_build` for the core, `craft.cmd_export`
    for a Tended craft — no second build mechanism, S4) and writes `BUNDLE.sha256` beside the
    archives, a generated file (package_rules.txt), never tracked."""
    if not a or a[0] not in ("check", "build"):
        print(__doc__, file=sys.stderr); return 2
    bundle = dyadlib.load_guard("infra", "bundle")
    if a[0] == "check":
        version, rows, msgs = bundle.check_bundle(REPO)
        for m in msgs:
            print(f"FAIL [bundle] {m}", file=sys.stderr)
        if not rows and not version:
            print("skip [bundle] no BUNDLE.md"); return 0
        if not msgs:
            print(f"ok   [bundle] {len(rows)} components, v{version}")
        return 1 if msgs else 0
    out_dir = Path(a[1]) if len(a) > 1 else Path(".")
    version, rows, msgs = bundle.check_bundle(REPO)
    if not rows:
        print("refused: no BUNDLE.md", file=sys.stderr); return 2
    if msgs:
        for m in msgs:
            print(f"FAIL [bundle] {m}", file=sys.stderr)
        print("refused: bundle fails its check; not built", file=sys.stderr); return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    craft = dyadlib.load_module(PKG / "scripts" / "craft.py", "craft")
    shas = []
    for comp, ver in rows:
        if comp == bundle.CORE_NAME:
            out = out_dir / f"dyad-{ver}.tar.gz"
            rc = cmd_build(str(out))
        else:
            out = out_dir / f"{comp}-{ver}.tar.gz"
            rc = craft.cmd_export(REPO, [comp, str(out)])
        if rc:
            print(f"refused: {comp} did not export; bundle incomplete", file=sys.stderr); return 1
        shas.append(f"{hashlib.sha256(out.read_bytes()).hexdigest()}  {out.name}")
    (out_dir / "BUNDLE.sha256").write_text("\n".join(shas) + "\n")
    print(f"bundled v{version}: {len(rows)} components -> {out_dir}")
    return 0

def cmd_ledger():
    sys.path.insert(0, str(PKG / "scripts")); import dyadlib
    rows = dyadlib.read_rows(REPO)
    out = dyadlib.ledger_path(REPO); out.write_text(dyadlib.render(rows))
    print(f"rendered {out.relative_to(REPO)}: {len(rows)} rows"); return 0

def cmd_dwork(a):
    sys.path.insert(0, str(PKG / "scripts")); import dyadlib, datetime
    try:
        dyadlib.check_invariants(dyadlib, label="dyadlib")   # a broken transition table must not write a row (syseng invariants.md p1)
    except dyadlib.InvariantError as e:
        sys.exit(f"refused: {e}")
    rows = {r.id: r for r in dyadlib.read_rows(REPO)}
    today = datetime.date.today().isoformat()
    if a and a[0] == "new" and len(a) >= 2:
        try:
            subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=REPO, check=False, timeout=30)
            remote = {r.id for r in dyadlib.read_rows(REPO, at="origin/main")}
        except Exception as e:
            print(f"warning: could not read origin/main's rows ({e}); allocating from local ids "
                  f"only — a concurrent session's unpushed id may collide (d-work #32 F3)", file=sys.stderr)
            remote = set()
        rid = max(set(rows) | remote, default=0) + 1
        state = "backlog" if "--backlog" in a else "open"          # d-work #140: dyadlib.NEW_STATES
        disposed = f"{today} {a[a.index('-d') + 1]}" if "-d" in a else ""
        pos = [x for x in a[2:] if not x.startswith("-") and (a.index(x) < 2 or a[a.index(x) - 1] != "-d")]
        r = dyadlib.Row(rid, a[1], today, state, disposed, pos[0] if pos else "")
        f = dyadlib.rows_dir(REPO) / f"{rid}.md"; f.write_text(dyadlib.format_row_file(r))
        print(f"{rid}"); return 0
    if a and a[0] == "state" and len(a) >= 3:
        rid, state = int(a[1]), a[2]
        if rid not in rows: sys.exit(f"no row {rid}")
        r = rows[rid]; disposed, refs = r.disposed, r.refs
        if state not in dyadlib.STATES:
            sys.exit(f"no such state {state!r}; states: {' '.join(sorted(dyadlib.STATES))}")
        if not dyadlib.allowed(r.state, state):
            sys.exit(f"transition {r.state}\u2192{state} not in the table (Rule-16); allowed from {r.state}: {' '.join(sorted(dyadlib.TRANSITIONS[r.state])) or 'none'}")
        if "-d" in a: disposed = (disposed + "; " if disposed else "") + f"{today} " + a[a.index("-d") + 1]
        if "-r" in a: refs = a[a.index("-r") + 1]
        r = dyadlib.Row(r.id, r.title, r.opened, state, disposed, refs)
        (dyadlib.rows_dir(REPO) / f"{rid}.md").write_text(dyadlib.format_row_file(r))
        print(f"{rid}: {state}"); return 0
    if a and a[0] == "list":
        state = a[a.index("--state") + 1] if "--state" in a else None
        craft = a[a.index("--craft") + 1] if "--craft" in a else None
        if state is not None and state not in dyadlib.STATES:
            sys.exit(f"no such state {state!r}; states: {' '.join(sorted(dyadlib.STATES))}")
        out = [r for r in sorted(rows.values(), key=lambda r: r.id)
               if (state is None or r.state == state) and (craft is None or craft in r.refs.split())]
        for r in out:
            print(f"#{r.id} [{r.state}] {r.title}")
        return 0
    sys.exit(__doc__)

# Projector registry (crafts/sysarch/rules/projection.md p4; #160): discovered over every
# crafts/<craft>/projectors/project_<surface>.py, sorted by craft then surface, never hand-listed. The runner
# loads the module and calls main() — every model and rendering decision is the projector's (S4).
# D3 (#100, #99): keyed `craft/surface` — qualified by construction, so two crafts naming the same
# surface coexist (the collision report #99 found, and the once-independent re-derivation
# `crafts/sysarch/guards/registry.py` used to run against a bare-name registry); a bare surface
# resolves through `cmd_project` when exactly one craft provides it, the convention `dyad check
# --list`'s `<group>/<entity>` already uses — no new pattern.
REGISTRY_FIELDS = ("surface", "craft", "module")
NO_PROJECTOR = "no installed craft provides projectors (dyad craft install crafts/sysarch)"

def projectors() -> dict[str, tuple[str, str]]:
    """{craft/surface: (craft, repo-relative module path)}: one entry per craft's own projector file."""
    return {f"{py.parents[1].name}/{py.stem.removeprefix('project_')}": (py.parents[1].name, str(py.relative_to(REPO)))
            for py in dyadlib.projector_files(PKG)}

PROJECTORS = {k: rel for k, (c, rel) in projectors().items()}   # craft/surface -> module path (the reference guard reads it)

def _resolve_surface(reg: dict, token: str) -> tuple[str | None, list[str]]:
    """`token` already qualified (`craft/surface`) resolves directly; a bare surface resolves when
    exactly one craft provides it. Returns (key or None, the qualified candidates when ambiguous)."""
    if token in reg:
        return token, []
    candidates = sorted(k for k in reg if k.split("/", 1)[-1] == token)
    return (candidates[0], []) if len(candidates) == 1 else (None, candidates)

def cmd_project(a):
    reg = projectors()
    if not a or a[0] == "--list":
        for key, (_craft, rel) in sorted(reg.items()):
            print(f"{key:<20} {rel}")
        if not reg:
            print(f"no projector: {NO_PROJECTOR}")
        return 0
    key, candidates = _resolve_surface(reg, a[0])
    if key is None:
        if candidates:
            print(f"{a[0]!r} is provided by more than one craft: {', '.join(candidates)} — name one", file=sys.stderr); return 2
        print(f"no projector for {a[0]!r}: " + (f"registered: {' '.join(sorted(reg))}" if reg else NO_PROJECTOR), file=sys.stderr); return 2
    return dyadlib.load_module(REPO / reg[key][1], f"project_{key.replace('/', '_')}").main()

def cmd_runbook(a):
    """Rule-19: the run-book CLI lives in scripts/runbook.py (core; the check it calls is the sysadmin
    craft's guard, absent-safe — #155 amendment); this is dispatch only (S4)."""
    return dyadlib.load_module(PKG / "scripts" / "runbook.py", "runbook").main(a)

def cmd_session(a):
    """Rule-16: the session-presence CLI lives at guards/agent/sessions.py (it is also the
    guard); this is dispatch only (S4, d-work #185)."""
    sys.path.insert(0, str(PKG / "scripts")); import dyadlib
    return dyadlib.load_guard("agent", "sessions").main(a)

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "runbook":
        sys.exit(cmd_runbook(a[1:]))
    if a and a[0] == "craft":
        sys.exit(cmd_craft(a[1:]))
    if a and a[0] == "bundle":
        sys.exit(cmd_bundle(a[1:]))
    if a and a[0] == "session":
        sys.exit(cmd_session(a[1:]))
    if a and a[0] == "ledger":
        sys.exit(cmd_ledger())
    if a and a[0] == "dwork":
        sys.exit(cmd_dwork(a[1:]))
    if a and a[0] == "project":
        sys.exit(cmd_project(a[1:]))
    if not a or a[0] not in ("check", "build", "install"):
        sys.exit(__doc__)
    if a[0] == "check" and "--evidence" in a:
        sys.exit(cmd_evidence())
    if a[0] == "check" and "--pr" in a:
        i = a.index("--pr"); sys.exit(cmd_pr(*a[i + 1:i + 3]))
    if a[0] == "check" and "--guards" in a:
        sys.exit(cmd_guards())
    if a[0] == "check" and "--list" in a:
        sys.exit(cmd_list())
    if a[0] == "check" and "--tests" in a:
        i = a.index("--tests"); sys.exit(cmd_tests(*a[i + 1:i + 2]))
    sys.exit({"check": lambda: cmd_check(), "build": lambda: cmd_build(*a[1:2]), "install": lambda: cmd_install(*a[1:2])}[a[0]]())
