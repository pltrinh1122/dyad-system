"""episodes.py (the chronicle craft's guard, entity `episode`; #502, #498 C4): the absent store, a good episode, each
failing shape (missing path, bad time line, undeclared repo, missing provenance entry), the commit: form, the inference warning for a
cross-repo citation with no clone, a citation resolved in a local clone, the invariants, and the live repo; the keyed
form (#650): a passing keyed piece and key, an unkeyed paragraph, a key line naming no paragraph, first words that
differ, an uncited or unresolvable record line, an undeclared composite, a marker, footnote or `fiction:` line left in
keyed prose, a missing key, and a labelled piece unchanged; the exact-quote fixed point (#650 revision 2): a fiction
line telling a system event passes, a quote keyed `fiction` fails, a quote not held verbatim at its `path:` or `prov:`
citation fails, one only at a `repo:` citation is warned, and quotes in a labelled piece are not read."""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "dyad" / "scripts"))
import dyadlib
episodes = dyadlib.load_guard_file(Path(__file__).resolve().parents[2] / "guards" / "episodes.py")
TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "episode.md"
SHA = "0123456789abcdef0123456789abcdef01234567"
PROV = "# Provenance #7\n\n## 1 prompt 2026-10-27\n```\nI began with AI agents a year ago.\n```\n\n## 2 disposition 2026-10-27\n```\nY\n```\n"

def episode(time="present, 2026-10-27", repos="none", notes=("path:agent-corpus/d-work/rows/1.md",), drop=()) -> str:
    head = {"title": "The announcement", "season": "1", "episode": "0", "time": time, "repos": repos}
    lines = [f"{k}: {v}" for k, v in head.items() if k not in drop]
    body = " ".join(f"Event {i}.[^{i}]" for i in range(1, len(notes) + 1))
    return "\n".join(lines) + "\n\n" + body + "\n\n" + "\n".join(f"[^{i}]: {n}" for i, n in enumerate(notes, 1)) + "\n"

class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        rows = self.root / "agent-corpus" / "d-work" / "rows"; rows.mkdir(parents=True); (rows / "1.md").write_text("id: 1\n")
        prov = self.root / "agent-corpus" / "d-work" / "provenance"; prov.mkdir(parents=True); (prov / "7.md").write_text(PROV)
        env = {k: v for k, v in os.environ.items() if k not in ("DYAD_SITE", "DYAD_REPOS_DIR", "DYAD_INSTANCE")}
        p = mock.patch.dict(os.environ, env, clear=True); p.start(); self.addCleanup(p.stop)
    def write(self, text: str, name: str = "s1e0.md") -> list[str]:
        d = self.root / "site" / "episodes"; d.mkdir(parents=True, exist_ok=True); (d / name).write_text(text)
        return episodes.check_package(self.root)
    def fails(self, msgs): return [m for m in msgs if not m.startswith("warning:")]

class Store(Fixture):
    def test_absent_store_skips(self):
        msgs = episodes.check_package(self.root)
        self.assertEqual(len(msgs), 1); self.assertTrue(msgs[0].startswith("warning: skip episodes: no site/episodes/"), msgs[0])
    def test_site_is_overridable(self):
        os.environ["DYAD_SITE"] = "pages"
        self.assertIn("no pages/episodes/", episodes.check_package(self.root)[0])

