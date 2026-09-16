"""distribute.py (the one distribution code path, Rule-11 p5, #156): two builds byte-identical; a modified tree
differs; install into a scratch repo then again -> 0; prune removes a dropped file; hooks seed templates and the
import line, hooks=None writes nothing outside the roots; extract refuses unsafe members; instance_state."""
import hashlib, os, shutil, subprocess, sys, tarfile, tempfile, time, unittest
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import distribute

def repo(files: dict[str, str], exe=()) -> Path:
    d = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q", str(d)], check=True)
    for rel, text in files.items():
        f = d / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
        if rel in exe: f.chmod(0o755)
    subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], check=True)
    return d

TREE = {"crafts/x/VERSION": "0.1.0\n", "crafts/x/rules/a.md": "# a\n", "crafts/x/guards/g.py": "ENTITY='g'\n", "crafts/x/bin/run": "#!/bin/sh\n",
        "dyad/VERSION": "0.1.0\n", "dyad/templates/T.md": "# seed\n", "dyad/README.md": "core\n", "README.md": "host\n", ".github/workflows/dyad-x.yml": "name: x\n"}

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.r = repo(TREE, exe=("crafts/x/bin/run",))
    def tearDown(self):
        shutil.rmtree(self.r, ignore_errors=True)
    def test_files_tracked_sorted_and_roots(self):
        self.assertEqual(distribute.files(self.r, ["crafts/x"]), ["crafts/x/VERSION", "crafts/x/bin/run", "crafts/x/guards/g.py", "crafts/x/rules/a.md"])
        (self.r / "crafts/x/untracked.txt").write_text("u")
        self.assertNotIn("crafts/x/untracked.txt", distribute.files(self.r, ["crafts/x"]))            # tracked only in a repo
        self.assertIn("crafts/x/untracked.txt", distribute.files(self.r, ["crafts/x"], tracked=False))   # the tree on disk
        self.assertEqual(distribute.files(self.r, ["dyad"], extra=[".github/workflows/dyad-x.yml"])[0], ".github/workflows/dyad-x.yml")
    def test_two_builds_byte_identical_despite_mtimes(self):
        a = distribute.archive_bytes(self.r, ["crafts/x"])
        for f in (self.r / "crafts/x").rglob("*"):
            if f.is_file(): os.utime(f, (1, 1))   # file mtimes must not leak (attack A16)
        time.sleep(0.01)
        b = distribute.archive_bytes(self.r, ["crafts/x"])
        self.assertEqual(hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest())
        self.assertEqual(distribute.archive_sha256(self.r, ["crafts/x"]), hashlib.sha256(a).hexdigest())
    def test_archive_entries_normalized(self):
        out = distribute.build(self.r, ["crafts/x"], self.r / "x.tar.gz")
        with tarfile.open(out) as tar:
            names = tar.getnames(); infos = tar.getmembers()
        self.assertEqual(names, ["crafts/x/VERSION", "crafts/x/bin/run", "crafts/x/guards/g.py", "crafts/x/rules/a.md"])
        self.assertEqual({(i.mtime, i.uid, i.gid, i.uname, i.gname) for i in infos}, {(0, 0, 0, "", "")})
        self.assertEqual({i.name: i.mode for i in infos}["crafts/x/bin/run"], 0o755); self.assertEqual({i.name: i.mode for i in infos}["crafts/x/VERSION"], 0o644)
        self.assertEqual(out.read_bytes()[4:8], b"\0\0\0\0")   # gzip header mtime 0
    def test_modified_tree_differs(self):
        a = distribute.archive_sha256(self.r, ["crafts/x"])
        (self.r / "crafts/x/rules/a.md").write_text("# changed\n")
        self.assertNotEqual(a, distribute.archive_sha256(self.r, ["crafts/x"]))
    def test_extract_refuses_unsafe_members(self):
        bad = self.r / "bad.tar.gz"
        with tarfile.open(bad, "w:gz") as tar:
            info = tarfile.TarInfo("../evil"); info.size = 0; tar.addfile(info)
        with self.assertRaises(ValueError):
            distribute.extract(bad, Path(tempfile.mkdtemp()))

