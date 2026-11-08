"""similar.py (d-work #642 revisions 2 and 3): a frozen precedent set's digest is stable across runs and changes with the
set; it holds ratified cases only (freeze refuses a row with no Y) with their prose inputs, structured fields and base
commit; `decide` matches on prose, distinguishes on structured fields and abstains with its reason (no-match, near-tie,
distinguish <field>, prose-only), citing the precedent row and score; `agreement` and the leave-one-out re-measure count
reproduced and abstained cases; a malformed set is refused; and hygiene's TF-IDF is similar.py's, its output unchanged."""
import json, os, shutil, sys, tempfile, unittest, unittest.mock
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib, similar
hy = dyadlib.load_module(PKG / "scripts" / "hygiene.py", "similar_test_hygiene")

EXAMPLES = [("stale", "backlog row untouched for months, nobody cited it", {"state": "backlog"}, 1),
            ("stale", "an old backlog row with no commit since spring", {"state": "backlog"}, 2),
            ("worked", "a branch commit cites the backlog row as d-work", {"state": "backlog"}, 3),
            ("worked", "someone pushed commits citing this row on a branch", {"state": "backlog"}, 4),
            ("orphan", "the parent row is done, this child is left behind", {"state": "backlog"}, 5),
            ("orphan", "a child whose parent was archived already", {"state": "backlog"}, 6)]
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
        other = similar.freeze(EXAMPLES + [("orphan", "a third orphan example", {}, 7)], self.d / "other.jsonl",
                               RATIFIED, BASE, max_df=0.5)
        self.assertNotEqual(other, self.sha)
        self.assertEqual(similar.labels(self.cset), {"stale", "worked", "orphan"})
        self.assertEqual((self.cset["base"], self.cset["rows"], self.cset["fields"][0]), (BASE, [1, 2, 3, 4, 5, 6], {"state": "backlog"}))

    def test_only_ratified_cases_are_precedents(self):
        with self.assertRaises(ValueError) as e:
            similar.freeze(EXAMPLES + [("stale", "an agent ruling no Y covered", {}, 9)], self.d / "x.jsonl", RATIFIED, BASE)
        self.assertIn("#9", str(e.exception))
        self.assertFalse((self.d / "x.jsonl").exists())                   # nothing written on a refusal

    def test_ratified_rows_are_those_holding_a_plan_or_done_y(self):
        R = lambda i, d: dyadlib.Row(id=i, title="t", opened="2026-11-01", state="done", disposed=d, refs="")
        rows = [R(1, "2026-11-01 Y plan; 2026-11-01 Y done (merges PR #7 at abc)"), R(2, "2026-11-01 Y intent"),
                R(3, "2026-11-01 Y backlog (mandate #1)"), R(4, "2026-11-01 Y plan (mandate #1)")]
        with unittest.mock.patch.object(dyadlib, "read_rows", return_value=rows):
            self.assertEqual(similar.ratified_rows(self.d), {1, 4})

    def test_decide_matches_cites_and_distinguishes(self):
        got = similar.decide(self.cset, "a branch commit cites the row", {"state": "backlog"}, 0.05, 0.0)
        self.assertEqual((got["outcome"], got["reason"]), ("worked", None))
        self.assertIn(got["row"], (3, 4)); self.assertGreater(got["score"], 0)       # the precedent cited (R7)
        got = similar.decide(self.cset, "a branch commit cites the row", {"state": "open"}, 0.05, 0.0)
        self.assertEqual((got["outcome"], got["reason"]), (similar.ABSTAIN, "distinguish state"))
        self.assertIn(got["row"], (3, 4))                                            # cited on an abstention too

    def test_decide_abstains_with_its_reason(self):
        text = "a branch commit cites the row"
        cos = similar.decide(self.cset, text, {"state": "backlog"}, 0.0, 0.0)["score"]
        _, top, (_, second) = similar.score(self.cset, text)
        reason = lambda **kw: similar.decide(self.cset, kw.get("prose", text), {"state": "backlog"},
                                             kw.get("threshold", 0.0), kw.get("margin", 0.0), kw.get("read", ()))["reason"]
        self.assertEqual(reason(prose="zzz qqq unknown words"), "no-match")               # no precedent at all
        self.assertEqual(reason(threshold=cos + 0.01), "no-match")                        # below the threshold
        self.assertEqual(reason(margin=top - second + 0.01), "near-tie")                  # inside the margin
        self.assertEqual(reason(read=["the plan's free text"]), "prose-only")             # a `read` input holds a value
        self.assertIsNone(reason())

    def test_label_keeps_its_prose_only_reading(self):
        self.assertEqual(similar.label(self.cset, "zzz qqq", 0.0, 0.0), similar.ABSTAIN)
        self.assertEqual(similar.label(self.cset, "a branch commit cites the row", 0.0, 0.0), "worked")

    def test_agreement_and_the_leave_one_out_re_measure(self):
        held = [("stale", "an untouched backlog row from months ago", {"state": "backlog"}),
                ("orphan", "its parent row is done", {"state": "backlog"}), ("worked", "zzz qqq", {})]
        got = similar.agreement(self.cset, held, threshold=0.05, margin=0.0)
        self.assertEqual((got["n"], got["reproduced"], got["abstained"]), (3, 2, 1))
        self.assertAlmostEqual(got["agreement"], 2 / 3)
        self.assertEqual(similar.agreement(self.cset, [])["agreement"], 0.0)
        loo = similar.loo_agreement(self.cset)
        self.assertEqual(loo["n"], 6); self.assertGreaterEqual(loo["reproduced"], 1)
        self.assertEqual(loo["agreement"], loo["reproduced"] / 6)
        similar.freeze([EXAMPLES[0], ("x", "unrelated words here", {}, 2)], self.d / "one.jsonl", RATIFIED, BASE)
        self.assertEqual(similar.loo_agreement(similar.load(self.d / "one.jsonl"))["reproduced"], 0)   # each label alone

    def test_a_malformed_set_is_refused(self):
        bad = self.d / "bad.jsonl"
        bad.write_text(json.dumps({"idf": {}, "max_df": 0.2}) + "\n" + json.dumps({"label": "x", "inputs": "y", "row": 1}) + "\n")
        with self.assertRaises(ValueError):
            similar.load(bad)
        with self.assertRaises(ValueError):
            similar.freeze([], self.d / "empty.jsonl", RATIFIED, BASE)

    def test_hygiene_reads_similars_tfidf_unchanged(self):
        self.assertIs(hy.tokens, similar.tokens); self.assertIs(hy.cosine, similar.cosine)
        docs = {i: t for i, (_, t, _, _) in enumerate(EXAMPLES * 2)} | {99: "fonts colours spacing margins borders"}
        self.assertEqual(hy.tfidf(docs), similar.tfidf(docs, hy.HYGIENE_MAX_DF))
        self.assertFalse(hasattr(hy, "TOKEN"))                            # one implementation (#642)


