"""dyad host adapter (`crafts/syseng/rules/host-facts.md`, d-work #179): the one place a host fact
is read, so every call site sees the same answer regardless of which one asked. Rule-14 ("Library
and The World"): The World is observed, not pinned — a host's own filesystem layout (macOS's `/var`
-> `/private/var`) is such an observation, not a thing the package controls or should special-case
per call site. A library: no check semantics of its own (S4); its own check is
`dyad/tests/test_hostadapter.py` (`crafts/syseng/rules/verifiable-code.md` p4's mapping). Kernel:
Python 3.12+; stdlib only (Rule-14: no new manifest row — `hostadapter` resolves as a
package-internal import, `dyad/guards/infra/manifest.py`'s `python_imports`).

Two functions, not a framework (`host-facts.md` property 2): `resolve` wraps `Path.resolve()` so
`distribute.py`/`package.py` never call it inline (G5, d-work #179: a test once compared an
unresolved path against `distribute.install`'s already-resolved one, passing only by the accident
that this kernel's `/tmp` is not itself a symlink). `ignore_patterns` derives the Rule-11 property 6
`generated:` list of `package_rules.txt` — never a second, hand-kept copy of it — translated to
gitignore syntax, and `write_gitignore` seeds it once (G9: a fresh install's first `dyad` command
writes `dyad/scripts/__pycache__/`, and `git add -A` then tracks it). A third host fact either fits
one of these two functions or earns its own, justified in the plan that adds it — never a generic
hook (`host-facts.md` property 2). Two more, each justified in plan #336 revision 7: `supervisor` —
which service manager keeps a per-user daemon alive on this host (`systemd` on Linux with a working
`systemctl --user`, `launchd` on macOS, else `proc`, a detached process that says it is not persistent)
— and `state_dir` — where a per-user service keeps its state (`$XDG_STATE_HOME/dyad/<name>`, default
`~/.local/state/dyad/<name>`, on Linux; `~/Library/Application Support/dyad/<name>` on macOS). Both are
facts of The World, observed once here; every call site sees the same answer. Each takes its inputs as
arguments (the platform, the environment, the probe) so a test exercises every branch without the host.
No `DYAD_*` variable is read here (the naming table's `env:` line is unchanged)."""
import os, platform, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

HEADER = "# seeded by dyad install (hostadapter.write_gitignore) from dyad/scripts/package_rules.txt\n"
SUPERVISORS = ("systemd", "launchd", "proc")             # what `supervisor()` answers; the adapters are ledgerd's (dyad/server/ledgerd/ledgerd/supervisor.py)
STATE_HOME_VAR = "XDG_STATE_HOME"                        # the XDG base directory for state (Linux); not a DYAD_ variable
STATE_SUBDIR = "dyad"                                    # `<state home>/dyad/<name>`
INVARIANTS: list[dyadlib.Invariant] = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("supervisors-are-three-distinct", lambda: len(set(SUPERVISORS)) == 3 and SUPERVISORS[-1] == "proc"),
    ("state-home-is-not-a-dyad-variable", lambda: not STATE_HOME_VAR.startswith("DYAD_") and bool(STATE_SUBDIR)),
]


def resolve(path) -> Path:
    """The one place a host path is resolved to its canonical, symlink-free form. Every
    install/build destination and repo-root comparison `distribute.py`/`package.py` make calls
    this instead of `Path(...).resolve()` inline — grepping the two files for `.resolve()` after
    this change finds only the bootstrap `PKG = Path(__file__).resolve().parent.parent` lines,
    which must run before this module can even be imported (`craft.py`'s own such line is the
    third; it has no other `.resolve()` call to route)."""
    return Path(path).resolve()


def _to_gitignore(pattern: str) -> str:
    """One `package_rules.txt` `generated:` pattern (matched by `check_generated` at any path
    depth, component-wise — the whole path, any one segment, or any suffix starting at a segment)
    as one gitignore line matching at the same depths: a `dir/*` pattern becomes `dir/` — a
    trailing-only slash is unanchored under gitignore's own rule ("a separator at the beginning or
    middle" anchors; one only at the end does not), so it matches a directory named `dir` at any
    depth. A literal `dir/*` would not: gitignore anchors a *middle* slash to the `.gitignore`
    file's own directory, so a naive translation would miss a nested `dyad/scripts/__pycache__/`
    (G9's exact case) and only catch a root-level one. Any other pattern with an interior slash
    (`ops/*.log`) is prefixed `**/` for the same any-depth match. A slash-free pattern (`*.pyc`,
    `LEDGER.md`) is already unanchored and needs no change."""
    if pattern.endswith("/*"):
        return pattern[:-1]
    return f"**/{pattern}" if "/" in pattern else pattern


def ignore_patterns(root) -> list[str]:
    """Rule-11 property 6's `generated:` patterns, translated by `_to_gitignore`; parsed straight
    from `<root>/dyad/scripts/package_rules.txt` — the same file `check_generated` reads — so the
    list can never drift from it (never hand-duplicated here). Sorted, deduplicated; `[]` when that
    file is not (yet) part of the tree at `root` (a Tended-craft-only root; a fixture without a
    core craft)."""
    p = Path(root) / "dyad" / "scripts" / "package_rules.txt"
    if not p.is_file():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kind, _, val = line.partition(":")
        if kind.strip() == "generated":
            out.append(_to_gitignore(val.strip()))
    return sorted(set(out))


def write_gitignore(dest) -> bool:
    """Seed `<dest>/.gitignore` from `ignore_patterns(dest)` when the file is absent. Never
    overwrites — idempotent (`crafts/syseng/rules/idempotence.md` property 1) and consistent with
    Rule-11 property 2, "never overwrites a host file". `True` when it wrote, so a caller can count
    it as one change the way `distribute.install`'s other hooks already do."""
    dest = Path(dest)
    f = dest / ".gitignore"
    if f.exists():
        return False
    patterns = ignore_patterns(dest)
    if not patterns:
        return False
    f.write_text(HEADER + "\n".join(patterns) + "\n")
    return True


def supervisor(system: str | None = None, which=shutil.which, run=subprocess.run) -> str:
    """The service manager that keeps a per-user daemon alive here: `launchd` on Darwin; `systemd` on a host
    where `systemctl --user` answers (a container whose PID 1 is not systemd has the binary and no user
    manager, so the probe runs it rather than looking for it); else `proc`. `system`, `which` and `run` are
    injectable so every branch is tested without the host."""
    system = system or platform.system()
    if system == "Darwin":
        return "launchd"
    if system == "Linux" and which("systemctl"):
        try:
            r = run(["systemctl", "--user", "show", "--property=Version"], capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return "systemd"
        except (OSError, subprocess.SubprocessError):
            pass
    return "proc"


def state_dir(name: str, system: str | None = None, env=None, home: Path | None = None) -> Path:
    """Where the per-user service `name` keeps its state: `$XDG_STATE_HOME/dyad/<name>` (default
    `~/.local/state/dyad/<name>`) on Linux and anything else; `~/Library/Application Support/dyad/<name>`
    on Darwin. Never created here."""
    system = system or platform.system()
    env = os.environ if env is None else env
    home = Path(home) if home is not None else Path.home()
    if system == "Darwin":
        return home / "Library" / "Application Support" / STATE_SUBDIR / name
    base = env.get(STATE_HOME_VAR) or ""
    return (Path(base) if base else home / ".local" / "state") / STATE_SUBDIR / name


dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding
