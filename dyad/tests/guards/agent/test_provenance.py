"""Provenance guard tests (agent/provenance.py, Rule-7): the record's shape (title id, entries
numbered from 1, known kinds, a fenced body), the disposition count against the row's `disposed`
cell, the credential shapes that fail and the 40-hex that only warns, a missing record against the
instance's legacy list (#191: fails when a list exists, warns while none does), the transaction check
that the row and its record move together, and the live store."""
import os, subprocess, sys, tempfile, unittest
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
        self.assertEqual((pv.ENTITY, pv.CORPUS, pv.TRANSACTION), ("provenance", "agent", True))
        self.assertTrue(callable(pv.check_transaction))
        self.assertFalse(hasattr(pv, "SINCE_ID"))    # #191: another ledger's id, replaced by the instance's list
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

    # #191: a missing record against the instance's legacy list (<instance>/provenance_legacy.local.txt)
    def legacy_fixture(self, listing: str | None, records: dict[str, str] | None = None, rows: dict[str, str] | None = None):
        root = fixture(records if records is not None else {"7.md": GOOD},
                       rows if rows is not None else {"7.md": ROW, "8.md": ROW.replace("id: 7", "id: 8")})
        if listing is not None:
            (root / "agent-corpus" / pv.LEGACY).write_text(listing)
        return root

    def test_missing_record_warns_while_the_instance_has_no_list(self):
        """A system installing this version has no list yet: each unrecorded row warns, naming the file."""
        msgs = pv.check_package(self.legacy_fixture(None))
        self.assertEqual(fails(msgs), [])
        self.assertTrue(any("row #8" in m and pv.LEGACY in m for m in warns(msgs)), msgs)

    def test_missing_record_fails_once_the_instance_keeps_a_list(self):
        msgs = fails(pv.check_package(self.legacy_fixture("# none yet\n")))
        self.assertEqual(len(msgs), 1, msgs); self.assertIn("row #8 has no provenance record", msgs[0])

    def test_a_listed_row_needs_no_record_while_its_dispositions_are_the_listed_ones(self):
        self.assertEqual(pv.check_package(self.legacy_fixture("8 1 predates enforcement\n")), [])   # ROW holds 1 disposition
        msgs = fails(pv.check_package(self.legacy_fixture("8 0 predates enforcement\n")))           # one more than listed
        self.assertEqual(len(msgs), 1, msgs); self.assertIn("row #8 records 1 disposition(s)", msgs[0])

    def test_legacy_list_lines_are_checked(self):
        msgs = pv.check_package(self.legacy_fixture("8 1 ok\nnot a line\n8 1 twice\n99 0 no such row\n7 5 more than it has\n#8 cited as the ledger does\n"))
        f = fails(msgs)
        self.assertTrue(any(":2: not `<id> <n> <reason>`" in m for m in f), f)
        self.assertTrue(any("row #8 named twice" in m for m in f), f)
        self.assertTrue(any("row #99 is not in the ledger" in m for m in f), f)
        self.assertTrue(any("row #7 lists 5 lost" in m for m in f), f)
        self.assertTrue(any("looks like a row id" in m for m in warns(msgs)), msgs)

    def test_a_listed_row_holds_exactly_its_lost_count_fewer(self):
        """Its old dispositions' words are lost (property 3); every later one is exact (the alarm still rings)."""
        two = ROW.replace("disposed: 2026-09-14 Y plan", "disposed: 2026-09-14 Y plan; 2026-09-14 Y done")
        root = self.legacy_fixture("7 1 old words lost\n", {"7.md": GOOD}, {"7.md": two})
        self.assertEqual(fails(pv.check_package(root)), [])                           # 2 - 1 lost = 1: exact
        root = self.legacy_fixture("7 0 nothing lost\n", {"7.md": GOOD}, {"7.md": two})
        self.assertIn("row #7 records 2", " ".join(fails(pv.check_package(root))))    # a later disposition without words
        root = self.legacy_fixture("7 0 nothing lost\n", {"7.md": GOOD}, {"7.md": ROW})
        self.assertEqual(fails(pv.check_package(root)), [])                           # the boundary got == want - lost
        root = self.legacy_fixture(None, {"7.md": GOOD}, {"7.md": two})
        self.assertIn("row #7 records 2", " ".join(fails(pv.check_package(root))))    # unlisted: exact

    def test_live_store_passes_with_its_legacy_list(self):
        root = dyadlib.repo_root()
        listed, problems = pv.legacy(root)
        if listed is None:
            self.skipTest(f"this instance keeps no {pv.LEGACY}: a system that installed the core alone")
        self.assertEqual(fails(problems), [])
        self.assertEqual([m for m in warns(pv.check_package(root)) if "has no provenance record" in m], [])

    def test_describe_and_summary(self):
        root = fixture({"7.md": GOOD})
        d = pv.describe(root, dyadlib.PKG)
        self.assertEqual([f[0] for f in d["fields"]], list(pv.FIELDS))
        self.assertIn("store", d); self.assertIn("parser", d)
        self.assertIn("1 records", pv.summary(root))