class InstallTests(unittest.TestCase):
    def setUp(self):
        self.src = repo(TREE, exe=("crafts/x/bin/run",)); self.dst = Path(tempfile.mkdtemp())
    def tearDown(self):
        shutil.rmtree(self.src, ignore_errors=True); shutil.rmtree(self.dst, ignore_errors=True)
    def test_install_then_again_is_zero(self):
        n = distribute.install(self.src, self.dst, ["crafts/x"])
        self.assertEqual(n, 4); self.assertTrue((self.dst / "crafts/x/rules/a.md").exists())
        self.assertTrue(os.access(self.dst / "crafts/x/bin/run", os.X_OK))
        self.assertEqual(distribute.install(self.src, self.dst, ["crafts/x"]), 0)
        self.assertEqual(sorted(p.relative_to(self.dst).as_posix() for p in self.dst.rglob("*") if p.is_file()), distribute.files(self.src, ["crafts/x"]))   # nothing outside the roots (A11)
    def test_install_from_archive_equals_install_from_tree(self):
        arc = distribute.build(self.src, ["crafts/x"], self.src / "x.tar.gz")
        distribute.install(arc, self.dst, ["crafts/x"])
        self.assertEqual(distribute.install(self.src, self.dst, ["crafts/x"]), 0)
        self.assertEqual(distribute.archive_sha256(self.dst, ["crafts/x"], tracked=False), distribute.archive_sha256(self.src, ["crafts/x"]))
    def test_prune_removes_dropped_file_and_empty_dir(self):
        distribute.install(self.src, self.dst, ["crafts/x"])
        (self.dst / "crafts/x/old/stale.md").parent.mkdir(); (self.dst / "crafts/x/old/stale.md").write_text("old")
        self.assertEqual(distribute.install(self.src, self.dst, ["crafts/x"]), 0)               # no prune: kept
        self.assertEqual(distribute.install(self.src, self.dst, ["crafts/x"], prune=True), 1)   # prune: removed
        self.assertFalse((self.dst / "crafts/x/old").exists()); self.assertTrue((self.dst / "crafts/x").is_dir())
    def test_hooks_seed_templates_and_import_line_once(self):
        hooks = distribute.Hooks(templates={"T.md": "inst/T.md"}, import_line="@dyad/CLAUDE.md")
        n = distribute.install(self.src, self.dst, ["dyad"], hooks=hooks, extra=[".github/workflows/dyad-x.yml"])
        self.assertEqual(n, 3 + 1 + 1 + 1)   # 3 dyad files, the workflow, the seed, the import line
        self.assertEqual((self.dst / "inst/T.md").read_text(), "# seed\n"); self.assertEqual((self.dst / "CLAUDE.md").read_text(), "@dyad/CLAUDE.md\n")
        (self.dst / "inst/T.md").write_text("edited")
        self.assertEqual(distribute.install(self.src, self.dst, ["dyad"], hooks=hooks, extra=[".github/workflows/dyad-x.yml"]), 0)
        self.assertEqual((self.dst / "inst/T.md").read_text(), "edited")   # a seed never overwrites (p2)
    def test_no_hooks_writes_nothing_outside_roots(self):
        distribute.install(self.src, self.dst, ["crafts/x"], hooks=None)
        self.assertFalse((self.dst / "CLAUDE.md").exists()); self.assertEqual([p.name for p in self.dst.iterdir()], ["crafts"])

def index_mode(r: Path, rel: str) -> str | None:
    out = subprocess.run(["git", "-C", str(r), "ls-files", "-s", "--", rel], capture_output=True, text=True).stdout.split()
    return out[0] if out else None

def force_index_mode(r: Path, rel: str, executable: bool) -> None:
    """Set the index bit directly, decoupled from whatever the disk bit says — the shape of a
    `core.fileMode=false` checkout (module docstring; #196 d-work #6), reproducible on any filesystem."""
    subprocess.run(["git", "-C", str(r), "update-index", "--add", "--chmod=" + ("+x" if executable else "-x"), "--", rel], check=True, capture_output=True)

