"""The CLI gate (d-work #592 R-a): `dyadlib.CLI`, the table of every `dyad <noun> [<verb>]` form, and `dyadlib.cli_gate`,
which `package.py`'s `__main__` runs before any dispatch.

- Every form: `--help` exits 0 with the form's usage and starts no child; `--bogus` exits 1 with
  `refused: dyad <noun> <verb> does not take --bogus`; through the entrypoint too, `git status --porcelain` unchanged.
- The positive cases pass with `a` unchanged: one example per form (every S1 row's), and the plan's own —
  `check --guards --pre-push origin https://x`, `dwork state 1 open --said -x`, `board set 1 next=a`, `dwork batch -`.
- A word past a form's positionals and a read-once flag given twice are refused too; a word not shaped like a flag,
  and every word from `inbox post`'s body on, is a word; `--help` before the verb or after an unknown one is answered.
- Each module's own `CLI_FLAGS` is the table's forms, and every flag literal its parser compares is a flag of the table
  (plan #592 F3); `DWORK_VERB_FLAGS` and `DWORK_VALUE_FLAGS` are views; every projector's flags are the `project` form's.
- `check --tests` refuses a dotted target the child cannot import; `craft export <c> --help` writes no file."""
import contextlib, io, os, re, subprocess, sys, tempfile, unittest, unittest.mock
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
ROOT = PKG.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib

PACKAGE = PKG / "scripts" / "package.py"
SHA = "a" * 40
EXAMPLES = {   # one argv per form, each S1 row's own example; every one passes the gate unchanged
    ("check", None): ["check"],
    ("check", "--list"): ["check", "--list"],
    ("check", "--guards"): ["check", "--guards", "--pre-push", "origin", "https://x"],
    ("check", "--corroborate"): ["check", "--corroborate", "HEAD~1", "HEAD"],
    ("check", "--pr"): ["check", "--pr", "origin/main", "HEAD"],
    ("check", "--tests"): ["check", "--tests", "dyad.tests.test_cli"],
    ("check", "--evidence"): ["check", "--evidence", "--brief", "--at", "HEAD"],
    ("build", None): ["build", "out.tar.gz"],
    ("install", None): ["install", "../other", "--from", "dyad-1.0.0.tar.gz"],
    ("bundle", "check"): ["bundle", "check"],
    ("bundle", "build"): ["bundle", "build", "dist"],
    ("craft", "new"): ["craft", "new", "pottery"],
    ("craft", "list"): ["craft", "list"],
    ("craft", "check"): ["craft", "check", "sysadmin"],
    ("craft", "export"): ["craft", "export", "sysadmin", "out.tar.gz"],
    ("craft", "install"): ["craft", "install", "src", "--force", "--dwork", "5", "--craft", "c", "--source", "s"],
    ("craft", "diff"): ["craft", "diff", "sysadmin", "--against", "src", "--patch"],
    ("ledger", None): ["ledger"],
    ("dwork", "new"): ["dwork", "new", "a title", "#1", "-d", "Y backlog", "--said", "Y", "--backlog", "--mandate", "570", "--slug", "a-title"],
    ("dwork", "state"): ["dwork", "state", "1", "open", "--said", "-x", "--slug", "one-row"],
    ("dwork", "retire"): ["dwork", "retire", "1", "2", "-d", "Y archive", "--said-file", "f"],
    ("dwork", "list"): ["dwork", "list", "--state", "open", "--craft", "sysadmin"],
    ("dwork", "land"): ["dwork", "land", "a.md", "b.md", "-m", "ledger: x", "--mirror", "m"],
    ("dwork", "batch"): ["dwork", "batch", "-", "--land"],
    ("dwork", "intent"): ["dwork", "intent", "615"],
    ("playbook", "profile"): ["playbook", "profile", "d-work"],
    ("dwork", "trace"): ["dwork", "trace", "592", "--transcript", "t.jsonl", "--out", "--said-file", "f"],
    ("plan", "check"): ["plan", "check", "589"],
    ("session", None): ["session"],
    ("session", "name"): ["session", "name", "--function", "engineer", "--hp", "1537d8fb", "--on", "-r-a"],
    ("session", "touch"): ["session", "touch", "-r", "592 594", "-f", "a.py"],
    ("session", "list"): ["session", "list"],
    ("session", "reconcile"): ["session", "reconcile"],
    ("project", None): ["project", "kanban", "--craft", "sysarch"],
    ("runbook", "check"): ["runbook", "check"],
    ("runbook", "list"): ["runbook", "list", "self-diagnostic"],
    ("runbook", "run"): ["runbook", "run", "self-diagnostic", "health", "--as", "operator"],
    ("runbook", "new"): ["runbook", "new", "git-server"],
    ("release", None): ["release", "--scan"],
    ("release", "ready"): ["release", "ready", "570", "v1.0.0", "--at", SHA, "--archive", "0" * 64],
    ("merge", None): ["merge", "7", "--head", SHA],
    ("board", None): ["board"],
    ("board", "set"): ["board", "set", "1", "next=a"],
    ("board", "resume"): ["board", "resume"],
    ("board", "advance"): ["board", "advance", "1", "2", "pr-up", "--expect", "building", "pr=7", "head=abc1234"],
    ("board", "phases"): ["board", "phases"],
    ("board", "draft"): ["board", "draft", "587", "--out", "/tmp/x/587-done.md"],
    ("board", "groom"): ["board", "groom"],
    ("inbox", "post"): ["inbox", "post", "engineer-1", "--row", "1", "--kind", "report", "--cc", "counsel-2", "a body"],
    ("inbox", "read"): ["inbox", "read", "20261102T174400Z-engineer-1537d8fb-1", "20261102T174400Z-counsel-0032b4c0-1"],
    ("inbox", "list"): ["inbox", "list", "engineer-1"],
    ("automaton", "scan"): ["automaton", "scan"],
    ("automaton", "run"): ["automaton", "run", "--evidence-from", "ev.jsonl"],
    ("automaton", "evidence"): ["automaton", "evidence", "--out", "ev.jsonl"],
    ("automaton", "sweep"): ["automaton", "sweep", "--row", "564"],
    ("steps", "verify-prs"): ["steps", "verify-prs"],
    ("steps", "done-record"): ["steps", "done-record", "--land"],
    ("steps", "close-landed"): ["steps", "close-landed", "--land"],
    ("steps", "sync-mirror"): ["steps", "sync-mirror"],
    ("bootstrap", None): ["bootstrap", "--check"],
}
MORE = [   # the plan's own positive cases, and flag values that spell a flag
    ["board", "set", "1", "--drop"], ["board", "set", "_cos", "next=-x"],
    ["dwork", "state", "1", "planned", "-d", "Y plan", "--said", "--help", "--land", "--mirror", "-m"],
    ["dwork", "new", "t", "--prompt", "-h"], ["check", "--evidence", "--show", "abc123def456"], ["check", "--tests"],
    ["inbox", "post", "x", "--row", "1", "--kind", "notice", "--body-file", "-"], ["dwork", "batch", "lines.txt", "--land"],
    ["project", "--list"], ["inbox", "post", "cos", "- item one", "--row", "5", "--kind", "report"],   # a markdown bullet body
    ["inbox", "post", "cos", "-urgent", "-1 rows", "-- see #12", "--bogus"],   # from the body on, every word is the body's
    ["inbox", "post", "x", "--cc", "a", "--cc", "b"], ["session", "touch", "-r", "1", "-r", "2", "-f", "a", "-f", "b"],
    ["dwork", "trace", "592", "--transcript", "a", "--transcript", "b"], ["check", "--tests", "-1 rows"],
    ["dwork", "retire", "1", "2", "3", "4", "5"], ["board", "set", "1", "a=1", "b=2", "c=3"],
]
PARSERS = {   # the functions of each noun's module that compare argv words with flags: every literal there is the table's
    "runbook": ("script", "runbook", ("main",)), "release": ("script", "release", ("main",)),
    "merge": ("script", "merge", ("parse", "main")), "craft": ("script", "craft", ("cmd_install", "cmd_diff", "main")),
    "bootstrap": ("script", "bootstrap", ("main",)), "automaton": ("script", "automaton", ("main",)),
    "steps": ("script", "steps", ("main",)), "board": ("guard", "board", ("parse_set", "cli", "cmd_draft", "main")),
    "inbox": ("guard", "inbox", ("parse_post", "cli", "main")), "session": ("guard", "sessions", ("seat_name_report", "main")),
    "plan": ("guard", "plans", ("cli", "main")), "dwork": ("script", "trace", ("main",)),
}
LAND_PARSERS = ("split_argv", "read_batch", "batch", "main")
FLAG_LITERAL = re.compile(r'''["'](--?[A-Za-z][A-Za-z0-9-]*)["']''')


