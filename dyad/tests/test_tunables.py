"""Tunables (d-work #590): `dyadlib.tunable(key, root)` reads an operator-tunable number from the instance's preference
table and falls back to the one home of its default, the `dyad:defaultValue` of the DMC record that claims the key:
- a valid preference overrides the default, parsed to the default's type, and is read at use time (never at import);
- a malformed one (unparseable, not positive, outside `between A and B`) falls back to the default;
- an unknown key raises KeyError; a record whose own default is not allowed raises ValueError (fail-loud);
- each reader the records' `dyad:readBy` names reads through the helper: hygiene, work in flight, the sweep, attendance;
- the two homes cannot drift: each reader's key list is the records' set for its path, no reader keeps a numeric copy
  of a default, and the template seeds every tunable at its record's default and S3 lists it."""
import datetime, json, re, shutil, subprocess, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib
hy = dyadlib.load_module(PKG / "scripts" / "hygiene.py", "hygiene")
am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
sv = dyadlib.load_guard("agent", "sessions")
TUNABLE = dyadlib.tunable                                            # before any spy wraps it
HEAD = "| key | value | allowed | read by |\n|-----|-------|---------|---------|\n"


def records() -> dict[str, dict]:
    """{key: entry} over every core record's `dyad:tunables`, read independently of the helper."""
    out = {}
    for p in sorted((PKG / "dmc").glob("*.jsonld")):
        for t in json.loads(p.read_text()).get("dyad:tunables") or ():
            out[t["dyad:preference"]] = t
    return out


class TunableTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)

    def prefs(self, **kv):
        p = self.d / dyadlib.PREFERENCES_REL; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# prefs\n\n" + HEAD + "".join(f"| {k} | {v} | x | Rule-3 |\n" for k, v in kv.items()))

    def test_absent_reads_the_record_default(self):
        for key, t in records().items():
            want = dyadlib.tunable_default(key)
            self.assertEqual(dyadlib.tunable(key, self.d), want, key)
            self.assertEqual(str(want), t["dyad:defaultValue"], key)        # int stays int, 0.35 stays 0.35
        self.assertIsInstance(dyadlib.tunable("hygiene-top", self.d), int)
        self.assertIsInstance(dyadlib.tunable("hygiene-similar", self.d), float)

    def test_a_preference_overrides(self):
        self.prefs(**{"hygiene-top": "4", "hygiene-similar": "0.5", "attendance-window": "30 days"})
        self.assertEqual(dyadlib.tunable("hygiene-top", self.d), 4)
        self.assertEqual(dyadlib.tunable("hygiene-similar", self.d), 0.5)
        self.assertEqual(dyadlib.tunable("attendance-window", self.d), 30)    # first word, as attendance_window read it
        self.prefs(**{"inflight-unread-hours": "`8`"})
        self.assertEqual(dyadlib.tunable("inflight-unread-hours", self.d), 8)   # emphasis is stripped, the value accepted

    def test_read_at_use_time(self):
        self.assertEqual(dyadlib.tunable("sweep-ci-hours", self.d), 24)
        self.prefs(**{"sweep-ci-hours": "48"})
        self.assertEqual(dyadlib.tunable("sweep-ci-hours", self.d), 48)

    def test_a_malformed_preference_falls_back(self):
        for key, bad in (("hygiene-top", "none"), ("hygiene-top", "-2"), ("hygiene-top", "0"), ("hygiene-top", "2.5"),
                         ("hygiene-similar", "1.5"), ("hygiene-similar", "0"), ("hygiene-similar", "lots"),
                         ("inflight-unread-hours", "four"), ("inflight-unread-hours", "0")):
            self.prefs(**{key: bad})
            self.assertEqual(dyadlib.tunable(key, self.d), dyadlib.tunable_default(key), f"{key}={bad}")

    def test_an_unknown_key_raises(self):
        with self.assertRaises(KeyError):
            dyadlib.tunable("no-such-tunable", self.d)
        with self.assertRaises(KeyError):
            dyadlib.tunable_entry("merge-disposition")                     # a preference, but no tunable

    def test_a_record_default_not_allowed_raises(self):
        pkg = self.d / "pkg"; (pkg / "dmc").mkdir(parents=True)
        (pkg / "dmc" / "x.jsonld").write_text(json.dumps({"dyad:tunables": [
            {"dyad:preference": "x-bad", "dyad:defaultValue": "0", "dyad:allowed": "a positive integer", "dyad:readBy": "scripts/x.py"},
            {"dyad:preference": "x-junk", "dyad:defaultValue": "many", "dyad:allowed": "a positive integer", "dyad:readBy": "scripts/x.py"}]}))
        for key in ("x-bad", "x-junk"):
            with self.assertRaises(ValueError):
                dyadlib.tunable(key, self.d, pkg)
        self.assertEqual(dyadlib.tunables_read_by("scripts/x.py", pkg), {"x-bad", "x-junk"})

    def test_invariants(self):
        self.assertEqual(dyadlib.check_invariants(dyadlib), len(dyadlib.INVARIANTS) + len(dyadlib.TREE_INVARIANTS))
        self.assertEqual(dyadlib.check_invariants(sv), len(sv.INVARIANTS) + len(sv.TREE_INVARIANTS))


