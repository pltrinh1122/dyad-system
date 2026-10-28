#!/usr/bin/env python3
"""Private-citation fence (a core script, run by the pre-push path; d-work #518, failure mode F4). Kernel: Python 3.12+,
stdlib and git only. A communicate seat once quoted text from private repos into a public repo — the one incident whose
consequence cannot be undone, since a push to a public remote publishes for good. This fence refuses that push.
When the remote git is pushing to (`$2` of the pre-push hook, threaded by `package.py check --guards --pre-push`) is one
the instance declares public, every commit leaving for it is read — its added lines, file by file, and its message — and
the push is refused when a **citation** into a repo the instance declares private sits **beside** a **quoted body**:
- citation: `repo:` / `commit:` fields (`repo:<owner>/<repo>@<sha>:<path>`, the chronicle craft's citation form, and
  `repo: <owner>/<repo>`), any `<owner>/<repo>@<7-40 hex>`, and a `github.com/<owner>/<repo>` URL (https or ssh form);
- quoted body: a line inside or opening a fenced block (``` or ~~~), a `>` blockquote line, or a span of at least
  LONG_QUOTE characters between double quotes (straight or curly) on one line;
- beside: both on added lines of the same file (or the message) at most NEAR lines apart, the same line included.
A bare `owner/repo` mention is no citation, and a citation with no quoted body near it passes: the fence is aimed at
publishing private text, never at naming a repo.
Instance data (Rule-11 property 1), both tracked under the instance location: `public_remotes.local.txt`, one remote
per line, compared after `normalize_remote` (scheme, userinfo, `.git`, trailing `/` and case dropped; the scp ssh form
`git@host:o/r` read as `host/o/r`); and `private_repos.local.txt`, one sha256 hex of a lowercased `owner/repo` per line —
hashes, because the list is tracked in a public repo and a plain name would itself be the leak. Either file absent:
one skip line, no refusal. Fail-closed once both exist: a malformed line, an unknown remote URL, or a commit git cannot
read refuses the push. No override flag. Whether the shapes catch every way a quote can travel is inference, stated.
  privatecite.py scan <rev-range> [repo-root]   informational: hits over a range, by commit and hash prefix only
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("privatecite.py: Python 3.12+ required")
import hashlib, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyadlib

PUBLIC, PRIVATE = "public_remotes.local.txt", "private_repos.local.txt"   # under the instance location (Rule-11 p3)
LONG_QUOTE = 80                     # characters between the quotes for a span to count as a quoted body
NEAR = 10                           # lines between a citation and a quoted body for them to sit beside each other
MESSAGE = "<commit message>"        # the pseudo-file a commit's message is scanned as
_NAME = r"[A-Za-z0-9][\w.-]*"
CITATION_SHAPES = (
    ("field", re.compile(rf"\b(?:repo|commit):\s*(?P<repo>{_NAME}/{_NAME})")),
    ("at-sha", re.compile(rf"(?<![\w./-])(?P<repo>{_NAME}/{_NAME})@[0-9a-fA-F]{{7,40}}\b")),
    ("url", re.compile(rf"github\.com[/:](?P<repo>{_NAME}/{_NAME})", re.IGNORECASE)),
)
FENCE = re.compile(r"^\s{0,3}(?:```|~~~)")
BLOCKQUOTE = re.compile(r"^\s{0,3}>(?![>=])\s*\S")
LONG_SPAN = re.compile(rf'"[^"\n]{{{LONG_QUOTE},}}"|“[^”\n]{{{LONG_QUOTE},}}”')
HASH = re.compile(r"^[0-9a-f]{64}$")

INVARIANTS = [   # crafts/syseng/rules/invariants.md
    ("thresholds-positive", lambda: LONG_QUOTE > 0 and NEAR >= 0),
    ("lists-are-local-txt", lambda: all(n.endswith(".local.txt") and "/" not in n for n in (PUBLIC, PRIVATE))),
    ("shapes-name-a-repo-group", lambda: all("repo" in p.groupindex for _, p in CITATION_SHAPES)),
    ("shape-names-distinct", lambda: len({n for n, _ in CITATION_SHAPES}) == len(CITATION_SHAPES)),
]
dyadlib.enforce(INVARIANTS, __name__)

def repo_hash(owner_repo: str) -> str:
    """sha256 hex of the lowercased `owner/repo`, a trailing `.git` dropped — the private list's entry form."""
    s = owner_repo.strip().lower().removesuffix(".git")
    return hashlib.sha256(s.encode()).hexdigest()

