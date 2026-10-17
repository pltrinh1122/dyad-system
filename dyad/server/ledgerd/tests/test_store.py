"""ledgerd/store.py: the store-adapter seam — `git` (a mirror clone whose pin advances on a new commit, a tree
extracted at a pin without any working tree, the credential-helper line present with `<state>/credentials` and
absent without), `dir` (a pin that moves on content and not on a touch), `module:<path>` (loaded by path, checked
against the contract) and the selection. Importing the module runs its INVARIANTS (verifiable-code.md p5)."""
import os, time, unittest
from pathlib import Path
import support
from support import Case
if not support.MISSING:
    from ledgerd import store

class ContractTests(Case):
    def test_contract_and_schemes(self):
        self.assertEqual(store.STORE_CONTRACT, ("SCHEME", "open")); self.assertEqual(store.STORE_OBJECT, ("pin", "tree", "describe"))
        self.assertIsNone(store.store_problem(store.GitStore)); self.assertIsNone(store.store_problem(store.DirStore))
        class Bad: SCHEME = "x"
        self.assertIn("lacks open", store.store_problem(Bad))
        class Obj: pin = describe = lambda self: ""
        self.assertIn("lacks tree", store.object_problem(Obj()))
    def test_split_git_url(self):
        self.assertEqual(store.split_git_url("git+https://x/y.git#dev"), ("https://x/y.git", "dev"))
        self.assertEqual(store.split_git_url("git+file:///r"), ("file:///r", "main"))
        self.assertEqual(store.split_git_url("https://x/y.git"), ("https://x/y.git", "main"))

class DirStoreTests(Case):
    def test_pin_moves_on_content_not_on_touch(self):
        d = support.instance(self.scratch())
        s = store.open_store(f"file://{d}", None, ("agent-corpus/d-work",))
        self.assertEqual(s.SCHEME, "dir"); self.assertTrue(s.describe().startswith("dir:"))
        p1 = s.pin()
        f = d / "agent-corpus" / "d-work" / "rows" / "1.md"
        os.utime(f, (time.time() + 100, time.time() + 100))
        self.assertEqual(s.pin(), p1, "a touch is not a change")
        f.write_text(f.read_text().replace("first open row", "first open row, edited"))
        self.assertNotEqual(s.pin(), p1, "content is")
        (d / "README.md").write_text("outside the stores\n")
        self.assertEqual(s.pin(), s.pin()); self.assertNotEqual(s.pin(), p1)
        self.assertEqual(s.tree(s.pin(), s.paths), d.resolve())
        self.assertEqual(store.pin_label(s, s.pin()), "dir:" + s.pin()[:16])
    def test_bare_path_and_missing_dir(self):
        d = self.scratch()
        self.assertEqual(store.DirStore.open(str(d)).root, d.resolve())
        with self.assertRaises(ValueError):
            store.DirStore.open(str(d / "nope"))
    def test_digest_covers_names_and_bytes(self):
        d = self.scratch(); (d / "s").mkdir(); (d / "s" / "a").write_text("x")
        one = store.dir_digest(d, ["s"])
        (d / "s" / "a").rename(d / "s" / "b")
        self.assertNotEqual(store.dir_digest(d, ["s"]), one)