class Episodes(Fixture):
    def test_good_episode_passes(self):
        self.assertEqual(self.write(episode(notes=("path:agent-corpus/d-work/rows/1.md a gloss", "prov:#7/1"))), [])
        self.assertIn("1 episode(s), 2 citation(s)", episodes.summary(self.root))
    def test_missing_in_repo_path_fails(self):
        f = self.fails(self.write(episode(notes=("path:agent-corpus/d-work/rows/2.md",))))
        self.assertEqual(len(f), 1); self.assertIn("does not exist in the tree", f[0])
        self.assertEqual(len(self.fails(self.write(episode(notes=("path:../etc/passwd",))))), 1)
    def test_bad_time_line_fails(self):
        for t in ("future, 2026-10-27", "present 2026-10-27", "past, 2026-13-01", "present, 27-10-2026"):
            f = self.fails(self.write(episode(time=t)))
            self.assertEqual(len(f), 1, t); self.assertIn("is not `present|past, YYYY-MM-DD`", f[0])
        self.assertEqual(self.write(episode(time="past, 2025-09-01")), [])
    def test_missing_header_key_fails(self):
        f = self.fails(self.write(episode(drop=("repos",))))
        self.assertEqual(len(f), 1); self.assertIn("lacks `repos:`", f[0])
    def test_unknown_citation_form_and_undefined_footnote_fail(self):
        f = self.fails(self.write("title: t\nseason: 1\nepisode: 0\ntime: present, 2026-10-27\nrepos: none\n\nA.[^1] B.[^2]\n\n[^1]: http://example.com\n"))
        self.assertEqual(len(f), 2); self.assertTrue(any("never defined" in m for m in f)); self.assertTrue(any("none of path:" in m for m in f))
    def test_no_citation_fails(self):
        f = self.fails(self.write(episode(notes=())))
        self.assertEqual(len(f), 1); self.assertIn("cites nothing", f[0])
    def test_undeclared_repo_fails(self):
        f = self.fails(self.write(episode(notes=(f"repo:pltrinh1122/dyad-bond@{SHA}:README.md",))))
        self.assertEqual(len(f), 1); self.assertIn("not declared in `repos:`", f[0])
        f = self.fails(self.write(episode(repos="pltrinh1122/dyad-bond", notes=("path:agent-corpus/d-work/rows/1.md",))))
        self.assertEqual(len(f), 1); self.assertIn("is not `<owner>/<repo>=public|private`", f[0])
    def test_short_sha_fails(self):
        f = self.fails(self.write(episode(repos="pltrinh1122/dyad-bond=public", notes=("repo:pltrinh1122/dyad-bond@0123abc:README.md",))))
        self.assertEqual(len(f), 1); self.assertIn("40-hex", f[0])
    def test_cross_repo_without_clone_warns_inference(self):
        msgs = self.write(episode(repos="pltrinh1122/dyad-bond=public pltrinh1122/old=private",
                                  notes=(f"repo:pltrinh1122/dyad-bond@{SHA}:README.md", f"repo:pltrinh1122/old@{SHA}:a.md")))
        self.assertEqual(self.fails(msgs), [])
        self.assertEqual(len(msgs), 2)
        self.assertRegex(msgs[0], r"^warning: .*2 cross-repo citation\(s\) unresolvable \(The World.*inference$")
        self.assertIn("private repo(s) pltrinh1122/old", msgs[1])
    def test_cross_repo_resolved_in_local_clone(self):
        repos = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, repos, ignore_errors=True)
        clone = repos / "dyad-bond"; clone.mkdir()
        g = lambda *a: subprocess.run(["git", "-C", str(clone), *a], check=True, capture_output=True, text=True, env=dyadlib.git_env()).stdout.strip()
        g("init", "-q"); (clone / "README.md").write_text("bond\n"); g("add", "README.md")
        g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"); sha = g("rev-parse", "HEAD")
        os.environ["DYAD_REPOS_DIR"] = str(repos)
        decl = "pltrinh1122/dyad-bond=public"
        self.assertEqual(self.write(episode(repos=decl, notes=(f"repo:pltrinh1122/dyad-bond@{sha}:README.md",))), [])
        f = self.fails(self.write(episode(repos=decl, notes=(f"repo:pltrinh1122/dyad-bond@{sha}:MISSING.md",))))
        self.assertEqual(len(f), 1); self.assertIn("is not in the clone", f[0])
    def test_commit_citation_declared_and_full_sha(self):
        f = self.fails(self.write(episode(notes=(f"commit:pltrinh1122/dyad-bond@{SHA}",))))
        self.assertEqual(len(f), 1); self.assertIn("commit:pltrinh1122/dyad-bond is not declared in `repos:`", f[0])
        f = self.fails(self.write(episode(repos="pltrinh1122/dyad-bond=public", notes=("commit:pltrinh1122/dyad-bond@0123abc",))))
        self.assertEqual(len(f), 1); self.assertIn("40-hex", f[0])
        msgs = self.write(episode(repos="pltrinh1122/dyad-bond=public", notes=(f"commit:pltrinh1122/dyad-bond@{SHA}",)))
        self.assertEqual(self.fails(msgs), [])
        self.assertRegex(msgs[0], r"^warning: .*1 cross-repo citation\(s\) unresolvable \(The World.*inference$")
    def test_commit_citation_resolved_in_local_clone(self):
        repos = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, repos, ignore_errors=True)
        clone = repos / "dyad-bond"; clone.mkdir()
        g = lambda *a: subprocess.run(["git", "-C", str(clone), *a], check=True, capture_output=True, text=True, env=dyadlib.git_env()).stdout.strip()
        g("init", "-q"); (clone / "README.md").write_text("bond\n"); g("add", "README.md")
        g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"); sha = g("rev-parse", "HEAD")
        os.environ["DYAD_REPOS_DIR"] = str(repos)
        decl = "pltrinh1122/dyad-bond=public"
        self.assertEqual(self.write(episode(repos=decl, notes=(f"commit:pltrinh1122/dyad-bond@{sha}",))), [])
        f = self.fails(self.write(episode(repos=decl, notes=(f"commit:pltrinh1122/dyad-bond@{SHA}",))))
        self.assertEqual(len(f), 1); self.assertIn("commit:pltrinh1122/dyad-bond@0123456789ab is not in the clone", f[0])
    def fiction(self, header=True, label=None, passage="*(fiction)* He lay awake, counting the questions he had not asked."):
        text = episode()
        if header:
            text = text.replace("repos: none\n", f"repos: none\nfiction: {label or episodes.FICTION_LABEL}\n", 1)
        head, _, rest = text.partition("\n\n")
        return head + "\n\n" + passage + "\n\n" + rest
    def test_fiction_layer_labelled_passes(self):
        self.assertEqual(self.write(self.fiction()), [])
    def test_marked_passage_without_header_fails(self):
        f = self.fails(self.write(self.fiction(header=False)))
        self.assertEqual(len(f), 1); self.assertIn("and no `fiction:` header", f[0])
    def test_fiction_header_other_label_fails(self):
        f = self.fails(self.write(self.fiction(label="persona")))
        self.assertEqual(len(f), 1); self.assertIn("part 'persona' is neither", f[0])
    def test_marked_passage_with_citation_fails(self):
        f = self.fails(self.write(self.fiction(passage="*(fiction)* He remembered the night the rule was made.[^1]")))
        self.assertEqual(len(f), 1); self.assertIn("the fiction layer cites nothing", f[0])
    def test_fiction_header_without_passage_warns(self):
        msgs = self.write(self.fiction(passage="An event.[^1]"))
        self.assertEqual(self.fails(msgs), [])
        self.assertEqual(len(msgs), 1); self.assertRegex(msgs[0], r"^warning: .*no passage marked")
    def test_record_layer_still_needs_citations(self):
        f = self.fails(self.write(self.fiction(passage="*(fiction)* Interior.\n\nAn event.[^9]")))
        self.assertEqual(len(f), 1); self.assertIn("[^9] is referenced and never defined", f[0])
    def test_composites_declared_in_the_fiction_line_pass(self):
        label = f"{episodes.FICTION_LABEL}; composites: Mara, The Apprentice"
        passage = "*(fiction)* Mara painted all night; The Apprentice watched."
        self.assertEqual(self.write(self.fiction(label=label, passage=passage)), [])
        self.assertEqual(self.write(self.fiction(label="composites: Mara", passage="*(fiction)* Mara laughed.")), [])
    def test_composite_outside_a_marked_passage_fails(self):
        label = f"{episodes.FICTION_LABEL}; composites: Mara"
        f = self.fails(self.write(self.fiction(label=label, passage="*(fiction)* Interior.\n\nMara read the release notes.[^1]")))
        self.assertEqual(len(f), 1); self.assertIn("composite(s) Mara in a passage not marked", f[0])
        self.assertEqual(self.fails(self.write(self.fiction(label=label, passage="*(fiction)* Interior.\n\nMaraschino.[^1]"))), [])
    def test_malformed_composites_part_fails(self):
        for label in ("composites:", "composites: Mara, ", "composites: Mara, Mara"):
            f = self.fails(self.write(self.fiction(label=label)))
            self.assertEqual(len(f), 1, label); self.assertIn("is neither", f[0])
    def test_prov_citation(self):
        self.assertEqual(self.write(episode(notes=("prov:#7/2",))), [])
        f = self.fails(self.write(episode(notes=("prov:#7/3",))))
        self.assertEqual(len(f), 1); self.assertIn("has no entry 3", f[0])
        f = self.fails(self.write(episode(notes=("prov:#8/1",))))
        self.assertEqual(len(f), 1); self.assertIn("no provenance record #8", f[0])