def normalize_remote(url: str) -> str:
    """`https://u:t@GitHub.com/o/r.git/`, `ssh://git@github.com/o/r`, `git@github.com:o/r.git` -> `github.com/o/r`;
    a local path keeps its path, `.git` and trailing `/` dropped. Lowercased: hosts are, and the hostings this
    instance uses fold owner and repo case."""
    u = url.strip()
    m = re.match(r"^[a-zA-Z][\w+.-]*://(?:[^@/]*@)?(.*)$", u)
    if m:
        u = m.group(1)
    else:
        m = re.match(r"^(?:[^@/:]+@)?([^/:]+):(?!/)(.*)$", u)   # scp form host:path (not a Windows-free local path)
        if m and "/" not in m.group(1):
            u = f"{m.group(1)}/{m.group(2)}"
    u = u.rstrip("/").removesuffix(".git").rstrip("/")
    return u.lower()

def read_lists(root: Path) -> tuple[set[str] | None, set[str] | None, list[str]]:
    """(public remotes normalized, private hashes, problems); a list is None when its file is absent."""
    inst, problems = dyadlib.instance(root), []
    def lines(name):
        p = inst / name
        if not p.exists():
            return None
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            problems.append(f"{name} unreadable ({e.__class__.__name__})"); return []
        return [(n, l.split("#", 1)[0].strip()) for n, l in enumerate(text.splitlines(), 1) if l.split("#", 1)[0].strip()]
    pub, priv = lines(PUBLIC), lines(PRIVATE)
    public = None if pub is None else {normalize_remote(v) for _, v in pub}
    private = None
    if priv is not None:
        private = set()
        for n, v in priv:
            if HASH.match(v):
                private.add(v)
            else:
                problems.append(f"{PRIVATE}:{n} is not 64 lowercase hex (a sha256 of a lowercased owner/repo)")
    return public, private, problems

def quoted_lines(added: list[tuple[int, str]]) -> set[int]:
    """The line numbers of `added` ([(new line number, text)] in order) that are a quoted body. A fence's state
    runs over contiguous added lines and resets at a gap, since only added text is judged."""
    out, inside, prev = set(), False, None
    for n, text in added:
        if prev is not None and n != prev + 1:
            inside = False
        prev = n
        if FENCE.match(text):
            out.add(n); inside = not inside; continue
        if inside or BLOCKQUOTE.match(text) or LONG_SPAN.search(text):
            out.add(n)
    return out

def citations(text: str) -> list[tuple[str, str]]:
    """[(shape, owner/repo)] cited on one line."""
    return [(name, m.group("repo").removesuffix(".git")) for name, p in CITATION_SHAPES for m in p.finditer(text)]

def findings(added: list[tuple[int, str]], private: set[str]) -> list[tuple[int, str]]:
    """[(line, hash prefix)] for every private citation in `added` with a quoted body within NEAR lines."""
    quotes = quoted_lines(added)
    hits = []
    for n, text in added:
        for _, repo in citations(text):
            h = repo_hash(repo)
            if h in private and any(abs(n - q) <= NEAR for q in quotes):
                hits.append((n, h[:12]))
    return hits

def parse_diff(diff: str) -> dict[str, list[tuple[int, str]]]:
    """A `git diff -U0` text -> {path: [(new line number, added text)]}."""
    files, path, n = {}, None, 0
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[4:].removeprefix("b/") if line[4:] != "/dev/null" else None
            continue
        if line.startswith("@@"):
            m = re.match(r"^@@ -\S+ \+(\d+)", line)
            n = int(m.group(1)) if m else 0
            continue
        if path and line.startswith("+"):
            files.setdefault(path, []).append((n, line[1:])); n += 1
    return files

def _git(root: Path, *a) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True, errors="replace")

def provenance_prefix(root: Path) -> str | None:
    """`<instance>/d-work/provenance/` relative to `root`, or None when the instance lies outside it. A hit there
    warns and never refuses (plan #520 revision 2, the Operator's option (d)): a provenance record holds the
    Operator's own words verbatim (Rule-7 property 4), which no rewrite may change, so the fence names the record
    and line and lets them through; every path the Agent writes stays fenced."""
    try:
        return (dyadlib.instance(root) / "d-work" / "provenance").resolve().relative_to(Path(root).resolve()).as_posix() + "/"
    except ValueError:
        return None

def commit_findings(root: Path, sha: str, private: set[str]) -> tuple[list[str], str | None, list[str]]:
    """(refusing finding lines, error, warning lines) for one commit: its added lines against its first parent (a
    root commit against nothing), and its message. `error` is set when git cannot read the commit — the caller
    refuses. A finding inside the provenance store is a warning (`provenance_prefix`), never a refusal."""
    parents = _git(root, "rev-list", "--parents", "-n", "1", sha)
    msg = _git(root, "log", "-1", "--format=%B", sha)
    if parents.returncode or msg.returncode:
        return [], f"git cannot read commit {sha[:12]}", []
    ps = parents.stdout.split()[1:]
    common = ("--no-color", "--no-ext-diff", "--no-renames", "--text", "-U0")
    d = _git(root, "diff", *common, ps[0], sha) if ps else _git(root, "diff-tree", "-p", "--root", *common, sha)
    if d.returncode:
        return [], f"git cannot diff commit {sha[:12]}", []
    files = parse_diff(d.stdout)
    files[MESSAGE] = list(enumerate(msg.stdout.splitlines(), 1))
    prov, hits, warns = provenance_prefix(root), [], []
    for path, added in files.items():
        for n, h in findings(added, private):
            line = f"{sha[:12]} {path}:{n} cites a private repo (sha256 {h}…) beside a quoted body"
            (warns if prov and path.startswith(prov) else hits).append(line)
    return hits, None, warns

