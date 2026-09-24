"""Tests for dyad/bin/dyad-python, the interpreter resolver the entrypoint and both hooks run
through (d-work #82; Rule-12 property 1 -- code entering the package carries its mechanical check).

The helper is shell of necessity (the thing it locates IS the interpreter), so it is exercised as
a subprocess against a synthetic PATH rather than imported. Three things are checked:

  * it picks a conforming interpreter when PATH's own `python3` is below the pin;
  * it exits non-zero, naming the pin and every candidate, when none conforms;
  * its pin constants equal the Python-side pin in dyad/scripts/package.py, so the shell pin and
    the Python pin cannot drift apart silently.

A fourth checks the three call sites still go through it, so the defect cannot quietly return.
"""
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent          # dyad/
HELPER = PKG / "bin" / "dyad-python"
PACKAGE_PY = PKG / "scripts" / "package.py"
CALL_SITES = (PKG / "bin" / "dyad", PKG / "hooks" / "pre-commit", PKG / "hooks" / "pre-push")

# a stub that behaves exactly as an interpreter below the pin does under the helper's probe:
# it prints its version and exits 1, whatever it is asked to run.
OLD_STUB = '#!/bin/sh\nprintf \'%s\\n\' "3.9.18"\nexit 1\n'


def _write(path: Path, text: str) -> Path:
    path.write_text(text)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def _run(args, path_dir):
    """Run the helper with PATH set to `path_dir` alone."""
    env = {**os.environ, "PATH": str(path_dir)}
    env.pop("PYTHONPATH", None)
    return subprocess.run([str(HELPER), *args], capture_output=True, text=True, env=env, cwd="/")


def _pin_from_shell(text: str) -> tuple[int, int]:
    major = re.search(r"^PIN_MAJOR=(\d+)$", text, re.M)
    minor = re.search(r"^PIN_MINOR=(\d+)$", text, re.M)
    assert major and minor, "dyad-python must declare PIN_MAJOR and PIN_MINOR as bare assignments"
    return int(major.group(1)), int(minor.group(1))


def _pin_from_python(text: str) -> tuple[int, int]:
    m = re.search(r"sys\.version_info\s*<\s*\((\d+),\s*(\d+)\)", text)
    assert m, "package.py must declare its kernel pin as `sys.version_info < (major, minor)`"
    return int(m.group(1)), int(m.group(2))


class PinTests(unittest.TestCase):
    """The single-source check: one pin, written twice, asserted equal here."""

    def test_shell_pin_equals_package_pin(self):
        self.assertEqual(_pin_from_shell(HELPER.read_text()), _pin_from_python(PACKAGE_PY.read_text()))

    def test_running_interpreter_satisfies_the_declared_pin(self):
        # the suite itself runs on the kernel, so the pin the helper enforces must admit it
        self.assertGreaterEqual(sys.version_info[:2], _pin_from_shell(HELPER.read_text()))

    def test_every_candidate_name_is_a_python3_name(self):
        m = re.search(r'^CANDIDATES="([^"]+)"$', HELPER.read_text(), re.M)
        self.assertIsNotNone(m, "dyad-python must declare CANDIDATES as a bare assignment")
        names = m.group(1).split()
        self.assertTrue(names)
        self.assertTrue(all(re.fullmatch(r"python3(\.\d+)?", n) for n in names), names)
        self.assertIn("python3", names)   # the unversioned name stays the last resort


class ResolutionTests(unittest.TestCase):
    def test_picks_conforming_interpreter_when_path_python3_is_older(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            bin_dir = d / "bin"
            bin_dir.mkdir()
            _write(bin_dir / "python3", OLD_STUB)            # what the host's `python3` is here
            _write(bin_dir / "python3.12",                   # a conforming interpreter, versioned name
                   f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
            script = d / "report.py"
            script.write_text("import sys\nprint('MARKER', '%d.%d' % sys.version_info[:2])\n")
            r = _run([str(script)], bin_dir)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(r.stdout.startswith("MARKER "), r.stdout)
            got = tuple(int(x) for x in r.stdout.split()[1].split("."))
            self.assertGreaterEqual(got, _pin_from_shell(HELPER.read_text()))

    def test_passes_arguments_through_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            bin_dir = d / "bin"
            bin_dir.mkdir()
            _write(bin_dir / "python3", OLD_STUB)
            _write(bin_dir / "python3.12", f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
            script = d / "argv.py"
            script.write_text("import sys\nprint('|'.join(sys.argv[1:]))\n")
            r = _run([str(script), "a b", "--flag", ""], bin_dir)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout.strip(), "a b|--flag|")

    def test_exits_non_zero_and_names_the_pin_when_nothing_conforms(self):
        with tempfile.TemporaryDirectory() as d:
            bin_dir = Path(d) / "bin"
            bin_dir.mkdir()
            _write(bin_dir / "python3", OLD_STUB)            # present but below the pin
            r = _run(["-c", "print('ran')"], bin_dir)
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn("ran", r.stdout)
            major, minor = _pin_from_shell(HELPER.read_text())
            self.assertIn(f"{major}.{minor}", r.stderr)      # the pin is named
            for name in re.search(r'^CANDIDATES="([^"]+)"$', HELPER.read_text(), re.M).group(1).split():
                self.assertIn(name, r.stderr)                # every candidate is named
            self.assertIn("below the pin", r.stderr)         # ... and what it was
            self.assertIn("not on PATH", r.stderr)

    def test_reports_a_candidate_that_is_not_a_python_interpreter(self):
        with tempfile.TemporaryDirectory() as d:
            bin_dir = Path(d) / "bin"
            bin_dir.mkdir()
            _write(bin_dir / "python3", "#!/bin/sh\nexit 127\n")   # prints nothing, fails
            r = _run(["-c", "print(1)"], bin_dir)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("not a usable Python interpreter", r.stderr)

    def test_runs_from_any_directory(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            bin_dir = d / "bin"
            bin_dir.mkdir()
            _write(bin_dir / "python3.12", f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
            script = d / "where.py"
            script.write_text("print('ok')\n")
            env = {**os.environ, "PATH": str(bin_dir)}
            for cwd in ("/", str(d), str(PKG)):
                r = subprocess.run([str(HELPER), str(script)], capture_output=True, text=True,
                                   env=env, cwd=cwd)
                self.assertEqual((r.returncode, r.stdout.strip()), (0, "ok"), f"{cwd}: {r.stderr}")


class CallSiteTests(unittest.TestCase):
    """The regression fence: the entrypoint and both hooks go through the helper, not `python3`."""

    def test_helper_is_executable_posix_sh(self):
        self.assertTrue(HELPER.is_file())
        self.assertEqual(HELPER.read_text().splitlines()[0], "#!/bin/sh")
        self.assertTrue(os.access(HELPER, os.X_OK), f"{HELPER} is not executable")

    def test_call_sites_go_through_the_helper(self):
        for p in CALL_SITES:
            with self.subTest(path=p.name):
                text = p.read_text()
                self.assertIn("dyad-python", text)
                self.assertIsNone(re.search(r"^\s*exec\s+python3\b", text, re.M),
                                  f"{p} still execs `python3` directly (d-work #82)")


if __name__ == "__main__":
    unittest.main()
