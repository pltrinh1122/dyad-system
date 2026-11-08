"""similar.py (d-work #642 revision 2): a frozen precedent set's digest is stable across runs and changes with the set;
it holds ratified cases only (freeze refuses a row with no Y) and records its base commit; scoring reads the frozen IDF;
`label` abstains with no precedent, below the threshold and inside the margin; `agreement` counts reproduced and
abstained cases; a malformed set is refused; and hygiene's TF-IDF is similar.py's, its output unchanged."""
import json, shutil, sys, tempfile, unittest
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib, similar
hy = dyadlib.load_module(PKG / "scripts" / "hygiene.py", "similar_test_hygiene")

EXAMPLES = [("stale", "backlog row untouched for months, nobody cited it", 1),
            ("stale", "an old backlog row with no commit since spring", 2),
            ("worked", "a branch commit cites the backlog row as d-work", 3),
            ("worked", "someone pushed commits citing this row on a branch", 4),
            ("orphan", "the parent row is done, this child is left behind", 5),
            ("orphan", "a child whose parent was archived already", 6)]
RATIFIED, BASE = {1, 2, 3, 4, 5, 6, 7}, "a" * 40


class SimilarTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        self.path = self.d / "set.jsonl"
        self.sha = similar.freeze(EXAMPLES, self.path, RATIFIED, BASE, max_df=0.5)
        self.cset = similar.load(self.path)

    def test_the_digest_is_stable_and_changes_with_the_set(self):
        again = similar.freeze(EXAMPLES, self.d / "again.jsonl", RATIFIED, BASE, max_df=0.5)
        self.assertEqual(again, self.sha)
        self.assertEqual((self.d / "again.jsonl").read_bytes(), self.path.read_bytes())
        self.assertEqual(self.cset["sha256"], self.sha)
        other = similar.freeze(EXAMPLES + [("orphan", "a third orphan example", 7)], self.d / "other.jsonl", RATIFIED, BASE, max_df=0.5)
        self.assertNotEqual(other, self.sha)
        self.assertEqual(similar.labels(self.cset), {"stale", "worked", "orphan"})
        self.assertEqual((self.cset["base"], self.cset["rows"]), (BASE, [1, 2, 3, 4, 5, 6]))

    def test_only_ratified_cases_are_precedents(self):
        with self.assertRaises(ValueError) as e:
            similar.freeze(EXAMPLES + [("stale", "an agent ruling no Y covered", 9)], self.d / "x.jsonl", RATIFIED, BASE)
        self.assertIn("#9", str(e.exception))
        self.assertFalse((self.d / "x.jsonl").exists())                   # nothing written on a refusal

    def test_score_reads_the_frozen_vocabulary(self):
        top, cos, (second, cos2) = similar.score(self.cset, "a branch commit cites the row")
        self.assertEqual(top, "worked"); self.assertGreater(cos, cos2)
        top, cos, _ = similar.score(self.cset, "zzz qqq unknown words only")
        self.assertEqual(cos, 0.0)                                         # no frozen token: no similarity
        self.assertEqual(similar.label(self.cset, "zzz qqq", 0.0, 0.0), similar.ABSTAIN)   # no precedent: first of its kind

    def test_label_abstains_below_the_threshold_and_inside_the_margin(self):
        text = "a branch commit cites the row"
        _, cos, (_, cos2) = similar.score(self.cset, text)
        self.assertEqual(similar.label(self.cset, text, 0.0, 0.0), "worked")
        self.assertEqual(similar.label(self.cset, text, cos + 0.01, 0.0), similar.ABSTAIN)   # below the threshold
        self.assertEqual(similar.label(self.cset, text, 0.0, cos - cos2 + 0.01), similar.ABSTAIN)   # a near-tie

    def test_agreement_counts_reproduced_and_abstained(self):
        held = [("stale", "an untouched backlog row from months ago"), ("orphan", "its parent row is done"),
                ("worked", "zzz qqq")]
        got = similar.agreement(self.cset, held, threshold=0.05, margin=0.0)
        self.assertEqual((got["n"], got["reproduced"], got["abstained"]), (3, 2, 1))
        self.assertAlmostEqual(got["agreement"], 2 / 3)
        self.assertEqual(similar.agreement(self.cset, [])["agreement"], 0.0)

    def test_a_malformed_set_is_refused(self):
        bad = self.d / "bad.jsonl"
        bad.write_text(json.dumps({"idf": {}, "max_df": 0.2}) + "\n" + json.dumps({"label": "x", "inputs": "y", "row": 1}) + "\n")
        with self.assertRaises(ValueError):
            similar.load(bad)
        with self.assertRaises(ValueError):
            similar.freeze([], self.d / "empty.jsonl", RATIFIED, BASE)

    def test_ratified_rows_are_those_holding_a_plan_or_done_y(self):
        import unittest.mock
        R = lambda i, d: dyadlib.Row(id=i, title="t", opened="2026-11-01", state="done", disposed=d, refs="")
        rows = [R(1, "2026-11-01 Y plan; 2026-11-01 Y done (merges PR #7 at abc)"), R(2, "2026-11-01 Y intent"),
                R(3, "2026-11-01 Y backlog (mandate #1)"), R(4, "2026-11-01 Y plan (mandate #1)")]
        with unittest.mock.patch.object(dyadlib, "read_rows", return_value=rows):
            self.assertEqual(similar.ratified_rows(self.d), {1, 4})

    def test_hygiene_reads_similars_tfidf_unchanged(self):
        self.assertIs(hy.tokens, similar.tokens); self.assertIs(hy.cosine, similar.cosine)
        docs = {i: t for i, (_, t, _) in enumerate(EXAMPLES * 2)} | {99: "fonts colours spacing margins borders"}
        self.assertEqual(hy.tfidf(docs), similar.tfidf(docs, hy.HYGIENE_MAX_DF))
        self.assertFalse(hasattr(hy, "TOKEN"))                            # one implementation (#642)


if __name__ == "__main__":
    unittest.main()
