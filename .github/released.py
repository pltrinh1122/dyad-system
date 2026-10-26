"""released: the release service run by .github/workflows/dyad-release.yml (d-work #461, plan revisions 3 and 4).

The trigger is the ledger entry that records the Operator's release Y (Rule-11 Ratification events), written on the
release's row by the cos, ledger-only: `<date> Y release <tag> at <cut sha> (archive <sha256>)`. On every push to main
touching the rows (and on dispatch) this script reads every row's `disposed` entries of that shape and, for each one,
checks the cut sha is on main and tag == VERSION at it, builds by the one code path in a worktree at that sha (Rule-11
property 5), verifies the archive sha256, then creates the annotated tag and the GitHub Release. Idempotent: a tag at
the cut sha with its Release is `already` and nothing runs; a tag at the cut sha without a Release gets its Release; a
tag elsewhere is refused (tags never move). An entry `Y release <tag>` without `at` predates the service and is not
read. Clerical execution of the recorded Y, never a disposer (Rule-2).

It writes nothing to the repo (plan #461 revision 4): its record is the annotated tag, the Release (with
`<tag>.release.json`) and the run's log and summary. On a push it reads only the entries the push added (`BEFORE`, the
push's `before` sha), so an entry refused once is not re-run, and re-red, on every later push; a dispatch with `tag`
retries one. Stdlib only; invoked by the workflow, never by the package.
"""
import hashlib, json, os, pathlib, re, subprocess, sys, tempfile

ROWS = pathlib.Path("agent-corpus/d-work/rows")
BEFORE = os.environ.get("BEFORE", "").strip()   # the push's `before` sha; empty or all-zero on a dispatch
ONLY, REPO, GATE = os.environ.get("ONLY", "").strip(), os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GATE", "ledger")
SCAN = "--scan" in sys.argv   # read-only: print `pending=true|false` for the gated job; nothing is built, tagged or written
TAG_RE = re.compile(r"(?:(?P<craft>[a-z0-9][a-z0-9-]*)-)?v(?P<ver>\d+\.\d+\.\d+)")
ENTRY_RE = re.compile(r"\S+ Y release (?P<tag>\S+) at (?P<sha>[0-9a-f]{7,40}) \(archive (?P<sha256>[0-9a-f]{64})\)")

class Refused(Exception):
    pass