def form_argv(key) -> list[str]:
    return [w for w in key if w]


def gate(a):
    """(rc, stdout, stderr) of `cli_gate(a)` in process, with every way to start a child made to fail."""
    out, err = io.StringIO(), io.StringIO()
    boom = unittest.mock.Mock(side_effect=AssertionError("the gate started a child"))
    with unittest.mock.patch.object(subprocess, "Popen", boom), unittest.mock.patch.object(subprocess, "run", boom), \
         unittest.mock.patch.object(os, "system", boom):
        rc = dyadlib.cli_gate(list(a), out=out, err=err)
    boom.assert_not_called()
    return rc, out.getvalue(), err.getvalue()


def status() -> str:
    return subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, capture_output=True,
                          text=True, env=dyadlib.git_env()).stdout


def entrypoint(a, cwd=ROOT):
    return subprocess.run([sys.executable, str(PACKAGE), *a], cwd=cwd, capture_output=True, text=True, timeout=60,
                          env=dyadlib.git_env())


class GateTests(unittest.TestCase):
    def test_the_table_holds_its_invariants(self):
        self.assertGreater(dyadlib.check_invariants(dyadlib), 0)

    def test_every_form_has_an_example_and_every_example_passes_unchanged(self):
        self.assertEqual(set(EXAMPLES), set(dyadlib.CLI))
        for key, a in [*EXAMPLES.items(), *((None, m) for m in MORE)]:
            with self.subTest(a=a):
                before = list(a)
                self.assertEqual(gate(a), (None, "", ""))
                self.assertEqual(a, before)
                if key:
                    self.assertEqual(dyadlib.cli_form(a)[0], key)

    def test_every_form_answers_help_with_its_usage_and_starts_no_child(self):
        for key in dyadlib.CLI:
            for h in dyadlib.HELP_FLAGS:
                with self.subTest(key=key, flag=h):
                    rc, out, err = gate([*EXAMPLES[key], h])
                    self.assertEqual((rc, err), (0, ""))
                    self.assertIn(dyadlib.cli_usage(key), out.splitlines())

    def test_every_form_refuses_an_unknown_flag_with_one_line(self):
        for key in dyadlib.CLI:
            with self.subTest(key=key):
                rc, out, err = gate([*form_argv(key), "--bogus"])
                self.assertEqual((rc, out), (1, ""))
                self.assertEqual(err, f"refused: dyad {' '.join(form_argv(key))} does not take --bogus\n")

    def test_a_flag_value_is_never_a_flag_nor_help(self):
        self.assertIsNone(gate(["dwork", "state", "1", "open", "--said", "-x"])[0])
        self.assertIsNone(gate(["dwork", "state", "1", "open", "--said", "--help"])[0])   # the words were `--help`
        self.assertEqual(gate(["dwork", "state", "1", "open", "--said", "-x", "-x"])[0], 1)   # the second -x is a flag
        self.assertEqual(gate(["dwork", "state", "1", "open", "--said"])[0], None)          # a missing value: the verb's

    def test_every_bounded_form_refuses_a_word_past_its_positionals(self):
        bounded = [k for k, x in dyadlib.CLI.items() if x.most is not None]
        self.assertIn(("check", "--list"), bounded); self.assertIn(("session", "list"), bounded)
        for key in bounded:
            with self.subTest(key=key):
                most = dyadlib.CLI[key].most
                self.assertIsNone(gate([*form_argv(key), *["w"] * most])[0])
                self.assertEqual(gate([*form_argv(key), *["w"] * most, "extra-word"]),
                                 (1, "", f"refused: dyad {' '.join(form_argv(key))} does not take extra-word\n"))
        for a, words in ((["check", "--list", "bogus-word"], "bogus-word"), (["craft", "list", "extra-word"], "extra-word"),
                         (["session", "list", "extra"], "extra"), (["check", "--guards", "a", "b", "c", "d"], "c d")):
            self.assertEqual(gate(a)[2], f"refused: dyad {' '.join(form_argv(dyadlib.cli_form(a)[0]))} does not take {words}\n")
        for key in (k for k, x in dyadlib.CLI.items() if x.most is None):   # `<id>...`, `key=value...`, a body
            self.assertIsNone(gate([*EXAMPLES[key], "w1", "w2"])[0], key)

    def test_a_flag_read_once_is_refused_when_given_twice(self):
        for key, x in dyadlib.CLI.items():
            for f in x.flags:
                a = [*form_argv(key), *((f, "a", f, "b") if f in x.value_flags else (f, f))]
                with self.subTest(a=a):
                    if f in x.repeat:
                        self.assertIsNone(gate(a)[0])
                    else:
                        self.assertEqual(gate(a), (1, "", f"refused: dyad {' '.join(form_argv(key))} takes {f} once\n"))
        self.assertEqual(gate(["dwork", "new", "t", "--prompt", "a", "--prompt", "b"])[2],
                         "refused: dyad dwork new takes --prompt once\n")   # the Operator's first words are never dropped
        self.assertEqual(set(f for x in dyadlib.CLI.values() for f in x.repeat), {"--cc", "--transcript", "-r", "-f"})

    def test_a_free_text_body_is_never_read_as_a_flag(self):
        for body in ("- item one", "-urgent", "- [ ] item", "-- see #12", "-1 rows"):
            a = ["inbox", "post", "cos", body, "--row", "5", "--kind", "report"]
            with self.subTest(body=body):
                self.assertIsNone(gate(a)[0])
                self.assertEqual(dyadlib.cli_parse(dyadlib.CLI[("inbox", "post")], a[2:]).pos, ["cos", body])
        inbox = dyadlib.load_guard("agent", "inbox")   # the module's own parser reads the same body
        self.assertEqual(inbox.parse_post(["cos", "- item one", "--row", "5", "--kind", "report"]),
                         ("cos", 5, "report", "- item one", ()))
        self.assertEqual(gate(["inbox", "post", "--bogus"])[0], 1)            # the unit is no body: a flag there is refused
        self.assertEqual(gate(["inbox", "post", "cos", "--help"])[0], 0)     # help is still help
        self.assertIsNone(gate(["check", "--tests", "- x"])[0])               # not flag-shaped: a word anywhere

    def test_a_value_that_spells_a_flag_is_read_as_the_value_by_every_consumer(self):
        r = dyadlib.cli_parse(dyadlib.CLI[("craft", "install")], ["src", "--source", "--force"])
        self.assertEqual((r.pos, r.one("--source"), r.bare), (["src"], "--force", []))
        r = dyadlib.cli_parse(dyadlib.CLI[("check", "--evidence")], ["--at", "--brief"])
        self.assertEqual((r.one("--at"), "--brief" in r.bare), ("--brief", False))
        self.assertEqual(dyadlib.cli_parse(dyadlib.CLI[("check", "--evidence")], ["--at"]).values, {"--at": []})
        craft = dyadlib.load_module(PKG / "scripts" / "craft.py", "cli_test_craft")
        for fn in (craft.cmd_install, craft.cmd_diff):
            src = inspect_source(fn)
            self.assertIn("dyadlib.cli_parse(", src)
            self.assertNotRegex(src, r'"--?[a-z-]+" in a\b|a\.index\(')
        main = PACKAGE.read_text()[PACKAGE.read_text().rindex('if __name__ == "__main__":'):]
        self.assertIn("dyadlib.cli_parse(", main)
        self.assertNotRegex(main, r"a\.index\(")

    def test_noun_level_help_and_refusal(self):
        rc, out, _ = gate(["dwork", "--help"])
        self.assertEqual(rc, 0)
        self.assertEqual(out.splitlines(), [dyadlib.cli_usage(k) for k in dyadlib.CLI if k[0] == "dwork"])
        self.assertEqual(gate(["dwork", "--bogus"]), (1, "", "refused: dyad dwork does not take --bogus\n"))
        rc, out, _ = gate(["check", "--help"])                                # a noun with a bare form prints every form
        self.assertEqual((rc, len(out.splitlines())), (0, sum(1 for k in dyadlib.CLI if k[0] == "check")))
        self.assertEqual(gate(["--help"], )[0], 0)
        self.assertIsNone(gate([])[0]); self.assertIsNone(gate(["nonoun", "--bogus"])[0])   # the dispatch's own answer
        self.assertIsNone(gate(["runbook", "bogus"])[0])                       # an unknown verb is its module's
        self.assertIsNone(gate(["dwork", "--prompt", "w", "new", "t"])[0])     # a known flag before the verb: dwork's "verb first"
        for a in (["dwork", "-d", "x", "state", "1", "done", "--help"], ["dwork", "bogus", "--help"], ["bundle", "bogus", "-h"]):
            rc, out, _ = gate(a)                                                # `--help` before the verb, or after an unknown one
            self.assertEqual((rc, out.splitlines()), (0, [dyadlib.cli_usage(k) for k in dyadlib.CLI if k[0] == a[0]]), a)
        self.assertIsNone(gate(["dwork", "--said", "--help", "state", "1", "open"])[0])   # a value, even before the verb

    def test_check_picks_its_form_in_the_dispatch_order(self):
        self.assertEqual(dyadlib.cli_form(["check", "--tests", "x", "--evidence"])[0], ("check", "--evidence"))
        self.assertEqual(gate(["check", "--tests", "x", "--evidence"])[2],
                         "refused: dyad check --evidence does not take --tests x\n")   # the flag, then the word past its (no) positionals
        src = PACKAGE.read_text()
        main = src[src.rindex('if __name__ == "__main__":'):]
        order = re.findall(r'a\[0\] == "check" and "(--[a-z]+)" in a', main)
        self.assertEqual(tuple(order), dyadlib.CHECK_MODES)