class GitStoreTests(Case):
    def test_pin_advances_on_a_new_commit_and_tree_is_extracted(self):
        repo = support.instance(self.scratch()); state = self.scratch()
        s = store.open_store(f"git+file://{repo}#main", state, ("agent-corpus/d-work",))
        self.assertEqual(s.SCHEME, "git"); self.assertTrue((state / store.CLONE_DIR / "HEAD").is_file())
        self.assertEqual(s.describe(), f"git:file://{repo}#main")
        p1 = s.pin(); self.assertEqual(len(p1), 40)
        head2 = support.add_row(repo, 7, "a new row")
        self.assertEqual(s.pin(), head2); self.assertNotEqual(head2, p1)
        t = s.tree(p1, ("agent-corpus/d-work", "workstation-corpus/runbooks/events", "nowhere/at/all"))
        self.addCleanup(store.remove_tree, t)
        self.assertTrue(store.is_temporary(t))
        self.assertTrue((t / "agent-corpus" / "d-work" / "rows" / "1.md").is_file())
        self.assertFalse((t / "agent-corpus" / "d-work" / "rows" / "7.md").exists(), "the tree is the pin's, not HEAD's")
        self.assertTrue((t / "workstation-corpus" / "runbooks" / "events" / "x.jsonl").is_file())
        self.assertFalse((t / "README.md").exists(), "only the named paths")
        t2 = s.tree(head2, ("agent-corpus/d-work",)); self.addCleanup(store.remove_tree, t2)
        self.assertTrue((t2 / "agent-corpus" / "d-work" / "rows" / "7.md").is_file())
        self.assertEqual(store.pin_label(s, p1), f"git:{p1}")
    def test_open_twice_reuses_the_clone(self):
        repo = support.instance(self.scratch()); state = self.scratch()
        store.open_store(f"git+file://{repo}", state); mtime = (state / store.CLONE_DIR / "HEAD").stat().st_mtime
        s = store.open_store(f"git+file://{repo}", state)
        self.assertEqual((state / store.CLONE_DIR / "HEAD").stat().st_mtime, mtime); self.assertEqual(s.ref, "main")
    def test_local_reads_a_repository_in_place(self):
        repo = support.instance(self.scratch())
        head = support.git(repo, "rev-parse", "HEAD").strip()
        s = store.GitStore.local(repo, head[:10])
        self.assertEqual(s.pin(), head); self.assertFalse(s.fetch)
        t = s.tree(head, ("agent-corpus/d-work",)); self.addCleanup(store.remove_tree, t)
        self.assertTrue((t / "agent-corpus" / "d-work" / "plans" / "2.md").is_file())
    def test_credential_helper_line_present_with_the_file_and_absent_without(self):
        state = self.scratch()
        self.assertEqual(store.git_argv(state), ["git"]); self.assertEqual(store.git_argv(None), ["git"])
        (state / store.CREDENTIALS).write_text("https://x-access-token:t@github.com\n")
        argv = store.git_argv(state)
        self.assertEqual(argv, ["git", "-c", f"credential.helper=store --file {state / store.CREDENTIALS}"])
        self.assertNotIn("t@github", " ".join(argv), "the token never reaches a command line")
    def test_unknown_ref_fails_loud(self):
        repo = support.instance(self.scratch()); state = self.scratch()
        s = store.open_store(f"git+file://{repo}#no-such-branch", state)
        with self.assertRaises(RuntimeError):
            s.pin()

class ModuleStoreTests(Case):
    def test_module_adapter_by_path(self):
        d = self.scratch(); p = d / "mystore.py"
        p.write_text('SCHEME = "mem"\nclass Obj:\n    def pin(self): return "p1"\n    def tree(self, pin, paths): return "/"\n    def describe(self): return "mem:"\n'
                     'def open(url, state, paths=()): return Obj()\n')
        s = store.open_store(f"module:{p}", None, ())
        self.assertEqual((s.pin(), s.describe()), ("p1", "mem:")); self.assertEqual(store.pin_label(s, "p1"), "store:p1")
    def test_module_missing_contract_is_refused(self):
        d = self.scratch(); p = d / "bad.py"; p.write_text("SCHEME = 'x'\n")
        with self.assertRaises(ValueError) as cm:
            store.adapter_for(f"module:{p}")
        self.assertIn("lacks open", str(cm.exception))
        with self.assertRaises(ValueError):
            store.adapter_for("module:/nowhere.py")
    def test_module_whose_object_lacks_a_method_is_refused(self):
        d = self.scratch(); p = d / "half.py"; p.write_text("SCHEME = 'h'\nclass O:\n    def pin(self): return 'x'\ndef open(url, state, paths=()): return O()\n")
        with self.assertRaises(ValueError) as cm:
            store.open_store(f"module:{p}", None)
        self.assertIn("lacks tree, describe", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
