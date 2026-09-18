import contextlib, io, os, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
ops = dyadlib.load_guard("workstation", "ops_scripts")

GOOD = """#!/usr/bin/env bash
# d-work: #126
# class: reversible
# undo: btrfs subvolume delete /srv/git
# change-log: 2026-09-14 #126 H1
# postcondition: /srv/git is a btrfs subvolume with nodatacow
# destructive: none
set -euo pipefail
git rev-parse --short HEAD; sha256sum "$0"
postcondition() { lsattr -d /srv/git | cut -c1-21 | grep -q C; }
postcondition && { echo "already satisfied"; exit 0; }
set -x
sudo btrfs subvolume show /srv/git >/dev/null 2>&1 || sudo btrfs subvolume create /srv/git
set +x
postcondition
"""

DESTRUCTIVE = GOOD.replace("# destructive: none", "# destructive: deletes /srv/git subvolume").replace(
    "set -x\n",
    'confirm() { echo "$1"; read -r -p "Y/N: " ans < /dev/tty; [[ $ans == Y ]] || { echo "declined"; exit 2; }; }\n'
    '[[ -t 0 ]] || { echo "no tty"; exit 2; }\nset -x\n'
    'sudo btrfs subvolume show /srv/old >/dev/null 2>&1 && { confirm "delete /srv/old; no undo"; sudo btrfs subvolume delete /srv/old; }\n')

def fixture(scripts: dict[str, str] | None, mode: int = 0o755, index: str | None = dyadlib.MODE_EXEC) -> Path:
    """A scratch **git** repo with (optionally) an ops dir under the default DYAD_OPS path. `mode` is the
    bit on disk, `index` the mode git records — set explicitly (`update-index --chmod`) so the two can
    disagree as they do on an NTFS checkout with `core.fileMode=false` (#135, #141); `index=None` leaves
    the scripts untracked."""
    root = Path(tempfile.mkdtemp(prefix="dyad-ops-"))
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    if scripts is not None:
        d = ops.ops_dir(root); d.mkdir(parents=True)
        for name, text in scripts.items():
            p = d / name; p.write_text(text); p.chmod(mode)
        if index is not None and scripts:
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "update-index",
                            f"--chmod={'+' if index == dyadlib.MODE_EXEC else '-'}x", "--", *[f"{ops.ops_dir(root).relative_to(root)}/{n}" for n in scripts]], check=True)
    return root

class OpsScriptTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("DYAD_OPS", None)
    def test_good_script_passes(self):
        self.assertEqual(ops.check_package(fixture({"126-h1-x.sh": GOOD})), [])
    def test_no_ops_dir_passes(self):
        self.assertEqual(ops.check_package(fixture(None)), [])
    def test_empty_ops_dir_passes(self):
        self.assertEqual(ops.check_package(fixture({})), [])
    def test_missing_header_fails(self):
        msgs = ops.check_package(fixture({"a.sh": GOOD.replace("# undo: btrfs subvolume delete /srv/git\n", "")}))
        self.assertEqual(len(msgs), 1); self.assertIn("`# undo:`", msgs[0])
    def test_missing_postcondition_header_fails(self):
        msgs = ops.check_package(fixture({"a.sh": GOOD.replace("# postcondition: /srv/git is a btrfs subvolume with nodatacow\n", "")}))
        self.assertEqual(len(msgs), 1); self.assertIn("`# postcondition:`", msgs[0])
    def test_missing_postcondition_function_fails(self):
        text = GOOD.replace("postcondition() { lsattr -d /srv/git | cut -c1-21 | grep -q C; }\n", "")
        msgs = ops.check_package(fixture({"a.sh": text}))
        self.assertEqual(len(msgs), 2)
        self.assertTrue(any("no `postcondition()` function" in m for m in msgs))
        self.assertTrue(any("named 2 time(s)" in m for m in msgs))
    def test_single_postcondition_call_fails(self):
        text = GOOD.replace("postcondition && { echo \"already satisfied\"; exit 0; }\n", "")
        msgs = ops.check_package(fixture({"a.sh": text}))
        self.assertEqual(len(msgs), 1); self.assertIn("named 2 time(s) in code, need 3", msgs[0])
    def test_postcondition_in_comments_not_counted(self):
        text = GOOD.replace("postcondition && { echo \"already satisfied\"; exit 0; }\n", "# postcondition postcondition postcondition\n")
        msgs = ops.check_package(fixture({"a.sh": text}))
        self.assertEqual(len(msgs), 1); self.assertIn("need 3", msgs[0])
    def test_function_keyword_form_accepted(self):
        text = GOOD.replace("postcondition() {", "function postcondition {")
        self.assertEqual(ops.check_package(fixture({"a.sh": text})), [])
    def test_destructive_with_confirm_passes(self):
        self.assertEqual(ops.check_package(fixture({"a.sh": DESTRUCTIVE})), [])
    def test_missing_destructive_header_fails(self):
        msgs = ops.check_package(fixture({"a.sh": GOOD.replace("# destructive: none\n", "")}))
        self.assertEqual(len(msgs), 1); self.assertIn("`# destructive:`", msgs[0])
    def test_destructive_without_confirm_function_fails(self):
        text = DESTRUCTIVE.replace('confirm() { echo "$1"; read -r -p "Y/N: " ans < /dev/tty; [[ $ans == Y ]] || { echo "declined"; exit 2; }; }\n', "")
        msgs = ops.check_package(fixture({"a.sh": text}))
        self.assertEqual(len(msgs), 2)
        self.assertTrue(any("no `confirm()` function" in m for m in msgs))
        self.assertTrue(any("`confirm` named 1 time(s) in code, need 2" in m for m in msgs))
    def test_destructive_confirm_without_call_fails(self):
        text = DESTRUCTIVE.replace('confirm "delete /srv/old; no undo"; ', "")
        msgs = ops.check_package(fixture({"a.sh": text}))
        self.assertEqual(len(msgs), 1); self.assertIn("`confirm` named 1 time(s) in code, need 2", msgs[0])
    def test_destructive_none_needs_no_confirm(self):
        self.assertNotIn("confirm", GOOD.split("set -euo pipefail")[1]); self.assertEqual(ops.check_package(fixture({"a.sh": GOOD})), [])
    def test_missing_strict_mode_fails(self):
        msgs = ops.check_package(fixture({"a.sh": GOOD.replace("set -euo pipefail\n", "")}))
        self.assertEqual(len(msgs), 1); self.assertIn("set -euo pipefail", msgs[0])
    def test_wrong_shebang_fails(self):
        msgs = ops.check_package(fixture({"a.sh": GOOD.replace("#!/usr/bin/env bash", "#!/bin/sh")}))
        self.assertEqual(len(msgs), 1); self.assertIn("first line", msgs[0])
    def test_syntax_error_fails(self):
        msgs = ops.check_package(fixture({"a.sh": GOOD + "if true; then\n"}))
        self.assertEqual(len(msgs), 1); self.assertIn("bash -n failed", msgs[0])
    def test_tracked_non_executable_fails_though_the_disk_bit_is_set(self):
        """#141: the check reads git's index. This is the #135 shape — 755 on disk, 100644 tracked."""
        root = fixture({"a.sh": GOOD}, mode=0o755, index=dyadlib.MODE_FILE)
        self.assertTrue(os.access(ops.ops_dir(root) / "a.sh", os.X_OK))
        msgs = ops.check_package(root)
        self.assertEqual(msgs, ["a.sh: tracked mode 100644 (git update-index --chmod=+x)"])
    def test_tracked_executable_passes_though_the_disk_bit_is_absent(self):
        self.assertEqual(ops.check_package(fixture({"a.sh": GOOD}, mode=0o644, index=dyadlib.MODE_EXEC)), [])
    def test_untracked_warns_and_falls_back_to_the_disk_bit(self):
        msgs = ops.check_package(fixture({"a.sh": GOOD}, mode=0o755, index=None))
        self.assertEqual(msgs, ["warning: a.sh: untracked: disk mode used"])
        msgs = ops.check_package(fixture({"a.sh": GOOD}, mode=0o644, index=None))
        self.assertEqual(msgs, ["a.sh: executable bit not set (chmod 755)", "warning: a.sh: untracked: disk mode used"])
    def test_check_script_without_a_root_falls_back_to_the_disk_bit(self):
        root = fixture({"a.sh": GOOD}, mode=0o755, index=dyadlib.MODE_FILE)
        self.assertEqual(ops.check_script(ops.ops_dir(root) / "a.sh"), ["warning: a.sh: untracked: disk mode used"])
        self.assertEqual(ops.check_script(ops.ops_dir(root) / "a.sh", root=root), ["a.sh: tracked mode 100644 (git update-index --chmod=+x)"])
    def test_non_sh_files_ignored(self):
        root = fixture({"a.sh": GOOD}); (ops.ops_dir(root) / "a.log").write_text("if\n")
        self.assertEqual(ops.check_package(root), [])
    def test_dyad_ops_env_overrides_dir(self):
        root = fixture(None); os.environ["DYAD_OPS"] = "elsewhere/ops"
        try:
            d = ops.ops_dir(root); d.mkdir(parents=True); p = d / "b.sh"; p.write_text("#!/bin/sh\n"); p.chmod(0o755)
            self.assertTrue(any("first line" in m for m in ops.check_package(root)))
        finally:
            os.environ.pop("DYAD_OPS", None)
    def test_main_ok_and_fail(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(ops.main([str(fixture({"a.sh": GOOD}))]), 0)
            self.assertEqual(ops.main([str(fixture({"a.sh": GOOD}, index=dyadlib.MODE_FILE))]), 1)
            self.assertEqual(ops.main([str(fixture({"a.sh": GOOD}, index=None))]), 0)   # a warning is not a failure
        self.assertIn("ok   [rule-18] 1 ops scripts", out.getvalue()); self.assertIn("FAIL [rule-18] a.sh: tracked mode 100644", err.getvalue())
        self.assertIn("warn [rule-18] a.sh: untracked: disk mode used", out.getvalue())
    def test_live_repo(self):
        self.assertEqual(ops.check_package(dyadlib.repo_root()), [])
    def test_contract(self):
        self.assertEqual((ops.ENTITY, ops.CORPUS, ops.TRANSACTION), ("ops", "workstation", False)); self.assertEqual(ops.FIELDS[0], "shebang")


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(ops, "craft", "sysadmin", {"workstation", "craft"})
        self.assertEqual(dyadlib.check_invariants(ops, extra), len(ops.INVARIANTS) + 4)
        names = [n for n, _ in ops.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
