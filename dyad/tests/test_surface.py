"""The public surface pin (d-work #573, v1.0 H3, plan step 2): `dyad/surface.md` against the code, in both directions.

Each section is derived from its source and compared with the file's table:
- S1: the CLI nouns of `package.py`'s dispatch, and each `dwork` verb's flags (`DWORK_VERB_FLAGS`, plus `--land` and
  `--mirror`, land's own); every row's forms and flags equal to `dyadlib.CLI` (#592 R-a).
- S2: each store's keys, from the guard constant its `source` cell names; the `waiting-on` forms from `board.WAITING`,
  the removed `seat <name>` refused (#604).
- S3: every key of the core's preference template and of this instance's table is listed, and every listed key that
  is not `moving` is one of them (or `paired-units`, `sessions.PAIRED_UNITS`); a retired key is listed nowhere.
- No `alias` mark in any run (#604: the #554 aliases are removed, and this pins it).
- S4: the Rule numbers, their files and their `##` headings; 17 retired.
- S5: every DMC `@id` name.
- S6: every `DYAD_*` name the package reads outside its tests, and every `vars.*` the `dyad-*` workflows read.
- S7: the two hooks and the `dyad-*.yml` workflows.
With `DYAD_SURFACE_RELEASE=1` any `moving` mark fails too: the gate before R1's cut (plan #573 step 2)."""
import json, os, re, sys, unittest
from pathlib import Path
PKG = Path(__file__).resolve().parent.parent
ROOT = PKG.parent
sys.path.insert(0, str(PKG / "scripts"))
import dyadlib

SURFACE = PKG / "surface.md"
TICK = re.compile(r"`([^`]+)`")


def sections() -> dict[str, list[list[str]]]:
    """{"S1": [cells, …], …}: the data rows of each `## S<n>` section's table, header and rule rows dropped."""
    out, cur = {}, None
    for line in SURFACE.read_text().splitlines():
        m = re.match(r"^## (S\d) ", line)
        if m:
            cur = out.setdefault(m.group(1), [])
            continue
        if line.startswith("## "):
            cur = None
        if cur is not None and line.startswith("|") and not re.match(r"^\|[-| ]+\|$", line):
            cells = dyadlib.split_cells(line)
            if cells and cells[-1] != "status":
                cur.append(cells)
    return out


def ticks(cell: str) -> list[str]:
    return TICK.findall(cell)


def s1_forms(rows: list[list[str]]) -> tuple[list[tuple[str, str | None]], list[tuple[set, set]]]:
    """(every (noun, verb) an S1 row names, [(the row's forms, the row's flags)…]). A form cell is `dyad <noun> …` and
    then further verbs of that noun (`list`, `board resume`), a `--flag` there a flag of the noun's `None` form
    (`project --list`), and `check`'s verb is its mode flag; the flags are each tick's first word that is a flag, in the
    flags cell and after the verb in a form cell (`inbox post … --cc <unit>`)."""
    named, out = [], []
    for r in rows:
        cells = ticks(r[0]); noun = cells[0].split()[1]
        keys, flags = set(), {t.split()[0] for t in ticks(r[1]) if t.startswith("-")}
        for n, cell in enumerate(cells):
            words = cell.split()[2:] if n == 0 else cell.split()
            if n and words[:1] == [noun]:
                words = words[1:]
            if noun == "check":
                verb = next((w for w in words if w in dyadlib.CHECK_MODES), None)
            elif words and (noun, words[0]) in dyadlib.CLI:
                verb = words[0]
            else:
                verb = None
            keys.add((noun, verb))
            flags |= {w for w in words if w.startswith("-") and len(w) > 1 and w != verb}
        named += sorted(keys, key=str); out.append((keys, flags))
    return named, out


def stale_keys(listed: dict[str, str], known: set[str], code_keys: set[str]) -> set[str]:
    """S3 keys that are neither `moving` nor a key of the preference tables (`known`) nor one the code still reads
    (`code_keys`: `paired-units`; no alias is read since #604): a listed key nothing has."""
    return {k for k, st in listed.items() if not st.startswith("moving") and k not in known | code_keys}


