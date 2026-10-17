"""ledgerd: the store-adapter seam (crafts/syseng/rules/invariants.md). Kernel: Python 3.12+, stdlib + git.
A store adapter answers two questions about a ledger: what is its latest **pin** — an opaque string that
changes if and only if the ledger's content changed — and give me the ledger's files at that pin as a
**tree** on disk. The daemon performs one operation on a pin: equality. An adapter is a module meeting
STORE_CONTRACT (`SCHEME`, `open(url, state, paths) -> store`); the store object meets STORE_OBJECT
(`pin()`, `tree(pin, paths) -> Path`, `describe()`). Shipped: `git` (`git+https://…`, `git+ssh://…`,
`git+file:///…`, `#<ref>` default `main`: a mirror clone under `<state>/repo.git`, `git fetch` per pin,
pin = `rev-parse <ref>`, tree = `git archive <sha> -- <paths>` extracted (stdlib tarfile) into a temporary directory —
never a working tree; when `<state>/credentials` exists every git call carries
`-c credential.helper="store --file <state>/credentials"`, so a token never appears on a command line);
`dir` (`file:///…` or a bare path: the directory as it is; pin = sha256 over the sorted relative paths and
contents under the schema's STORES; tree = the directory itself — the in-process fallback, honest about
its pin); `module:<path>` (any Python file meeting the contract, loaded by path — the seam for any other
store; nothing else is written for it here). Nothing here knows what a d-work is.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("store.py: Python 3.12+ required")
import hashlib, io, shutil, subprocess, tarfile, tempfile
from pathlib import Path
COMPONENT = Path(__file__).resolve().parents[1]
for _p in (str(COMPONENT), str(COMPONENT.parents[1] / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dyadlib

STORE_CONTRACT = ("SCHEME", "open")                      # a store adapter module
STORE_OBJECT = ("pin", "tree", "describe")               # what `open` returns
SCHEMES = ("git", "dir")                                  # the adapters shipped here, by SCHEME
GIT_PREFIX = "git+"
FILE_PREFIX = "file://"
MODULE_PREFIX = "module:"
DEFAULT_REF = "main"
CLONE_DIR = "repo.git"                                    # `<state>/repo.git`, the mirror clone
CREDENTIALS = "credentials"                               # `<state>/credentials`, git credential-store form, 0600 (auth.py writes it)
GIT_TIMEOUT = 600

INVARIANTS: list[dyadlib.Invariant] = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("contract-names-distinct", lambda: len(set(STORE_CONTRACT)) == len(STORE_CONTRACT) and len(set(STORE_OBJECT)) == len(STORE_OBJECT)),
    ("object-has-pin-tree-describe", lambda: set(STORE_OBJECT) == {"pin", "tree", "describe"}),
    ("schemes-distinct", lambda: len(set(SCHEMES)) == len(SCHEMES)),
    ("prefixes-distinct", lambda: len({GIT_PREFIX, FILE_PREFIX, MODULE_PREFIX}) == 3),
    ("clone-dir-is-bare-named", lambda: CLONE_DIR.endswith(".git")),
]

def store_problem(mod) -> str | None:
    """None when `mod` is a store adapter; else the problem (the shape of dyadlib.contract_problem)."""
    missing = [n for n in STORE_CONTRACT if not hasattr(mod, n)]
    if missing:
        return f"lacks {', '.join(missing)} (store adapter contract, dyad/server/ledgerd/README.md)"
    if not isinstance(mod.SCHEME, str) or not mod.SCHEME:
        return "SCHEME must be a non-empty string"
    if not callable(mod.open):
        return "open is not callable"
    return None

def object_problem(obj) -> str | None:
    missing = [n for n in STORE_OBJECT if not callable(getattr(obj, n, None))]
    return f"store object lacks {', '.join(missing)}" if missing else None

# ---- git
def git_argv(state: Path | None) -> list[str]:
    """`git`, with the credential helper when `<state>/credentials` exists: the token stays in the file,
    never on a command line or in `ps`; a public repository fetches anonymously without it."""
    argv = ["git"]
    if state is not None and (Path(state) / CREDENTIALS).is_file():
        argv += ["-c", f"credential.helper=store --file {Path(state) / CREDENTIALS}"]
    return argv

def _git(argv: list[str], cwd: Path | None, timeout: int = GIT_TIMEOUT) -> str:
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, env=dyadlib.git_env(), timeout=timeout)
    if r.returncode:
        raise RuntimeError(f"{' '.join(argv[:3])}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else f'exit {r.returncode}'}")
    return r.stdout

def split_git_url(url: str) -> tuple[str, str]:
    """`git+<url>[#<ref>]` -> (url, ref); a bare `<url>` is accepted too (the prefix only selects the adapter)."""
    u = url[len(GIT_PREFIX):] if url.startswith(GIT_PREFIX) else url
    u, _, ref = u.partition("#")
    return u, (ref or DEFAULT_REF)

class GitStore:
    """A git repository as a store: a mirror clone the daemon owns (`<state>/repo.git`), or — `local` —
    an existing repository read in place with no clone and no fetch (the client's `--at <sha>`)."""
    SCHEME = "git"
    def __init__(self, url: str, ref: str, repo: Path, state: Path | None, fetch: bool):
        self.url, self.ref, self.repo, self.state, self.fetch = url, ref, Path(repo), (Path(state) if state else None), fetch
    @classmethod
    def open(cls, url: str, state: Path, paths=()):
        u, ref = split_git_url(url)
        state = Path(state); repo = state / CLONE_DIR
        if not (repo / "HEAD").is_file():
            state.mkdir(parents=True, exist_ok=True)
            _git(git_argv(state) + ["clone", "--quiet", "--mirror", u, str(repo)], None)
        return cls(u, ref, repo, state, fetch=True)
    @classmethod
    def local(cls, repo: Path, ref: str = DEFAULT_REF):
        return cls(f"{FILE_PREFIX}{Path(repo).resolve()}", ref, Path(repo), None, fetch=False)
    def pin(self) -> str:
        if self.fetch:
            _git(git_argv(self.state) + ["fetch", "--quiet", "--prune", "origin"], self.repo)
        return _git(["git", "rev-parse", "--verify", f"{self.ref}^{{commit}}"], self.repo).strip()
    def tree(self, pin: str, paths) -> Path:
        """The named paths at `pin`, extracted under a fresh temporary directory (the caller removes it).
        A path absent at that commit is left out rather than failing the archive."""
        out = Path(tempfile.mkdtemp(prefix="ledgerd-tree-"))
        present = [p for p in paths if _git(["git", "ls-tree", "--name-only", pin, "--", p.rstrip("/")], self.repo).strip()]
        if present:
            archive = subprocess.run(["git", "archive", "--format=tar", pin, "--", *present], cwd=self.repo, capture_output=True, env=dyadlib.git_env(), timeout=GIT_TIMEOUT)
            if archive.returncode:
                raise RuntimeError(f"git archive {pin[:12]}: {archive.stderr.decode(errors='replace').strip()}")
            with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as tar:   # the stdlib, not a `tar` row (Rule-14)
                tar.extractall(out, filter="data")
        return out
    def describe(self) -> str:
        return f"git:{self.url}#{self.ref}"
    def pin_label(self, pin: str) -> str:
        return f"git:{pin}"

# ---- dir
def dir_digest(root: Path, paths) -> str:
    """sha256 over the sorted relative paths and contents under `paths` — a pin that moves on content and
    not on a touch, with a name and a byte for every file."""
    h = hashlib.sha256()
    root = Path(root)
    for rel in sorted(paths):
        base = root / rel
        files = sorted(p for p in base.rglob("*") if p.is_file()) if base.is_dir() else ([base] if base.is_file() else [])
        for p in files:
            r = p.relative_to(root).as_posix().encode()
            h.update(len(r).to_bytes(4, "big") + r)
            data = p.read_bytes()
            h.update(len(data).to_bytes(8, "big") + data)
    return h.hexdigest()

class DirStore:
    """A directory as it is on disk: the in-process fallback, honest about its pin (a content digest, never
    a sha of `main`)."""
    SCHEME = "dir"
    def __init__(self, root: Path, paths):
        self.root, self.paths = Path(root).resolve(), tuple(paths)
    @classmethod
    def open(cls, url: str, state: Path | None = None, paths=()):
        u = url[len(FILE_PREFIX):] if url.startswith(FILE_PREFIX) else url
        root = Path(u).expanduser()
        if not root.is_dir():
            raise ValueError(f"dir store {url!r}: not a directory")
        return cls(root, paths)
    def pin(self) -> str:
        return dir_digest(self.root, self.paths)
    def tree(self, pin: str, paths) -> Path:
        return self.root
    def describe(self) -> str:
        return f"dir:{self.root}"
    def pin_label(self, pin: str) -> str:
        return f"dir:{pin[:16]}"

# ---- selection
def adapter_for(url: str):
    """The adapter module-like object a store URL selects: `module:<path>` loads and checks a module; `git+…`
    the git adapter; anything else (`file://…` or a bare path) the dir adapter. ValueError names the problem."""
    if url.startswith(MODULE_PREFIX):
        path = Path(url[len(MODULE_PREFIX):]).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"store {url!r}: no module at {path}")
        mod = dyadlib.load_module(path, f"ledgerd_store_{path.stem}")
        problem = store_problem(mod)
        if problem:
            raise ValueError(f"store {url!r}: {problem}")
        return mod
    if url.startswith(GIT_PREFIX):
        return GitStore
    return DirStore

def open_store(url: str, state: Path | None, paths=()):
    """The store object for `url`: the adapter's `open`, its result checked against STORE_OBJECT."""
    adapter = adapter_for(url)
    obj = adapter.open(url, state, paths)
    problem = object_problem(obj)
    if problem:
        raise ValueError(f"store {url!r}: {problem}")
    return obj

def pin_label(store, pin: str) -> str:
    """`<scheme>:<pin>` as printed: what a pin means is shown, never interpreted (plan #336 G4)."""
    f = getattr(store, "pin_label", None)
    return f(pin) if callable(f) else f"{getattr(store, 'SCHEME', 'store')}:{pin}"

def is_temporary(tree: Path) -> bool:
    """Whether a tree the git adapter extracted may be removed after a build (a dir store's tree is the store)."""
    return Path(tree).name.startswith("ledgerd-tree-") and Path(tree).parent == Path(tempfile.gettempdir())

def remove_tree(tree: Path) -> None:
    if is_temporary(tree):
        shutil.rmtree(tree, ignore_errors=True)

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding
