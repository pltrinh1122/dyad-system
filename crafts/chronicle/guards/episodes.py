#!/usr/bin/env python3
"""Episode guard (entity `episode`, corpus `infra`; the chronicle craft's one guard — its rule `chronicle.md` owns the
check; placed per `crafts/sysarch/rules/guards.md` under `crafts/chronicle/guards/`; d-work #502, #498 C4).
Kernel: Python 3.12+, stdlib and git only.
Reads every episode `<site>/episodes/*.md` (`DYAD_SITE`, default `site`; absent store: one `warning: skip` line)
and fails what the record cannot hold (the core `chronicle.md` §1, §2, §4, §8; the serial `serial.md` §1, §3, §7):
- a header key missing (`title`, `season`, `episode`, `time`, `repos`), a `season`/`episode` that is not a
  number, a `time:` line not `present|past, YYYY-MM-DD`, a `repos:` entry not `<owner>/<repo>=public|private`;
- an episode with no citation, a footnote referenced in the body and never defined, a footnote whose citation is
  none of the four forms;
- `path:<rel>` that does not exist in the tree; `prov:#<id>/<n>` with no provenance record `<id>` or no entry `n`
  in it (the core's provenance guard parses the record, `dyadlib.load_guard("agent", "provenance")`);
- `repo:<owner>/<repo>@<sha>:<path>` whose repo is not declared in `repos:` or whose sha is not 40 hex, or which a
  local clone (`DYAD_REPOS_DIR/<repo>` or `DYAD_REPOS_DIR/<owner>/<repo>`) does not hold;
- `commit:<owner>/<repo>@<sha>` (a commit itself, no path) on the same terms, the clone holding the commit;
- the fiction layer's labels (`chronicle.md` §2): a marked passage (a paragraph opening `*(fiction)*`) in an episode
  whose header lacks `fiction: persona, based on a real-life model`, a `fiction:` value other than that label, or a
  footnote reference inside a marked passage. A `fiction:` header with no marked passage is one warning line.
A `repo:` or `commit:` citation with no local clone is The World (the core's Rule-20 register, property 2, `world` severity):
one `warning: … inference` line per episode, never a pass by assumption. A cited private repo is one warning line
naming it (`chronicle.md` §4). Left to inference, stated: whether a cited artifact says what the episode says.
  episodes.py [repo-root]
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("episodes.py: Python 3.12+ required")
import datetime, os, re, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "dyad" / "scripts"))   # crafts/chronicle/guards/ -> dyad/scripts
import dyadlib

ENTITY, CORPUS, TRANSACTION = "episode", "infra", False
NAME, OWNER = "episode (a serial's instalment)", "crafts/chronicle/rules/chronicle.md"
FIELDS = ("file", "title", "season", "episode", "time", "repos")   # what `parse` yields per episode, header keys after `file`
HEADER = FIELDS[1:]
TIMES = ("present", "past")
VISIBILITY = ("public", "private")
FORMS = ("path", "prov", "repo", "commit")                          # the four citation forms (chronicle.md §1)
FICTION_KEY, FICTION_LABEL, MARKER = "fiction", "persona, based on a real-life model", "*(fiction)*"   # chronicle.md §2
SITE_ENV, SITE_DEFAULT, REPOS_ENV = "DYAD_SITE", "site", "DYAD_REPOS_DIR"
_TIME = re.compile(r"^(present|past),\s*(\d{4}-\d{2}-\d{2})$")
_REPO_DECL = re.compile(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)=(public|private)$")
_FOOTDEF = re.compile(r"^\[\^([^\]\s]+)\]:\s*(.*)$")
_FOOTREF = re.compile(r"\[\^([^\]\s]+)\](?!:)")
_PATH = re.compile(r"^path:(\S+)$")
_PROV = re.compile(r"^prov:#(\d+)/(\d+)$")
_REPO = re.compile(r"^repo:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([^:\s]+):(\S+)$")
_COMMIT = re.compile(r"^commit:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@(\S+)$")
_SHA = re.compile(r"^[0-9a-f]{40}$")
INVARIANTS = [("fields-start-with-file", lambda: FIELDS[0] == "file" and len(set(FIELDS)) == len(FIELDS)),   # crafts/syseng/rules/invariants.md
              ("time-pattern-matches-times", lambda: all(_TIME.match(f"{t}, 2026-01-01") for t in TIMES)),
              ("four-citation-forms", lambda: FORMS == ("path", "prov", "repo", "commit")
               and all(p.pattern.startswith(f"^{f}:") for f, p in zip(FORMS, (_PATH, _PROV, _REPO, _COMMIT)))),
              ("visibility-two", lambda: set(VISIBILITY) == {"public", "private"}),
              ("fiction-key-optional", lambda: FICTION_KEY not in HEADER and FICTION_LABEL.startswith("persona, ")
               and MARKER.strip() == MARKER and MARKER != "")]
dyadlib.enforce(INVARIANTS, __name__)

def store(root: Path | None = None) -> Path:
    return (root or dyadlib.repo_root()) / os.environ.get(SITE_ENV, SITE_DEFAULT) / "episodes"

def episodes(root: Path | None = None) -> list[Path]:
    d = store(root)
    return sorted(p for p in d.glob("*.md") if p.name.lower() != "readme.md") if d.is_dir() else []

def parse(text: str) -> tuple[dict[str, str], list[str], dict[str, str]]:
    """(header, body lines, footnotes): the header is the leading `key: value` lines up to the first blank line;
    footnotes are `[^n]: <citation>` lines, keyed by n, anywhere after the header."""
    lines = text.splitlines()
    header, i = {}, 0
    while i < len(lines) and lines[i].strip():
        k, sep, v = lines[i].partition(":")
        if sep and k.strip():
            header[k.strip()] = v.strip()
        i += 1
    body, notes = [], {}
    for line in lines[i:]:
        m = _FOOTDEF.match(line)
        if m:
            notes[m.group(1)] = m.group(2).strip()
        else:
            body.append(line)
    return header, body, notes

def citation(text: str) -> tuple[str, tuple[str, ...]] | None:
    """(form, groups) for a footnote's citation — its first token; the rest is a free gloss — else None."""
    tok = text.split(maxsplit=1)[0] if text.split() else ""
    for form, pat in zip(FORMS, (_PATH, _PROV, _REPO, _COMMIT)):
        if m := pat.match(tok):
            return form, m.groups()
    return None