def leaving(root: Path, ref_lines: list[str], remote: str) -> tuple[list[str], list[str]]:
    """(commits, problems): every commit the pushed refs carry that the remote is not known to hold — not under
    `refs/remotes/<remote>/` and not behind the remote's own sha for the ref. A first push to a remote this clone
    has no refs for carries the whole history, and so it is read whole."""
    tips, nots = [], [f"--remotes={remote}/*"] if remote and _git(root, "remote", "get-url", remote).returncode == 0 else []
    for line in ref_lines:
        parts = line.split()
        if len(parts) != 4:
            continue
        _, local_sha, _, remote_sha = parts
        if set(local_sha) <= {"0"}:
            continue
        sha = _git(root, "rev-parse", "--verify", "-q", f"{local_sha}^{{commit}}").stdout.strip()
        if not sha:
            continue                                     # a tag on a tree or blob: no commit leaves
        tips.append(sha)
        if not set(remote_sha) <= {"0"} and _git(root, "cat-file", "-e", f"{remote_sha}^{{commit}}").returncode == 0:
            nots.append(remote_sha)
    if not tips:
        return [], []
    r = _git(root, "rev-list", *tips, "--not", *nots, "--")
    if r.returncode:
        return [], [f"git cannot list the commits leaving ({r.stderr.strip()[:120]})"]
    return r.stdout.split(), []

def check_push(root: Path, remote: str | None, url: str | None, ref_lines: list[str]) -> tuple[list[str], list[str]]:
    """(refusals, info lines) for one push. The pre-push path prints both and refuses on any refusal."""
    public, private, problems = read_lists(root)
    if public is None or private is None:
        absent = " and ".join(n for n, v in ((PUBLIC, public), (PRIVATE, private)) if v is None)
        return [], [f"skip [private-cite] no {absent} under the instance: nothing declared, nothing judged"]
    if problems:
        return [f"{p}: fail-closed" for p in problems], []
    if not url:
        return ["the pushed-to URL is unknown (the hook passes git's `<remote> <url>`): cannot tell whether it is public — fail-closed"], []
    target = normalize_remote(url)
    if target not in public:
        return [], [f"ok   [private-cite] {target} is not a declared public remote"]
    commits, problems = leaving(root, ref_lines, remote or "")
    if problems:
        return [f"{p}: fail-closed" for p in problems], []
    refusals, warns = [], []
    for sha in commits:
        hits, err, prov = commit_findings(root, sha, private)
        if err:
            refusals.append(f"{err}: fail-closed"); continue
        refusals.extend(hits); warns.extend(prov)
    notes = [f"warn [private-cite] {w} — a provenance record, the Operator's own words (Rule-7): not refused" for w in warns]
    if refusals:
        refusals.append(f"{target} is declared public: quoting a private repo there publishes it for good — remove the "
                        f"quoted body or the citation from those commits (rewrite them), then push; there is no override")
    return refusals, notes + [f"ok   [private-cite] {len(commits)} commit(s) to public {target}: no private citation beside a quoted body"
                              f"{' outside the provenance store' if warns else ''}"]

def scan_range(root: Path, rev_range: str) -> tuple[list[str], list[str]]:
    """Informational: (finding lines, problems) over a rev range, by commit and hash prefix only."""
    _, private, problems = read_lists(root)
    if private is None:
        return [], [f"no {PRIVATE}"]
    r = _git(root, "rev-list", rev_range, "--")
    if r.returncode:
        return [], [r.stderr.strip()]
    out = []
    for sha in r.stdout.split():
        hits, err, prov = commit_findings(root, sha, private)
        out.extend((hits + [f"{w} (provenance: warns, never refused)" for w in prov]) if not err else [err])
    return out, problems

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "scan":
        root = Path(a[2]) if len(a) > 2 else dyadlib.repo_root()
        hits, problems = scan_range(root, a[1])
        for p in problems:
            print(f"FAIL {p}")
        for h in hits:
            print(h)
        print(f"{len(hits)} finding(s) over {a[1]}")
        sys.exit(1 if hits or problems else 0)
    sys.exit(__doc__)
