"""craft.py (`dyad craft list | check | export | install`, Rule-11 p5, #156) in a scratch repo with the core craft
installed: list, check, export (file name, determinism, entries), install twice -> `0 changes`, install refuses a
modified tree without --force and --force overwrites, `requires` refused, the registry row rewritten only when
different, a failing craft is neither exported nor installed, nothing outside crafts/<name>/ + REGISTRY.md written
(A11) even when the craft declares `seeds:` (#180) — install prints a reminder for an absent seed and stays silent
once it exists, but never writes it itself."""
import hashlib, os, shutil, subprocess, sys, tarfile, tempfile, unittest
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib

GUARD = 'ENTITY, CORPUS, TRANSACTION = "widget", "workstation", False\nFIELDS = ("a",)\ndef check_package(root): return []\n'
CRAFT = {"VERSION": "0.2.0\n", "rules/r.md": "# r\n", "vocabulary/CRAFT.md": "| term | definition | rule |\n|---|---|---|\n| widget | a thing | r |\n",
         "templates/t.md": "# t\n", "guards/w.py": GUARD, "docs/d.md": "# d\n", "falsification/rules/r.md": "# rec\n"}

HOME = "/ho" + "me/pt"; MARK = "/ho" + "me/"   # a package_rules.txt marker, assembled so this file carries none (Rule-11 p1)

def env():
    return {**os.environ, "DYAD_NO_NESTED_TESTS": "1"}

def git(d, *a):
    subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True)

def scratch() -> Path:
    """A scratch git repo with the core craft installed and committed."""
    d = Path(tempfile.mkdtemp()); git(d, "init", "-q")
    r = subprocess.run([sys.executable, str(PKG / "scripts" / "package.py"), "install", str(d)], capture_output=True, text=True); assert r.returncode == 0, r.stderr
    git(d, "add", "-A"); git(d, "commit", "-qm", "scratch")
    return d

def author(d: Path, name="fx", files=CRAFT):
    for rel, text in files.items():
        f = d / "crafts" / name / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
    git(d, "add", "-A"); git(d, "commit", "-qm", f"author {name}")

def dyad(d: Path, *a):
    return subprocess.run([sys.executable, str(d / "dyad" / "scripts" / "package.py"), "craft", *a], capture_output=True, text=True, env=env(), cwd=d)

def snapshot(d: Path) -> dict[str, str]:
    return {p.relative_to(d).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in d.rglob("*") if p.is_file() and ".git/" not in p.relative_to(d).as_posix() and "__pycache__" not in p.parts}

class CraftCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = scratch(); author(cls.src)                       # the authoring system
        r = dyad(cls.src, "export", "fx", str(cls.src / "fx.tar.gz")); assert r.returncode == 0, r.stdout + r.stderr
        cls.archive = cls.src / "fx.tar.gz"
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.src, ignore_errors=True)
    def setUp(self):
        self.dst = scratch()                                        # the receiving system
    def tearDown(self):
        shutil.rmtree(self.dst, ignore_errors=True)

    def test_usage(self):
        r = dyad(self.dst); self.assertEqual(r.returncode, 2); self.assertIn("dyad craft list", r.stderr)
        r = dyad(self.dst, "export"); self.assertEqual(r.returncode, 2)
        r = dyad(self.dst, "export", "nope"); self.assertEqual(r.returncode, 2); self.assertIn("no craft crafts/nope", r.stderr)
    def test_new_scaffold_passes_check_and_is_never_overwritten(self):
        """#165: `dyad craft new <name>` scaffolds a craft that passes `craft check`; a second run refuses; names are checked."""
        r = dyad(self.dst, "new", "zzz"); self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("scaffolded crafts/zzz 0.1.0", r.stdout)
        d = self.dst / "crafts" / "zzz"
        for rel in ("VERSION", "README.md", "rules/README.md", "vocabulary/CRAFT.md", "templates/README.md", "guards/README.md", "docs/README.md", "falsification/rules/README.md"):
            self.assertTrue((d / rel).is_file(), rel)
        self.assertEqual((d / "VERSION").read_text(), "0.1.0\n")
        r = dyad(self.dst, "check", "zzz"); self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertIn("ok   [craft] crafts/zzz 0.1.0", r.stdout)
        r = dyad(self.dst, "list"); self.assertIn("zzz", r.stdout); self.assertIn("authored", r.stdout)
        before = snapshot(self.dst)
        r = dyad(self.dst, "new", "zzz"); self.assertEqual(r.returncode, 2); self.assertIn("exists; not overwritten", r.stderr); self.assertEqual(snapshot(self.dst), before)
        for bad in ("Zzz", "1x", "a_b", "dyad-operator"):
            r = dyad(self.dst, "new", bad); self.assertEqual(r.returncode, 2, bad)
        r = dyad(self.dst, "new"); self.assertEqual(r.returncode, 2)
    def test_list_authored_and_core(self):
        r = dyad(self.src, "list")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = [l.split() for l in r.stdout.splitlines()]
        self.assertEqual(lines[0], ["craft", "version", "origin"]); self.assertEqual(lines[1][:3], ["dyad-operator", (PKG / "VERSION").read_text().strip(), "core"])
        self.assertEqual(lines[2], ["fx", "0.2.0", "authored"])
    def test_check(self):
        r = dyad(self.src, "check", "fx"); self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("ok   [craft] crafts/fx 0.2.0", r.stdout)
        r = dyad(self.src, "check"); self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("ok   [craft] crafts/fx 0.2.0", r.stdout)
        r = dyad(self.src, "check", "nope"); self.assertEqual(r.returncode, 2)
    def test_export_name_entries_and_determinism(self):
        r = dyad(self.src, "export", "fx"); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("exported crafts/fx 0.2.0 -> fx-0.2.0.tar.gz", r.stdout); self.assertTrue((self.src / "fx-0.2.0.tar.gz").exists())
        self.assertEqual(hashlib.sha256((self.src / "fx-0.2.0.tar.gz").read_bytes()).hexdigest(), hashlib.sha256(self.archive.read_bytes()).hexdigest())
        with tarfile.open(self.archive) as tar:
            self.assertEqual(tar.getnames(), sorted(f"crafts/fx/{k}" for k in CRAFT))
    def test_failing_craft_not_exported_nor_installed(self):
        bad = scratch(); author(bad, files={**CRAFT, "docs/d.md": f"backups at {HOME}/b\n"})
        r = dyad(bad, "export", "fx", str(bad / "bad.tar.gz")); self.assertEqual(r.returncode, 1); self.assertIn(f"host-specific string '{MARK}'", r.stderr); self.assertIn("not exported", r.stderr)
        self.assertFalse((bad / "bad.tar.gz").exists())
        r = dyad(self.dst, "install", str(bad / "crafts" / "fx")); self.assertEqual(r.returncode, 1); self.assertIn("not installed", r.stderr)
        self.assertFalse((self.dst / "crafts").exists()); shutil.rmtree(bad, ignore_errors=True)
    def test_install_twice_writes_only_the_craft_and_registry(self):
        before = snapshot(self.dst)
        r = dyad(self.dst, "install", str(self.archive), "--dwork", "156")
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), f"installed crafts/fx 0.2.0: {len(CRAFT) + 1} changes")
        after = snapshot(self.dst)
        self.assertEqual({k for k in after if k not in before or after[k] != before[k]}, {f"crafts/fx/{k}" for k in CRAFT} | {"crafts/REGISTRY.md"})   # A11: nothing else
        reg = (self.dst / "crafts" / "REGISTRY.md").read_text()
        self.assertIn("| craft | version | source | sha256 | d-work |", reg)
        row = [l for l in reg.splitlines() if l.startswith("| fx |")][0].split("|")
        self.assertEqual([c.strip() for c in row[1:6]], ["fx", "0.2.0", "fx.tar.gz", row[4].strip(), "#156"]); self.assertEqual(len(row[4].strip()), 64)
        r = dyad(self.dst, "install", str(self.archive)); self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "installed crafts/fx 0.2.0: 0 changes")
        self.assertEqual(snapshot(self.dst), after)   # the registry row is rewritten only when different (d-work kept)
        r = dyad(self.dst, "list"); self.assertIn(f"fx               0.2.0      installed {row[4].strip()[:8]}", r.stdout)
        self.assertFalse((self.dst / "CLAUDE.md").read_text().count("@dyad/CLAUDE.md") > 1)
    def test_seeds_are_advisory_never_written(self):
        """#180: `seeds:` is read-only metadata. Install still writes only crafts/fx/** + REGISTRY.md (A11
        extended); it prints a reminder naming the `cp` to run while the destination is absent, and falls
        silent once the Operator has copied it by hand — nothing here ever creates the destination file."""
        src2 = scratch(); author(src2, files={**CRAFT, "MANIFEST.md": "name: fx\nseeds: t.md->workstation-corpus/fx-seed.md\n"})
        r = dyad(src2, "check", "fx"); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = dyad(src2, "export", "fx", str(src2 / "fx.tar.gz")); self.assertEqual(r.returncode, 0, r.stderr)
        before = snapshot(self.dst)
        r = dyad(self.dst, "install", str(src2 / "fx.tar.gz"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("installed crafts/fx 0.2.0:", r.stdout)
        self.assertIn("warn [craft] crafts/fx: seed 't.md' not copied to workstation-corpus/fx-seed.md — copy it by hand: "
                       "cp crafts/fx/templates/t.md workstation-corpus/fx-seed.md", r.stdout)
        after = snapshot(self.dst)
        self.assertEqual({k for k in after if k not in before or after[k] != before[k]},
                          {f"crafts/fx/{k}" for k in CRAFT} | {"crafts/fx/MANIFEST.md", "crafts/REGISTRY.md"})   # A11: nothing else, seeds included
        self.assertFalse((self.dst / "workstation-corpus" / "fx-seed.md").exists())   # never written by install
        (self.dst / "workstation-corpus").mkdir(exist_ok=True); (self.dst / "workstation-corpus" / "fx-seed.md").write_text("seeded by hand\n")
        r = dyad(self.dst, "install", str(src2 / "fx.tar.gz"))
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "installed crafts/fx 0.2.0: 0 changes")
        self.assertNotIn("warn [craft]", r.stdout)   # destination now present: no more reminder
        shutil.rmtree(src2, ignore_errors=True)
    def test_install_refuses_modified_tree_unless_forced(self):
        dyad(self.dst, "install", str(self.archive))
        (self.dst / "crafts/fx/docs/d.md").write_text("# local edit\n"); (self.dst / "crafts/fx/local.md").write_text("mine\n")
        r = dyad(self.dst, "list"); self.assertIn("(modified)", r.stdout)
        r = dyad(self.dst, "install", str(self.archive)); self.assertEqual(r.returncode, 1); self.assertIn("locally modified or authored here; `--force` overwrites", r.stderr)
        self.assertEqual((self.dst / "crafts/fx/docs/d.md").read_text(), "# local edit\n"); self.assertTrue((self.dst / "crafts/fx/local.md").exists())
        r = dyad(self.dst, "install", str(self.archive), "--force"); self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "installed crafts/fx 0.2.0: 2 changes")   # rewrite + prune (A18)
        self.assertEqual((self.dst / "crafts/fx/docs/d.md").read_text(), "# d\n"); self.assertFalse((self.dst / "crafts/fx/local.md").exists())
        r = dyad(self.dst, "list"); self.assertNotIn("(modified)", r.stdout)
    def test_install_refuses_authored_craft(self):
        author(self.dst)   # the same name authored here: no registry row
        r = dyad(self.dst, "install", str(self.archive)); self.assertEqual(r.returncode, 1); self.assertIn("locally modified or authored here", r.stderr)
    def test_new_version_prunes_dropped_file(self):
        dyad(self.dst, "install", str(self.archive))
        v2 = {k: v for k, v in CRAFT.items() if k != "docs/d.md"}; v2["VERSION"] = "0.3.0\n"; v2["docs/e.md"] = "# e\n"
        src2 = scratch(); author(src2, files=v2)
        r = dyad(src2, "export", "fx", str(src2 / "fx2.tar.gz")); self.assertEqual(r.returncode, 0, r.stderr)
        r = dyad(self.dst, "install", str(src2 / "fx2.tar.gz")); self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "installed crafts/fx 0.3.0: 4 changes")   # VERSION, e.md, -d.md, row
        self.assertFalse((self.dst / "crafts/fx/docs/d.md").exists()); self.assertTrue((self.dst / "crafts/fx/docs/e.md").exists())
        self.assertIn("| fx | 0.3.0 | fx2.tar.gz |", (self.dst / "crafts/REGISTRY.md").read_text()); shutil.rmtree(src2, ignore_errors=True)
    def test_requires_refused_at_install_and_met(self):
        src2 = scratch(); author(src2, files={**CRAFT, "MANIFEST.md": "name: fx\nrequires: syseng>=0.2.0 dyad-operator>=0.1.0\n"})
        r = dyad(src2, "check", "fx"); self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("warn [craft] crafts/fx: requires syseng>=0.2.0: not installed (checked at install)", r.stdout)
        r = dyad(src2, "export", "fx", str(src2 / "fx.tar.gz")); self.assertEqual(r.returncode, 0, r.stderr)
        r = dyad(self.dst, "install", str(src2 / "fx.tar.gz")); self.assertEqual(r.returncode, 1)
        self.assertIn("requires syseng>=0.2.0: not installed", r.stderr); self.assertIn("requirements unmet", r.stderr); self.assertFalse((self.dst / "crafts").exists())
        author(self.dst, name="syseng", files={**CRAFT, "VERSION": "0.2.0\n"})
        r = dyad(self.dst, "install", str(src2 / "fx.tar.gz")); self.assertEqual(r.returncode, 0, r.stderr); shutil.rmtree(src2, ignore_errors=True)
    def test_install_from_directory_and_repo_root(self):
        r = dyad(self.dst, "install", str(self.src / "crafts" / "fx"), "--source", "the-src-repo"); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("| fx | 0.2.0 | the-src-repo |", (self.dst / "crafts/REGISTRY.md").read_text())
        r = dyad(self.dst, "install", str(self.src), "--craft", "fx", "--source", "the-src-repo"); self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(r.stdout.strip(), "installed crafts/fx 0.2.0: 0 changes")
        r = dyad(self.dst, "install", str(self.src)); self.assertEqual(r.returncode, 2); self.assertIn("needs --craft", r.stderr)
        r = dyad(self.dst, "install", str(self.src / "nope")); self.assertEqual(r.returncode, 2); self.assertIn("no such source", r.stderr)
    def test_check_in_receiving_repo_after_install(self):
        dyad(self.dst, "install", str(self.archive)); git(self.dst, "add", "-A"); git(self.dst, "commit", "-qm", "craft")
        r = subprocess.run([sys.executable, str(self.dst / "dyad" / "scripts" / "package.py"), "check", "--guards"], capture_output=True, text=True, env=env())
        self.assertIn("ok   [guards] craft/crafts (1 craft(s))", r.stdout); self.assertIn("ok   [guards] fx/w", r.stdout)   # the craft guard and the craft's guard run there
        self.assertFalse(any("FAIL [guards] craft/" in l or "FAIL [guards] fx/" in l for l in r.stdout.splitlines()), r.stdout)
        # (the whole run is not asserted: Rules 8, 18, 19 name `crafts/sysadmin/…` paths, which references.py skips only on a core-only install — Rule-20, outside #156)


class InvariantTests(unittest.TestCase):
    def test_invariants_hold(self):
        craft = dyadlib.load_module(PKG / "scripts" / "craft.py", "craft")
        self.assertEqual(dyadlib.check_invariants(craft), len(craft.INVARIANTS)); self.assertEqual(len(craft.INVARIANTS), 2)

if __name__ == "__main__":
    unittest.main()
