#!/usr/bin/env python3
"""dyad package tool (Rule-11; runner per S4). Kernel: Python 3.12+.
Entrypoint: dyad/bin/dyad (`dyad <noun> <verb>`, preference cli-pattern, ledger #152); `dyad` below
means `dyad/bin/dyad` from the git root (or python3.12 dyad/scripts/package.py).

  dyad check              the invariant pass (every model module's INVARIANTS and TREE_INVARIANTS, crafts/syseng/rules/invariants.md:
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
  dyad check --guards --pre-push   what dyad/hooks/pre-push runs: the same, over the refs git is pushing
                                (read from stdin, `<local ref> <local sha> <remote ref> <remote sha>`); a
                                push the guards cannot judge is refused — a ref other than the checked-out
                                HEAD, or a working tree with changes (#194); Rule-12's suite is skipped
                                when the suite memo proves this tree already passed on this checkout (#162),
                                and a test root is skipped whose craft tree is byte-identical to its
                                crafts/REGISTRY.md row, an install's, unmodified (#176)
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
  dyad check --evidence --at <rev>
                                the same block for <rev> (HEAD allowed), computed by that tree's own runner in
                                a detached worktree under the git common dir (dyad-evidence-<sha12>-*, no
                                bytecode written), removed afterwards on failure too; the caller's checkout,
                                HEAD and index are never touched, and no suite memo is read (#448, #443 C2).
                                A <rev> that names no commit is refused with one line (exit 2)
  dyad check --evidence --brief [--at <rev>]
                                the same run, read short (d-work #476, #473 C3): head=, tree=, dirty=, one
                                `counts: ok= warn= skip= fail=` line, every line that is not ok verbatim and in
                                order (an indented continuation line follows its parent), `stored: <path>` and
                                the same evidence-sha256= the full form prints, computed over the full block; the
                                same exit code. Warnings fold against origin/main's own (`baseline: origin/main
                                <sha12> (self|cached|stored|computed)`): a warning whose kind (`warn_kind`: ids,
                                quoted spans, paths and numbers made placeholders, the guard kept) main also has is
                                standing, one `warn [<guard>] <k> standing (<m> lines)` line per guard; a new kind
                                prints verbatim, once. Main's kinds come from a stored block of its head, else from
                                its `check` without the suite in a detached worktree, cached at
                                <git common dir>/dyad-evidence/baseline-<sha>.kinds; without one every warning
                                prints and one `warn [evidence] no baseline …` line says why. Never the exit code.
                                Every --evidence run, full or brief, stores its full block at
                                <git common dir>/dyad-evidence/<sha256>.txt (never tracked; a failed store warns)
  dyad check --evidence --show <sha256>
                                print a stored block; a unique prefix of at least 12 hex is enough. Too short,
                                ambiguous or not stored is refused with one line (exit 2)
  dyad build [out.tar.gz] deterministic archive of the core craft (scripts/distribute.py, the one
                                distribution code path every craft uses; #156)
  dyad install <repo> [--from <src>]
                          idempotent install of the core craft into another repo (same code path), with its
                                `dyad-operator` row in crafts/REGISTRY.md (#199). By default this checkout's tree;
                                with --from, a release archive (`dyad-<version>.tar.gz`, bundled crafts inside) or a
                                tree (an authoring clone at its tag) — VERSION, roots and bundled crafts read from
                                it, nothing from here (#353). The row's `source` names what was installed from:
                                the archive's file name, `<dir>@<tag>` or `<dir>@<sha12>` (distribute.source_name)
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
  dyad dwork new <title> [refs] [--backlog] [-d text] (--prompt[-file] <p> | --said[-file] <s>)
                                allocate the next id, write its row file (state open, or
                                backlog with --backlog; -d records the creating disposition) and
                                its provenance record: the Operator's words verbatim, a `prompt`
                                entry from --prompt, a `disposition` entry from --said (Rule-7).
                                -d needs --said; --backlog needs -d (Rule-3: a disposition opens it)
  dyad dwork new <title> [refs] --mandate <id>
                                the accreted row an authorized plan already describes (implicit mode,
                                d-work #290): state open, `mode: implicit`, the one entry
                                `<date> Y plan (mandate #<id>)`, and entry 1 of its record the
                                mandate's own authorizing words copied verbatim, noted
                                `mandate #<id>, <the mandate's own date>` (Rule-7 property 4). It takes
                                no disposition of its own, so --mandate refuses -d, --said, --prompt
                                and --backlog, and refuses a target that is no row or carries no
                                `Y plan`. refs defaults to `parent #<id>`
  dyad dwork state <id> <state> [-d text --said[-file] <s>] [--prompt[-file] <p>] [--relayed-via <seat>] [-r refs]
                                change state. A Done-`Y` that ratifies a merge is recorded with the
                                state unchanged and the head it was given on (`-d 'Y done (merges PR
                                #n at <head>)'`); the row reaches `done` by a second, dispositionless
                                call once that head is on `main` (Rule-3 Completion, #202). Under `dwork-trace:
                                always` a `Y done` is refused until <instance>/d-work/traces/<id>.md exists
                                (`dwork trace <id> --out`; a `--mandate` close excepted, #465) / append a disposition to the row and its words to
                                the record in one step; --prompt records a prompt received (#191).
                                --relayed-via notes the entries as relayed from <seat> (`relayed via
                                <seat>`, appended to a disposition's note), with --prompt or --said (#422)
  dyad dwork state <id> done --mandate <parent>
                                close an accreted row on its mandate's Done-`Y` (implicit mode, d-work
                                #422): the row's entry `<date> Y done (mandate #<parent>, <its date>)` and
                                its record's entry the mandate's own Done-`Y` words, noted `mandate
                                #<parent>, <its date>` (Rule-7 property 4). Refuses -d, --said, --prompt
                                and --relayed-via, a row neither `refs: parent #<parent>` nor born `Y plan
                                (mandate #<parent>)`, and a mandate whose row or record holds no `Y done`
  dyad dwork new|state … --land [--mirror <branch>]
                                the verb, committed and pushed in one call (scripts/land.py; #447, child C1
                                of plan #443): run in the tool-owned worktree `<git common dir>/dyad-land`,
                                detached at a freshly fetched origin/main and cleaned (PYTHONDONTWRITEBYTECODE=1),
                                never this checkout; every written path under <instance>/d-work/ or nothing
                                lands; one `ledger: …` commit citing no `d-work #`; one `git push --atomic
                                origin HEAD:main [HEAD:refs/heads/<branch>]`, so the hook runs once; a moved
                                main is rebuilt from the inputs (a `new` re-allocates), at most 3 tries, and an
                                entry already on origin/main is refused as `already landed`. Prints the landed
                                sha; fast-forwards this checkout when it is on a clean `main`
  dyad dwork land <path>... -m <msg> [--mirror <branch>]
                                the same for files this checkout already wrote — plan files, presence, traces:
                                copied into that worktree, committed under <msg>, pushed the same way; then, when
                                this checkout is on `main` and its only changes are those paths, each identical
                                to its landed blob, they are restored from HEAD and the checkout fast-forwarded (#459)
  dyad dwork batch <file>|- --land [--mirror <branch>]
                                several records in one commit and one push (#459): the file (or stdin) holds one
                                `dwork` argv per line, shell-quoted — `new …`, `state …` or `land <path>…`; blank
                                and `#` lines skipped; -m, --land and --mirror refused on a line. Every line is
                                parsed first; one row id both recording a merge-naming `Y done` and set `done` is
                                refused, naming both lines (the fence's Done order: record batch, merges, close
                                batch). Then one worktree pass: a line already on origin/main is skipped by name
                                (`skipped (already landed): …`), a batch of only such lines is refused, the rest run
                                in order and a refused line stops the batch with nothing committed; one `ledger:
                                batch …` commit citing no `d-work #`, one push, a moved main rebuilt (3 tries). A
                                later line cannot name an id a `new` line of the same batch creates: it is allocated
                                in the worktree and re-allocated on a rebuild. Under `dwork-trace: always` a `Y done`
                                line needs its trace: a `land <instance>/d-work/traces/<id>.md` line before it (#465)
  dyad dwork retire <id>... -d text --said[-file] <s>
                                the retirement form (Rule-3 `archived`, d-work #290): backlog or done
                                → archived over k rows in one call, one Operator question behind it.
                                -d and --said are given once for the whole set and the batch suffix
                                `(batch #a,#b,#c)` is composed from the ids named, so every row's
                                entry reads `<date> <d> (batch #a,#b,#c)` and every record gains the
                                same words (Rule-3 Batch disposition). Every refusal — an unknown id,
                                a state the table cannot archive from, a repeated id — precedes the
                                first write
  dyad dwork list [--state <s>] [--craft <c>]
                                rows from the row store (Rule-16), one `#<id> [<state>] <title>`
                                line each, sorted by id; `--craft <c>` keeps only rows whose `refs`
                                carries the bare token `<c>` (row.refs->craft, Rule-20; d-work #22)
                                — a routing tag, not a re-check of the guard's own resolution
  dyad dwork trace <id> [--transcript <path>]... [--out]
                                the d-work trace (scripts/trace.py, play-book dyad/playbooks/dwork-trace.md;
                                #213): timeline, buckets, counts and bottleneck line from the row, its
                                provenance and plan, git and the harness transcript (read in place, never
                                copied, never quoted); --out writes <instance>/d-work/traces/<id>.md,
                                at the Done-Y, in the commit that records it; without it, a preview to stdout
  dyad session name [--function <f>] [--topic <t>] [--hp <h>] [--system <s>] [--on <text>]
                                print this seat's name, <function>[-<topic>]-<hp>, and the harness session
                                title to set, from the environment (Rule-16 Presence; the organization
                                craft's form when installed, #369 C7); prints only, sets nothing
  dyad session touch [-r <row>]... [-f <file>]... | list
                                Rule-16 presence (guards/agent/sessions.py): touch refreshes this
                                session's file (DYAD_SESSION env, else a fresh id); no args, the
                                files from this session's own open/planned rows' stored plans;
                                list prints every session's file, flagging one past the stale window, with the
                                attendance mode over the live seats (M3 | M4 | hybrid), the `attended-seats`
                                declared beside the leader, each seat `attended` or `relayed`, and the records'
                                check of the declaration: `undeclared` for an own disposition in an undeclared
                                live seat, `warn` for a declared seat with none within `attendance-window`
                                (Rule-16 Presence, #388, #412)
  dyad session reconcile        the live presence files against the harness's own session list
                                (scripts/hostadapter.py harness_sessions; #434, child C1 of #431): one line per
                                mismatch — `no harness session`, `no presence`, `title differs`, `stale while
                                titled` — exit 1, else one `ok` line; the operate seat's run-book health command,
                                advisory, never a guard (Rule-16 Presence); the remedy is the writer's
  dyad project <surface> | --list   run a projector: the core's dyad/scripts/project_*.py, or one discovered under crafts/*/projectors/ (crafts/sysarch/rules/projection.md)
                                / print the registry as `<surface> <craft> <module>`; no craft: one line, exit 2
  dyad runbook check | list <instance> | run <instance> <name> [--as operator|agent] | new <instance>
                                Rule-19 run-books (scripts/runbook.py, the core runner; the check is the
                                sysadmin craft's guard, crafts/sysadmin/guards/runbooks.py): check every
                                run-book (exit 2 when no craft provides the check), list one's commands,
                                execute one command through the one runner — it prints the native
                                command line, tests the postcondition and appends an event to
                                <runbooks>/events/<instance>.jsonl — or seed a run-book from the craft's template
  dyad release [--scan]         the release service (scripts/release.py, d-work #470; run by the `released` workflow,
                                dyad-release.yml): every `<date> Y release <tag> at <cut sha> (archive <sha256>)` entry
                                on <instance>/d-work/rows that this push added (BEFORE) or a dispatch names (ONLY) —
                                cut on main and tag == VERSION at it, built by the cut's own one code path in a
                                detached worktree, sha256 verified, then the annotated tag pushed to origin and
                                `gh release create`; a tag at the cut with its Release is skipped, a tag elsewhere
                                refused, nothing written to the repo (Rule-11 Ratification events: clerical
                                execution of the recorded Y). --scan is read-only: `pending: <tags>|none`, and
                                `pending=true|false` appended to GITHUB_OUTPUT when set
  dyad bootstrap [--check]      make this clone fit to evidence and push from (scripts/bootstrap.py, d-work #474): set
                                `core.hooksPath dyad/hooks`, unshallow a shallow clone with its tags, fetch tags when
                                a core release tag is expected (BUNDLE.md names dyad-operator) and none is here; one
                                `ok|changed|warn [bootstrap]` line per step, exit 0 even offline (a SessionStart hook
                                never blocks); --check is read-only. `check --evidence` refuses a shallow clone, or a
                                tagless one where a core tag is expected, in one line naming this verb
"""
import sys
if sys.version_info < (3, 12):
    sys.exit(f"package.py: Python 3.12+ required (kernel pin), found {sys.version.split()[0]}")