def s7_workflow_problems(rows, on_disk: set[str]) -> tuple[list[str], list[str]]:
    """(workflows on disk that no S7 row lists, listed workflows absent from disk whose row is not `moving`): S7's pin
    of `.github/workflows/dyad-*.yml`, which admits a row ahead of its file only while it moves (#609 revision 4)."""
    listed = {}
    for r in rows:
        for t in re.findall(r"`(\.github/workflows/[^`]+)`", r[0]):
            listed[t.rsplit("/", 1)[-1]] = r[-1]
    return (sorted(on_disk - set(listed)),
            sorted(n for n in set(listed) - on_disk if not listed[n].startswith("moving")))


class SurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = sections()

    def test_every_section_is_present(self):
        self.assertEqual(sorted(self.s), [f"S{i}" for i in range(1, 10)])

    def test_s1_cli_nouns_and_dwork_flags(self):
        src = (PKG / "scripts" / "package.py").read_text()
        main = src[src.rindex('if __name__ == "__main__":'):]
        code = set(re.findall(r'a\[0\] == "([a-z]+)"', main)) | set(re.findall(r'a\[0\] not in \(([^)]*)\)', main)[0].replace('"', "").replace(",", " ").split())
        listed = {re.match(r"dyad (\w+)", ticks(r[0])[0]).group(1) for r in self.s["S1"]}
        self.assertEqual(listed, code, "S1 nouns differ from package.py's dispatch")
        pkg = dyadlib.load_module(PKG / "scripts" / "package.py", "package_surface")
        for verb, (vals, bare, _) in pkg.DWORK_VERB_FLAGS.items():
            row = next(r for r in self.s["S1"] if ticks(r[0])[0].startswith(f"dyad dwork {verb}"))
            want = set(vals) | set(bare) | ({"--land", "--mirror"} if verb in ("new", "state") else set())
            self.assertEqual({t.split()[0] for t in ticks(row[1]) if t.startswith("-")}, want, f"S1 `dwork {verb}` flags")

    def test_s1_every_row_equals_the_cli_table(self):
        """#592 R-a: S1 is `dyadlib.CLI` — every form a row names is a form of the table and every form of the table is
        named by a row; a row's flags are the union of its forms' flags in the table, and every flag of a form is in a
        row naming it (`dyad inbox post … --cc` is a row of its own)."""
        named, row_flags = s1_forms(self.s["S1"])
        self.assertEqual(set(named), set(dyadlib.CLI), "S1 forms differ from dyadlib.CLI")
        for i, forms in enumerate(row_flags):
            keys, flags = forms
            want = {f for k in keys for f in dyadlib.CLI[k].flags}
            self.assertTrue(flags <= want, f"S1 row {self.s['S1'][i][0]}: {sorted(flags - want)} no form of it takes")
        for k, x in dyadlib.CLI.items():
            got = set().union(*(fl for keys, fl in row_flags if k in keys))
            self.assertEqual(set(x.flags) - got, set(), f"S1 lists no row with {k}'s flags")

    def test_s2_store_keys_match_their_guards(self):
        board, inbox, sessions = (dyadlib.load_guard("agent", n) for n in ("board", "inbox", "sessions"))
        runbook = dyadlib.load_module(PKG / "scripts" / "runbook.py", "runbook_surface")
        trace = dyadlib.load_module(PKG / "scripts" / "trace.py", "trace_surface")
        want = {"row": (*dyadlib.FIELDS, *dyadlib.OPTIONAL_FIELDS), "board entry": board.FIELDS,
                "board cross-row": board.COS_FIELDS, "inbox message": inbox.FIELDS, "inbox marker": inbox.MARK_FIELDS,
                "trace": trace.SECTIONS, "event": runbook.EVENT_FIELDS, "run-book command header": runbook.FIELDS}
        rows = {r[0]: r for r in self.s["S2"]}
        for store, keys in want.items():
            self.assertEqual(set(ticks(rows[store][2])), set(keys), f"S2 {store}")
        self.assertTrue(set(sessions.FIELDS) <= set(ticks(rows["presence"][2])), "S2 presence")
        self.assertEqual(set(ticks(rows["row states"][2])), set(dyadlib.TRANSITIONS))
        cell = rows["board `waiting-on` value"]
        for form in ticks(cell[2]):   # each listed form is one `board.WAITING` reads; `seat <name>` is no longer one (#604)
            self.assertTrue(board.WAITING.fullmatch(form.replace("<name>", "counsel").replace("<ref>", "run 1")), form)
        self.assertNotIn("seat", cell[2]); self.assertFalse(hasattr(board, "UNIT_ALIAS"))
        self.assertFalse(board.WAITING.fullmatch(board.RETIRED_WAITING + "counsel"))
        values = ticks(rows["board `cabinet` value"][2])                       # #594: the cabinet form
        self.assertEqual(values, ["program", "program-<operator>"])
        self.assertTrue(board.CABINET.fullmatch(values[0]) and board.CABINET.fullmatch(values[1].replace("<operator>", "bob")))
        self.assertEqual(rows["board `cabinet` value"][3], "`board.CABINET`")
        self.assertEqual(ticks(rows["board cross-row"][1]), [f"d-work/board/{board.COS}.md", f"{board.cos_name('program-<operator>')}.md"])

    def test_s1_the_board_names_every_cabinets_cos(self):
        """#594: `board set <id>|_cos[-<operator>]`, in the surface row, the board's usage and `dyad help`."""
        board = dyadlib.load_guard("agent", "board")
        row = next(r for r in self.s["S1"] if ticks(r[0])[0] == "dyad board")
        self.assertIn("board set <id>|_cos[-<operator>] key=value...", ticks(row[0]))
        self.assertIn("board set <id>|_cos[-<operator>] key=value…", board.USAGE)
        self.assertIn("set <id>|_cos[-<operator>] key=value…", (PKG / "scripts" / "package.py").read_text())
        self.assertFalse([r[0] for rows in self.s.values() for r in rows if "#594" in r[-1]], "no `moving (#594)` mark")

    def test_s3_preference_keys(self):
        sessions = dyadlib.load_guard("agent", "sessions")
        def keys(p):
            return {c[0] for c in (dyadlib.split_cells(l) for l in p.read_text().splitlines() if l.startswith("| "))
                    if c and c[0] not in ("key",) and re.fullmatch(r"[a-z][a-z-]*", c[0])}
        known = keys(PKG / "templates" / "PREFERENCES.md")
        inst = ROOT / "preferences-corpus" / "PREFERENCES.md"
        known |= keys(inst) if inst.exists() else set()
        listed = {r[0]: r[-1] for r in self.s["S3"]}
        self.assertEqual(known - set(listed), set(), "a preference key S3 does not list")
        self.assertEqual(stale_keys(listed, known, {sessions.PAIRED_UNITS}), set(), "an S3 key that is no preference")
        self.assertEqual(set(sessions.RETIRED_KEYS) & (set(listed) | known), set(), "a retired key is listed or seeded (#604)")

    def test_s3_a_fresh_install_seeds_every_frozen_key(self):
        """A fresh install has the core's template and no instance table (#603: the 0.18.0 cut failed its own suite
        because S3 froze two keys only this instance seeded): every S3 key that is no `moving` mark is a key of the
        template alone, or one the code still reads."""
        sessions = dyadlib.load_guard("agent", "sessions")
        tmpl = {c[0] for c in (dyadlib.split_cells(l) for l in (PKG / "templates" / "PREFERENCES.md").read_text().splitlines()
                               if l.startswith("| ")) if c and c[0] != "key" and re.fullmatch(r"[a-z][a-z-]*", c[0])}
        listed = {r[0]: r[-1] for r in self.s["S3"]}
        self.assertEqual(stale_keys(listed, tmpl, {sessions.PAIRED_UNITS}), set(),
                         "an S3 key a fresh install's template does not seed")
    def test_s3_a_removed_alias_row_is_stale(self):
        """#604 (step 4): the code no longer reads `attended-seats`, so an S3 row for it is a key nothing has."""
        sessions = dyadlib.load_guard("agent", "sessions")
        self.assertFalse(hasattr(sessions, "ATTENDED_SEATS"))
        listed = {"paired-units": "frozen", "attended-seats": "frozen", "altitude": "moving (#570)"}
        self.assertEqual(stale_keys(listed, {"paired-units"}, {sessions.PAIRED_UNITS}), {"attended-seats"})

    def test_s4_rules_and_their_headings(self):
        listed = {r[0]: r for r in self.s["S4"]}
        files = {re.match(r"RULE-(\d+)-", p.name).group(1): p for p in (PKG / "rules").glob("RULE-*.md")}
        self.assertEqual(set(listed) - {"17"}, set(files))
        self.assertIn("retired", listed["17"][2])
        for n, p in files.items():
            heads = [re.sub(r" \(.*\)$", "", h) for h in re.findall(r"(?m)^## (.+)$", p.read_text())]
            self.assertEqual(ticks(listed[n][1]), [p.name], f"S4 Rule-{n} file")
            self.assertEqual([h.strip() for h in listed[n][2].split(";")], heads, f"S4 Rule-{n} headings")

    def test_s5_dmc_ids(self):
        ids = set()
        for p in (PKG / "dmc").glob("*.jsonld"):
            for m in re.finditer(r'"@id"\s*:\s*"urn:dyad:dmc:dyad-operator/([^"]+)"', p.read_text()):
                ids.add(m.group(1))
        self.assertEqual({r[0] for r in self.s["S5"]}, ids)

    def test_s6_variables(self):
        code = set()
        for p in PKG.rglob("*.py"):
            if "tests" not in p.relative_to(PKG).parts:
                code |= set(re.findall(r"\b(DYAD_[A-Z_]+)\b", p.read_text()))
        for p in (ROOT / ".github" / "workflows").glob("dyad-*.yml"):
            code |= set(re.findall(r"\bvars\.([A-Z_]+)\b", p.read_text()))
        self.assertEqual({ticks(r[0])[0] for r in self.s["S6"]}, code)

    def test_s7_hooks_and_workflows(self):
        """Every `dyad-*.yml` workflow on disk is listed in S7; a listed workflow may be absent from disk only while its
        row's status starts `moving`, the rule S3's test applies to a key the code does not read yet (#609 revision 4:
        a new workflow's row and its file sit in two zones, so neither could land first). Release mode refuses every
        `moving` row (test_release_mode_has_no_moving_or_alias_mark), so at a cut the pin holds both ways."""
        text = " ".join(r[0] for r in self.s["S7"])
        for hook in ("pre-commit", "pre-push"):
            self.assertTrue((PKG / "hooks" / hook).is_file()); self.assertIn(f"dyad/hooks/{hook}", text)
        on_disk = {p.name for p in (ROOT / ".github" / "workflows").glob("dyad-*.yml")}
        self.assertEqual(s7_workflow_problems(self.s["S7"], on_disk), ([], []),
                         "(a dyad-*.yml on disk with no S7 row, an S7 workflow row with no file and no `moving` mark)")

    def test_s7_admits_a_moving_workflow_not_yet_on_disk(self):
        """#609 revision 4: the rule above on tables of its own: a `moving` row whose file is absent passes, a `frozen`
        one fails, and a file with no row fails."""
        row = lambda name, status: ("`.github/workflows/" + name + "`", status)
        a = {"dyad-a.yml"}
        self.assertEqual(s7_workflow_problems([row("dyad-a.yml", "frozen"), row("dyad-b.yml", "moving (#609)")], a), ([], []))
        self.assertEqual(s7_workflow_problems([row("dyad-a.yml", "frozen"), row("dyad-b.yml", "frozen")], a), ([], ["dyad-b.yml"]))
        self.assertEqual(s7_workflow_problems([row("dyad-a.yml", "frozen")], a | {"dyad-c.yml"}), (["dyad-c.yml"], []))

    def test_no_alias_mark_is_left(self):
        """#604 (#573 DoD): every #554 alias is removed, in every run and not only under `DYAD_SURFACE_RELEASE=1`;
        an `alias` mark returning to any section fails here."""
        self.assertEqual([(sec, r[0]) for sec, rows in self.s.items() for r in rows if r[-1].startswith("alias")], [])

    def test_release_mode_has_no_moving_or_alias_mark(self):
        marks = [(sec, r[0]) for sec, rows in self.s.items() for r in rows if r[-1].startswith(("moving", "alias"))]
        if os.environ.get("DYAD_SURFACE_RELEASE") == "1":
            self.assertEqual(marks, [], "the surface still moves: 1.0 cannot be cut (plan #573 step 2)")
        else:
            self.assertTrue(all(sec in self.s for sec, _ in marks))


if __name__ == "__main__":
    unittest.main()