def marked_passages(body: list[str]) -> list[list[str]]:
    """The fiction layer's passages: each paragraph of the body (lines up to a blank line) whose first line opens
    with MARKER (chronicle.md §2)."""
    paras, cur = [], []
    for line in body + [""]:
        if line.strip():
            cur.append(line)
        elif cur:
            paras.append(cur); cur = []
    return [p for p in paras if p[0].lstrip().startswith(MARKER)]

def declared_repos(value: str) -> tuple[dict[str, str], list[str]]:
    """({owner/repo: visibility}, bad entries) from a `repos:` value; `none` is the empty declaration."""
    if value.strip() == "none":
        return {}, []
    out, bad = {}, []
    for tok in value.split():
        m = _REPO_DECL.match(tok)
        if m:
            out[m.group(1)] = m.group(2)
        else:
            bad.append(tok)
    return out, bad

def _in_tree(root: Path, rel: str) -> bool:
    p = Path(rel)
    if p.is_absolute() or ".." in p.parts:
        return False
    return (root / p).exists()

def _prov_entry(root: Path, rid: str, n: str) -> str | None:
    """None when record `rid` holds entry `n`; else the problem."""
    prov = dyadlib.find_guard("agent", "provenance")
    if prov is None:
        return "no provenance guard here to parse it (the core's agent/provenance)"
    rec = prov.store(root) / f"{int(rid)}.md"
    if not rec.is_file():
        return f"no provenance record #{int(rid)}"
    if not any(e["n"] == str(int(n)) for e in prov.parse(rec.read_text())):
        return f"provenance record #{int(rid)} has no entry {int(n)}"
    return None

def _clone(repo: str) -> Path | None:
    base = os.environ.get(REPOS_ENV)
    if not base:
        return None
    owner, name = repo.split("/", 1)
    for c in (Path(base) / name, Path(base) / owner / name):
        if (c / ".git").exists() or (c / "HEAD").is_file():
            return c
    return None