def run(*a, cwd=None, check=True):
    r = subprocess.run(a, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(a[:3])} exit {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
    return r

def entries_at(rev):
    """The release-entry strings on the rows at `rev` (git show), for the push filter."""
    seen = set()
    names = run("git", "ls-tree", "--name-only", f"{rev}:{ROWS}", check=False).stdout.split()
    for n in names:
        m = re.search(r"^disposed:[ \t]*(.*)$", run("git", "show", f"{rev}:{ROWS}/{n}", check=False).stdout, re.M)
        seen.update((n[:-3], e.strip()) for e in (m.group(1).split(";") if m else []))
    return seen

def entries():
    """(row, tag, sha, sha256) for every release entry on the rows main holds; a `Y release <tag> at …` entry of
    another shape comes back with empty fields, so it is refused rather than skipped."""
    out = []
    for p in sorted(ROWS.glob("*.md"), key=lambda p: (len(p.stem), p.stem)):
        m = re.search(r"^disposed:[ \t]*(.*)$", p.read_text(), re.M)
        for e in (m.group(1).split(";") if m else []):
            e, w = e.strip(), e.split()
            if w[1:3] != ["Y", "release"] or " at " not in e:
                continue
            if OLD is not None and (p.stem, e) in OLD:
                continue                           # on main before this push: processed by an earlier run
            g = ENTRY_RE.fullmatch(e)
            out.append((p.stem, g["tag"] if g else (w[3] if len(w) > 3 else ""), g["sha"] if g else "", g["sha256"] if g else ""))
    return out

def want_tag(tag, tree):
    # bundle: v + BUNDLE.md's version; core: dyad-operator-v + dyad/VERSION; craft: <craft>-v + its VERSION
    m = TAG_RE.fullmatch(tag)
    if not m:
        raise Refused(f"`{tag}` is no release tag (vX.Y.Z, dyad-operator-vX.Y.Z, <craft>-vX.Y.Z)")
    craft = m["craft"]
    if not craft:
        v = re.search(r"^version:[ \t]*(\S+)", (tree / "BUNDLE.md").read_text(), re.M)
        return "bundle", "", f"v{v.group(1) if v else '?'}"
    if craft == "dyad-operator":
        return "core", craft, f"dyad-operator-v{(tree / 'dyad/VERSION').read_text().strip()}"
    vf = tree / "crafts" / craft / "VERSION"
    if not vf.is_file():
        raise Refused(f"no craft `{craft}` at the cut sha")
    return "craft", craft, f"{craft}-v{vf.read_text().strip()}"

def tag_commit(tag):
    return run("git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}", check=False).stdout.strip()

def release_exists(tag):
    return run("gh", "api", f"repos/{REPO}/releases/tags/{tag}", check=False).returncode == 0

def build(tag, sha):
    """The one distribution code path in a worktree at the cut sha: (kind, sha256, archive files, scratch dir)."""
    tmp = pathlib.Path(tempfile.mkdtemp()); tree, out = tmp / "tree", tmp / "out"; out.mkdir()
    run("git", "worktree", "add", "-q", "--detach", str(tree), sha)
    kind, craft, want = want_tag(tag, tree)
    if want != tag:
        raise Refused(f"tag {tag} != {want} at {sha[:7]} (Rule-11 properties 4, 7)")
    ver = tag.rsplit("v", 1)[-1]
    if kind == "bundle":
        run("python3", "dyad/scripts/package.py", "bundle", "build", str(out), cwd=tree)
        digest_of = out / "BUNDLE.sha256"
    elif kind == "core":
        digest_of = out / f"dyad-{ver}.tar.gz"
        run("python3", "dyad/scripts/package.py", "build", str(digest_of), cwd=tree)
    else:
        digest_of = out / f"{craft}-{ver}.tar.gz"
        run("python3", "dyad/scripts/craft.py", "export", craft, str(digest_of), cwd=tree)
    return kind, hashlib.sha256(digest_of.read_bytes()).hexdigest(), sorted(str(f) for f in out.iterdir()), tmp

def run_url():
    return f"{os.environ.get('GITHUB_SERVER_URL', '')}/{REPO}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"

def publish(row, tag, sha, want_sha256):
    """One entry: (outcome, postcondition, detail); raises Refused, or anything else as a failure."""
    if not (tag and sha and want_sha256):
        raise Refused("a release entry is `<date> Y release <tag> at <cut sha> (archive <64-hex sha256>)`")
    full = run("git", "rev-parse", "-q", "--verify", f"{sha}^{{commit}}", check=False).stdout.strip()
    if not full or run("git", "merge-base", "--is-ancestor", full, "HEAD", check=False).returncode:
        raise Refused(f"cut sha {sha} is not a commit on main")
    at = tag_commit(tag)
    if at and at != full:
        raise Refused(f"tag {tag} exists at {at[:7]}, not {full[:7]}: tags never move")
    if at and release_exists(tag):
        return "already", "already", f"{tag} at {full[:7]} and its Release exist; nothing done"
    kind, observed, files, tmp = build(tag, full)
    if observed != want_sha256:
        raise Refused(f"archive sha256 {observed} != recorded {want_sha256}")
    if not at:
        run("git", "tag", "-a", tag, full, "-m", f"{tag} (row #{row}; released, d-work #461)")
        run("git", "push", "origin", f"refs/tags/{tag}")
    note = tmp / f"{tag}.release.json"
    note.write_text(json.dumps({"tag": tag, "row": row, "sha": full, "sha256": observed, "gate": GATE,
                                "run": run_url(), "service": os.environ.get("GITHUB_SHA", "")}, sort_keys=True) + "\n")
    run("gh", "release", "create", tag, *files, str(note), "--repo", REPO, "--verify-tag", "--title", tag,
        "--notes", f"dyad {kind} {tag}: row #{row}, cut {full[:7]}, sha256 {observed} (released, d-work #461)")
    return "released", "ok", f"{tag} at {full[:7]}: {'tag created' if not at else 'tag existed'}, Release created, sha256 {observed}"

def pending():
    """Entries the publishing job has work for: added by this push (or named by a dispatch) and not already tagged at
    their cut sha with a Release."""
    out = []
    for row, tag, sha, _ in entries():
        if ONLY and tag != ONLY:
            continue
        full = run("git", "rev-parse", "-q", "--verify", f"{sha}^{{commit}}", check=False).stdout.strip() if sha else ""
        if full and tag_commit(tag) == full and release_exists(tag):
            continue
        out.append(tag)
    return out

def main():
    if SCAN:
        p = pending()
        print(f"pending: {' '.join(p) or 'none'}")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"pending={'true' if p else 'false'}\n")
        return 0
    seen, bad = [], 0
    for row, tag, sha, want_sha256 in entries():
        if ONLY and tag != ONLY:
            continue
        try:
            outcome, _, detail = publish(row, tag, sha, want_sha256)
        except Refused as e:
            outcome, detail = "refused", str(e); bad += 1
        except Exception as e:
            outcome, detail = "failed", str(e)[-300:]; bad += 1
        seen.append((tag, row, outcome, detail))
        print(json.dumps({"tag": tag, "row": row, "outcome": outcome, "detail": detail}, sort_keys=True))
    if ONLY and not seen:
        print(f"no release entry names {ONLY}"); bad += 1
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as s:
            s.write("| tag | row | outcome | detail |\n|---|---|---|---|\n")
            s.writelines(f"| {t} | {r} | {o} | {d} |\n" for t, r, o, d in seen)
    print(f"{len(seen)} release entries")
    return 1 if bad else 0

OLD = entries_at(BEFORE) if BEFORE and set(BEFORE) != {"0"} and not ONLY else None

if __name__ == "__main__":
    sys.exit(main())