if __name__ == "__main__":
    # crafts/syseng/rules/invariants.md p4 (amended #203): a false import-time invariant in the runner's own modules
    # (dyadlib, this file) stops every `dyad` command — fail-closed — with one line on stderr, never a traceback.
    def _invariant_error_one_line(kind, exc, tb, _previous=sys.excepthook):
        if kind.__name__ == "InvariantError":
            print(f"InvariantError: {exc}", file=sys.stderr)
        else:
            _previous(kind, exc, tb)
    sys.excepthook = _invariant_error_one_line
import os, re, subprocess, functools, fnmatch, hashlib, json, datetime, tempfile, shutil, threading
from concurrent.futures import ThreadPoolExecutor
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
        # another tree's guards (`dyad install --from`, #353) are read, never executed: `load_module` caches by
        # name, so importing them would answer with this tree's module of the same name, and an archive's code
        # runs nowhere before it is installed. The declaration is one assignment line, read as text there.
        declared = (re.search(r"^BUNDLED_WITH_CORE\s*=\s*True\b", py.read_text(), re.M) is not None if pkg != dyadlib.PKG
                    else getattr(dyadlib.load_guard_file(py, pkg), "BUNDLED_WITH_CORE", False))
        if declared:
            out.add(craft)
    return sorted(out)


def release_roots(pkg=None):
    """The roots the core *release* carries: `CORE_ROOTS` plus every bundled craft's tree. Used by
    `build` and `install` only — never by `check`, whose craft/instance scan (property 1) still
    judges the core craft alone, and never by the craft guard, which judges each Tended craft on
    its own. Bundling changes what ships, not what anything is."""
    return CORE_ROOTS + [f"crafts/{c}" for c in bundled_crafts(pkg)]


def core_extra(repo=None):
    """The `dyad-*` workflow files: the core craft's host-side hooks that ship in its archive (p2) — this repo's
    tracked ones, or any source tree's (an extracted release, an authoring clone; `--from`, #353)."""
    out = distribute.files(repo or REPO, [".github/workflows"])
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