def _git_has(clone: Path, sha: str, path: str | None) -> bool:
    """The clone holds `sha:path`, or with no path the commit `sha` itself."""
    obj = f"{sha}:{path}" if path is not None else f"{sha}^{{commit}}"
    try:
        r = subprocess.run(["git", "-C", str(clone), "cat-file", "-e", obj], capture_output=True,
                           env=dyadlib.git_env(), timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0

def check_episode(root: Path, path: Path, text: str | None = None) -> list[str]:
    where = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
    header, body, notes = parse(text if text is not None else path.read_text())
    msgs = [f"{where}: header lacks `{k}:` (templates/episode.md)" for k in HEADER if k not in header]
    for k in ("season", "episode"):
        if k in header and not header[k].isdigit():
            msgs.append(f"{where}: `{k}: {header[k]}` is not a number")
    if "time" in header:
        m = _TIME.match(header["time"])
        try:
            ok = bool(m) and datetime.date.fromisoformat(m.group(2)) is not None
        except ValueError:
            ok = False
        if not ok:
            msgs.append(f"{where}: `time: {header['time']}` is not `present|past, YYYY-MM-DD` (serial.md §3)")
    fiction, marked = header.get(FICTION_KEY), marked_passages(body)
    if fiction is not None and fiction != FICTION_LABEL:
        msgs.append(f"{where}: `{FICTION_KEY}: {fiction}` is not `{FICTION_KEY}: {FICTION_LABEL}` (chronicle.md §2)")
    if marked and fiction is None:
        msgs.append(f"{where}: {len(marked)} passage(s) marked {MARKER} and no `{FICTION_KEY}: {FICTION_LABEL}` header (chronicle.md §2)")
    if fiction is not None and not marked:
        msgs.append(f"warning: {where}: `{FICTION_KEY}:` header and no passage marked {MARKER} (chronicle.md §2)")
    for para in marked:
        if refs := sorted({r for line in para for r in _FOOTREF.findall(line)}):
            msgs.append(f"{where}: a passage marked {MARKER} cites [^{'], [^'.join(refs)}]; the fiction layer cites nothing (chronicle.md §2)")
    repos, bad = declared_repos(header.get("repos", "none"))
    msgs += [f"{where}: `repos:` entry {b!r} is not `<owner>/<repo>=public|private` (chronicle.md §4)" for b in bad]
    if not notes:
        msgs.append(f"{where}: cites nothing; every event cites the record or the Operator's context (chronicle.md §1)")
    used = {r for line in body for r in _FOOTREF.findall(line)}
    msgs += [f"{where}: footnote [^{r}] is referenced and never defined" for r in sorted(used - set(notes))]
    world, private = 0, set()
    for n, txt in notes.items():
        c = citation(txt)
        if c is None:
            msgs.append(f"{where}: [^{n}] {txt!r} is none of path:, prov:#<id>/<n>, repo:<owner>/<repo>@<sha>:<path>, commit:<owner>/<repo>@<sha> (chronicle.md §1)")
            continue
        form, g = c
        if form == "path":
            if not _in_tree(root, g[0]):
                msgs.append(f"{where}: [^{n}] path:{g[0]} does not exist in the tree")
        elif form == "prov":
            if problem := _prov_entry(root, *g):
                msgs.append(f"{where}: [^{n}] prov:#{g[0]}/{g[1]}: {problem}")
        else:
            repo, sha, rel = g if form == "repo" else (*g, None)
            if repo not in repos:
                msgs.append(f"{where}: [^{n}] {form}:{repo} is not declared in `repos:` with its visibility (chronicle.md §4)")
                continue
            if not _SHA.match(sha):
                msgs.append(f"{where}: [^{n}] {form}:{repo}@{sha}: not a full 40-hex commit sha")
                continue
            if repos[repo] == "private":
                private.add(repo)
            clone = _clone(repo)
            if clone is None:
                world += 1
            elif not _git_has(clone, sha, rel):
                what = f"repo:{repo}@{sha[:12]}:{rel}" if rel is not None else f"commit:{repo}@{sha[:12]}"
                msgs.append(f"{where}: [^{n}] {what} is not in the clone at {clone}")
    if world:
        msgs.append(f"warning: {where}: {world} cross-repo citation(s) unresolvable (The World: no clone under ${REPOS_ENV}), inference")
    if private:
        msgs.append(f"warning: {where}: cites private repo(s) {', '.join(sorted(private))}; its publication names them (chronicle.md §4)")
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    if not store(root).is_dir():
        return [f"warning: skip episodes: no {os.environ.get(SITE_ENV, SITE_DEFAULT)}/episodes/ here (the instance's serial; seeded from crafts/chronicle/templates/episode.md)"]
    msgs = []
    for p in episodes(root):
        msgs += check_episode(root, p)
    return msgs

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    root = root or dyadlib.repo_root()
    eps = episodes(root)
    cites = sum(len(parse(p.read_text())[2]) for p in eps)
    return f"{len(eps)} episode(s), {cites} citation(s)"

def describe(root: Path, pkg: Path = dyadlib.PKG) -> dict:
    eps = episodes(root)
    ex = parse(eps[0].read_text())[0] if eps else {}
    allowed = {"file": "the episode's file name", "title": "free text", "season": "a number", "episode": "a number",
               "time": "present|past, YYYY-MM-DD", "repos": "none, or <owner>/<repo>=public|private, space-separated"}
    return {"store": f"<{SITE_ENV}, default {SITE_DEFAULT}>/episodes/*.md", "parser": "`episodes.parse`", "observed": len(eps),
            "note": "footnote citations: path:, prov:#<id>/<n>, repo:<owner>/<repo>@<sha>:<path>, commit:<owner>/<repo>@<sha> (chronicle.md §1)",
            "fields": [(f, "text", allowed[f], True, (eps[0].name if f == "file" else ex.get(f, "")) if eps else "", "episodes.FIELDS")
                       for f in FIELDS]}

def main(a: list[str]) -> int:
    root = Path(a[0]).resolve() if a else dyadlib.repo_root()
    msgs = check_package(root)
    for m in msgs:
        print(m)
    bad = [m for m in msgs if not m.startswith("warning:")]
    print(f"{'FAIL' if bad else 'ok  '} [chronicle/episodes] {summary(root)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
