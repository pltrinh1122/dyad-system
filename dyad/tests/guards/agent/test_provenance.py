"""Provenance guard tests (agent/provenance.py, Rule-7): the record's shape (title id, entries
numbered from 1, known kinds, a fenced body), the disposition count against the row's `disposed`
cell, the credential shapes that fail and the 40-hex that only warns, the SINCE_ID warning for a
row with no record, and the live store."""
import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
pv = dyadlib.load_guard("agent", "provenance")

GOOD = ("# Provenance #7 - t\n\nsession: s\nraw transcript: not committed (Rule-7 property 2)\n\n"
        "## 1 prompt 2026-09-14\n```text\ndo the thing\n```\n\n## 2 disposition 2026-09-14 Y plan\n```text\nY\n```\n")
ROW = "id: 7\ntitle: t\nopened: 2026-09-14\nstate: planned\ndisposed: 2026-09-14 Y plan\nrefs: \n"

def fixture(records: dict[str, str], rows: dict[str, str] | None = None):
    root = Path(tempfile.mkdtemp())
    (root / "agent-corpus" / "d-work" / "provenance").mkdir(parents=True)
    (root / "agent-corpus" / "d-work" / "rows").mkdir(parents=True)
    for n, t in records.items(): (root / "agent-corpus" / "d-work" / "provenance" / n).write_text(t)
    for n, t in (rows if rows is not None else {"7.md": ROW}).items():
        (root / "agent-corpus" / "d-work" / "rows" / n).write_text(t)
    return root

def fails(msgs): return [m for m in msgs if not m.startswith("warning:")]
def warns(msgs): return [m for m in msgs if m.startswith("warning:")]

class ProvenanceTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)

    def test_contract(self):
        self.assertEqual((pv.ENTITY, pv.CORPUS, pv.TRANSACTION), ("provenance", "agent", False))
        self.assertEqual(pv.FIELDS, ("n", "kind", "date", "note", "text"))
        for name in ("check_package", "describe", "summary"):
            self.assertTrue(callable(getattr(pv, name)), name)

    def test_good_record_passes(self):
        root = fixture({"7.md": GOOD})
        self.assertEqual(pv.check_package(root), [])
        e = pv.parse(GOOD)
        self.assertEqual([x["kind"] for x in e], ["prompt", "disposition"])
        self.assertEqual(e[0]["text"], "do the thing")
        self.assertEqual(e[1]["note"], "Y plan")

    def test_fenced_body_is_data(self):
        """A prompt that looks like markup does not reshape the file that stores it."""
        body = "## 9 prompt 2026-01-01\n| a | b |\n# Provenance #99"
        text = GOOD.replace("do the thing", body)
        e = pv.parse(text)
        self.assertEqual(len(e), 2)
        self.assertEqual(e[0]["text"], body)

    def test_title_id_must_match_file_name(self):
        root = fixture({"7.md": GOOD.replace("# Provenance #7", "# Provenance #8")})
        self.assertIn("differs from the file name", " ".join(fails(pv.check_package(root))))

    def test_entries_numbered_from_one_without_gaps(self):
        root = fixture({"7.md": GOOD.replace("## 2 disposition", "## 3 disposition")})
        self.assertIn("is numbered 3", " ".join(fails(pv.check_package(root))))

    def test_unknown_kind_fails(self):
        root = fixture({"7.md": GOOD.replace("## 1 prompt", "## 1 remark")})
        msgs = fails(pv.check_package(root))
        self.assertIn("kind 'remark'", " ".join(msgs))

    def test_missing_fenced_body_fails(self):
        root = fixture({"7.md": "# Provenance #7\n\n## 1 prompt 2026-09-14\nbare text, no fence\n"})
        self.assertIn("no fenced body", " ".join(fails(pv.check_package(root))))

    def test_no_entries_fails(self):
        root = fixture({"7.md": "# Provenance #7 - t\n\nsession: s\n"})
        self.assertIn("no entries", " ".join(fails(pv.check_package(root))))

    def test_disposition_count_must_match_the_row(self):
        two = ROW.replace("disposed: 2026-09-14 Y plan", "disposed: 2026-09-14 Y plan; 2026-09-14 Y done")
        root = fixture({"7.md": GOOD}, {"7.md": two})
        self.assertIn("row #7 records 2", " ".join(fails(pv.check_package(root))))
        self.assertEqual(pv.dispositions("2026-09-14 Y plan; 2026-09-14 Y done"),
                         ["2026-09-14 Y plan", "2026-09-14 Y done"])
        self.assertEqual(pv.dispositions(""), [])

    def test_record_without_a_row_fails(self):
        root = fixture({"9.md": GOOD.replace("#7", "#9")}, {"7.md": ROW})
        self.assertIn("no row #9", " ".join(fails(pv.check_package(root))))

    def test_credential_shapes_fail(self):
        for secret in ("ghp_abcdefghijklmnopqrstuvwxyz0123456789",
                       "github_pat_11ABCDEFG0abcdefghijklmnop",
                       "-----BEGIN OPENSSH PRIVATE KEY-----",
                       "Authorization: Bearer abc.def.ghi"):
            root = fixture({"7.md": GOOD.replace("do the thing", secret)})
            self.assertTrue(fails(pv.check_package(root)), secret)

    def test_forty_hex_only_warns(self):
        """A commit sha and a Gitea token are the same shape; the Operator pastes shas constantly."""
        sha = "c0711b02266c5d79be8fcf5d482214e759e45da6"
        self.assertEqual(len(sha), 40)
        root = fixture({"7.md": GOOD.replace("do the thing", f"main is at {sha} now")})
        msgs = pv.check_package(root)
        self.assertEqual(fails(msgs), [])
        self.assertTrue(any("40-hex" in m for m in warns(msgs)))

    def test_missing_record_warns_never_fails(self):
        """Rule-16: a concurrent session opens a row without having loaded Rule-7."""
        rows = {"7.md": ROW, f"{pv.SINCE_ID + 1}.md": ROW.replace("id: 7", f"id: {pv.SINCE_ID + 1}")}
        root = fixture({"7.md": GOOD}, rows)
        msgs = pv.check_package(root)
        self.assertEqual(fails(msgs), [])
        self.assertTrue(any(f"row #{pv.SINCE_ID + 1}" in m for m in warns(msgs)))

    def test_rows_below_since_id_need_no_record(self):
        root = fixture({}, {"7.md": ROW})
        self.assertEqual(pv.check_package(root), [])

    def test_describe_and_summary(self):
        root = fixture({"7.md": GOOD})
        d = pv.describe(root, dyadlib.PKG)
        self.assertEqual([f[0] for f in d["fields"]], list(pv.FIELDS))
        self.assertIn("store", d); self.assertIn("parser", d)
        self.assertIn("1 records", pv.summary(root))

    def test_live_store_passes(self):
        root = dyadlib.repo_root()
        self.assertEqual(fails(pv.check_package(root)), [])

if __name__ == "__main__":
    unittest.main()
