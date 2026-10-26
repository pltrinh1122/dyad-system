"""released: the release service run by .github/workflows/dyad-release.yml (d-work #461; run-book
`workstation-corpus/runbooks/released.md`). Reads every request `<REQUESTS>/<tag>.md` on main and, for each whose row
carries the Operator's `Y release <tag>`, builds by the one code path at the cut sha, verifies the sha256 and creates the
tag and the GitHub Release; idempotent. Stdlib only; invoked by the workflow, never by the package."""
import datetime, hashlib, json, os, pathlib, re, subprocess, sys, tempfile

REQ, ONLY, REPO = pathlib.Path(os.environ["REQUESTS"]), os.environ.get("ONLY", "").strip(), os.environ["GITHUB_REPOSITORY"]
TAG_RE = re.compile(r"(?:(?P<craft>[a-z0-9][a-z0-9-]*)-)?v(?P<ver>\d+\.\d+\.\d+)")

class Refused(Exception):
    pass

def run(*a, cwd=None, check=True):
    r = subprocess.run(a, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(a[:3])} exit {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
    return r

def field(text, key):
    m = re.search(rf"^{key}:[ \t]*(\S+)[ \t]*$", text, re.M)
    return m.group(1) if m else ""

def ratified(row, tag):
    # the row on main carries `<date> Y release <tag>` as one entry of `disposed` (Rule-3 Ledger)
    p = pathlib.Path(f"agent-corpus/d-work/rows/{row}.md")
    m = re.search(r"^disposed:[ \t]*(.*)$", p.read_text(), re.M) if p.is_file() else None
    return bool(m) and any(e.split()[1:4] == ["Y", "release", tag] for e in m.group(1).split(";"))

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
    # the one distribution code path, run in a worktree at the cut sha (Rule-11 property 5)
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
    files = sorted(str(f) for f in out.iterdir())
    return kind, hashlib.sha256(digest_of.read_bytes()).hexdigest(), files, tmp

events, bad = [], 0
reqs = sorted(p for p in REQ.glob("*.md") if p.name.lower() != "readme.md") if REQ.is_dir() else []
for p in reqs:
    text = p.read_text()
    tag, sha, want_sha256, row = (field(text, k) for k in ("tag", "sha", "sha256", "row"))
    if ONLY and tag != ONLY:
        continue
    ev = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "request": str(p),
          "tag": tag, "sha": sha, "row": row, "sha256_expected": want_sha256, "sha256_observed": "",
          "gate": os.environ["GATE"], "service": os.environ["GITHUB_SHA"], "outcome": "", "detail": "",
          "run": f"{os.environ['GITHUB_SERVER_URL']}/{REPO}/actions/runs/{os.environ['GITHUB_RUN_ID']}"}
    try:
        if p.stem != tag:
            raise Refused(f"file name {p.name} does not name its tag `{tag}`")
        if not (re.fullmatch(r"[0-9a-f]{40}", sha) and re.fullmatch(r"[0-9a-f]{64}", want_sha256) and row.isdigit()):
            raise Refused("a request needs `tag:`, a 40-hex `sha:`, a 64-hex `sha256:` and a numeric `row:`")
        if not ratified(row, tag):
            raise Refused(f"row #{row} carries no `Y release {tag}` on main (Rule-11, Rule-2)")
        if run("git", "merge-base", "--is-ancestor", sha, "HEAD", check=False).returncode:
            raise Refused(f"cut sha {sha[:7]} is not on main")
        at = tag_commit(tag)
        if at and at != sha:
            raise Refused(f"tag {tag} exists at {at[:7]}, not {sha[:7]}: tags never move")
        if at and release_exists(tag):
            ev.update(outcome="already", detail="the tag at the cut sha and its Release exist; nothing done")
            continue
        kind, observed, files, tmp = build(tag, sha)
        ev["sha256_observed"] = observed
        if observed != want_sha256:
            raise Refused(f"archive sha256 {observed[:12]} != requested {want_sha256[:12]}")
        if not at:
            run("git", "tag", "-a", tag, sha, "-m", f"{tag} (d-work #{row}; released, request {p})")
            run("git", "push", "origin", f"refs/tags/{tag}")
        ev.update(outcome="released", detail=("tag created" if not at else "tag existed at the cut sha") + "; Release created")
        evf = tmp / f"{tag}.event.json"
        evf.write_text(json.dumps(ev, sort_keys=True) + "\n")
        run("gh", "release", "create", tag, *files, str(evf), "--repo", REPO, "--verify-tag", "--title", tag,
            "--notes", f"dyad {kind} {tag}: row #{row}, cut {sha[:7]}, sha256 {observed} (released, d-work #461)")
    except Refused as e:
        ev.update(outcome="refused", detail=str(e)); bad += 1
    except Exception as e:
        ev.update(outcome="failed", detail=str(e)[-400:]); bad += 1
    finally:
        events.append(ev)
        print(json.dumps(ev, sort_keys=True))

if ONLY and not events:
    print(f"no request names {ONLY}"); bad += 1
with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as s:
    s.write("| tag | row | outcome | detail |\n|---|---|---|---|\n")
    s.writelines(f"| {e['tag']} | {e['row']} | {e['outcome']} | {e['detail']} |\n" for e in events)
sys.exit(1 if bad else 0)