class ReaderTests(unittest.TestCase):
    """Each family's reader calls the helper when it runs (a spy on `dyadlib.tunable`), with the instance's root."""
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        self.spy = unittest.mock.patch.object(dyadlib, "tunable", wraps=dyadlib.tunable)
        self.calls = self.spy.start(); self.addCleanup(self.spy.stop)

    def keys(self):
        return {c.args[0] for c in self.calls.call_args_list}

    def test_backlog_hygiene_ranking(self):
        self.assertEqual(hy.ranking([], {}, [], self.d), [])
        self.assertEqual(self.keys(), {"hygiene-similar", "hygiene-top"})
        self.assertTrue(all(c.args[1] == self.d for c in self.calls.call_args_list))

    def test_backlog_hygiene_top_is_honoured(self):
        p = self.d / dyadlib.PREFERENCES_REL; p.parent.mkdir(parents=True)
        p.write_text(HEAD + "| hygiene-top | 1 | x | Rule-3 |\n| hygiene-similar | 0.01 | x | Rule-3 |\n")
        Row = type("Row", (), {})
        rows = []
        titles = ["apple banana", "apple banana", "cherry grape", "cherry grape", "lemon mango", "lemon mango"]
        titles += [f"filler{c}{c}{c} word{c}{c}{c}" for c in "abcdefghij"]                # unique: no shared token
        for i, t in enumerate(titles, 1):
            r = Row(); r.id, r.title, r.refs = i, t, ""; rows.append(r)
        self.assertEqual(len(hy.ranking(rows, {}, rows, self.d)), 1)                    # three pairs score; top is 1
        p.write_text(HEAD + "| hygiene-similar | 0.01 | x | Rule-3 |\n")
        self.assertEqual(len(hy.ranking(rows, {}, rows, self.d)), 3)                    # the default top, 10

    def test_work_in_flight(self):
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.d)], check=True, capture_output=True)
        with unittest.mock.patch.object(hy, "_board_files", lambda *a: {}), \
             unittest.mock.patch.object(hy, "_messages", lambda *a: []), \
             unittest.mock.patch.object(dyadlib, "read_rows", lambda *a, **k: []):
            hy.inflight(self.d, "HEAD", 0.0, None, lambda seat, at: True)
        self.assertEqual(self.keys(), {v for k, v in hy.TUNABLES.items() if k.startswith("W")})

    def test_sweep(self):
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.d)], check=True, capture_output=True)
        am.sweep_ci(self.d, "HEAD", datetime.datetime.now(datetime.timezone.utc))
        self.assertIn(("sweep-ci-hours", self.d), {c.args[:2] for c in self.calls.call_args_list})
        import inspect                                                         # #619: delivery reuses the same window
        self.assertEqual(inspect.getsource(am.sweep_ci).count("dyadlib.tunable("), 1)
        self.assertIn("dyadlib.tunable(SWEEP_LANDING_HOURS, prefs or repo)", (PKG / "scripts" / "automaton.py").read_text())
        self.assertIn("dyadlib.tunable(SWEEP_STALE_DAYS, prefs or repo)", (PKG / "scripts" / "automaton.py").read_text())

    def test_sweep_ci_huge_hours_falls_back(self):   # a valid but huge value overflows timedelta: the default, no raise
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.d)], check=True, capture_output=True)
        p = self.d / dyadlib.PREFERENCES_REL; p.parent.mkdir(parents=True)
        for huge in ("100000000000", "100000000"):
            p.write_text(HEAD + f"| sweep-ci-hours | {huge} | x | Rule-3 |\n")
            self.assertEqual(am.sweep_ci(self.d, "HEAD", datetime.datetime.now(datetime.timezone.utc)), [])
        p.write_text(HEAD + "| attendance-window | 100000000000 | x | Rule-16 |\n")
        self.assertEqual(sv.attendance_window(self.d), datetime.timedelta(days=dyadlib.tunable_default("attendance-window")))

    def test_sweep_reads_tunables_at_base_not_the_working_tree(self):
        """`stall_lines` (#617: the stalls `sweep()` read until then) reads rows at `base`; its thresholds come from
        `prefs` when given — the same commit's tree — never the uncommitted working tree."""
        git = lambda *a: subprocess.run(["git", "-C", str(self.d), *a], check=True, capture_output=True, text=True).stdout
        git("init", "-q", "-b", "main"); git("config", "user.email", "t@t"); git("config", "user.name", "t")
        p = self.d / dyadlib.PREFERENCES_REL; p.parent.mkdir(parents=True)
        p.write_text(HEAD + "| hygiene-top | 3 | x | Rule-3 |\n| sweep-ci-hours | 7 | x | Rule-3 |\n")
        git("add", "-A"); git("commit", "-q", "-m", "base")
        base = git("rev-parse", "HEAD").strip()
        p.write_text(HEAD + "| hygiene-top | 20 | x | Rule-3 |\n| sweep-ci-hours | 99 | x | Rule-3 |\n")   # uncommitted
        seen = {}
        real = TUNABLE                                               # the helper itself, not the spy around it
        def record(key, root=None, *a, **k):
            v = real(key, root, *a, **k); seen.setdefault(key, set()).add(v); return v
        self.calls.side_effect = record
        at = self.d.parent / (self.d.name + "-at-base")             # the tree at `base`, as a caller prepares it
        (at / dyadlib.PREFERENCES_REL).parent.mkdir(parents=True, exist_ok=True)
        (at / dyadlib.PREFERENCES_REL).write_text(git("show", f"{base}:{dyadlib.PREFERENCES_REL}"))
        self.addCleanup(lambda: __import__("shutil").rmtree(at, ignore_errors=True))
        with unittest.mock.patch.object(am, "sweep_pulls", lambda: None), \
             unittest.mock.patch.object(am, "home", lambda *a: None), \
             unittest.mock.patch.object(hy, "_board_files", lambda *a: {}), \
             unittest.mock.patch.object(hy, "_messages", lambda *a: []), \
             unittest.mock.patch.object(dyadlib, "read_rows", lambda *a, **k: []), \
             unittest.mock.patch.dict("os.environ", {"GITHUB_TOKEN": "", "GITHUB_REPOSITORY": ""}):
            am.stall_lines(self.d, base, prefs=at)
        self.assertEqual(seen.get("hygiene-top"), {3}, seen)
        self.assertEqual(seen.get("sweep-ci-hours"), {7}, seen)
        self.assertEqual(seen.get("inflight-unread-hours"), {4}, seen)

    def test_attendance(self):
        self.assertEqual(sv.attendance_window(self.d), datetime.timedelta(days=dyadlib.tunable_default("attendance-window")))
        self.assertIn(("attendance-window", self.d), {c.args[:2] for c in self.calls.call_args_list})