class ModuleFlagTests(unittest.TestCase):
    """Each module's parser reads the table (plan #592 F3): its `CLI_FLAGS` is the table's forms for the verbs it
    dispatches, and every flag literal its parsing functions compare argv with is a flag of that noun's forms — so a
    flag renamed in a parser alone fails here, not at a user's prompt."""
    def load(self, kind, name):
        if kind == "guard":
            return dyadlib.load_guard("agent", name)
        return dyadlib.load_module(PKG / "scripts" / f"{name}.py", f"cli_test_{name}")

    def test_each_modules_cli_flags_are_the_tables_forms(self):
        for noun, (kind, name, _) in [*PARSERS.items(), ("dwork", ("script", "land", ()))]:
            mod = self.load(kind, name)
            with self.subTest(module=name):
                self.assertTrue(mod.CLI_FLAGS)
                for verb, form in mod.CLI_FLAGS.items():
                    self.assertIs(form, dyadlib.CLI[(noun, verb)])
                if noun != "dwork":   # dwork's other verbs are package.py's own (the views below)
                    self.assertEqual(set(mod.CLI_FLAGS), {v for n, v in dyadlib.CLI if n == noun})

    def test_every_flag_a_parser_compares_is_the_tables(self):
        parsers = [*PARSERS.items(), ("dwork", ("script", "land", LAND_PARSERS))]
        for noun, (kind, name, fns) in parsers:
            mod, table = self.load(kind, name), {f for (n, _), x in dyadlib.CLI.items() if n == noun for f in x.flags}
            for fn in fns:
                with self.subTest(module=name, fn=fn):
                    read = set(FLAG_LITERAL.findall(inspect_source(getattr(mod, fn)))) - set(dyadlib.HELP_FLAGS)
                    self.assertEqual(read - table, set())
        drifted = 'role = a[a.index("--role") + 1] if "--role" in a else "agent"'   # the F3 drift: a parser renamed alone
        self.assertEqual(set(FLAG_LITERAL.findall(drifted)) - {f for x in dyadlib.cli_forms("runbook").values() for f in x.flags},
                         {"--role"})

    def test_named_constants_are_the_tables_words(self):
        mods = {n: self.load(k, n) for n, (k, *_) in {"runbook": ("script",), "release": ("script",), "merge": ("script",),
                                                     "trace": ("script",), "bootstrap": ("script",), "automaton": ("script",),
                                                     "land": ("script",), "board": ("guard",), "inbox": ("guard",)}.items()}
        CLI = dyadlib.CLI
        self.assertEqual(mods["runbook"].ROLE_FLAG, "--as")
        self.assertEqual((mods["release"].SCAN, mods["release"].AT, mods["release"].ARCHIVE), ("--scan", "--at", "--archive"))
        self.assertEqual(mods["merge"].HEAD_FLAG, "--head")
        self.assertEqual((mods["trace"].TRANSCRIPT, mods["trace"].SAID_FILE, mods["trace"].OUT), ("--transcript", "--said-file", "--out"))
        self.assertEqual(mods["bootstrap"].CHECK_FLAG, "--check")
        self.assertEqual(mods["automaton"].ROW_FLAG, "--row")
        self.assertEqual((mods["land"].MESSAGE, mods["land"].MIRROR, mods["land"].LAND), ("-m", "--mirror", "--land"))
        self.assertEqual(mods["board"].DROP, "--drop")
        self.assertEqual(mods["board"].OUT, "--out")
        self.assertEqual((mods["inbox"].POST_VALUES, mods["inbox"].CC), (("--row", "--kind", "--body-file"), "--cc"))
        self.assertEqual(CLI[("inbox", "read")].flags, ())                     # #587 S10: names mark, nothing else; no `--all`
        self.assertEqual(set(mods["inbox"].POST_VALUES) | {mods["inbox"].CC}, set(CLI[("inbox", "post")].value_flags))

    def test_every_projector_flag_is_the_project_forms(self):
        """`dyad project <surface>` hands its argv to the projector's `main()`, which reads `sys.argv` (#22's
        `--craft`): every flag literal a projector's `main` reads is a flag of the `project` form."""
        form, seen = dyadlib.CLI[("project", None)], set()
        for py in dyadlib.projector_files(PKG):
            mod = dyadlib.load_module(py, f"cli_test_{py.parent.parent.name}_{py.stem}")
            read = set(FLAG_LITERAL.findall(inspect_source(mod.main))) - set(dyadlib.HELP_FLAGS)
            with self.subTest(projector=str(py.relative_to(ROOT))):
                self.assertEqual(read - set(form.flags), set())
            seen |= read
        self.assertIn("--craft", seen)
        self.assertEqual(set(form.flags), seen | {"--list"})   # no flag the table holds that no projector reads

    def test_dwork_flag_tables_are_views_of_the_table(self):
        pkg = dyadlib.load_module(PACKAGE, "cli_test_package")
        land = {"--land", "--mirror"}
        for verb, (vals, bare, most) in pkg.DWORK_VERB_FLAGS.items():
            x = dyadlib.CLI[("dwork", verb)]
            self.assertEqual(vals | bare | (land & set(x.flags)), set(x.flags), verb)
            self.assertEqual(most, None if x.most is None else x.most + 1, verb)
        self.assertEqual(set(pkg.DWORK_VERB_FLAGS) | {"land", "batch", "trace", "intent"}, {v for n, v in dyadlib.CLI if n == "dwork"})
        self.assertEqual(set(pkg.DWORK_VALUE_FLAGS),
                         {"-d", "-r", "--prompt", "--prompt-file", "--said", "--said-file", "--said-ref", "--relayed-via",
                          "--state", "--craft", "--mandate", "--retired-by", "--mirror", "-m", "--slug", "--decisions"})   # as before the table, + #622, #644

    def test_package_main_reads_only_the_tables_check_and_install_flags(self):
        src = PACKAGE.read_text()
        main = src[src.rindex('if __name__ == "__main__":'):]
        literal = set(re.findall(r'"(--[a-z-]+)"', main)) - set(dyadlib.HELP_FLAGS)
        table = {f for (n, v), x in dyadlib.CLI.items() if n in ("check", "install") for f in (*x.flags, *([v] if v else []))}
        self.assertEqual(literal, table)
        self.assertIn("--list", inspect_source(dyadlib.load_module(PACKAGE, "cli_test_package2").cmd_project))
        self.assertEqual(dyadlib.CLI[("project", None)].bare, ("--list",))