# crafts/syseng/rules/invariants.md: the runner's own facts. `INVARIANTS` is pure, over its constants, enforced at
# import (the call at the bottom of this file); `TREE_INVARIANTS` reads the package files they name, so only the
# pass runs it (#203).
INVARIANTS = [
    ("contract-names-distinct", lambda: len(set(CONTRACT)) == len(CONTRACT)),
    ("suite-status-keys-distinct", lambda: len(set(SUITE_STATUS_KEYS)) == len(SUITE_STATUS_KEYS)),
]
TREE_INVARIANTS = [
    ("projector-modules-exist-with-main", lambda: all((REPO / rel).is_file() and hasattr(dyadlib.load_module(REPO / rel, f"project_{s.replace('/', '_')}"), "main") for s, rel in PROJECTORS.items())),
    ("templates-exist", lambda: all((PKG / "templates" / t).is_file() for t in TEMPLATES)),
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
    memo = suite_memo_parts()   # read before the run, compared after it: a tree that moved mid-run is never memoized
    suites = test_suites()
    # #326: through `run_suite`, the one child, so the temp-root sweep covers the push gate and the
    # evidence run too. This loop used to spawn its own `unittest` with no sweep, which is why the
    # docstring's claim that `run_suite` spawns it "the way `check_rule_12` spawns it" was two code
    # paths rather than one, and why the leak survived a fix applied to only the other. #475: every root at
    # once, printed in this order after all of them finish.
    for suite, (code, summary, err) in zip(suites, run_suites(suites)):   # no timing in `summary`: the evidence block is deterministic (#138)
        print(f"     [Rule-12] {suite.relative_to(REPO)}: " + " ".join(summary))  # `Ran N tests … OK (skipped=k)`: skips are visible in CI
        if code != 0:
            msgs.append(f"tests failed ({suite.relative_to(REPO)}):\n" + "\n".join(suite_failures(err) + err.strip().splitlines()[-1:]))
    if not msgs and memo and suite_memo_parts() == memo:
        suite_memo_write(memo)   # a full, all-roots pass on a clean tree (d-work #162)
    return msgs

# ---- the suite memo (Rule-12 property 2, d-work #162): proof, on this checkout, that one tree already passed
# every root of Rule-12's suite in one environment. Written after a full, all-roots pass on a clean tree
# (`check_rule_12`, `cmd_tests()` without a target); read only by `suite_gate` under `pre_push`, never by
# `check --evidence` nor by `check --guards` without `--pre-push` (Rule-2 Binding, Rule-14 property 3). One
# file per key under `<git common dir>/dyad-suite-memo/`, so every worktree of the checkout shares it; never
# tracked. Its absence only costs time: a cold or mismatched key runs the suite for real.
SUITE_MEMO_DIR = "dyad-suite-memo"
SUITE_MEMO_KEEP = 64
# The env knobs the runner, dyadlib and the craft guards read that can change a check's verdict. Not keyed:
# DYAD_NO_NESTED_TESTS (unset whenever a memo is written or read; `suite_env` sets it in every child) and
# DYAD_SESSION (a presence id, never an input to a verdict; keyed, it would make every session cold).
SUITE_MEMO_ENV = ("DYAD_INSTANCE", "DYAD_HOST", "DYAD_HOST_ZONE", "DYAD_OPS", "DYAD_RUNBOOKS", "DYAD_ROLE")
SUITE_MEMO_NAME = re.compile(r"[0-9a-f]{64}")

def _git(*a):
    """One read-only git call for the suite memo (and the evidence store's common dir, #476), in the repo judged and without a hook's GIT_VARS; its
    stdout stripped, or None when git cannot say."""
    try:
        r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, env=dyadlib.git_env(), timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None

def utc_date() -> str:
    return datetime.datetime.now(datetime.timezone.utc).date().isoformat()

def suite_memo_parts(rev="HEAD"):
    """Every input of a Rule-12 pass the memo keys on: `rev`'s tree, the interpreter (`sys.executable`,
    `sys.version`), git's version, the roots `test_suites()` runs, the env knobs (`SUITE_MEMO_ENV`), a digest
    of `refs/tags` (`check_drift` reads tags), a digest of the instance's `*.local.txt` files (ignored by git,
    so per worktree, and read by guards) and the UTC day. None on a dirty working tree (untracked files
    count: a new craft's `tests/` is a root) or when git cannot say — no memo is written or read then."""
    if _git("status", "--porcelain", "--untracked-files=normal") != "":
        return None
    tree, gitv = _git("rev-parse", "--verify", "-q", f"{rev}^{{tree}}"), _git("--version")
    tags = _git("for-each-ref", "--format=%(objectname) %(refname)", "refs/tags")
    if not tree or not gitv or tags is None:
        return None
    local = hashlib.sha256()
    for f in sorted(dyadlib.instance(REPO).glob("*.local.txt")):   # instance data git ignores, read by guards (#191, #192)
        local.update(f.name.encode() + b"\0" + f.read_bytes() + b"\0")
    return {"tree": tree, "executable": sys.executable, "python": sys.version, "git": gitv,
            "roots": sorted(Path(os.path.relpath(p, REPO)).as_posix() for p in test_suites()),
            "env": {k: os.environ.get(k) for k in SUITE_MEMO_ENV},
            "tags": hashlib.sha256(tags.encode()).hexdigest(), "local": local.hexdigest(), "date": utc_date()}

def suite_memo_key(parts: dict) -> str:
    """Pure: the memo's key, the sha256 of every part as canonical JSON, so any part changed is a miss."""
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()

def suite_memo_dir():
    common = _git("rev-parse", "--path-format=absolute", "--git-common-dir")
    return Path(common) / SUITE_MEMO_DIR if common else None

def suite_memo_write(parts):
    """Record a pass: the key file written atomically (`os.replace`), then the store pruned to the newest
    `SUITE_MEMO_KEEP`. Returns the file, or None when nothing was written. Never raises: a memo is an
    optimisation, and failing to write one fails nothing."""
    d = suite_memo_dir() if parts else None
    if d is None:
        return None
    key = suite_memo_key(parts)
    try:
        d.mkdir(exist_ok=True)
        tmp = d / f".{key}.{os.getpid()}.tmp"
        tmp.write_text(json.dumps(parts, sort_keys=True, indent=1) + "\n")
        os.replace(tmp, d / key)
        memos = sorted((f for f in d.iterdir() if SUITE_MEMO_NAME.fullmatch(f.name)),
                       key=lambda f: (f.stat().st_mtime_ns, f.name), reverse=True)
        for f in memos[SUITE_MEMO_KEEP:]:
            f.unlink(missing_ok=True)
    except OSError:
        return None
    return d / key

def suite_memo_hit(parts) -> bool:
    d = suite_memo_dir() if parts else None
    return bool(d) and (d / suite_memo_key(parts)).is_file()

def suite_memo_diff(parts: dict, memo: dict) -> list[str]:
    """Pure: the names of the key parts in which `parts` differs from a recorded pass's `memo`, in `parts`' own
    order; an env knob is named `env:<knob>` (d-work #474)."""
    out = []
    for k, v in parts.items():
        if k == "env" and isinstance(v, dict) and isinstance(memo.get(k), dict):
            out += [f"env:{e}" for e in v if v[e] != memo[k].get(e)]
        elif memo.get(k) != v:
            out.append(k)
    return out

def suite_memo_miss(parts):
    """The one informational line a pre-push memo miss prints (d-work #474): which key parts differ from the
    nearest recorded pass on this checkout — the memo file (each holds its parts as JSON, `suite_memo_write`) that
    differs in the fewest parts, newest first on a tie — so a `fetch --tags` or a new UTC day between an evidence
    run and its push is named rather than paid for silently. None when no memo was consulted (`parts` None)."""
    d = suite_memo_dir() if parts else None
    if d is None:
        return None
    best = None
    try:
        files = sorted((f for f in d.iterdir() if SUITE_MEMO_NAME.fullmatch(f.name)),
                       key=lambda f: (f.stat().st_mtime_ns, f.name), reverse=True) if d.is_dir() else []
    except OSError:
        files = []
    for f in files:
        try:
            memo = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(memo, dict):
            diff = suite_memo_diff(parts, memo)
            if best is None or len(diff) < len(best):
                best = diff
    if best is None:
        return "     [Rule-12] suite memo miss: no pass recorded on this checkout"
    return f"     [Rule-12] suite memo miss: {', '.join(best)} differ{'s' if len(best) == 1 else ''} from the nearest pass on this checkout"

def suite_memo_clause(base, head):
    """`suite_gate`'s memo clauses (pre-push only): the skip line, or None. First, `head`'s own tree already
    passed. Second, the range's own non-merge commits all touch only `<instance>/d-work/` (the three-dot walk
    the plan gate reads, `dyadlib.ledger_only`), `head`'s tree differs from its merge-base's only under
    `<instance>/d-work/` too (so a merge commit's own changes count), and that merge-base's tree already
    passed: a ledger branch behind `origin/main`, whose two-dot range carries `main`'s own advances. The
    same two steps hold for an events-only range, `<host>/runbooks/events/` (`dyadlib.events_only`, d-work
    #438), each class read whole: a range mixing the two is neither."""
    parts = suite_memo_parts(head)
    if suite_memo_hit(parts):
        return f"skip [guards] Rule-12 suite: tree {parts['tree'][:9]} already passed on this checkout (d-work #162)"
    for kind, only in (("ledger-only", dyadlib.ledger_only), ("events-only", dyadlib.events_only)):
        if parts and only(REPO, base, head):
            mb = _git("merge-base", base, head)
            if mb and only(REPO, mb, head, merge_base=False):
                mparts = suite_memo_parts(mb)
                if suite_memo_hit(mparts):
                    return (f"skip [guards] Rule-12 suite: {base}...HEAD is {kind} and its merge-base tree "
                            f"{mparts['tree'][:9]} already passed on this checkout (d-work #162)")
    return None

def suite_gate(base, head, pre_push=False, base_ok=True):
    """Rule-12's suite at the local gate (d-work #155, #164): whether `cmd_guards` runs it, and the one
    line it prints when it does not. Returns (run, line); `line` is None when nothing is printed. In order:
    inside a test run, or `cmd_check` already ran it in this process → no run, silently; `base` does not
    resolve (`cmd_guards` has printed its own skip line) → run; then the two-dot range `base..head`, read
    tri-state from `dyadlib.range_paths`: unreadable (None) → run, since an unknown range cannot be shown
    harmless; empty → skip, since a range that changes nothing cannot change a suite's outcome; every path
    under `<instance>/d-work/` → skip, the prefix and never the file suffix (a `.py` filter would have let
    #137's markdown run-book through, which broke the core suite by falsifying a pinned count); every path
    under `<host>/runbooks/events/` → skip likewise (`dyadlib.events_rel`, d-work #438), the two never mixed;
    anything else → run. Rename detection off (#191), so a move of code into the ledger still runs it. The plan gate
    and the fence keep `dyadlib.ledger_only`, where an empty range is never ledger-only. Last, and only under
    `pre_push` (the hook's flag), a readable range that would run consults the suite memo
    (`suite_memo_clause`, #162), and a miss returns run with the line naming the parts that missed
    (`suite_memo_miss`, #474); an unknown range never does. `cmd_evidence` never reaches a skip: its
    `cmd_check` runs the suite first, and it never passes `pre_push`."""
    if os.environ.get("DYAD_NO_NESTED_TESTS") or _SUITE_RAN:
        return False, None
    if not base_ok:
        return True, None
    paths = dyadlib.range_paths(REPO, base, head, merge_base=False)
    if paths is None:
        return True, None
    if not paths:
        return False, f"skip [guards] Rule-12 suite: {base}..HEAD is empty (d-work #164)"
    rel = dyadlib.instance_rel(REPO)
    if rel and all(p.startswith(f"{rel}/d-work/") for p in paths):
        return False, f"skip [guards] Rule-12 suite: {base}..HEAD is ledger-only (d-work #155)"
    events = dyadlib.events_rel(REPO)
    if events and all(p.startswith(f"{events}/") for p in paths):
        return False, f"skip [guards] Rule-12 suite: {base}..HEAD is events-only (d-work #438)"
    if pre_push:
        line = suite_memo_clause(base, head)
        if line:
            return False, line
        return True, suite_memo_miss(suite_memo_parts(head))   # which key part missed, one line (d-work #474)
    return True, None

def installed_roots(base, head):
    """`suite_gate`'s per-root clause (Rule-12 property 2, d-work #199 for backlog row #176), consulted by
    `cmd_guards` only under `pre_push`, only once `suite_gate` has said run. Returns (roots to run, skip
    lines): a test root skips when the craft tree it belongs to — `dyad/` for `dyad/tests`, `crafts/<c>/`
    for `crafts/<c>/tests` — hashes to its row in the craft registry (`craft.unmodified`): the installed
    tree, byte for byte, which its authoring system's own evidence already observed. A Tended craft's root
    also needs the core's tree unmodified, since its tests import the core. Anything else runs: no row (an
    authoring system, this one), a modified file, a registry the range itself changes (a hand-edited or a
    new row is judged once, in this system, before it is trusted), or a range that cannot be read."""
    roots = test_suites()
    paths = dyadlib.range_paths(REPO, base, head, merge_base=False)
    craft = craft_cli()
    if paths is None or craft.REGISTRY in paths:
        return roots, []
    rows = craft.registry_rows(REPO)
    if not rows:
        return roots, []
    core = craft.unmodified(REPO, craft.CORE_NAME, rows)
    run, lines = [], []
    for root in roots:
        rel = Path(os.path.relpath(root, REPO)).as_posix()
        name = craft.CORE_NAME if rel == f"{craft.CORE_ROOT}/tests" else rel.split("/")[1] if rel.startswith("crafts/") else None
        row = (core if name == craft.CORE_NAME else craft.unmodified(REPO, name, rows) if core and name else None)
        if row:
            lines.append(f"skip [guards] Rule-12 suite: {rel} — {name} {row['version']} installed unmodified ({craft.REGISTRY})")
        else:
            run.append(root)
    return run, lines

# the git config every test child runs under, appended after the caller's own `GIT_CONFIG_*` entries (suite_env)
SUITE_GIT_CONFIG = (("commit.gpgsign", "false"),   # #206: nothing reads a fixture's signature
                    ("gc.auto", "0"),              # #475: no background gc or maintenance after a fixture's commit,
                    ("maintenance.auto", "false")) # which packed a template's loose objects under a copy on git 2.55

def suite_env(tmp: str | None = None) -> dict[str, str]:
    """The environment a test child runs in: `DYAD_NO_NESTED_TESTS` set and every `GIT_VARS` dropped,
    and — given `tmp` — `TMPDIR`/`TMP`/`TEMP` pointed at it, so every fixture the child creates lands
    where `run_suite` can sweep it (#326). All three names, because a grandchild may read any of them.
    A git hook exports an absolute `GIT_DIR` when it runs in a linked worktree; a suite that inherits
    it points every scratch-repo git call at the real repository (#152: `core.bare`, a `feature`
    branch and a tag written into the live repo by the pre-push hook's run). Fixture commits are never
    signed (#206): a host whose global config signs every commit (a cloud container's) paid ~90 ms per
    scratch-repo commit for signatures nothing reads; appended as one more `GIT_CONFIG_*` entry, so an
    entry the caller already set survives. Nor does a fixture's commit start git's automatic gc or maintenance
    (#475): on git 2.55 (a CI runner's) a commit in `livetest.ScratchInstalls`' template detached a background
    repack that deleted loose objects while `copy` was reading them (`shutil.Error … .git/objects/17 … ENOENT`). A caller's `git -c` is dropped (#456): git exports every `-c` to
    its children as `GIT_CONFIG_PARAMETERS`, so `git -c core.hooksPath=dyad/hooks push` reached every
    fixture repo the suite builds and failed its commits (`INCIDENTS.md` row 153, row 123's cause)."""
    env = {k: v for k, v in dyadlib.git_env().items() if k != "GIT_CONFIG_PARAMETERS"}
    env["DYAD_NO_NESTED_TESTS"] = "1"
    n = int(env.get("GIT_CONFIG_COUNT") or 0)
    for i, (k, v) in enumerate(SUITE_GIT_CONFIG, n):
        env.update({f"GIT_CONFIG_KEY_{i}": k, f"GIT_CONFIG_VALUE_{i}": v})
    env["GIT_CONFIG_COUNT"] = str(n + len(SUITE_GIT_CONFIG))
    if tmp:
        env.update({"TMPDIR": tmp, "TMP": tmp, "TEMP": tmp})
    return env

# ---- the suite in parallel (d-work #475, C2 of #473): a root is listed once, its test classes run as separate
# children at most SUITE_JOBS at a time across every root, each child in its own temp root, and the root's summary
# is the sum of theirs, printed once the root is whole and in the roots' own order — so the evidence block's lines
# are the serial run's, whatever order the children finish in. A class is the unit because `setUpClass` and the
# class's fixtures are shared by its methods; a module-level fixture (`livetest.ScratchInstalls`) is paid once per
# child instead of once per module, which is what the parallelism buys back several times over.
SUITE_JOBS = os.cpu_count() or 1
_SUITE_SLOTS = threading.BoundedSemaphore(SUITE_JOBS)   # every child of every root, listings included
SUITE_STATUS_KEYS = ("failures", "errors", "skipped", "expected failures", "unexpected successes")   # unittest's order
# the listing child: discover the root exactly as `unittest discover -s <root>` does, print one test id per line
SUITE_LIST_CHILD = ("import sys, unittest\nsys.path.insert(0, sys.argv[1])\n"
                    "def ids(s):\n    for t in s:\n        yield from ids(t) if isinstance(t, unittest.TestSuite) else [t.id()]\n"
                    "print(*ids(unittest.defaultTestLoader.discover(sys.argv[1])), sep='\\n')")
# one unit's child: the root on sys.path as discover puts it there, then those ids by name
SUITE_UNIT_CHILD = ("import sys, unittest; sys.path.insert(0, sys.argv[1]); "
                    "unittest.main(module=None, argv=['python -m unittest', '-q', *sys.argv[2:]])")

def suite_child(argv):
    """The one `unittest` child — every listing, unit, root and target comes here, which is what makes "the
    way the runner runs it" one thing rather than two (#326). Always `DYAD_NO_NESTED_TESTS`, which is what
    makes it cost 39 s instead of 120 s (the nested scratch installs do not re-run their own suites), always
    inside a temp root of its own this function removes, and at most SUITE_JOBS at once (#475). Returns the
    completed process and the root it kept, or None.

    The root is made here, in the parent, and swept in `finally`, because the child is killed outright
    at the `timeout` below and runs no cleanup of its own — which is how 24,876 fixture directories
    accumulated and took `/tmp` to 100% of its 1,048,576 inodes, after which `unittest discover` died
    with `OSError: Errno 28` and no push could leave any clone, the pre-push gate running the suite.
    The fixtures still call `tempfile.mkdtemp()` without cleanup — 102 call sites over 42 files and two
    zones — so the sweep sits at the one place every sanctioned run passes through (Rule-12 property 2:
    the suite is run by the runner, not by hand); a hand-typed `unittest` is outside it and still leaks.
    A run that fails, or never returns, keeps its root, because that is the tree worth reading; a run that
    passes leaves nothing. A root of its own per child is also what lets two children run at once: a
    fixture that writes a fixed name under the temp dir (`test_craft.py`'s bundled archive, `d.parent`)
    writes it under its own child's root. No environment variable gates this: a new `DYAD_*`
    name would have to be declared in the syseng craft's naming table, which is a second zone and a
    craft release (Rule-1, Rule-11 property 7), and the return code already says which runs matter."""
    tmp, keep = tempfile.mkdtemp(prefix="dyad-suite-"), True   # a child that never returns is worth reading
    try:
        with _SUITE_SLOTS:
            r = subprocess.run([sys.executable, *argv], capture_output=True, text=True, timeout=600, cwd=REPO,
                               env=suite_env(tmp))
        keep = r.returncode != 0
    finally:
        if not keep:
            shutil.rmtree(tmp, ignore_errors=True)
    return r, (tmp if keep else None)

def suite_units(suite):
    """The root's test ids grouped by class, largest class first (ties in discovery order), or None when the
    listing cannot be trusted to name every test: the listing failed, found nothing, or a module failed to import
    (unittest names it `unittest.loader._FailedTest`) — the caller then runs the root as one discover child, so
    the failure is reported exactly as before."""
    r, kept = suite_child(["-c", SUITE_LIST_CHILD, str(suite)])
    if kept:
        shutil.rmtree(kept, ignore_errors=True)   # a listing's root holds nothing worth reading
    ids = r.stdout.split()
    if r.returncode or not ids or any(i.startswith("unittest.loader.") for i in ids):
        return None
    groups = {}
    for i in ids:
        groups.setdefault(i.rsplit(".", 1)[0], []).append(i)
    return sorted(groups.values(), key=len, reverse=True)

def suite_failures(err):
    """Each failing test of a child's stderr as one line, `ERROR: test_x (mod.Cls.test_x) — <the exception's last
    line>`, in the order unittest printed them. The summary says how many; these say which, so a red run on a host
    nobody can log into (a CI runner, whose kept temp root is gone with it) names its test (#475)."""
    out, head, last = [], None, ""
    for line in err.splitlines() + ["=" * 70]:
        if line.startswith(("ERROR: ", "FAIL: ")):
            head, last = line, ""
        elif head and (line.startswith("=" * 70) or re.match(r"Ran \d+ tests? in ", line)):
            out.append(f"{head} — {last}" if last else head); head = None
        elif head and line.strip() and not line.startswith("-" * 70):
            last = line.strip()
    return out

def suite_summary(stderrs, failed):
    """The children's summaries summed into one, in unittest's own words and order: `Ran N tests`, then
    `OK` or `FAILED` with `(failures=…, errors=…, skipped=…, …)` — what one discover child over the root prints."""
    ran, counts = 0, dict.fromkeys(SUITE_STATUS_KEYS, 0)
    for err in stderrs:
        for line in err.splitlines():
            if m := re.match(r"Ran (\d+) tests? in ", line):
                ran += int(m.group(1))
            elif m := re.fullmatch(r"(?:OK|FAILED) \((.*)\)", line):
                for k, v in (kv.split("=") for kv in m.group(1).split(", ")):
                    counts[k] = counts.get(k, 0) + int(v)
    info = ", ".join(f"{k}={counts[k]}" for k in SUITE_STATUS_KEYS if counts[k])
    return [f"Ran {ran} test{'' if ran == 1 else 's'}", ("FAILED" if failed else "OK") + (f" ({info})" if info else "")]

def run_suite(suite, target=None):
    """One root, or one target, through `suite_child`; returns (rc, summary lines, stderr). A target is one
    child. A root is listed and its classes run concurrently (`suite_units`); the summary is summed
    (`suite_summary`) and the stderr is every failing child's followed by that summary, so its last line says
    what the root's discover child would have said. A root the listing cannot split runs as one discover child.
    A failing child's root is kept and printed, in unit order once the root is whole (#326, #475)."""
    units = None if target else suite_units(suite)
    if units is None:
        argv = ["-m", "unittest", target, "-q"] if target else ["-m", "unittest", "discover", "-s", str(suite), "-q"]
        r, kept = suite_child(argv)
        if kept:
            print(f"     [Rule-12] temp root kept for reading: {kept}")
        summary = [re.sub(r" in [\d.]+s$", "", l) for l in r.stderr.strip().splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
        return r.returncode, summary, r.stderr
    with ThreadPoolExecutor(min(SUITE_JOBS, len(units))) as pool:
        done = list(pool.map(lambda ids: suite_child(["-c", SUITE_UNIT_CHILD, str(suite), *ids]), units))
    failed = [(r, kept) for r, kept in done if r.returncode]
    for _, kept in failed:
        if kept:
            print(f"     [Rule-12] temp root kept for reading: {kept}")
    summary = suite_summary([r.stderr for r, _ in done], bool(failed))
    return (1 if failed else 0), summary, "".join(r.stderr for r, _ in failed) + summary[-1]

def run_suites(suites):
    """Every root at once through `run_suite` (their children share SUITE_JOBS slots), results in the roots'
    order, so the caller prints them as the serial loop did (#475)."""
    suites = list(suites)
    if len(suites) <= 1:
        return [run_suite(s) for s in suites]
    with ThreadPoolExecutor(len(suites)) as pool:
        return list(pool.map(run_suite, suites))

def cmd_tests(target=None, roots=None):
    """Rule-13 property 1: the suites, run the way the runner runs them, as one verb. Without a
    target every root of `test_suites()`; with a directory that root; with anything else a dotted
    module, class or method handed to `unittest`. The point is the environment, not the typing:
    a hand-run without `DYAD_NO_NESTED_TESTS` pays about three times (d-work #154's audit).
    `roots` (the push gate's, d-work #199): exactly those roots, a subset of `test_suites()` — a
    partial run, never memoized, like a targeted one."""
    global _SUITE_RAN
    rc = 0
    if os.environ.get("DYAD_NO_NESTED_TESTS"):
        return rc       # already inside a test run (a suite invoking `check`); do not recurse
    _SUITE_RAN = True
    memo = None if target or roots is not None else suite_memo_parts()   # only a full, all-roots run is memoized (#162)
    if target and not Path(target).is_dir():
        code, summary, err = run_suite(None, target)
        print(f"     [Rule-12] {target}: " + " ".join(summary))
        if code:
            print("\n".join(suite_failures(err) + err.strip().splitlines()[-1:]), file=sys.stderr); rc = 1
        return rc
    suites = [Path(target)] if target else test_suites() if roots is None else list(roots)
    for suite, (code, summary, err) in zip(suites, run_suites(suites)):
        print(f"     [Rule-12] {suite.relative_to(REPO) if suite.is_absolute() else suite}: " + " ".join(summary))
        if code:
            print("\n".join(suite_failures(err) + err.strip().splitlines()[-1:]), file=sys.stderr); rc = 1
    if rc == 0 and memo and suite_memo_parts() == memo:
        suite_memo_write(memo)
    return rc

# ---- the guard registry (crafts/sysarch/rules/guards.md p4): discovered from dyad/guards/<corpus>/<entity>.py (core) and
# crafts/<craft>/guards/<entity>.py (every Tended craft, #155), never hand-listed. Each module declares
# ENTITY, CORPUS, FIELDS, TRANSACTION, check_package(root) and, when TRANSACTION, check_transaction(root, base, head);
# the runner owns none of their semantics (S4). A core guard's CORPUS equals its directory; a craft
# guard's CORPUS is a zone name (containment.ZONES), the zone of the entity's store, or `workstation`,
# the logical host corpus resolving to the host path's zone (containment.corpora, #175).
GUARD_FIELDS = ("corpus", "entity", "module", "transaction", "root")
CONTRACT = dyadlib.CONTRACT   # one definition, shared with the craft guard (dyadlib.contract_problem, #156)

def zone_names():
    try:
        return dyadlib.load_guard("infra", "containment", PKG).corpora(REPO)   # zones plus the logical host corpus (#175)
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
def invariant_modules(failures: list | None = None):
    """[(label, module, extra invariants)] in pass order: dyadlib, this runner, every guard in registry order
    (each with the four contract invariants appended, dyadlib.contract_invariants), every projector in
    PROJECTORS order, then the run-book runner, the craft CLI and the distribution path. A module that does not
    load — a guard (the registry's own failure too) or any other, whose import-time `enforce` raised (#203) — is
    left out and, when `failures` is a list, appended to it as (label, problem), so one module never aborts the pass."""
    out = [("dyadlib", dyadlib, ()), ("package", sys.modules[__name__], ())]
    failures = [] if failures is None else failures
    zones = None
    for group, entity, rel, tx, mod, problem in registry():
        if mod is None:
            if problem.startswith("does not load"):
                failures.append((f"{group}/{entity}", problem))
            continue
        root = guard_root(rel)
        if root == "craft" and zones is None:
            zones = zone_names()
        out.append((f"{group}/{entity}", mod, dyadlib.contract_invariants(mod, root, group, zones)))
    later = [(f"project_{s.replace('/', '_')}", REPO / rel) for s, rel in sorted(PROJECTORS.items())]   # `/`-free: distinct from a guard label
    later += [(name, PKG / "scripts" / f"{name}.py") for name in ("runbook", "craft", "distribute")]
    for label, path in later:
        try:
            out.append((label, dyadlib.load_module(path, label), ()))
        except Exception as e:
            failures.append((label, f"does not load: {type(e).__name__}: {e}"))
    return out

def cmd_invariants():
    """Print one line per module over both lists; rc 1 when any invariant is false or a module does not load (its
    import-time `enforce` raised). Run by `check`, `check --guards`, `--pr` and `--evidence`, never by --list/--help."""
    rc, failures = 0, []
    for label, mod, extra in invariant_modules(failures):
        try:
            n = dyadlib.check_invariants(mod, extra, label)
            print(f"ok   [invariant] {label} ({n})")
        except dyadlib.InvariantError as e:
            for name in e.failed:
                print(f"FAIL [invariant] {label}: {name}")
            rc = 1
    for label, problem in failures:
        print(f"FAIL [invariant] {label}: {problem}")
        rc = 1
    return rc

def cmd_list():
    print(f"{'corpus':<12} {'entity':<12} {'module':<44} {'transaction':<12} root")
    for corpus, entity, rel, tx, mod, problem in registry():
        print(f"{corpus:<12} {entity:<12} {rel:<44} {'yes' if tx else 'no':<12} {guard_root(rel)}{'  FAIL ' + problem if problem else ''}")
    return int(any(e[5] for e in registry()))

ZERO_SHA = frozenset("0")

def pushed_refs(lines, base="origin/main"):
    """The refs git is pushing (pre-push stdin), judged for whether the guards can see them (#194).
    Returns (head, refusals): `head`, the one commit every judged ref resolves to (None when every ref is
    a deletion or already on `base`); `refusals`, each ref the guards cannot judge, with the command
    that fixes it. The state checks read the checked-out tree, so a pushed commit must be HEAD and the
    tree clean; a ref whose commit `base` already holds (a release tag on `main`) adds nothing to judge."""
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    here = git("rev-parse", "HEAD").stdout.strip()
    heads, refusals = set(), []
    for line in lines:
        parts = line.split()
        if len(parts) != 4:
            continue
        local_ref, local_sha, remote_ref, _ = parts
        if set(local_sha) <= ZERO_SHA:
            continue                                     # a deletion carries no commit
        sha = git("rev-parse", "--verify", "-q", f"{local_sha}^{{commit}}").stdout.strip()
        if not sha:
            continue                                     # not a commit-ish (a tag on a tree or blob): nothing the guards judge
        if git("merge-base", "--is-ancestor", sha, base).returncode == 0:
            continue                                     # already on the base: no new commit leaves
        if sha != here:
            refusals.append(f"{local_ref} is at {sha[:9]} but HEAD is {here[:9]}: the guards judge the checked-out tree — "
                            f"check it out and push it from there (`git switch {local_ref.removeprefix('refs/heads/')} && git push`)")
            continue
        heads.add(sha)
    if heads:
        dirty = git("status", "--porcelain", "--untracked-files=normal").stdout.splitlines()
        if dirty:
            shown = ", ".join(l[3:] for l in dirty[:5]) + (f" and {len(dirty) - 5} more" if len(dirty) > 5 else "")
            refusals.append(f"the working tree has changes the push does not carry ({shown}): the guards would judge "
                            f"them, not the commit — commit, stash or remove them, then push")
    return (heads.pop() if heads else None), refusals

def cmd_guards(base="origin/main", pre_push=False):
    """I2: run every guard locally, the way a push would be judged — each guard's package check,
    then every TRANSACTION guard over base..HEAD. Returns rc. With `pre_push` (the hook, #194) the
    refs git is pushing come on stdin: a push the guards cannot judge is refused before any check
    runs, a push that adds no commit passes at once, and otherwise the transaction head is the
    pushed commit, which the refusal rule makes the checked-out HEAD."""
    if pre_push:
        pushed, refusals = pushed_refs(sys.stdin.read().splitlines(), base)
        for m in refusals:
            print(f"FAIL [pre-push] {m}")
        if refusals:
            return 1
        if pushed is None:
            print(f"ok   [pre-push] nothing new to judge: every ref is a deletion or already on {base}")
            return 0
    else:
        pushed = None
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
    head = pushed or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
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
    # ran it by hand 134 times in one session (#154's audit). A ledger-only, events-only (#438) or empty range cannot
    # change a suite's outcome, so it skips (`suite_gate`, #164) and the push stays at the guards' own
    # ~1.7 s; anything else pays the suite here rather than by hand at three times the price. The
    # guards above are never gated.
    run, line = suite_gate(base, head, pre_push, base_ok)
    if line:
        print(line)
    roots = None
    if run and pre_push and base_ok:   # an installed, unmodified tree skips its own root (#176, d-work #199); never for --evidence
        roots, lines = installed_roots(base, head)
        for l in lines:
            print(l)
        if not lines:
            roots = None               # every root runs: the full run, memoized as before
        run = bool(roots) or roots is None
    if run and cmd_tests(roots=roots):
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

def cmd_evidence(brief=False):
    """Rule-14 property 3: the evidence block. Runs `check` and `check --guards` on the exact
    head, prints head/tree/dirty, every line they print, and a sha256 of all preceding lines
    (joined by newline) so the Operator can re-run it on the same head and compare. The full block is
    stored (`evidence_store`) whatever is printed; `brief` prints `evidence_brief` of it instead (#476)."""
    import io, contextlib
    unfit = dyadlib.load_module(PKG / "scripts" / "bootstrap.py", "bootstrap").clone_problems(REPO)
    if unfit:   # d-work #474: a shallow or tagless clone yields false FAILs (infra/bundle, plan.base->commit); one line, nothing run
        print(f"FAIL [evidence] {unfit[0]}")
        return 2
    git = lambda *a: subprocess.check_output(["git", *a], cwd=REPO, text=True).strip()
    lines = [f"head={git('rev-parse', 'HEAD')}", f"tree={git('rev-parse', 'HEAD^{tree}')}",
             f"dirty={'yes' if git('status', '--porcelain') else 'no'}"]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cmd_check() | cmd_guards()
    lines += buf.getvalue().splitlines()
    block = lines + [f"evidence-sha256={evidence_sha256(lines)}"]
    stored = evidence_store(block)                       # #476: every run, full or brief; never raises
    for l in (evidence_brief(block, stored, evidence_baseline(block)) if brief else block):
        print(l)
    return int(rc)

EVIDENCE_STORE = "dyad-evidence"   # `<git common dir>/dyad-evidence/<sha256>.txt`: every full block a run printed or
                                   # read short, never tracked; `--show` reads it back (d-work #476, #473 C3)
EVIDENCE_PREFIX_MIN = 12           # the shortest prefix `--show` accepts: 48 bits, as `--at`'s worktree names use
EVIDENCE_TOKENS = {"ok": "ok", "warn": "warn", "skip": "skip", "FAIL": "fail"}   # leading token -> counts key
EVIDENCE_HEADER = ("head=", "tree=", "dirty=")
EVIDENCE_SHA = "evidence-sha256="

def evidence_counts(lines):
    """Pure: `{ok, warn, skip, fail, other}` over a block's check and guard lines. A line is classified by its first
    whitespace-separated token (`ok`, `warn`, `skip`, `FAIL`); the head=/tree=/dirty= and evidence-sha256= lines
    are not check lines, and a line that starts with whitespace is a continuation of the line above it (a FAIL's
    `     [Rule-12] …` detail) and is not counted. Any other line is `other`: never silently dropped (#476)."""
    n = dict.fromkeys(("ok", "warn", "skip", "fail", "other"), 0)
    for l in lines:
        if not l.strip() or l[0].isspace() or l.startswith(EVIDENCE_HEADER) or l.startswith(EVIDENCE_SHA):
            continue
        n[EVIDENCE_TOKENS.get(l.split()[0], "other")] += 1
    return n

WARN_KIND_VERSION = 1   # bumped whenever `warn_kind`'s rule changes: a cached baseline of another version is a miss
WARN_GUARDS = re.compile(r"^warn \[guards\] (\S+) ?")
WARN_LABEL = re.compile(r"^warn \[([^\]]*)\] ?(.*)$", re.S)
WARN_HEX = re.compile(r"\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,}\b")
WARN_QUOTE = re.compile(r"`[^`]*`|(?<!\w)'[^']*'(?!\w)")
WARN_TOKEN = re.compile(r"[^\s,;:()\[\]'\"`<>]+")
WARN_EXT = re.compile(r".*\.(md|py|txt|sh|yml|yaml|json|jsonl|toml|cfg|ini|gz|tar|html|css|js|lock|kinds)", re.I)
WARN_NUMBER = re.compile(r"\d+(?:\.\d+)*")
WARN_RUN = re.compile(r"<(sha|q|path|n)>(?:(?:, | )<\1>)+")

def warn_unprefix(line):
    """Pure: a guard warning as `check` prints it. `check --guards` prints each guard's warning as
    `warn [guards] <corpus>/<entity> <text>` where `check` prints `warn [<corpus>/<entity>] <text>`; the first is
    rewritten to the second, so the two sources of one warning are one line. Any other line is returned unchanged."""
    return WARN_GUARDS.sub(lambda m: f"warn [{m.group(1)}] ", line, count=1).rstrip(" ") if line.startswith("warn [guards] ") else line

def warn_guard(line):
    """Pure: the guard label of a warn line after `warn_unprefix` (`agent/plans`), or None for a line that is not one."""
    m = WARN_LABEL.match(warn_unprefix(line))
    return m.group(1) if m else None

def warn_kind(line):
    """Pure: the kind of a warn line, the key `--brief` compares with origin/main's to tell a standing warning from a
    new one (d-work #476); None for a line that is not a warning. The rule, applied in this order:
    1. `warn_unprefix`: `warn [guards] X …` becomes `warn [X] …`, so both sources of a warning share its kind;
    2. the guard label `[X]` is kept as it is: the same text from another guard is another kind;
    3. in the text after it — a hex word of 7 or more characters mixing digits and a–f (a 40- or 64-hex sha, a
       seat's 8-hex `<hp>`) becomes `<sha>`; a backtick-quoted span, or a single-quoted one not inside a word, `<q>`;
       a token (split at whitespace and `,;:()[]'"`<>`) holding a `/` or ending in a file extension (`WARN_EXT`)
       `<path>`; a decimal number, dotted versions included, `<n>`;
    4. a run of one placeholder separated by `, ` or a space (`<path>, <path>, <path>`) becomes one, so a list that
       grows or shrinks keeps its kind; whitespace collapses to one space.
    So `warn [guards] agent/plans 43.md: never mentions `intent as read` (dyadlib.PLAN_PARTS)` is
    `warn [agent/plans] <path>: never mentions <q> (dyadlib.PLAN_PARTS)`. Words are kept: a list of names that are
    not ids, paths or numbers (a seat's function, a craft's name) changes the kind when it changes, which prints the
    warning verbatim — the safe direction: a rule that collapsed too much would hide a new warning as standing."""
    if not line.startswith("warn "):
        return None
    m = WARN_LABEL.match(warn_unprefix(line))
    if not m:
        return " ".join(line.split())
    text = WARN_HEX.sub("<sha>", m.group(2))
    text = WARN_QUOTE.sub("<q>", text)
    text = WARN_TOKEN.sub(lambda t: "<path>" if "/" in t.group(0) or WARN_EXT.fullmatch(t.group(0)) else t.group(0), text)
    text = WARN_NUMBER.sub("<n>", text)
    text = WARN_RUN.sub(lambda r: f"<{r.group(1)}>", text)
    return " ".join(f"warn [{m.group(1)}] {text}".split())

def evidence_warn_kinds(lines):
    """Pure: the set of `warn_kind`s of a block's (or a `check` run's) warn lines; a continuation line is no warning."""
    return {warn_kind(l) for l in lines if l.startswith("warn ")}

def evidence_fold(body, kinds):
    """Pure: the non-ok lines of a block's body as `--brief` prints them, in order (d-work #476). Every line that is not
    ok is kept verbatim — FAIL, skip, any other line — and a continuation line is kept exactly when its parent is.
    With `kinds` None (no baseline) every warning is kept too. With a baseline set, a warning whose `warn_kind` is in it
    is *standing*: it is folded into one line per guard, `warn [<guard>] <k> standing (<m> lines)`, placed where that
    guard's first standing warning was — `k` the distinct warnings once `warn_unprefix` has made `check`'s and
    `check --guards`' copies of one warning the same line (deduped), `m` the lines folded (both copies counted; the
    counts line's `warn=` counts lines too). A warning whose kind is not in it is *new*: printed verbatim, once — its
    twin from the other source, the same line after `warn_unprefix`, is dropped with its continuation lines."""
    keep, folds, seen, parent_kept = [], {}, set(), False
    for l in body:
        if not l.strip() or l.startswith(EVIDENCE_HEADER) or l.startswith(EVIDENCE_SHA):
            continue
        if l[0].isspace():
            if parent_kept: keep.append(l)
            continue
        tok = l.split()[0]
        parent_kept = tok != "ok"
        if not parent_kept:
            continue
        if tok != "warn" or kinds is None:
            keep.append(l); continue
        same = warn_unprefix(l)
        if warn_kind(l) in kinds:
            guard = warn_guard(l) or "?"
            if guard not in folds:
                folds[guard] = [set(), 0, len(keep)]; keep.append(None)
            folds[guard][0].add(same); folds[guard][1] += 1
            parent_kept = False
        elif same in seen:
            parent_kept = False
        else:
            seen.add(same); keep.append(l)
    for guard, (distinct, n, at) in folds.items():
        keep[at] = f"warn [{guard}] {len(distinct)} standing ({n} lines)"
    return keep

def evidence_brief(block, stored=None, baseline=None):
    """Pure: the brief form of a full evidence block (`block`: exactly the lines `check --evidence` prints, its last
    the evidence-sha256= line). head=, tree=, dirty=; one counts line (` other=<n>` appended only when a line had no
    known token); one baseline line — `baseline: <source>` when `baseline` is `(kinds, source)` with a kind set, else
    `warn [evidence] no baseline for origin/main: warnings not folded (<reason>)`, the reason being `baseline`'s second
    item or `not looked up` when `baseline` is None; every line that is not ok, as `evidence_fold` keeps it against
    that baseline; `stored: <path>` (`stored: none` when the store failed); and the evidence-sha256= line recomputed
    over the full block, which is the full form's own value, since the hash is never of what brief prints."""
    body = block[:-1] if block and block[-1].startswith(EVIDENCE_SHA) else list(block)
    head = [l for l in body if l.startswith(EVIDENCE_HEADER)]
    n = evidence_counts(body)
    counts = f"counts: ok={n['ok']} warn={n['warn']} skip={n['skip']} fail={n['fail']}"
    kinds, source = baseline if baseline else (None, "not looked up")
    base = f"baseline: {source}" if kinds is not None else \
        f"warn [evidence] no baseline for origin/main: warnings not folded ({source})"
    return [*head, counts + (f" other={n['other']}" if n["other"] else ""), base, *evidence_fold(body, kinds),
            f"stored: {stored if stored else 'none'}", f"{EVIDENCE_SHA}{evidence_sha256(body)}"]

def evidence_dir():
    """`<git common dir>/dyad-evidence`, shared by every worktree of the checkout; None when git cannot say."""
    common = _git("rev-parse", "--path-format=absolute", "--git-common-dir")
    return Path(common) / EVIDENCE_STORE if common else None

def evidence_store(block):
    """Write a full evidence block to `<git common dir>/dyad-evidence/<sha256>.txt` and return the path; the name
    is the block's own evidence-sha256, so a re-run of the same head and result rewrites the same file. Never
    raises: a store that fails prints one warn line to stderr and returns None, and the evidence still prints."""
    try:
        if not block or not block[-1].startswith(EVIDENCE_SHA):
            raise ValueError("no evidence-sha256= line")
        sha = block[-1].removeprefix(EVIDENCE_SHA)
        if sha != evidence_sha256(block[:-1]):
            raise ValueError("evidence-sha256= does not match the block")
        d = evidence_dir()
        if d is None:
            raise OSError("git common dir not found")
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"{sha}.txt"
        tmp = d / f".{sha}.{os.getpid()}.tmp"
        tmp.write_text(chr(10).join(block) + chr(10)); tmp.replace(path)   # atomic: a reader never sees half a block
        return path
    except Exception as e:   # a store is a convenience for `--show`, never part of the evidence
        print(f"warn [evidence] block not stored: {e}", file=sys.stderr)
        return None

def cmd_evidence_show(prefix):
    """`check --evidence --show <sha256>`: print a stored block. A unique prefix of at least EVIDENCE_PREFIX_MIN
    lowercase hex is accepted; too short, not hex, ambiguous or not stored is refused with one line, exit 2."""
    p = (prefix or "").lower()
    if len(p) < EVIDENCE_PREFIX_MIN or len(p) > 64 or any(c not in "0123456789abcdef" for c in p):
        print(f"FAIL [evidence] --show {prefix or '(missing)'}: give a sha256 or a prefix of at least "
              f"{EVIDENCE_PREFIX_MIN} hex"); return 2
    d = evidence_dir()
    hits = sorted(d.glob(f"{p}*.txt")) if d is not None and d.is_dir() else []
    if len(hits) != 1:
        why = "no stored evidence block" if not hits else f"ambiguous ({len(hits)} stored blocks)"
        print(f"FAIL [evidence] --show {prefix}: {why}"); return 2
    sys.stdout.write(hits[0].read_text())
    return 0

EVIDENCE_WORKTREE = "dyad-evidence-"   # `<git common dir>/dyad-evidence-<sha12>-<random>`: one per `--at` run, never kept

def evidence_env() -> dict[str, str]:
    """The environment the `--at` child runs in: every `GIT_VARS` dropped, so the child's git calls see the
    worktree it runs in and never a hook's GIT_DIR (#152), and no bytecode written into that tree (#412–#414:
    stale ignored directories). `DYAD_NO_NESTED_TESTS` is the caller's, neither set nor dropped: the child
    runs the suite exactly when `check --evidence` here would (Rule-12 p2), and a test that calls it stays fast."""
    return {**dyadlib.git_env(), "PYTHONDONTWRITEBYTECODE": "1"}

def baseline_env() -> dict[str, str]:
    """The environment the baseline child runs in (d-work #476): `evidence_env()` with `DYAD_NO_NESTED_TESTS` set, so
    origin/main's `check` runs every guard and never the suite — a baseline is warn kinds, which no test prints."""
    return {**evidence_env(), "DYAD_NO_NESTED_TESTS": "1"}

def evidence_in_worktree(sha, fn):
    """Run `fn(<worktree path>)` in a detached worktree of `sha` under the git common dir
    (`dyad-evidence-<sha12>-<random>`) and return its result; the worktree is removed afterwards, on failure or
    interruption too, and the caller's checkout, HEAD and index are never touched (#448). A worktree that cannot be
    added raises RuntimeError naming git's last stderr line. Shared by `--at` and the baseline (#476)."""
    env = dyadlib.git_env()
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=REPO, env=env,
                            capture_output=True, text=True, check=True).stdout.strip()
    wt = Path(tempfile.mkdtemp(prefix=f"{EVIDENCE_WORKTREE}{sha[:12]}-", dir=common))   # unique: two runs never collide
    try:
        r = subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(wt), sha], cwd=REPO, env=env,
                           capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(f"git worktree add: {(r.stderr.strip().splitlines() or ['?'])[-1]}")
        return fn(wt)
    finally:
        removed = subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=REPO, env=env,
                                 capture_output=True, text=True).returncode == 0
        if not removed:   # never registered (the add failed) or half gone: the directory, then git's record of it
            shutil.rmtree(wt, ignore_errors=True)
            subprocess.run(["git", "worktree", "prune"], cwd=REPO, env=env, capture_output=True)
        if wt.exists():
            print(f"warn [evidence] worktree not removed: {wt}", file=sys.stderr)

