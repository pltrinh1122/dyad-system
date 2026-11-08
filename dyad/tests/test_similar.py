"""similar.py (d-work #642): a frozen comparator set's digest is stable across runs and changes with the set; scoring
reads the frozen IDF; `label` abstains below the threshold and inside the margin; `agreement` counts reproduced and
abstained cases; a malformed set is refused; and hygiene's TF-IDF is similar.py's, its output unchanged."""
import json, shutil, sys, tempfile, unittest
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib, similar
hy = dyadlib.load_module(PKG / "scripts" / "hygiene.py", "similar_test_hygiene")

EXAMPLES = [("stale", "backlog row untouched for months, nobody cited it"),
            ("stale", "an old backlog row with no commit since spring"),
            ("worked", "a branch commit cites the backlog row as d-work"),
            ("worked", "someone pushed commits citing this row on a branch"),
            ("orphan", "the parent row is done, this child is left behind"),
            ("orphan", "a child whose parent was archived already")]


class SimilarTests(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)
        self.path = self.d / "set.jsonl"
        self.sha = similar.freeze(EXAMPLES, self.path, max_df=0.5)
        self.cset = similar.load(self.path)

    def test_the_digest_is_stable_and_changes_with_the_set(self):
        again = similar.freeze(EXAMPLES, self.d / "again.jsonl", max_df=0.5)
        self.assertEqual(again, self.sha)
        self.assertEqual((self.d / "again.jsonl").read_bytes(), self.path.read_bytes())
        self.assertEqual(self.cset["sha256"], self.sha)
        other = similar.freeze(EXAMPLES + [("orphan", "a third orphan example")], self.d / "other.jsonl", max_df=0.5)
        self.assertNotEqual(other, self.sha)
        self.assertEqual(similar.labels(self.cset), {"stale", "worked", "orphan"})

    def test_score_reads_the_frozen_vocabulary(self):
        top, cos, (second, cos2) = similar.score(self.cset, "a branch commit cites the row")
        self.assertEqual(top, "worked"); self.assertGreater(cos, cos2)
        top, cos, _ = similar.score(self.cset, "zzz qqq unknown words only")
        self.assertEqual(cos, 0.0)                                         # no frozen token: no similarity

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
        bad.write_text(json.dumps({"label": "x", "text": "y"}) + "\n")
        with self.assertRaises(ValueError):
            similar.load(bad)
        with self.assertRaises(ValueError):
            similar.freeze([], self.d / "empty.jsonl")

    def test_hygiene_reads_similars_tfidf_unchanged(self):
        self.assertIs(hy.tokens, similar.tokens); self.assertIs(hy.cosine, similar.cosine)
        docs = {i: t for i, (_, t) in enumerate(EXAMPLES * 2)} | {99: "fonts colours spacing margins borders"}
        self.assertEqual(hy.tfidf(docs), similar.tfidf(docs, hy.HYGIENE_MAX_DF))
        self.assertFalse(hasattr(hy, "TOKEN"))                            # one implementation (#642)


if __name__ == "__main__":
    unittest.main()