def inspect_source(fn) -> str:
    import inspect
    return inspect.getsource(fn)


class EntrypointTests(unittest.TestCase):
    """The gate wired into `__main__`, through the real entrypoint, in the live checkout."""
    def test_every_form_through_the_entrypoint(self):
        before = status()
        argvs = [[*EXAMPLES[k], "--help"] for k in dyadlib.CLI] + [[*form_argv(k), "--bogus"] for k in dyadlib.CLI]
        with ThreadPoolExecutor(8) as pool:
            done = list(pool.map(entrypoint, argvs))
        for a, r in zip(argvs, done):
            key = dyadlib.cli_form(a)[0]
            with self.subTest(a=a):
                if a[-1] == "--help":
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertIn(dyadlib.cli_usage(key), r.stdout.splitlines())
                else:
                    self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                    self.assertEqual(r.stderr, f"refused: dyad {' '.join(form_argv(key))} does not take --bogus\n")
        self.assertEqual(status(), before)
        self.assertFalse((ROOT / "--help").exists())

    def test_live_faces(self):
        for a, line in ((["check", "--help"], "usage: dyad check --tests [<target>]"),
                        (["session", "--help"], "usage: dyad session touch [-r <rows>] [-f <file>]")):
            r = entrypoint(a)
            self.assertEqual(r.returncode, 0, r.stderr); self.assertIn(line, r.stdout.splitlines())

    def test_craft_export_help_writes_no_file(self):
        with tempfile.TemporaryDirectory() as d:
            r = entrypoint(["craft", "export", "sysadmin", "--help"], cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(list(Path(d).iterdir()), [])


class TestsTargetTests(unittest.TestCase):
    """`check --tests` refuses a dotted target the child cannot import (INCIDENTS row 179, the plan's live face)."""
    def setUp(self):
        self.pkg = dyadlib.load_module(PACKAGE, "cli_test_package3")

    def test_an_unqualified_target_is_refused_with_its_qualified_name(self):
        self.assertEqual(self.pkg.tests_target_refusal("test_incidents"),
                         "refused: dyad check --tests: no test root or module named test_incidents; "
                         "qualify it (dyad.tests.test_incidents)")
        self.assertIn("(dyad.tests.test_incidents.T.test_x)", self.pkg.tests_target_refusal("test_incidents.T.test_x"))

    def test_a_nested_module_is_found_at_any_depth_of_any_root(self):
        r = self.pkg.tests_target_refusal
        self.assertEqual(r("test_provenance"), "refused: dyad check --tests: no test root or module named test_provenance; "
                                               "qualify it (dyad.tests.guards.agent.test_provenance)")
        self.assertEqual(r("test_ops_scripts"), "refused: dyad check --tests: no test root or module named test_ops_scripts; "
                                                "qualify it (crafts.sysadmin.tests.guards.test_ops_scripts)")
        self.assertEqual(r("guards.agent.test_rows"), "refused: dyad check --tests: no test root or module named "
                                                      "guards.agent.test_rows; qualify it (dyad.tests.guards.agent.test_rows)")
        # the whole dotted path resolves under a root, never its first part alone: no root but the core's holds guards/agent/test_rows.py
        self.assertNotIn("crafts.", r("guards.agent.test_rows"))

    def test_a_name_no_root_holds_is_refused_without_a_suggestion(self):
        self.assertEqual(self.pkg.tests_target_refusal("no_such_592"),
                         "refused: dyad check --tests: no test root or module named no_such_592")

    def test_a_py_suffix_is_refused_with_the_path_form(self):
        for t in ("test_cli.py", "dyad.tests.test_cli.py"):
            with self.subTest(t=t):
                self.assertEqual(self.pkg.tests_target_refusal(t),
                                 f"refused: dyad check --tests: no test root or module named {t}; qualify it (dyad/tests/test_cli.py)")

    def test_a_resolvable_target_runs_as_today(self):
        for t in (None, "dyad.tests.test_incidents", "dyad/tests/test_cli.py", "dyad/tests", str(PKG / "tests"),
                  "dyad.tests.no_such_module_155", "crafts.sysadmin.tests.guards.test_ops_scripts"):   # its first part imports: unittest's own answer
            with self.subTest(t=t):
                self.assertIsNone(self.pkg.tests_target_refusal(t))

    def test_the_refusal_is_one_line_and_exit_1_even_inside_a_run(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(self.pkg.cmd_tests("test_incidents"), 1)   # DYAD_NO_NESTED_TESTS is set: refused first
        self.assertEqual(len(err.getvalue().splitlines()), 1)
        r = entrypoint(["check", "--tests", "test_incidents"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("no test root or module named test_incidents; qualify it (dyad.tests.test_incidents)", r.stderr)


if __name__ == "__main__":
    unittest.main()