BASELINE_CACHE = "baseline-{sha}.kinds"   # in the evidence store: one origin/main commit's warn kinds, never tracked

def evidence_baseline_compute(sha):
    """origin/main's warn kinds without the suite (d-work #476): `package.py check` of `sha`, run by that tree's own
    runner in a detached worktree (`evidence_in_worktree`) under `baseline_env()`. `check` alone suffices: its lines
    are every guard's `check_package` plus Rule-11's and Rule-12's, so its warnings are a superset of
    `check --guards`' once `warn_unprefix` maps them, and the transaction guards print no warnings. A non-zero exit
    is fine (main may fail a check); a child that printed no check line at all raises."""
    r = evidence_in_worktree(sha, lambda wt: subprocess.run(   # a lambda: the spawn fence reads the enclosing function
        [sys.executable, str(wt / "dyad" / "scripts" / "package.py"), "check"], cwd=wt, env=baseline_env(),
        capture_output=True, text=True, timeout=600))
    lines = r.stdout.splitlines()
    n = evidence_counts(lines)
    if not n["ok"] + n["warn"] + n["skip"] + n["fail"]:
        raise RuntimeError(f"check printed no check line (exit {r.returncode}): "
                           f"{(r.stderr.strip().splitlines() or ['?'])[-1]}")
    return evidence_warn_kinds(lines)