class AdmissionTests(unittest.TestCase):
    """dmc:precedent-admission (#644): one case per outcome of `admission`, the cases covering exactly the record's
    outcomes; `admit` and `freeze_record` over a scratch decision log; the amendment test over a scratch git tree."""
    LINE = {"record": "session-overlap", "case": "r1", "fields": {"root": "other"}, "inputs": "both plans touch dmc.py",
            "outcome": "overlap", "row": 5, "status": "precedent", "source": "structured", "date": "2026-11-08",
            "y": "2026-11-08 Y precedent (2 cases: session-overlap×2)"}

    def test_every_outcome_is_decided(self):
        P, C = self.LINE, {**self.LINE, "status": "candidate"}
        cases = {"operator-side": similar.admission(P, [], True), "unnamed": similar.admission(None, [], False),
                 "self-derived": similar.admission({**P, "precedent": "0" * 64}, [], False),
                 "superseded": similar.admission(P, [C], False), "uncovered": similar.admission(C, [], False),
                 "admitted": similar.admission(P, [], False)}
        for code, got in cases.items():
            with self.subTest(outcome=code):
                self.assertEqual(got, code)
        self.assertEqual(similar.admission(P, [], False, amended=True), "superseded")
        record = json.loads((PKG / "dmc" / "precedent-admission.jsonld").read_text())
        self.assertEqual({o["termCode"] for o in record["hasDefinedTerm"]}, set(cases)); self.assertEqual(set(cases), set(similar.ADMISSION))

    def test_operator_side_reads_the_consequences(self):
        self.assertTrue(similar.operator_side({"hasDefinedTerm": [{"dyad:then": "the agent merges the PR"}]}))
        self.assertFalse(similar.operator_side({"hasDefinedTerm": [{"dyad:then": "the agent re-plans"}]}))

    def test_admit_and_freeze_record_over_the_log(self):
        e = unittest.mock.patch.dict(os.environ, {"DYAD_INSTANCE": "inst"}); e.start(); self.addCleanup(e.stop)
        rows = self.d / "inst" / "d-work" / "rows"; rows.mkdir(parents=True)
        for i in (5, 6):
            (rows / f"{i}.md").write_text(f"id: {i}\ntitle: t\nopened: 2026-11-01\nstate: planned\ndisposed: 2026-11-01 Y plan\nrefs: \n")
        log = self.d / "inst" / "d-work" / "decisions"; log.mkdir(parents=True)
        P = self.LINE
        lines = [P, {**P, "case": "r2", "inputs": "the plans touch different files", "outcome": "disjoint", "row": 6},
                 {**P, "case": "r3", "status": "candidate"}, {**P, "case": "r4", "precedent": "1" * 64},
                 {**P, "case": "r5"}, {**P, "case": "r5", "status": "candidate", "date": "2026-11-09"}]
        dl = dyadlib.load_guard("agent", "decision_log")
        (log / "6.md").write_text("\n".join(dl.render(l) for l in lines))
        entries, refused = similar.admit(self.d, "session-overlap")
        self.assertEqual([(lab, row) for lab, _, _, row in entries], [("overlap", 5), ("disjoint", 6)])
        self.assertEqual(refused, [("r3", "uncovered"), ("r4", "self-derived"), ("r5", "superseded")])
        self.assertEqual(similar.admit(self.d, "session-overlap", ["r1", "r9"])[1], [("r9", "unnamed")])
        sha, refused = similar.freeze_record(self.d, "session-overlap", self.d / "set.jsonl", BASE, max_df=0.9)
        cset = similar.load(self.d / "set.jsonl")
        self.assertEqual((cset["sha256"], cset["rows"], similar.labels(cset)), (sha, [5, 6], {"overlap", "disjoint"}))
        with self.assertRaises(ValueError) as e:
            similar.freeze_record(self.d, "session-overlap", self.d / "none.jsonl", BASE, cases=["r3"])
        self.assertIn("r3 uncovered", str(e.exception)); self.assertFalse((self.d / "none.jsonl").exists())
        (log / "6.md").write_text(dl.render({**P, "record": "replan", "outcome": "replan"}))
        self.assertEqual(similar.admit(self.d, "replan")[1], [("r1", "operator-side")])   # its consequence asks a plan-Y
        with self.assertRaises(ValueError):
            similar.admit(self.d, "no-such-record")

    def test_an_amendment_naming_the_case_supersedes_it(self):
        import subprocess
        run = lambda *a: subprocess.run(["git", "-C", str(self.d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                                        check=True, capture_output=True, text=True, env={**os.environ, **dyadlib.git_env(),
                                        "GIT_COMMITTER_DATE": "2026-11-10T12:00:00Z", "GIT_AUTHOR_DATE": "2026-11-10T12:00:00Z"})
        run("init", "-q", "-b", "main"); (self.d / "home.md").write_text("one\n"); run("add", "-A"); run("commit", "-qm", "a")
        (self.d / "home.md").write_text("one\ncase r1 now reads otherwise\n"); run("commit", "-qam", "amend")
        self.assertTrue(similar.amended_since(self.d, ["home.md"], "2026-11-08", "r1"))
        self.assertFalse(similar.amended_since(self.d, ["home.md"], "2026-11-08", "r2"))       # the case is not named
        self.assertFalse(similar.amended_since(self.d, ["home.md"], "2026-11-11", "r1"))       # before the line's date
        self.assertFalse(similar.amended_since(self.d, [], "2026-11-08", "r1"))

    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.d, True)


if __name__ == "__main__":
    unittest.main()
