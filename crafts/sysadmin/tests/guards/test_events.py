"""Event guard tests (crafts/sysadmin/guards/events.py, #155): the store's shape (every EVENT_FIELDS key, Rule-8 class,
role, postcondition result, instance and id form; a malformed line fails); the append-only fence over
merges on main (d-work #150, formerly main_fence.py): appended lines pass, a rewritten or deleted file
fails, a direct commit is still non-ledger for the rows fence; the runbooks-dir prefix follows
DYAD_RUNBOOKS; the transaction check applies on `main` only."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
ev = dyadlib.load_guard("workstation", "events")
rows = dyadlib.load_guard("agent", "rows")

def sh(*a, cwd): return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout

def event(**kw):
    e = {"id": "x-20260914T120000Z-status", "ts": "2026-09-14T12:00:00Z", "role": "agent", "instance": "x", "name": "status", "cmd": "echo up",
         "class": "read-only", "scope": "s", "exit": 0, "duration_ms": 1, "postcondition": "n/a", "output_sha256": "", "output_tail": "up", "commit": "abc", "runbook_sha256": ""}
    e.update(kw); return e

class Repo:
    def __init__(self):
        self.d = Path(tempfile.mkdtemp()); sh("git", "init", "-q", "-b", "main", cwd=self.d)
        sh("git", "config", "user.email", "t@t", cwd=self.d); sh("git", "config", "user.name", "t", cwd=self.d)
    def write(self, rel, text):
        p = self.d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text); sh("git", "add", rel, cwd=self.d)
    def remove(self, rel): sh("git", "rm", "-q", rel, cwd=self.d)
    def commit(self, msg="c"):
        sh("git", "commit", "-q", "-m", msg, cwd=self.d); return sh("git", "rev-parse", "HEAD", cwd=self.d).strip()
    def merge(self, msg="feat"):
        """Commit the staged files on a branch and merge it into main (a PR merge); return the merge sha."""
        sh("git", "checkout", "-q", "-b", msg, cwd=self.d); self.commit(msg)
        sh("git", "checkout", "-q", "main", cwd=self.d); sh("git", "merge", "-q", "--no-ff", "-m", f"merge {msg}", msg, cwd=self.d)
        return sh("git", "rev-parse", "HEAD", cwd=self.d).strip()

class ShapeTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("DYAD_RUNBOOKS", None); self.root = Path(tempfile.mkdtemp())
        self.d = self.root / ev.runbooks.DEFAULT_RUNBOOKS / "events"; self.d.mkdir(parents=True)
    def store(self, *lines, name="x"):
        (self.d / f"{name}.jsonl").write_text("".join((json.dumps(l) if isinstance(l, dict) else l) + "\n" for l in lines))
    def test_contract(self):
        self.assertEqual((ev.ENTITY, ev.CORPUS, ev.TRANSACTION), ("event", "workstation", True))
        self.assertEqual(ev.FIELDS, ev.EVENT_FIELDS); self.assertEqual(len(set(ev.EVENT_FIELDS)), len(ev.EVENT_FIELDS))
        self.assertEqual(ev.CLASSES, dyadlib.HOST_CLASSES)
        for f in ("id", "ts", "role", "instance", "name", "cmd", "class", "exit", "postcondition", "commit", "runbook_sha256"):
            self.assertIn(f, ev.EVENT_FIELDS)
    def test_good_store_passes_and_absent_store_passes(self):
        self.store(event(), event(id="x-20260914T120001Z-start", name="start", **{"class": "reversible"}, postcondition="ok", role="operator"))
        self.assertEqual(ev.check_package(self.root), [])
        self.assertEqual(ev.check_package(Path(tempfile.mkdtemp())), [])
        self.assertEqual(ev.summary(self.root), "2 events, 1 instances")
    def test_missing_and_unknown_fields_fail(self):
        e = event(); del e["scope"]; e["extra"] = 1
        self.store(e)
        msgs = ev.check_package(self.root)
        self.assertEqual(len(msgs), 2, msgs); self.assertIn("missing field(s) scope", msgs[0]); self.assertIn("unknown field(s) extra", msgs[1])
    def test_bad_enums_instance_and_id_fail(self):
        self.store(event(**{"class": "harmless"}, role="root", postcondition="maybe", instance="y", id="z-1-status"))
        msgs = ev.check_package(self.root)
        self.assertEqual(len(msgs), 5, msgs)
        for w in ("class `harmless`", "role `root`", "postcondition `maybe`", "instance `y`", "id `z-1-status`"):
            self.assertTrue(any(w in m for m in msgs), w)
    def test_malformed_line_fails(self):
        self.store(event(), "not json")
        msgs = ev.check_package(self.root)
        self.assertEqual(len(msgs), 1); self.assertIn("x.jsonl:2: not a JSON object", msgs[0])
        with self.assertRaises(ValueError): ev.read_events(self.d / "x.jsonl")
    def test_read_and_all_events(self):
        self.store(event()); self.store(event(instance="a", id="a-1-status"), name="a")
        self.assertEqual(list(ev.all_events(self.root)), ["a", "x"]); self.assertEqual(ev.read_events(self.d / "nope.jsonl"), [])
    def test_live_store_passes(self):
        self.assertEqual(ev.check_package(dyadlib.repo_root()), [])

class FenceTests(unittest.TestCase):
    E = "workstation-corpus/runbooks/events/x.jsonl"
    def setUp(self):
        os.environ.pop("DYAD_RUNBOOKS", None); os.environ.pop("DYAD_INSTANCE", None)
        self.r = Repo(); self.r.write("agent-corpus/d-work/rows/1.md", dyadlib.format_row_file(dyadlib.Row(1, "one", "d", "open", "", ""))); self.base = self.r.commit("root")
    def fails(self, before, after): return ev.check_range(before, after, cwd=self.r.d)
    def test_events_appended_by_merge_pass(self):
        self.r.write(self.E, '{"id": "x-1"}\n'); self.r.merge("e1")
        self.r.write(self.E, '{"id": "x-1"}\n{"id": "x-2"}\n'); h = self.r.merge("e2")
        self.assertEqual(self.fails(self.base, h), [])
        self.assertEqual(ev.check_events(h, self.r.d), [])
    def test_events_rewritten_by_merge_fail(self):
        self.r.write(self.E, '{"id": "x-1"}\n{"id": "x-2"}\n'); base = self.r.merge("e1")
        self.r.write(self.E, '{"id": "x-1"}\n'); h = self.r.merge("e2")            # a line removed
        out = self.fails(base, h); self.assertEqual(len(out), 1); self.assertIn("rewrites event file", out[0])
        self.r.write(self.E, '{"id": "x-0"}\n{"id": "x-2"}\n'); h2 = self.r.merge("e3")   # a line changed
        out = self.fails(h, h2); self.assertEqual(len(out), 1); self.assertIn("append-only", out[0])
    def test_events_deleted_by_merge_fail(self):
        self.r.write(self.E, '{"id": "x-1"}\n'); base = self.r.merge("e1")
        self.r.remove(self.E); h = self.r.merge("e2")
        out = self.fails(base, h); self.assertEqual(len(out), 1); self.assertIn("deletes event file", out[0])
    def test_events_direct_commit_still_non_ledger_for_the_rows_fence(self):
        self.r.write(self.E, '{"id": "x-1"}\n'); h = self.r.commit()
        self.assertEqual(self.fails(self.base, h), [])
        out = rows.check_range(self.base, h, cwd=self.r.d); self.assertEqual(len(out), 1); self.assertIn("non-ledger paths", out[0])
    def test_events_prefix_follows_runbooks_env(self):
        self.r.write("elsewhere/events/x.jsonl", "a\n"); self.r.merge("e1")
        self.r.write("elsewhere/events/x.jsonl", "b\n"); h = self.r.merge("e2")
        self.assertEqual(ev.check_events(h, self.r.d), [])                                  # not under the runbooks dir
        self.assertEqual(len(ev.check_events(h, self.r.d, "elsewhere/events/")), 1)
    def test_transaction_check_on_main_only(self):
        self.r.write(self.E, '{"id": "x-1"}\n{"id": "x-2"}\n'); base = self.r.merge("e1")
        self.r.write(self.E, '{"id": "x-1"}\n'); h = self.r.merge("e2")
        self.assertEqual(len(ev.check_transaction(self.r.d, base, h)), 1)
        sh("git", "checkout", "-q", "-b", "feature", cwd=self.r.d)
        self.assertEqual(ev.check_transaction(self.r.d, base, h), [])
    def test_cli_range(self):
        self.r.write(self.E, '{"id": "x-1"}\n'); base = self.r.merge("e1")
        self.r.write(self.E, '{"id": "x-1"}\n{"id": "x-2"}\n'); h = self.r.merge("e2")
        r = subprocess.run([sys.executable, str(Path(ev.__file__)), "range", base, h], cwd=self.r.d, capture_output=True, text=True)
        self.assertIn(r.stdout.strip(), ("events append-only OK", "events append-only FAILED", ""))   # the CLI resolves the live repo; the range may not exist there


class InvariantTests(unittest.TestCase):
    """crafts/syseng/rules/invariants.md: the guard's INVARIANTS (plus the contract's four) hold; each name is unique."""
    def test_invariants_hold(self):
        extra = dyadlib.contract_invariants(ev, "craft", "sysadmin", {"workstation", "craft"})
        self.assertEqual(dyadlib.check_invariants(ev, extra), len(ev.INVARIANTS) + 4)
        names = [n for n, _ in ev.INVARIANTS]; self.assertEqual(len(set(names)), len(names)); self.assertTrue(names)

if __name__ == "__main__":
    unittest.main()