def evidence_baseline_cache_read(path, sha):
    """The kind set a cache file holds, or None when it is absent or of another `WARN_KIND_VERSION` or sha."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return None
    if not lines or lines[0] != f"# warn_kind v{WARN_KIND_VERSION} {sha}":
        return None
    return set(lines[1:])

def evidence_baseline_cache_write(path, sha, kinds):
    """Write the cache file atomically; a failure is ignored — a cache only saves time."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        tmp.write_text("\n".join([f"# warn_kind v{WARN_KIND_VERSION} {sha}", *sorted(kinds)]) + "\n"); tmp.replace(path)
    except OSError:
        pass

def evidence_baseline_stored(d, sha):
    """The kind set of a stored block (`<store>/<sha256>.txt`) whose `head=` is `sha`, with `dirty=no` and an
    evidence-sha256= line that matches it, or None when the store holds none."""
    for f in sorted(d.glob("*.txt")) if d is not None and d.is_dir() else ():
        try:
            with f.open() as h:
                if h.readline().rstrip("\n") != f"head={sha}":
                    continue
            block = f.read_text().splitlines()
        except OSError:
            continue
        if "dirty=no" in block[:3] and block and block[-1] == EVIDENCE_SHA + evidence_sha256(block[:-1]):
            return evidence_warn_kinds(block)
    return None