class TransactionTests(unittest.TestCase):
    """#191: each commit of the range's own history, against its parent — the gap is refused on the push
    that creates it, never left for a state check to find on everyone's `main` (Rule-7 property 3)."""
    INST = "agent-corpus"
    def setUp(self):
        os.environ.pop("DYAD_INSTANCE", None)
        self.ROWS, self.REC = f"{self.INST}/d-work/rows", f"{self.INST}/d-work/provenance"
        self.d = Path(tempfile.mkdtemp())
        self.git("init", "-q", "-b", "main"); self.git("config", "user.email", "t@t"); self.git("config", "user.name", "t")
        self.write(f"{self.ROWS}/7.md", ROW); self.write(f"{self.REC}/7.md", GOOD)
        self.base = self.commit("root")
    def git(self, *a): return subprocess.run(["git", *a], cwd=self.d, check=True, capture_output=True, text=True).stdout
    def write(self, rel, text):
        p = self.d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
    def commit(self, msg="c"):
        self.git("add", "-A"); self.git("commit", "-qm", msg); return self.git("rev-parse", "HEAD").strip()
    def tx(self, head, base=None): return pv.check_transaction(self.d, base or self.base, head)
    def row(self, rid, state="open", disposed=""):
        return f"id: {rid}\ntitle: t{rid}\nopened: 2026-09-14\nstate: {state}\ndisposed: {disposed}\nrefs: \n"
    def rec(self, rid, *entries):
        body = "".join(f"\n## {n} {k} 2026-09-14\n```\n{t}\n```\n" for n, (k, t) in enumerate(entries, 1))
        return f"# Provenance #{rid}\n{body}"
    def one(self, out, text):
        self.assertEqual(len(out), 1, out); self.assertIn(text, out[0])


    def test_row_added_without_record_fails(self):
        self.write(f"{self.ROWS}/8.md", self.row(8))
        self.one(self.tx(self.commit()), "adds row #8 and its record gains no entry")

    def test_row_added_with_a_title_only_record_fails(self):
        self.write(f"{self.ROWS}/8.md", self.row(8)); self.write(f"{self.REC}/8.md", "# Provenance #8\n")
        self.one(self.tx(self.commit()), "adds row #8 and its record gains no entry")

    def test_row_added_with_its_prompt_passes(self):
        self.write(f"{self.ROWS}/8.md", self.row(8)); self.write(f"{self.REC}/8.md", self.rec(8, ("prompt", "do eight")))
        self.assertEqual(self.tx(self.commit()), [])

    def test_row_added_with_a_disposition_but_no_words_for_it_fails(self):
        self.write(f"{self.ROWS}/8.md", self.row(8, disposed="2026-09-14 Y open")); self.write(f"{self.REC}/8.md", self.rec(8, ("prompt", "p")))
        self.one(self.tx(self.commit()), "gains 1 disposed entry and its record gains 0")

    def test_backlog_row_needs_a_disposition_entry(self):
        self.write(f"{self.ROWS}/8.md", self.row(8, "backlog")); self.write(f"{self.REC}/8.md", self.rec(8, ("prompt", "later")))
        self.one(self.tx(self.commit()), "as backlog")
        self.write(f"{self.ROWS}/9.md", self.row(9, "backlog", "2026-09-14 Y backlog")); self.write(f"{self.REC}/9.md", self.rec(9, ("disposition", "Y")))
        self.assertEqual(self.tx(self.commit(), base=self.git("rev-parse", "HEAD~1").strip()), [])

    def test_born_backlog_is_judged_at_its_birth_commit(self):
        """Born backlog with no disposition, then opened in a later commit of the same push: still refused."""
        self.write(f"{self.ROWS}/8.md", self.row(8, "backlog")); self.commit("born")
        self.write(f"{self.ROWS}/8.md", self.row(8, "open")); self.write(f"{self.REC}/8.md", self.rec(8, ("prompt", "go")))
        out = self.tx(self.commit("opened"))
        self.assertTrue(any("adds row #8 and its record gains no entry" in m for m in out), out)

    def test_backlog_to_open_needs_a_prompt(self):
        self.write(f"{self.ROWS}/8.md", self.row(8, "backlog", "2026-09-14 Y backlog")); self.write(f"{self.REC}/8.md", self.rec(8, ("disposition", "Y")))
        base = self.commit()
        self.write(f"{self.ROWS}/8.md", self.row(8, "open", "2026-09-14 Y backlog"))
        self.one(self.tx(self.commit(), base=base), "opens backlog row #8")
        self.write(f"{self.REC}/8.md", self.rec(8, ("disposition", "Y"), ("prompt", "now")))
        self.git("commit", "--amend", "-qam", "with the prompt")
        self.assertEqual(self.tx(self.git("rev-parse", "HEAD").strip(), base=base), [])

    def test_disposition_without_its_words_fails(self):
        self.write(f"{self.ROWS}/7.md", ROW.replace("Y plan", "Y plan; 2026-09-14 Y done").replace("planned", "done"))
        self.one(self.tx(self.commit()), "gains 1 disposed entry and its record gains 0")

    def test_words_without_a_disposition_fail(self):
        self.write(f"{self.REC}/7.md", GOOD + "\n## 3 disposition 2026-09-14\n```\nY\n```\n")
        self.one(self.tx(self.commit()), "gains 0 disposed entries and its record gains 1")

    def test_words_gathered_in_a_later_commit_fail(self):
        """Property 3: written in the commit of the event it records — not gathered before the push."""
        self.write(f"{self.ROWS}/7.md", ROW.replace("Y plan", "Y plan; 2026-09-14 Y done").replace("planned", "done")); self.commit("row")
        self.write(f"{self.REC}/7.md", GOOD + "\n## 3 disposition 2026-09-14 Y done\n```\nY\n```\n")
        out = self.tx(self.commit("record"))
        self.assertEqual(len(out), 2, out)   # the row commit lacks the words, the record commit lacks the disposition

    def test_disposition_with_its_words_in_one_commit_passes(self):
        self.write(f"{self.ROWS}/7.md", ROW.replace("Y plan", "Y plan; 2026-09-14 Y done").replace("planned", "done"))
        self.write(f"{self.REC}/7.md", GOOD + "\n## 3 disposition 2026-09-14 Y done\n```\nY\n```\n")
        self.assertEqual(self.tx(self.commit()), [])

    def test_a_record_only_grows(self):
        self.write(f"{self.REC}/7.md", GOOD.replace("do the thing", "do another thing"))
        self.one(self.tx(self.commit()), "rewrites or removes entries")
        self.git("reset", "-q", "--hard", self.base)
        self.write(f"{self.ROWS}/7.md", ROW.replace("disposed: 2026-09-14 Y plan", "disposed: "))
        self.write(f"{self.REC}/7.md", GOOD[:GOOD.index("## 2")])                   # a disposition and its words both erased
        self.one(self.tx(self.commit()), "rewrites or removes entries")
        self.git("reset", "-q", "--hard", self.base)
        (self.d / self.REC / "7.md").unlink()
        self.one(self.tx(self.commit()), "deletes the record of row #7")

    def test_a_prompt_on_an_existing_row_passes(self):
        self.write(f"{self.REC}/7.md", GOOD + "\n## 3 prompt 2026-09-14\n```\nand also\n```\n")
        self.assertEqual(self.tx(self.commit()), [])

    def test_an_inconsistent_change_main_made_after_the_branch_point_is_not_the_branchs(self):
        """Only the commits head has and base lacks are judged: main gained a disposition without its words
        (a bypass) after the branch point; the branch that only adds a prompt does not answer for it."""
        self.git("checkout", "-q", "-b", "branch")
        self.write(f"{self.REC}/7.md", GOOD + "\n## 3 prompt 2026-09-14\n```\nmore\n```\n"); head = self.commit("branch work")
        self.git("checkout", "-q", "main")
        self.write(f"{self.ROWS}/7.md", ROW.replace("Y plan", "Y plan; 2026-09-14 Y done")); moved = self.commit("main, around the hook")
        self.assertEqual(pv.check_transaction(self.d, moved, head), [])

    def test_a_renamed_row_file_is_seen_under_both_names(self):
        """Rename detection off: `rows/7.md` -> `rows/007.md` with a disposition added is not hidden."""
        self.git("mv", f"{self.ROWS}/7.md", f"{self.ROWS}/007.md")
        self.write(f"{self.ROWS}/007.md", ROW.replace("Y plan", "Y plan; 2026-09-14 Y done"))
        head = self.commit()
        out = self.tx(head)
        self.assertEqual(out, [])   # 007 is not a canonical id; 7 is deleted: both are the row guard's report
        rows_guard = dyadlib.load_guard("agent", "rows")
        root_fixture = Path(tempfile.mkdtemp()); (root_fixture / self.ROWS).mkdir(parents=True)
        (root_fixture / self.ROWS / "007.md").write_text(ROW)
        self.assertIn("differs from the file name", " ".join(rows_guard.check_package(root_fixture)))

    def test_words_rewritten_while_resolving_a_merge_fail(self):
        self.git("checkout", "-q", "-b", "branch")
        self.write(f"{self.REC}/7.md", GOOD + "\n## 3 prompt 2026-09-14\n```\nmore\n```\n"); self.commit("branch")
        self.git("checkout", "-q", "main")
        self.write(f"{self.ROWS}/8.md", self.row(8)); self.write(f"{self.REC}/8.md", self.rec(8, ("prompt", "eight"))); moved = self.commit("main")
        self.git("checkout", "-q", "branch"); self.git("merge", "-q", "--no-commit", "main")
        self.write(f"{self.REC}/7.md", GOOD.replace("do the thing", "do NOT do the thing") + "\n## 3 prompt 2026-09-14\n```\nmore\n```\n")
        self.git("add", "-A"); self.git("commit", "-qm", "merge main")
        out = self.tx(self.git("rev-parse", "HEAD").strip(), base=moved)
        self.assertTrue(any("merge" in m and "row #7" in m for m in out), out)

    def test_a_clean_merge_of_main_passes(self):
        self.git("checkout", "-q", "-b", "branch")
        self.write(f"{self.REC}/7.md", GOOD + "\n## 3 prompt 2026-09-14\n```\nmore\n```\n"); self.commit("branch")
        self.git("checkout", "-q", "main")
        self.write(f"{self.ROWS}/8.md", self.row(8)); self.write(f"{self.REC}/8.md", self.rec(8, ("prompt", "eight"))); moved = self.commit("main")
        self.git("checkout", "-q", "branch"); self.git("merge", "-q", "--no-edit", "main")
        self.assertEqual(self.tx(self.git("rev-parse", "HEAD").strip(), base=moved), [])

    def test_the_failure_says_how_to_recover(self):
        self.write(f"{self.ROWS}/7.md", ROW.replace("Y plan", "Y plan; 2026-09-14 Y done").replace("planned", "done"))
        self.assertIn("git reset --keep origin/main", self.tx(self.commit())[0])

    def test_ledger_unrelated_range_is_silent(self):
        self.write("dyad/x.py", "x")
        self.assertEqual(self.tx(self.commit()), [])

    def test_unrelated_history_falls_back_to_the_base(self):
        self.git("checkout", "-q", "--orphan", "other"); self.git("rm", "-rqf", ".")
        self.write(f"{self.ROWS}/8.md", self.row(8)); head = self.commit("orphan")
        self.assertTrue(any("adds row #8" in m for m in self.tx(head)))

class TransactionInstanceTests(TransactionTests):
    """The same checks where DYAD_INSTANCE names another directory, relative, absolute inside the tree,
    or with a trailing slash: the transaction check and the package check read the same instance."""
    INST = "other-corpus"
    def setUp(self):
        super().setUp()
        os.environ["DYAD_INSTANCE"] = self.INST; self.addCleanup(os.environ.pop, "DYAD_INSTANCE", None)
    def test_absolute_and_trailing_slash_forms(self):
        self.write(f"{self.ROWS}/8.md", self.row(8)); head = self.commit()
        for form in (str(self.d / self.INST), self.INST + "/"):
            with self.subTest(form=form):
                os.environ["DYAD_INSTANCE"] = form
                self.one(self.tx(head), "adds row #8")

if __name__ == "__main__":
    unittest.main()