class OneHomeTests(unittest.TestCase):
    """The default lives in the record only: the code names keys, the template and S3 follow the records."""
    def test_reader_key_lists_are_the_records(self):
        self.assertEqual(set(hy.TUNABLES.values()), dyadlib.tunables_read_by("scripts/hygiene.py"))
        self.assertEqual({am.SWEEP_LANDING_HOURS, am.SWEEP_STALE_DAYS, am.SWEEP_CI_HOURS},
                         dyadlib.tunables_read_by("scripts/automaton.py"))
        self.assertEqual({sv.ATTENDANCE_WINDOW}, dyadlib.tunables_read_by("guards/agent/sessions.py"))
        self.assertEqual({"promotion-ceiling", "promotion-adjacency-min"}, dyadlib.tunables_read_by("playbooks/d-work.md"))

    def test_no_reader_keeps_a_numeric_copy_of_a_default(self):
        for mod in (hy, am, sv):
            for name in dir(mod):
                if re.fullmatch(r"(HYGIENE|INFLIGHT|SWEEP)_[A-Z0-9_]+|DEFAULT_ATTENDANCE_DAYS", name) and name != "HYGIENE_MAX_DF":
                    self.assertNotIsInstance(getattr(mod, name), (int, float), f"{mod.__name__}.{name} is a second home of a default")

    def test_template_seeds_every_tunable_at_its_default(self):
        rows = {r[0]: r for r in dyadlib.table_rows((PKG / "templates" / "PREFERENCES.md").read_text()) if r}
        for key, t in records().items():
            self.assertIn(key, rows, key)
            self.assertEqual(rows[key][1], t["dyad:defaultValue"], key)
            if key != "attendance-window":                                   # its row predates #590 and says "number of days"
                self.assertEqual(rows[key][2], t["dyad:allowed"], key)
            self.assertEqual(dyadlib.tunable_value(rows[key][1], dyadlib.tunable_default(key), t["dyad:allowed"]),
                             dyadlib.tunable_default(key), key)

    def test_s3_lists_every_tunable_frozen(self):
        text = (PKG / "surface.md").read_text().split("## S3", 1)[1].split("\n## ", 1)[0]
        listed = {c[0]: c[-1] for c in (dyadlib.split_cells(l) for l in text.splitlines() if l.startswith("| "))}
        for key in records():
            self.assertEqual(listed.get(key), "frozen", key)


if __name__ == "__main__":
    unittest.main()