KEYED_HEAD = "title: The key\nseason: 1\nepisode: 1\ntime: present, 2026-11-09\nrepos: {repos}\nform: keyed\nkey: {key}\n"
KEYED_BODY = ["The cos opened the board at dawn.", "He lay awake, counting the questions.", "Mara painted all night."]
KEY_LINES = ["¶1 The cos opened | record path:agent-corpus/d-work/rows/1.md; prov:#7/1",
             "¶2 He lay awake | fiction persona", "¶3 Mara painted | fiction composites: Mara"]

class Keyed(Fixture):
    def keyed(self, body=KEYED_BODY, key=KEY_LINES, repos="none", head_extra="", keyname="s1e1.key.md", write_key=True):
        d = self.root / "site" / "episodes"; d.mkdir(parents=True, exist_ok=True)
        if write_key:
            (d / "s1e1.key.md").write_text("<!-- the key of s1e1 -->\n\n" + "\n".join(key) + "\n")
        return self.write(KEYED_HEAD.format(repos=repos, key=keyname) + head_extra + "\n" + "\n\n".join(body) + "\n", "s1e1.md")
    def test_keyed_piece_passes_and_its_key_is_no_episode(self):
        self.assertEqual(self.keyed(), [])
        self.assertEqual([p.name for p in episodes.episodes(self.root)], ["s1e1.md"])
        self.assertIn("1 episode(s), 2 citation(s)", episodes.summary(self.root))
    def test_unkeyed_paragraph_and_doubled_line_fail(self):
        f = self.fails(self.keyed(key=KEY_LINES[:2]))
        self.assertEqual(f, ["site/episodes/s1e1.md: paragraph 3 has no key line (chronicle.md §2)"])
        f = self.fails(self.keyed(key=KEY_LINES + ["¶3 Mara painted | fiction persona"]))
        self.assertEqual(len(f), 1); self.assertIn("paragraph 3 has 2 key lines", f[0])
    def test_key_line_naming_no_paragraph_fails(self):
        f = self.fails(self.keyed(key=KEY_LINES + ["¶4 Gone | fiction persona"]))
        self.assertEqual(len(f), 1); self.assertIn("key line ¶4 names no paragraph; the piece has 3", f[0])
    def test_first_words_must_match(self):
        f = self.fails(self.keyed(key=["¶1 The home opened | record prov:#7/1"] + KEY_LINES[1:]))
        self.assertEqual(len(f), 1); self.assertIn("'The home opened' is not how paragraph 1 opens", f[0])
    def test_record_line_uncited_or_unresolvable_fails(self):
        f = self.fails(self.keyed(key=["¶1 The cos opened | record "] + KEY_LINES[1:]))
        self.assertTrue(any("is not `¶<n> <first words> | record" in m for m in f), f)
        f = self.fails(self.keyed(key=["¶1 The cos opened | record prov:#7/9; http://example.com"] + KEY_LINES[1:]))
        self.assertEqual(len(f), 2, f); self.assertTrue(any("¶1 prov:#7/9: provenance record #7 has no entry 9" in m for m in f))
        self.assertTrue(any("¶1 'http://example.com' is none of path:" in m for m in f))
        f = self.fails(self.keyed(key=["¶1 The cos opened | fiction persona"] + KEY_LINES[1:]))
        self.assertEqual(len(f), 1); self.assertIn("its key holds no record line", f[0])
    def test_cross_repo_key_line_is_judged_as_a_footnote(self):
        key = [f"¶1 The cos opened | record repo:pltrinh1122/old@{SHA}:a.md"] + KEY_LINES[1:]
        f = self.fails(self.keyed(key=key))
        self.assertEqual(len(f), 1); self.assertIn("¶1 repo:pltrinh1122/old is not declared in `repos:`", f[0])
        msgs = self.keyed(key=key, repos="pltrinh1122/old=private")
        self.assertEqual(self.fails(msgs), [])
        self.assertTrue(any("1 cross-repo citation(s) unresolvable" in m for m in msgs))
        self.assertTrue(any("private repo(s) pltrinh1122/old" in m for m in msgs))
    def test_undeclared_composite_fails(self):
        f = self.fails(self.keyed(body=KEYED_BODY[:2] + ["Mara painted all night; Ivo watched."],
                                  key=KEY_LINES[:2] + ["¶3 Mara painted | fiction composites: Mara, Ivo"]))
        self.assertEqual(f, [])
        f = self.fails(self.keyed(body=KEYED_BODY + ["Mara read the release notes."],
                                  key=KEY_LINES + ["¶4 Mara read | record prov:#7/2"]))
        self.assertEqual(len(f), 1); self.assertIn("composite(s) Mara in paragraph 4, which its key line does not label", f[0])
        f = self.fails(self.keyed(key=KEY_LINES[:2] + ["¶3 Mara painted | fiction composites: Mara, Mara"]))
        self.assertEqual(len(f), 1); self.assertIn("empty or repeated", f[0])
    def test_labels_left_in_keyed_prose_fail(self):
        f = self.fails(self.keyed(body=KEYED_BODY[:1] + ["*(fiction)* He lay awake, counting."] + KEYED_BODY[2:],
                                  key=KEY_LINES[:1] + ["¶2 *(fiction)* He lay | fiction persona"] + KEY_LINES[2:]))
        self.assertEqual(len(f), 1); self.assertIn("marks paragraph(s) 2 *(fiction)*", f[0])
        f = self.fails(self.keyed(body=["The cos opened the board at dawn.[^1]"] + KEYED_BODY[1:] + ["[^1]: prov:#7/1"]))
        self.assertEqual(len(f), 1); self.assertIn("holds footnotes", f[0])
        f = self.fails(self.keyed(head_extra=f"fiction: {episodes.FICTION_LABEL}\n"))
        self.assertEqual(len(f), 1); self.assertIn("carries a `fiction:` line", f[0])
    def test_missing_or_misnamed_key_fails(self):
        f = self.fails(self.keyed(write_key=False))
        self.assertEqual(len(f), 1); self.assertIn("`key: s1e1.key.md` names no `*.key.md` file beside the piece", f[0])
        f = self.fails(self.keyed(keyname="../s1e1.key.md"))
        self.assertEqual(len(f), 1); self.assertIn("names no `*.key.md` file", f[0])
        f = self.fails(self.write(KEYED_HEAD.format(repos="none", key="x").replace("key: x\n", "") + "\nA.\n", "s1e1.md"))
        self.assertEqual(len(f), 1); self.assertIn("header lacks `key:`", f[0])
    def test_unknown_form_fails(self):
        f = self.fails(self.write(episode().replace("repos: none\n", "repos: none\nform: annotated\n"), "s1e0.md"))
        self.assertEqual(len(f), 1); self.assertIn("`form: annotated` is neither labelled nor keyed", f[0])
    def test_bad_key_line_fails(self):
        f = self.fails(self.keyed(key=KEY_LINES + ["paragraph four is record"]))
        self.assertEqual(len(f), 1); self.assertIn("key line 'paragraph four is record' is not", f[0])
    def test_labelled_piece_unchanged(self):
        self.assertEqual(self.write(episode(), "s1e0.md"), [])
        self.assertEqual(self.write(episode().replace("repos: none\n", "repos: none\nform: labelled\n"), "s1e0.md"), [])
    def test_key_template_parses(self):
        lines, bad = episodes.parse_key((TEMPLATE.parent / "key.md").read_text())
        self.assertEqual(bad, []); self.assertEqual([l["layer"] for l in lines], ["record", "record", "fiction", "fiction"])
        self.assertEqual(lines[1]["citations"][1].split(":", 1)[0], "commit")