def evidence_baseline(block):
    """The baseline `--brief` folds against (d-work #476): `(kinds, source)` — origin/main's own warn kinds and the
    line naming where they came from — or `(None, reason)`. Cheapest first: the head being evidenced *is* origin/main
    (`self`: every warning is standing, it is the baseline); a cache file `<store>/baseline-<sha>.kinds` (`cached`); a
    stored block of origin/main's head (`stored`); else `evidence_baseline_compute` (`computed`). A kind set found
    by the last two is written to the cache. Never raises: whatever fails is the reason, and the evidence — its lines,
    its sha256 and its exit code — is the same either way."""
    try:
        sha = _git("rev-parse", "--verify", "-q", "origin/main^{commit}")
        if not sha:
            return None, "origin/main does not resolve"
        name = f"origin/main {sha[:12]}"
        body = block[:-1] if block and block[-1].startswith(EVIDENCE_SHA) else list(block)
        if body and body[0] == f"head={sha}":
            return evidence_warn_kinds(body), f"{name} (self)"
        d = evidence_dir()
        if d is None:
            return None, "git common dir not found"
        cache = d / BASELINE_CACHE.format(sha=sha)
        kinds = evidence_baseline_cache_read(cache, sha)
        if kinds is not None:
            return kinds, f"{name} (cached)"
        for how, get in (("stored", lambda: evidence_baseline_stored(d, sha)), ("computed", lambda: evidence_baseline_compute(sha))):
            kinds = get()
            if kinds is not None:
                evidence_baseline_cache_write(cache, sha, kinds)
                return kinds, f"{name} ({how})"
        return None, "no kinds"
    except Exception as e:   # a baseline only shortens what is printed; it never fails the evidence
        return None, f"{type(e).__name__}: {e}"

def evidence_at_print(out, brief):
    """The `--at` child's stdout, as the parent prints it: verbatim (full) or `evidence_brief` of it against
    `evidence_baseline`, the block stored either way. A child that printed no well-formed block (a refusal, a crash)
    is printed verbatim and nothing is stored, brief or not: there is no block to read short (#476)."""
    block = out.splitlines()
    whole = bool(block) and block[0].startswith("head=") and block[-1] == EVIDENCE_SHA + evidence_sha256(block[:-1])
    stored = evidence_store(block) if whole else None
    if brief and whole:
        for l in evidence_brief(block, stored, evidence_baseline(block)): print(l)
    else:
        sys.stdout.write(out)

def cmd_evidence_at(rev, brief=False):
    """`check --evidence --at <rev>` (d-work #448, child C2 of #443): the evidence block of `<rev>`, computed by
    that tree's own runner in a detached worktree under the git common dir (`evidence_in_worktree`), never in the
    caller's checkout, whose files, HEAD and index stay as they were (#427: an evidence run in a shared checkout was
    invalid). stdout is the child's block exactly as `check --evidence` prints it there — `head=` names `<rev>`'s
    commit, `tree=` its tree, `dirty=no` — and the return code is the child's. The worktree is removed afterwards, on
    failure or interruption too. Like `--evidence` it never reads the suite memo (Rule-12 p2): the child is
    that command. A `<rev>` that names no commit is refused with one line, before anything is written. The
    child's stdout is captured (#476): printed byte for byte, or read short under `brief`, and its block stored."""
    env = dyadlib.git_env()
    sha = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "--end-of-options", f"{rev}^{{commit}}"],
                         cwd=REPO, env=env, capture_output=True, text=True).stdout.strip() if rev else ""
    if not sha:
        print(f"FAIL [evidence] --at {rev or '(missing)'}: not a commit in this repository")
        return 2
    try:
        child = evidence_in_worktree(sha, lambda wt: subprocess.run(   # a lambda: the spawn fence reads the enclosing function
            [sys.executable, str(wt / "dyad" / "scripts" / "package.py"), "check", "--evidence"], cwd=wt,
            env=evidence_env(), stdout=subprocess.PIPE, text=True))
    except RuntimeError as e:
        print(f"FAIL [evidence] --at {rev}: {e}")
        return 2
    evidence_at_print(child.stdout, brief)   # the child buffers its block anyway: nothing streams (#476)
    return child.returncode

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

def cmd_install(target, src=None):
    """The core craft's install: the same code path, with the core's hooks (templates, import line; p2).
    `prune=True` (#178): the core is one tree (CORE_ROOTS), so a file the new version dropped (a
    retired Rule, a relocated script) must not survive an upgrade — an unpruned stale file can
    resurrect a retired Rule for the frame guard and reintroduce a superseded test module (#178
    empirical finding: 23 stale files, `agent/frame` FAIL plus 28 test failures, replaying the
    pre-#160 -> current upgrade unpruned). Destination path resolution goes through the host
    adapter (#179), not a bare `.resolve()` call at the site."""
    target = hostadapter.resolve(target)
    tmp = tempfile.mkdtemp(prefix="dyad-install-") if src is not None else None
    try:
        # --from (#353): the source is a release archive or a tree, and everything the install reads about the
        # core — VERSION, the bundled crafts, the release roots, the workflow hooks — is read from *that* tree, so
        # the version installed is the version doing the describing; the default stays this checkout (REPO, PKG).
        root = distribute.source_tree(Path(src), tmp) if src is not None else REPO
        pkg = root / "dyad"
        if not (pkg / "VERSION").exists():
            print(f"refused: {src} holds no dyad/VERSION; not a core craft release or tree", file=sys.stderr); return 2
        bundled, roots, extra = bundled_crafts(pkg), release_roots(pkg), core_extra(root)
        ver, source = (pkg / "VERSION").read_text().strip(), distribute.source_name(Path(src) if src is not None else REPO)
        changed = distribute.install(Path(src) if src is not None and not Path(src).is_dir() else root, target, roots, prune=True, hooks=CORE_HOOKS, extra=extra)
        cc = craft_cli()
        rows = [(cc.CORE_NAME, ver, source)]                          # the core's registry row (Rule-11 p2, d-work #199)
        # and one per bundled craft (#228 for #201), but only where the installed tree is not already
        # recorded unmodified: `dyad craft install` of that same craft writes a richer row (its archive as
        # `source`, its d-work), and re-asserting this one would clobber it on the next core install — the
        # two commands would then ping-pong and neither install would be `0 changes` (Rule-11 p5).
        rows += [(c, cc.guard().version(root / "crafts" / c), source) for c in bundled if cc.unmodified(target, c) is None]
        changed += cc.record_install(target, rows)
        print(f"installed into {target}: {changed} changes" + (f"; bundled: {', '.join(bundled)}" if bundled else "")
              + (f"; from {source}" if src is not None else "") + f"; run: git -C {target} config core.hooksPath dyad/hooks")
        return 0
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)

def craft_cli():
    """scripts/craft.py, the craft registry's one reader and writer (Rule-11 p2)."""
    return dyadlib.load_module(PKG / "scripts" / "craft.py", "craft")

def cmd_craft(a):
    """Rule-11 p5: the Tended-craft CLI lives in scripts/craft.py; this is dispatch only (S4)."""
    return craft_cli().main(a)

def bundle_messages(msgs):
    """Print the bundle guard's messages as Rule-11's runner prints every guard's — a
    `warning:`-prefixed message is a warning, anything else a failure — and return the hard
    ones. `cmd_bundle` had printed every message as `FAIL` and refused the build on any of
    them, so #232's deliberate hold of two unreleased crafts (Rule-11 p7 permits an unreleased
    craft to have no row) made `bundle check` exit 1 and `bundle build` refuse: the release
    path was disabled by a warning (#241)."""
    hard = [m for m in msgs if not m.startswith("warning:")]
    for m in msgs:
        if m.startswith("warning:"):
            print(f"warn [bundle] {m.removeprefix('warning:').strip()}")
        else:
            print(f"FAIL [bundle] {m}", file=sys.stderr)
    return hard

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
        hard = bundle_messages(msgs)
        if not rows and not version:
            print("skip [bundle] no BUNDLE.md"); return 0
        if not hard:
            print(f"ok   [bundle] {len(rows)} components, v{version}")
        return 1 if hard else 0
    out_dir = Path(a[1]) if len(a) > 1 else Path(".")
    version, rows, msgs = bundle.check_bundle(REPO)
    if not rows:
        print("refused: no BUNDLE.md", file=sys.stderr); return 2
    if bundle_messages(msgs):
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

DWORK_VALUE_FLAGS = ("-d", "-r", "--prompt", "--prompt-file", "--said", "--said-file", "--relayed-via", "--state", "--craft", "--mandate", "--mirror", "-m")   # the last two: `--land` and `land` (#447)
DWORK_VERB_FLAGS = {   # what each verb reads; anything else is refused before a write, never silently dropped (#191)
    "new": ({"-d", "-r", "--prompt", "--prompt-file", "--said", "--said-file", "--relayed-via", "--mandate"}, {"--backlog"}, 3),
    "state": ({"-d", "-r", "--prompt", "--prompt-file", "--said", "--said-file", "--relayed-via", "--mandate"}, set(), 3),
    "retire": ({"-d", "--said", "--said-file"}, set(), None),   # #290: k ids, so the positional count is unbounded (None)
    "list": ({"--state", "--craft"}, set(), 1)}

def dwork_args(a):
    """`dwork` argv as (positionals, {flag: value}, {bare flags}). A flag's value is never a
    positional, whatever it spells — the position, not a second `index()` lookup, decides (#133)."""
    pos, vals, bare, i = [], {}, set(), 0
    while i < len(a):
        x = a[i]
        if x in DWORK_VALUE_FLAGS:
            if i + 1 >= len(a):
                sys.exit(f"refused: {x} needs a value")
            vals[x] = a[i + 1]; i += 2; continue
        if x.startswith("-") and len(x) > 1:
            bare.add(x)
        else:
            pos.append(x)
        i += 1
    return pos, vals, bare

