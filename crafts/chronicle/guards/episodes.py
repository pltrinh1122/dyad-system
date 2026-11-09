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
  with no `fiction:` header; a `fiction:` part that is neither `persona, based on a real-life model` nor
  `composites: <name>, <name>`; a footnote reference inside a marked passage; a declared composite's name in a
  paragraph not marked (#530). A `fiction:` header with no marked passage is one warning line;
- a keyed piece (`form: keyed`, `chronicle.md` §1, §2, §8; #650), read against its key `<piece>.key.md` beside it,
  named by `key:` (a key is never read as an episode): a `form:` that is neither `labelled` nor `keyed`; a `key:`
  missing or naming no file beside the piece; a `fiction:` line, a footnote or a `*(fiction)*` marker in the piece; a
  key line not `¶<n> <first words> | record <citation>[; <citation>]`, `… | fiction persona` or
  `… | fiction composites: <name>, …`; a paragraph with no key line, or more than one, or whose first words differ
  from its line's; a key line naming no paragraph; a key with no record line; a record citation judged as a footnote
  is (the same forms, resolution and warnings); a composite a key line declares named in a paragraph whose line does
  not label it. That a composite is in the series bible is inference: the bible is no file the guard reads.
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
COMPOSITES = "composites:"                                         # the fiction header's composite part (chronicle.md §2, #530)
FORM_KEY, KEY_KEY, FORMS_OF_PIECE, KEY_SUFFIX = "form", "key", ("labelled", "keyed"), ".key.md"   # chronicle.md §1, §2 (#650)
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
_KEYLINE = re.compile(r"^¶(\d+) (.+?) \| (record (.+)|fiction persona|fiction composites: (.+))$")   # templates/key.md
INVARIANTS = [("fields-start-with-file", lambda: FIELDS[0] == "file" and len(set(FIELDS)) == len(FIELDS)),   # crafts/syseng/rules/invariants.md
              ("time-pattern-matches-times", lambda: all(_TIME.match(f"{t}, 2026-01-01") for t in TIMES)),
              ("four-citation-forms", lambda: FORMS == ("path", "prov", "repo", "commit")
               and all(p.pattern.startswith(f"^{f}:") for f, p in zip(FORMS, (_PATH, _PROV, _REPO, _COMMIT)))),
              ("visibility-two", lambda: set(VISIBILITY) == {"public", "private"}),
              ("fiction-key-optional", lambda: FICTION_KEY not in HEADER and FICTION_LABEL.startswith("persona, ")
               and MARKER.strip() == MARKER and MARKER != ""),
              ("composites-part-is-not-the-label", lambda: not FICTION_LABEL.startswith(COMPOSITES) and COMPOSITES.endswith(":")),
              ("key-line-grammar", lambda: _KEYLINE.match("¶2 The cos | record prov:#7/1; path:a.md").group(4) == "prov:#7/1; path:a.md"
               and _KEYLINE.match("¶1 He lay | fiction composites: Mara").group(5) == "Mara"
               and _KEYLINE.match("¶1 He lay | fiction") is None),
              ("labelled-form-first", lambda: FORMS_OF_PIECE[0] == "labelled" and KEY_SUFFIX.endswith(".md"))]
dyadlib.enforce(INVARIANTS, __name__)

def store(root: Path | None = None) -> Path:
    return (root or dyadlib.repo_root()) / os.environ.get(SITE_ENV, SITE_DEFAULT) / "episodes"

def episodes(root: Path | None = None) -> list[Path]:
    d = store(root)
    return sorted(p for p in d.glob("*.md") if p.name.lower() != "readme.md" and not p.name.endswith(KEY_SUFFIX)) if d.is_dir() else []

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

def fiction_parts(value: str) -> tuple[bool, list[str], list[str]]:
    """(persona labelled, declared composites, bad parts) from a `fiction:` value: parts separated by `;`, each the
    persona label or `composites: <name>, <name>` (chronicle.md §2, #530)."""
    persona, names, bad = False, [], []
    for part in (s.strip() for s in value.split(";")):
        if part == FICTION_LABEL:
            persona = True
        elif part.startswith(COMPOSITES):
            got = [n.strip() for n in part[len(COMPOSITES):].split(",")]
            if not got or any(not n for n in got) or len(set(got)) != len(got):
                bad.append(part)
            else:
                names += got
        else:
            bad.append(part)
    return persona, names, bad

def paragraphs(body: list[str]) -> list[list[str]]:
    """The body's paragraphs: runs of non-blank lines."""
    paras, cur = [], []
    for line in body + [""]:
        if line.strip():
            cur.append(line)
        elif cur:
            paras.append(cur); cur = []
    return paras

def marked_passages(body: list[str]) -> list[list[str]]:
    """The fiction layer's passages: each paragraph of the body (lines up to a blank line) whose first line opens
    with MARKER (chronicle.md §2)."""
    return [p for p in paragraphs(body) if p[0].lstrip().startswith(MARKER)]

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

def parse_key(text: str) -> tuple[list[dict], list[str]]:
    """(lines, bad lines) of a key (templates/key.md): each `¶<n> <first words> | <layer>` line as {n, words, layer
    (`record` or `fiction`), citations, composites}; an HTML comment and blank lines are skipped."""
    out, bad = [], []
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    for line in (l.strip() for l in text.splitlines()):
        if not line:
            continue
        m = _KEYLINE.match(line)
        if not m:
            bad.append(line); continue
        cites = [c.strip() for c in (m.group(4) or "").split(";")] if m.group(4) is not None else []
        names = [c.strip() for c in m.group(5).split(",")] if m.group(5) is not None else []
        out.append({"n": int(m.group(1)), "words": m.group(2).strip(), "layer": "record" if m.group(4) is not None else "fiction",
                    "citations": cites, "composites": names, "line": line})
    return out, bad

def _resolve(root: Path, where: str, label: str, txt: str, repos: dict[str, str], seen: dict) -> list[str]:
    """The problems of one citation `txt` at `label` (`[^n]` or `¶n`), judged as chronicle.md §1 and §8 say; counts an
    unresolvable cross-repo citation in seen["world"] and a cited private repo in seen["private"]."""
    c = citation(txt)
    if c is None:
        return [f"{where}: {label} {txt!r} is none of path:, prov:#<id>/<n>, repo:<owner>/<repo>@<sha>:<path>, commit:<owner>/<repo>@<sha> (chronicle.md §1)"]
    form, g = c
    if form == "path":
        return [] if _in_tree(root, g[0]) else [f"{where}: {label} path:{g[0]} does not exist in the tree"]
    if form == "prov":
        problem = _prov_entry(root, *g)
        return [f"{where}: {label} prov:#{g[0]}/{g[1]}: {problem}"] if problem else []
    repo, sha, rel = g if form == "repo" else (*g, None)
    if repo not in repos:
        return [f"{where}: {label} {form}:{repo} is not declared in `repos:` with its visibility (chronicle.md §4)"]
    if not _SHA.match(sha):
        return [f"{where}: {label} {form}:{repo}@{sha}: not a full 40-hex commit sha"]
    if repos[repo] == "private":
        seen["private"].add(repo)
    clone = _clone(repo)
    if clone is None:
        seen["world"] += 1
    elif not _git_has(clone, sha, rel):
        what = f"repo:{repo}@{sha[:12]}:{rel}" if rel is not None else f"commit:{repo}@{sha[:12]}"
        return [f"{where}: {label} {what} is not in the clone at {clone}"]
    return []

def _named(names: list[str], text: str) -> list[str]:
    return [n for n in names if re.search(rf"(?<!\w){re.escape(n)}(?!\w)", text)]

def check_keyed(root: Path, path: Path, where: str, header: dict, body: list[str], notes: dict,
                repos: dict[str, str], seen: dict) -> list[str]:
    """The keyed form's checks (chronicle.md §2, §8; #650): the piece declares nothing, its key labels every paragraph."""
    msgs = []
    if FICTION_KEY in header:
        msgs.append(f"{where}: a keyed piece carries a `{FICTION_KEY}:` line; its key labels the fiction (chronicle.md §2)")
    if notes or any(_FOOTREF.search(l) for l in body):
        msgs.append(f"{where}: a keyed piece holds footnotes; its citations live in its key (chronicle.md §2)")
    paras = paragraphs(body)
    if marked := [i for i, p in enumerate(paras, 1) if p[0].lstrip().startswith(MARKER)]:
        msgs.append(f"{where}: a keyed piece marks paragraph(s) {', '.join(map(str, marked))} {MARKER}; its key labels the fiction (chronicle.md §2)")
    name = header.get(KEY_KEY, "")
    if not name:
        return msgs + [f"{where}: a keyed piece's header lacks `{KEY_KEY}:` (chronicle.md §2)"]
    kp = path.parent / name
    if Path(name).name != name or not name.endswith(KEY_SUFFIX) or not kp.is_file():
        return msgs + [f"{where}: `{KEY_KEY}: {name}` names no `*{KEY_SUFFIX}` file beside the piece (chronicle.md §1)"]
    lines, bad = parse_key(kp.read_text())
    msgs += [f"{where}: key line {b!r} is not `¶<n> <first words> | record <citation>` or `… | fiction persona|composites: <name>, …` (templates/key.md)"
             for b in bad]
    by_n: dict[int, list[dict]] = {}
    for kl in lines:
        by_n.setdefault(kl["n"], []).append(kl)
    for n in sorted(set(by_n) - set(range(1, len(paras) + 1))):
        msgs.append(f"{where}: key line ¶{n} names no paragraph; the piece has {len(paras)}")
    declared = [c for kl in lines for c in kl["composites"]]
    for i, para in enumerate(paras, 1):
        got, text = by_n.get(i, []), " ".join(l.strip() for l in para)
        if not got:
            msgs.append(f"{where}: paragraph {i} has no key line (chronicle.md §2)"); continue
        if len(got) > 1:
            msgs.append(f"{where}: paragraph {i} has {len(got)} key lines; one labels it (chronicle.md §2)"); continue
        kl = got[0]
        if not text.startswith(kl["words"]):
            msgs.append(f"{where}: key line ¶{i} {kl['words']!r} is not how paragraph {i} opens")
        if hits := [c for c in _named(declared, text) if c not in kl["composites"]]:
            msgs.append(f"{where}: composite(s) {', '.join(hits)} in paragraph {i}, which its key line does not label "
                        f"`fiction {COMPOSITES} {', '.join(hits)}`; a composite is fiction (chronicle.md §2)")
    for kl in lines:
        names = kl["composites"]
        if kl["layer"] == "fiction" and names and (any(not c for c in names) or len(set(names)) != len(names)):
            msgs.append(f"{where}: key line ¶{kl['n']} declares composites {', '.join(names)!r}: empty or repeated (templates/key.md)")
        for c in kl["citations"]:
            msgs += _resolve(root, where, f"¶{kl['n']}", c, repos, seen) if c else [f"{where}: key line ¶{kl['n']} has an empty record citation"]
    if not any(kl["layer"] == "record" for kl in lines):
        msgs.append(f"{where}: its key holds no record line; every event cites the record or the Operator's context (chronicle.md §1, serial.md §7)")
    return msgs

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
    form = header.get(FORM_KEY, FORMS_OF_PIECE[0])
    repos, bad = declared_repos(header.get("repos", "none"))
    msgs += [f"{where}: `repos:` entry {b!r} is not `<owner>/<repo>=public|private` (chronicle.md §4)" for b in bad]
    seen = {"world": 0, "private": set()}
    if form not in FORMS_OF_PIECE:
        msgs.append(f"{where}: `{FORM_KEY}: {form}` is neither {' nor '.join(FORMS_OF_PIECE)} (chronicle.md §1)")
    elif form == "keyed":
        msgs += check_keyed(root, path, where, header, body, notes, repos, seen)
    else:
        msgs += check_labelled(root, where, header, body, notes, repos, seen)
    if seen["world"]:
        msgs.append(f"warning: {where}: {seen['world']} cross-repo citation(s) unresolvable (The World: no clone under ${REPOS_ENV}), inference")
    if seen["private"]:
        msgs.append(f"warning: {where}: cites private repo(s) {', '.join(sorted(seen['private']))}; its publication names them (chronicle.md §4)")
    return msgs

def check_labelled(root: Path, where: str, header: dict, body: list[str], notes: dict,
                   repos: dict[str, str], seen: dict) -> list[str]:
    """The labelled form's checks (chronicle.md §1, §2, §8): footnotes, the `fiction:` line and marked passages."""
    msgs = []
    fiction, marked = header.get(FICTION_KEY), marked_passages(body)
    composites: list[str] = []
    if fiction is not None:
        _, composites, bad_parts = fiction_parts(fiction)
        msgs += [f"{where}: `{FICTION_KEY}:` part {b!r} is neither `{FICTION_LABEL}` nor `{COMPOSITES} <name>, <name>` (chronicle.md §2)"
                 for b in bad_parts]
    if marked and fiction is None:
        msgs.append(f"{where}: {len(marked)} passage(s) marked {MARKER} and no `{FICTION_KEY}:` header (chronicle.md §2)")
    for para in paragraphs(body):
        if para[0].lstrip().startswith(MARKER):
            continue
        if hits := _named(composites, " ".join(para)):
            msgs.append(f"{where}: composite(s) {', '.join(hits)} in a passage not marked {MARKER}; a composite is fiction (chronicle.md §2)")
    if fiction is not None and not marked:
        msgs.append(f"warning: {where}: `{FICTION_KEY}:` header and no passage marked {MARKER} (chronicle.md §2)")
    for para in marked:
        if refs := sorted({r for line in para for r in _FOOTREF.findall(line)}):
            msgs.append(f"{where}: a passage marked {MARKER} cites [^{'], [^'.join(refs)}]; the fiction layer cites nothing (chronicle.md §2)")
    if not notes:
        msgs.append(f"{where}: cites nothing; every event cites the record or the Operator's context (chronicle.md §1)")
    used = {r for line in body for r in _FOOTREF.findall(line)}
    msgs += [f"{where}: footnote [^{r}] is referenced and never defined" for r in sorted(used - set(notes))]
    for n, txt in notes.items():
        msgs += _resolve(root, where, f"[^{n}]", txt, repos, seen)
    return msgs

def check_package(root: Path | None = None, pkg: Path = dyadlib.PKG) -> list[str]:
    root = root or dyadlib.repo_root()
    if not store(root).is_dir():
        return [f"warning: skip episodes: no {os.environ.get(SITE_ENV, SITE_DEFAULT)}/episodes/ here (the instance's serial; seeded from crafts/chronicle/templates/episode.md)"]
    msgs = []
    for p in episodes(root):
        msgs += check_episode(root, p)
    return msgs

def _citations(path: Path) -> int:
    """How many citations a piece makes: its footnotes, or in the keyed form its key's record citations."""
    header, _, notes = parse(path.read_text())
    if header.get(FORM_KEY) != "keyed":
        return len(notes)
    kp = path.parent / header.get(KEY_KEY, "")
    return sum(len(kl["citations"]) for kl in parse_key(kp.read_text())[0]) if header.get(KEY_KEY) and kp.is_file() else 0

def summary(root: Path | None = None, pkg: Path = dyadlib.PKG) -> str:
    root = root or dyadlib.repo_root()
    eps = episodes(root)
    cites = sum(_citations(p) for p in eps)
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