class Quotes(Fixture):
    keyed = Keyed.keyed
    def test_fiction_line_may_tell_a_system_event(self):
        body = KEYED_BODY[:1] + ["The automaton merged all forty PRs at midnight and the cos wept."] + KEYED_BODY[2:]
        key = KEY_LINES[:1] + ["¶2 The automaton merged | fiction persona"] + KEY_LINES[2:]
        self.assertEqual(self.keyed(body=body, key=key), [])
    def test_quote_keyed_fiction_fails(self):
        body = KEYED_BODY[:1] + ['He lay awake: "I began with AI agents a year ago."'] + KEYED_BODY[2:]
        f = self.fails(self.keyed(body=body))
        self.assertEqual(len(f), 1); self.assertIn("paragraph 2 quotes 'I began with AI agents a year ago.' and its key line is `fiction`", f[0])
    def test_quote_held_verbatim_at_prov_or_path_passes(self):
        body = ['The cos opened the board: “I began with\nAI agents a year ago.” Then "id: 1".'] + KEYED_BODY[1:]
        self.assertEqual(self.keyed(body=body), [])
    def test_quote_not_held_fails(self):
        body = ['The cos opened the board: "I began with AI agents two years ago."'] + KEYED_BODY[1:]
        f = self.fails(self.keyed(body=body))
        self.assertEqual(len(f), 1); self.assertIn("quotes 'I began with AI agents two years ago.', which its key line's path:/prov: citations do not hold verbatim", f[0])
        f = self.fails(self.keyed(body=['The cos opened: "a year ago"'] + KEYED_BODY[1:],
                                  key=["¶1 The cos opened | record prov:#7/2"] + KEY_LINES[1:]))
        self.assertEqual(len(f), 1); self.assertIn("do not hold verbatim", f[0])
    def test_quote_at_cross_repo_citation_only_is_warned(self):
        body = ['The cos opened: "bond"'] + KEYED_BODY[1:]
        msgs = self.keyed(body=body, repos="pltrinh1122/dyad-bond=public",
                          key=[f"¶1 The cos opened | record repo:pltrinh1122/dyad-bond@{SHA}:README.md"] + KEY_LINES[1:])
        self.assertEqual(self.fails(msgs), [])
        self.assertTrue(any(m.startswith("warning:") and "repo:/commit: citations only; not read" in m for m in msgs), msgs)
    def test_labelled_piece_quotes_unread(self):
        self.assertEqual(self.write(episode().replace("Event 1.", 'He said "nothing like this".'), "s1e0.md"), [])

class Template(Fixture):
    def test_template_header_has_every_key(self):
        header, _, notes = episodes.parse(TEMPLATE.read_text())
        self.assertEqual(tuple(k for k in header if k in episodes.HEADER), episodes.HEADER)
        self.assertEqual(sorted(n.split(":", 1)[0] for n in notes.values()), sorted(episodes.FORMS))

class Invariants(unittest.TestCase):
    def test_invariants_hold(self):
        self.assertEqual(dyadlib.false_invariants(episodes.INVARIANTS), [])
    def test_contract(self):
        self.assertIsNone(dyadlib.contract_problem(episodes, "craft", "chronicle", {"agent", "workstation", "preferences", "infra", "craft"}))
    def test_live_repo_never_fails(self):
        root = dyadlib.repo_root()
        msgs = episodes.check_package(root)
        self.assertTrue(all(m.startswith("warning:") for m in msgs), msgs)
        self.assertEqual([f[0] for f in episodes.describe(root)["fields"]], list(episodes.FIELDS))

if __name__ == "__main__":
    unittest.main()