def words(vals, flag):
    """The Operator's words for `--<flag>` / `--<flag>-file`, or None. A file is read as UTF-8 with its
    line endings kept (`newline=""`), and only one final line ending is dropped. Both given is refused:
    one entry, one source."""
    inline, path = vals.get(f"--{flag}"), vals.get(f"--{flag}-file")
    if inline is not None and path is not None:
        sys.exit(f"refused: give --{flag} or --{flag}-file, not both")
    if path is not None:
        try:
            with open(path, encoding="utf-8", newline="") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            sys.exit(f"refused: --{flag}-file {path}: {e}")
        for end in ("\r\n", "\n", "\r"):
            if text.endswith(end):
                return text[:-len(end)]
        return text
    return inline

def fence_for(kind, text):
    """The fence a record entry holds `text` in, or a refusal. `provenance.parse` opens and closes a
    fence only at column 0, so a column-0 ``` or ~~~ in the text is what rules a fence out; an
    indented one is data. Text that opens column-0 lines with both, or holds nothing, is refused."""
    if not text.strip():
        sys.exit(f"refused: an empty {kind} (Rule-7 property 1: a fenced body)")
    starts = {l[:3] for l in text.splitlines()}
    fence = next((f for f in ("```", "~~~") if f not in starts), None)
    if fence is None:
        sys.exit(f"refused: the {kind} opens lines with both ``` and ~~~; no fence can hold it as data")
    return fence

def append_provenance(rid, entries, today, fresh=False):
    """Append entries [(kind, text, note)] to `<instance>/d-work/provenance/<rid>.md` (Rule-7 property
    1), creating the record when absent. Every entry's fence is chosen before this is called; with
    `fresh` an existing record for a newly allocated id is refused — it would be another row's words."""
    import dyadlib
    pv = dyadlib.load_guard("agent", "provenance")
    path = pv.store(REPO) / f"{rid}.md"
    if fresh and path.exists():
        sys.exit(f"refused: {path} already exists for the new id #{rid}; it holds words no row owns — resolve it first")
    head = path.read_text(encoding="utf-8") if path.is_file() else f"# Provenance #{rid}\n" + (
        f"\nsession: {os.environ['DYAD_SESSION']}\n" if os.environ.get("DYAD_SESSION") else "")
    n, body = len(pv.parse(head)), head.rstrip("\n") + "\n"
    for kind, text, note in entries:
        n += 1; fence = fence_for(kind, text)
        body += f"\n## {n} {kind} {today}{' ' + note if note else ''}\n\n{fence}\n{text}\n{fence}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path

def mandate_words(rows, raw, kind="Y plan"):
    """The mandate's own words and the date they were given: the *last* `disposition` entry of
    `<instance>/d-work/provenance/<id>.md` whose note holds `kind` — `Y plan` for the authorization an accreted
    row is born under (`dwork new --mandate`, d-work #290), `Y done` for the Done-`Y` it closes on (`dwork state
    <id> done --mandate`, d-work #422) — last, because a re-plan or a re-asked Done supersedes an earlier one
    and the live one is what an accreted row stands on. Every refusal is made here, before anything is
    written: a target that is no row, one whose `disposed` holds no `kind` (for `Y plan`, the same substring
    test the plan gate makes, `guards/agent/prs.py`; its unreliability on free text is inherited, and named in
    plan #290), and one whose record holds no such entry — there being then no Operator words to copy, which
    Rule-7 property 4 requires and property 3 forbids inventing later."""
    if not raw.isdigit():
        sys.exit(f"refused: --mandate {raw!r} is not a number")
    mid = int(raw)
    row = rows.get(mid)
    if row is None:
        sys.exit(f"refused: --mandate #{mid} is no row; a mandate stands on a d-work this ledger holds")
    if kind not in row.disposed:
        sys.exit(f"refused: --mandate #{mid} carries no '{kind}' disposition, so " + (
            "no mandate stands on it (Rule-3 plan gate)" if kind == "Y plan" else
            "the mandate has no Done-`Y` for an accreted row to close on (Rule-3 Completion: its Done rides the mandate's)"))
    import dyadlib
    pv = dyadlib.load_guard("agent", "provenance")
    path = pv.store(REPO) / f"{mid}.md"
    es = pv.parse(path.read_text(encoding="utf-8")) if path.is_file() else []
    cands = [e for e in es if e["kind"] == "disposition" and kind in e["note"]]
    if not cands:
        sys.exit(f"refused: #{mid}'s record holds no `disposition` entry noted '{kind}'; there are no Operator "
                 f"words to copy, and Rule-7 property 3 forbids writing them now")
    return mid, cands[-1]["text"], cands[-1]["date"]