class ModeTests(unittest.TestCase):
    """The bug this d-work fixes (workstation#173): `_mode()` read the disk bit, which a
    `core.fileMode=false` checkout (NTFS) decouples from the index — every file reads executable
    there regardless of what git records. These force an index/disk disagreement directly, so the
    fix is verified on any filesystem, not only a broken mount."""
    def setUp(self):
        self.r = repo(TREE, exe=("crafts/x/bin/run",))
        subprocess.run(["git", "-C", str(self.r), "config", "core.fileMode", "false"], check=True)
    def tearDown(self):
        shutil.rmtree(self.r, ignore_errors=True)
    def test_git_modes_reads_the_index_not_the_disk(self):
        force_index_mode(self.r, "crafts/x/bin/run", executable=False)   # disk still 755 (repo() chmod'd it); index now says not
        self.assertTrue(os.access(self.r / "crafts/x/bin/run", os.X_OK), "fixture sanity: disk bit still says executable")
        modes = distribute.git_modes(self.r, ["crafts/x"])
        self.assertEqual(modes["crafts/x/bin/run"], 0o644)   # the index wins
        self.assertEqual(modes["crafts/x/VERSION"], 0o644)
    def test_git_modes_not_a_work_tree_is_empty(self):
        self.assertEqual(distribute.git_modes(Path(tempfile.mkdtemp()), ["x"]), {})
    def test_archive_bytes_uses_index_mode_despite_disk(self):
        force_index_mode(self.r, "crafts/x/bin/run", executable=False)
        out = distribute.build(self.r, ["crafts/x"], self.r / "x.tar.gz")
        with tarfile.open(out) as tar:
            modes = {i.name: i.mode for i in tar.getmembers()}
        self.assertEqual(modes["crafts/x/bin/run"], 0o644, "disk says executable; the index (not-executable) must win")
    def test_archive_modes_reads_tar_members(self):
        out = distribute.build(self.r, ["crafts/x"], self.r / "x.tar.gz")
        modes = distribute.archive_modes(out)
        self.assertEqual(modes["crafts/x/bin/run"], 0o755); self.assertEqual(modes["crafts/x/VERSION"], 0o644)
    def test_install_from_archive_stages_the_dest_index_bit(self):
        arc = distribute.build(self.r, ["crafts/x"], self.r / "x.tar.gz")
        dst = repo({"README.md": "x\n"})   # a work tree (so install can stage the bit); needs one file for an initial commit
        subprocess.run(["git", "-C", str(dst), "config", "core.fileMode", "false"], check=True)
        try:
            distribute.install(arc, dst, ["crafts/x"])
            self.assertEqual(index_mode(dst, "crafts/x/bin/run"), "100755")
            self.assertEqual(index_mode(dst, "crafts/x/VERSION"), "100644")
            self.assertEqual(distribute.install(arc, dst, ["crafts/x"]), 0)   # idempotent: index already matches
        finally:
            shutil.rmtree(dst, ignore_errors=True)
    def test_install_idempotent_reads_dest_index_not_dest_disk(self):
        # dest already has the right content and index mode; only the disk bit lies (as fileMode=false lets it) —
        # a second install must still report 0, not rewrite based on a disk-bit mismatch that means nothing here
        dst = repo(TREE, exe=("crafts/x/bin/run",))
        subprocess.run(["git", "-C", str(dst), "config", "core.fileMode", "false"], check=True)
        try:
            distribute.install(self.r, dst, ["crafts/x"])
            (dst / "crafts/x/bin/run").chmod(0o644)   # corrupt the disk bit only; the index still says 755
            self.assertEqual(distribute.install(self.r, dst, ["crafts/x"]), 0)
        finally:
            shutil.rmtree(dst, ignore_errors=True)

class InstanceStateTests(unittest.TestCase):
    HOME = "/ho" + "me/pt"; MARK = "/ho" + "me/"   # assembled: the test file must not itself carry a package_rules.txt marker (Rule-11 p1)
    RULES = {"string": [HOME], "name": ["CHANGELOG.md", ".jsonl"], "header": ["# Host change log"], "generated": []}
    def test_markers(self):
        r = repo({"crafts/x/VERSION": "0.1.0\n", "crafts/x/docs/h.md": f"see {self.HOME}/x\n", "crafts/x/templates/CHANGELOG.md": "# Host change log\n",
                  "crafts/x/CHANGELOG.md": "# Host change log\n", "crafts/x/events/e.jsonl": "{}\n", "crafts/x/rows/1.md": "id: 1\n"})
        fails = distribute.instance_state(r, ["crafts/x"], self.RULES, names=["events/", "rows/", "REGISTRY.md"], what="a craft")
        self.assertTrue(any(f.startswith(f"crafts/x/docs/h.md: host-specific string '{self.HOME}'") for f in fails), fails)
        self.assertTrue(any(f.startswith("crafts/x/CHANGELOG.md: instance artifact by name") for f in fails), fails)
        self.assertTrue(any(f.startswith("crafts/x/CHANGELOG.md: instance artifact by header") for f in fails), fails)
        self.assertTrue(any("events/e.jsonl: instance store directory 'events/'" in f for f in fails), fails)
        self.assertTrue(any("rows/1.md: instance store directory 'rows/'" in f for f in fails), fails)
        self.assertFalse(any("templates/" in f for f in fails), fails)   # seeds exempt
        self.assertTrue(all("inside a craft" in f for f in fails))
        shutil.rmtree(r, ignore_errors=True)
    def test_clean_tree_passes(self):
        r = repo({"crafts/x/VERSION": "0.1.0\n", "crafts/x/rules/a.md": "# a\n"})
        self.assertEqual(distribute.instance_state(r, ["crafts/x"], self.RULES), [])
        shutil.rmtree(r, ignore_errors=True)


class InvariantTests(unittest.TestCase):
    def test_invariants_hold(self):
        import dyadlib
        self.assertEqual(dyadlib.check_invariants(distribute), len(distribute.INVARIANTS)); self.assertEqual(len(distribute.INVARIANTS), 2)

if __name__ == "__main__":
    unittest.main()