def landing_refusal(rg, done_entries):
    """The closing act's landing test (#202), the fence's `rows.landing_problems` said earlier: every head the
    operative (last) `Y done` entry names must be an ancestor of `origin/main`, `main` or `HEAD`, whichever
    resolve here; a head this clone cannot resolve prints one warning and is not checked. Returns the refusal
    text, or None. A function of its own so its locals cannot reach the verb that calls it: inlined in
    `cmd_dwork`, its branch list was bound to the name `refs`, which the close then wrote into the row as
    `['origin/main', 'main', 'HEAD']` — 28 rows between 2026-10-15 and 2026-10-25 (#439)."""
    for e in done_entries[-1:]:     # the operative record only (rows.landing_problems' own rule)
        for sha in rg.HEAD_AT.findall(e):
            try:
                subprocess.check_output(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=REPO, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                print(f"warning: head {sha}, which {e!r} names, is unknown in this clone: not checked (#202)", file=sys.stderr); continue
            branches = [b for b in ("origin/main", "main", "HEAD")
                        if subprocess.run(["git", "rev-parse", "--verify", "-q", b], cwd=REPO, capture_output=True).returncode == 0]
            if all(subprocess.run(["git", "merge-base", "--is-ancestor", sha, b], cwd=REPO, capture_output=True).returncode for b in branches):
                return (f"refused: head {sha}, which {e!r} names, is on none of {' '.join(branches)}: the "
                        f"merge that `Y` ratified has not landed (Rule-3 Completion, #202). Merge it, "
                        f"or ask the Done again on the head that did land — the later entry governs")
    return None

def trace_refusal(rg, rid, d):
    """The fence's `rows.trace_problems` said before the first write (#465): under `dwork-trace: always` a `Y done`
    entry — a mandate close excepted, whose note holds `mandate #` — is recorded only with
    `<instance>/d-work/traces/<id>.md` already in this work tree, so the commit that records it can carry it
    (Rule-3 Completion). Returns the refusal text, or None."""
    import dyadlib
    if d is None or not rg.DONE_Y.match(f"2000-01-01 {d}") or "mandate #" in d:
        return None
    if dyadlib.preference(rg.TRACE_KEY, REPO) != rg.TRACE_ALWAYS:
        return None
    tp = dyadlib.instance(REPO) / "d-work" / "traces" / f"{rid}.md"
    if tp.is_file():
        return None
    rel = tp.relative_to(REPO).as_posix() if tp.is_relative_to(REPO) else str(tp)
    return (f"refused: a `Y done` entry is recorded with its trace under `dwork-trace: always` (Rule-3 Completion: "
            f"the Done record commit carries it, #465), and {rel} does not exist; write it first: "
            f"dyad dwork trace {rid} --out, and re-run; under --land the trace rides the same commit: "
            f"`dyad dwork batch <file> --land` with a `land {rel}` line before this line")

def cmd_dwork(a):
    sys.path.insert(0, str(PKG / "scripts")); import dyadlib, datetime
    if a and a[0] == "trace":   # #213: read-only, its own flags; loaded by path (`trace` is also a stdlib module's name)
        return dyadlib.load_module(PKG / "scripts" / "trace.py", "dyad_trace").main(a[1:])
    pos, _, bare = dwork_args(a)
    if (pos and pos[0] in ("land", "batch")) or "--land" in bare:
        # #447 (child C1 of plan #443): the verb run, committed and pushed from the tool-owned worktree in one call;
        # scripts/land.py runs the worktree's own `dyad dwork`, so this checkout is never written or reset.
        # #459: `batch <file>|- --land` lands several such lines in one commit and one push
        return dyadlib.load_module(PKG / "scripts" / "land.py", "land").main(a, REPO, DWORK_VALUE_FLAGS, dwork_args, words)
    try:
        dyadlib.check_invariants(dyadlib, label="dyadlib")   # a broken transition table must not write a row (syseng invariants.md p1)
    except dyadlib.InvariantError as e:
        sys.exit(f"refused: {e}")
    rows = {r.id: r for r in dyadlib.read_rows(REPO)}
    today = datetime.date.today().isoformat()
    pos, vals, bare = dwork_args(a)
    verb = pos[0] if pos else None
    if verb in DWORK_VERB_FLAGS:
        takes, flags, most = DWORK_VERB_FLAGS[verb]
        extra = sorted((set(vals) - takes) | (bare - flags))
        if extra:
            sys.exit(f"refused: dwork {verb} does not take {' '.join(extra)}")
        if most is not None and len(pos) > most:   # #290: `retire` declares None — k ids, an unbounded count
            sys.exit(f"refused: dwork {verb}: unexpected argument(s) {' '.join(pos[most:])!r}")
    d = vals.get("-d")
    if d is not None and ";" in d:
        # d-work #133: `;` joins `disposed` entries (Rule-3 Ledger); inside the text it splits one
        # disposition in two (#67, #100). The Operator's words go verbatim to provenance (Rule-7).
        sys.exit("refused: -d text contains ';', which separates disposed entries; use ',' or '—'")
    for flag in ("-d", "-r", "--relayed-via"):
        if any(c in vals.get(flag, "") for c in "\r\n"):
            # #191: -d lands unfenced in the row and in a record heading, where a line break forges structure
            sys.exit(f"refused: {flag} text holds a line break; it is one line of a row or a heading")
    given_refs = [vals["-r"]] if "-r" in vals else []
    if verb == "new" and len(pos) > 2:
        given_refs.append(pos[2])
    refused = dyadlib.load_guard("agent", "rows").REFS_REFUSED if given_refs else ""
    if any(c in v for v in given_refs for c in refused):
        # #439: refs is space-separated tokens (`7 parent #3 PR #9`); a bracket, a quote or a comma is the shape of a
        # Python list written into the row — the fence's `rows.refs_shape_problems` clause, said where it costs a line
        sys.exit(f"refused: refs holds one of {' '.join(refused)}; write space-separated tokens, e.g. '7 parent #3 PR #9'")
    prompt, said = words(vals, "prompt"), words(vals, "said")
    if d is not None and said is None:
        # d-work #191: a disposition written to the row without its words is property 5's gap at birth
        sys.exit("refused: -d records a disposition; give its words verbatim with --said or --said-file (Rule-7)")
    if said is not None and d is None:
        sys.exit("refused: --said records a disposition's words; name it in the row with -d (Rule-3 Ledger)")
    if "--relayed-via" in vals and prompt is None and said is None:
        sys.exit("refused: --relayed-via notes the Operator's words relayed from another seat (Rule-7 property 4); "
                 "give them with --prompt[-file] or --said[-file]")
    # #422: a relayed disposition is still the Operator's words; its note says where it was given, so the
    # attendance reading (`sessions.own_disposition`) does not count it as given in this seat.
    relayed = f"relayed via {vals['--relayed-via']}" if "--relayed-via" in vals else ""
    dnote = f"{d}, {relayed}" if relayed and d else (d or relayed)
    entries = ([("prompt", prompt, relayed)] if prompt is not None else []) + ([("disposition", said, dnote)] if said is not None else [])
    for kind, text, _ in entries:
        fence_for(kind, text)                  # every refusal before the first write (#191): nothing half-written
    if verb == "new" and len(pos) >= 2:
        title = pos[1]
        if a[0] != "new" or title.startswith("-"):
            # d-work #133: the title is the first argument after `new`; a flag there became rows #129-#134's title
            sys.exit(f"refused: usage: dwork new <title> [refs] [--backlog] [-d text] (--prompt[-file] … | --said[-file] …), the verb first")
        backlog = "--backlog" in bare
        mandate, mode = vals.get("--mandate"), dyadlib.DEFAULT_MODE
        if mandate is not None:
            # #290: implicit mode. The row takes no disposition of its own — its one entry is the mandate's,
            # and its record's entry 1 is the mandate's own words, copied with a note that discloses that they
            # predate the row (Rule-7 property 4, parallel to the relayed prompt already there).
            if backlog or d is not None or prompt is not None or said is not None:
                sys.exit("refused: --mandate carries the mandate's own disposition (implicit mode, Rule-3); "
                         "it takes no -d, --said, --prompt or --backlog — a row born backlog carries no PR "
                         "and moves only on the Operator's prompt")
            mid, mwords, mdate = mandate_words(rows, mandate)
            fence_for("disposition", mwords)
            entries, mode = [("disposition", mwords, f"mandate #{mid}, {mdate}")], "implicit"
        if backlog and d is None:
            sys.exit("refused: --backlog opens a row by disposition (Rule-3); give -d and --said")
        if not entries:
            sys.exit("refused: a row is opened by the Operator's words; give --prompt[-file] or -d with --said[-file] (Rule-7, #191)")
        try:
            subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=REPO, check=False, timeout=30)
            remote = {r.id for r in dyadlib.read_rows(REPO, at="origin/main")}
        except Exception as e:
            print(f"warning: could not read origin/main's rows ({e}); allocating from local ids "
                  f"only — a concurrent session's unpushed id may collide (d-work #32 F3)", file=sys.stderr)
            remote = set()
        rid = max(set(rows) | remote, default=0) + 1
        state = "backlog" if backlog else "open"          # d-work #140: dyadlib.NEW_STATES
        disposed = f"{today} {d}" if d is not None else ""
        if len(pos) > 2 and "-r" in vals:
            sys.exit("refused: refs given twice, as an argument and with -r")
        refs = vals.get("-r", pos[2] if len(pos) > 2 else "")
        if mandate is not None:
            disposed = f"{today} Y plan (mandate #{mid})"
            refs = refs or f"parent #{mid}"   # the mandate is the row's parent; `row.refs->row` resolves it (Rule-20)
        refusal = trace_refusal(dyadlib.load_guard("agent", "rows"), rid, d) if mandate is None else None
        if refusal:   # #465: a row born with a `Y done` carries its trace as any other record does
            sys.exit(refusal)
        r = dyadlib.Row(rid, title, today, state, disposed, refs, mode)
        try:   # the transition check (dyadlib.require_transition, #203) runs before either write
            dyadlib.write_row(REPO, r, None, first=lambda: append_provenance(rid, entries, today, fresh=True))
        except dyadlib.TransitionError as e:
            sys.exit(f"refused: {e}")
        print(f"{rid}"); return 0
    if verb == "state" and len(pos) >= 3:
        if not pos[1].isdigit():
            sys.exit(f"refused: id {pos[1]!r} is not a number")
        rid, state = int(pos[1]), pos[2]
        if rid not in rows: sys.exit(f"no row {rid}")
        r = rows[rid]; disposed, refs = r.disposed, r.refs
        if "--mandate" in vals:
            # #422: the close form of an accreted row (Rule-3 Scope: its Done rides the mandate's Done-`Y`). The row's
            # entry and its record's entry are both composed here, as `dwork new --mandate` composes entry 1: the
            # mandate's own Done-`Y` words, noted `mandate #<id>, <the mandate's own date>` (Rule-7 property 4), so
            # the attendance reading never counts them as a disposition given in this row's seat (#421).
            if state != "done":
                sys.exit("refused: --mandate closes an accreted row on its mandate's Done-`Y`; the state is `done`")
            if d is not None or said is not None or prompt is not None or "--relayed-via" in vals:
                sys.exit("refused: --mandate carries the mandate's own Done-`Y` (implicit mode, Rule-3); "
                         "it takes no -d, --said, --prompt or --relayed-via")
            mid, mwords, mdate = mandate_words(rows, vals["--mandate"], "Y done")
            if mid == rid:
                sys.exit(f"refused: #{rid} cannot be its own mandate")
            if not (re.search(rf"\bparent #{mid}\b", refs) or f"(mandate #{mid})" in disposed):
                sys.exit(f"refused: #{rid} is not accreted under #{mid}: its refs name no `parent #{mid}` and its "
                         f"`disposed` no `Y plan (mandate #{mid})` (Rule-3 Scope)")
            fence_for("disposition", mwords)
            d = f"Y done (mandate #{mid}, {mdate})"
            entries = [("disposition", mwords, f"mandate #{mid}, {mdate}")]
        if r.state == "backlog" and state == "open" and prompt is None:
            sys.exit(f"refused: a backlog row opens on the Operator's prompt (Rule-3); give its words with --prompt[-file] (Rule-7)")
        # #202: the Done state follows the merge. Every refusal here precedes the first write (Rule-7 p3),
        # and each is the fence's own clause said earlier, where it costs a line instead of a push.
        rg = dyadlib.load_guard("agent", "rows")
        if d is not None and rg.DONE_MERGES.search(f"{today} {d}"):
            heads, prs = rg.HEAD_AT.findall(d), re.findall(r"#(\d+)", d.split("merge", 1)[1] if "merge" in d else "")
            if len(heads) < max(1, len(prs)):
                sys.exit(f"refused: a `Y done` that ratifies a merge names each PR and the head its `Y` was "
                         f"given on — -d 'Y done (merges PR #n at <head-n>)' (Rule-3 Completion, #202): "
                         f"{len(prs) or 1} named, {len(heads)} head(s) given, and the fence tests every one "
                         f"of them before the row may reach done")
            if state == "done":
                sys.exit("refused: the state follows the merge (Rule-3 Completion, #202). Record this entry "
                         f"with the state unchanged (`dwork state {rid} {r.state} -d …`), merge, then "
                         f"`dwork state {rid} done`")
        refusal = trace_refusal(rg, rid, d)   # #465: a `--mandate` close writes `Y done (mandate #…)`, exempt
        if refusal:
            sys.exit(refusal)
        if state == "done" and r.state != "done":
            done_entries = [e for e in rg.entries(disposed) + ([f"{today} {d}"] if d else []) if rg.DONE_Y.search(e)]
            if not done_entries:
                sys.exit(f"refused: row {rid} carries no `Y done` entry, so there is no Done-`Y` for this "
                         f"state to execute (Rule-3 Completion: only the Operator closes a d-work)")
            refusal = landing_refusal(rg, done_entries)
            if refusal:
                sys.exit(refusal)
        if d is not None: disposed = (disposed + "; " if disposed else "") + f"{today} " + d
        if "-r" in vals: refs = vals["-r"]
        new = dyadlib.Row(r.id, r.title, r.opened, state, disposed, refs, r.mode)   # #290: `mode` is carried, never rewritten
        try:   # an unknown state or a transition outside Rule-16's table is refused here, before either write (#203)
            dyadlib.write_row(REPO, new, r.state, first=(lambda: append_provenance(rid, entries, today)) if entries else None)
        except dyadlib.TransitionError as e:
            sys.exit(str(e))
        print(f"{rid}: {state}"); return 0
    if verb == "retire":
        # #290: the retirement form. `archived` is the board's one terminal exit and had been used 0 times in
        # 280 rows, because the table gave `backlog` only `open`: 75 rows could not be retired without being
        # worked. One Operator question (`Y/N: archive #a, #b, … #k?`) stands behind one call, so the k rows
        # get one disposition — its words written into every named row's record, as Rule-3's batch clause
        # already prescribes for a plan or a Done batch — and the batch suffix is composed from the ids named
        # rather than typed k times (the error this instance has made four times: `;` in the entry text).
        ids = pos[1:]
        if not ids:
            sys.exit("refused: usage: dwork retire <id>... -d text --said[-file] <s>")
        if d is None or said is None:
            sys.exit("refused: dwork retire records one Operator disposition over the rows it names; give "
                     "-d and --said[-file] (Rule-3 Batch disposition, Rule-7)")
        if "(batch" in d:
            sys.exit("refused: -d carries a batch note; dwork retire composes `(batch #a,#b,#c)` from the ids named")
        seen, targets = set(), []
        for x in ids:
            if not x.isdigit():
                sys.exit(f"refused: id {x!r} is not a number")
            rid = int(x)
            if rid in seen:
                sys.exit(f"refused: id #{rid} named twice; one disposition writes one entry into one row")
            seen.add(rid)
            if rid not in rows:
                sys.exit(f"refused: no row {rid}")
            src = rows[rid].state
            if "archived" not in dyadlib.TRANSITIONS.get(src, frozenset()):
                # the table decides what may be archived (Rule-16), read as data so adding a source state needs
                # no edit here. Membership, not `require_transition`: that allows a same-state edit, and an
                # already-`archived` row must not collect a second retirement entry.
                sys.exit(f"refused: #{rid} is {src}; dwork retire archives a row from "
                         f"{' or '.join(sorted(s for s, t in dyadlib.TRANSITIONS.items() if 'archived' in t))} (Rule-16)")
            targets.append(rows[rid])
        note = d if len(targets) == 1 else f"{d} (batch {','.join(f'#{t.id}' for t in targets)})"
        fence_for("disposition", said)
        for t in targets:
            new = dyadlib.Row(t.id, t.title, t.opened, "archived",
                              (t.disposed + "; " if t.disposed else "") + f"{today} {note}", t.refs, t.mode)
            dyadlib.write_row(REPO, new, t.state,
                              first=lambda rid=t.id: append_provenance(rid, [("disposition", said, note)], today))
        print(f"archived {' '.join(f'#{t.id}' for t in targets)}"); return 0
    if verb == "list":
        state, craft = vals.get("--state"), vals.get("--craft")
        if state is not None and state not in dyadlib.STATES:
            sys.exit(f"no such state {state!r}; states: {' '.join(sorted(dyadlib.STATES))}")
        out = [r for r in sorted(rows.values(), key=lambda r: r.id)
               if (state is None or r.state == state) and (craft is None or craft in r.refs.split())]
        for r in out:
            print(f"#{r.id} [{r.state}] {r.title}")
        return 0
    sys.exit(__doc__)

# Projector registry (crafts/sysarch/rules/projection.md p4; #160): discovered over the core craft's own
# dyad/scripts/project_<surface>.py (keyed `dyad-operator/<surface>`, #378) and every
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
    """{craft/surface: (craft, repo-relative module path)}: one entry per craft's own projector file, the core craft's
    under its own name (`dyadlib.projector_craft`)."""
    return {f"{dyadlib.projector_craft(py, PKG)}/{py.stem.removeprefix('project_')}": (dyadlib.projector_craft(py, PKG), str(py.relative_to(REPO)))
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

def cmd_release(a):
    """Rule-11 Ratification events: the release service lives in scripts/release.py (d-work #470, moved in from
    `.github/released.py`); this is dispatch only (S4)."""
    return dyadlib.load_module(PKG / "scripts" / "release.py", "release").main(a, REPO)

def cmd_bootstrap(a):
    """The seat bootstrap lives in scripts/bootstrap.py (d-work #474); this is dispatch only (S4)."""
    return dyadlib.load_module(PKG / "scripts" / "bootstrap.py", "bootstrap").main(a, REPO)

def cmd_session(a):
    """Rule-16: the session-presence CLI lives at guards/agent/sessions.py (it is also the
    guard); this is dispatch only (S4, d-work #185)."""
    sys.path.insert(0, str(PKG / "scripts")); import dyadlib
    return dyadlib.load_guard("agent", "sessions").main(a)

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding (#203)

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
    if a and a[0] == "release":
        sys.exit(cmd_release(a[1:]))
    if a and a[0] == "bootstrap":
        sys.exit(cmd_bootstrap(a[1:]))
    if a and a[0] == "ledger":
        sys.exit(cmd_ledger())
    if a and a[0] == "dwork":
        sys.exit(cmd_dwork(a[1:]))
    if a and a[0] == "project":
        sys.exit(cmd_project(a[1:]))
    if not a or a[0] not in ("check", "build", "install"):
        sys.exit(__doc__)
    if a[0] == "check" and "--evidence" in a:
        if "--show" in a:                                                # check --evidence --show <sha256> (#476)
            i = a.index("--show"); sys.exit(cmd_evidence_show(a[i + 1] if i + 1 < len(a) else None))
        brief = "--brief" in a                                           # check --evidence --brief (#476)
        if "--at" in a:                                                  # check --evidence --at <rev> (#448)
            i = a.index("--at"); sys.exit(cmd_evidence_at(a[i + 1] if i + 1 < len(a) else None, brief=brief))
        sys.exit(cmd_evidence(brief=brief))
    if a[0] == "check" and "--pr" in a:
        i = a.index("--pr"); sys.exit(cmd_pr(*a[i + 1:i + 3]))
    if a[0] == "check" and "--guards" in a:
        sys.exit(cmd_guards(pre_push="--pre-push" in a))
    if a[0] == "check" and "--list" in a:
        sys.exit(cmd_list())
    if a[0] == "check" and "--tests" in a:
        i = a.index("--tests"); sys.exit(cmd_tests(*a[i + 1:i + 2]))
    if a[0] == "install" and "--from" in a:                              # dyad install <repo> --from <src> (#353)
        i = a.index("--from"); rest = a[1:i] + a[i + 2:]
        sys.exit(cmd_install(rest[0], a[i + 1]) if rest and i + 1 < len(a) else __doc__)
    sys.exit({"check": lambda: cmd_check(), "build": lambda: cmd_build(*a[1:2]), "install": lambda: cmd_install(*a[1:2])}[a[0]]())
