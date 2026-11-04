"""The public surface pin (d-work #573, v1.0 H3, plan step 2): `dyad/surface.md` against the code, in both directions.

Each section is derived from its source and compared with the file's table:
- S1: the CLI nouns of `package.py`'s dispatch, and each `dwork` verb's flags (`DWORK_VERB_FLAGS`, plus `--land` and
  `--mirror`, land's own).
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


def stale_keys(listed: dict[str, str], known: set[str], code_keys: set[str]) -> set[str]:
    """S3 keys that are neither `moving` nor a key of the preference tables (`known`) nor one the code still reads
    (`code_keys`: `paired-units`; no alias is read since #604): a listed key nothing has."""
    return {k for k, st in listed.items() if not st.startswith("moving") and k not in known | code_keys}


class SurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = sections()

    def test_every_section_is_present(self):
        self.assertEqual(sorted(self.s), [f"S{i}" for i in range(1, 9)])

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
            self.assertEqual({t.split()[0] for t in ticks(row[1])}, want, f"S1 `dwork {verb}` flags")

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
        text = " ".join(r[0] for r in self.s["S7"])
        for hook in ("pre-commit", "pre-push"):
            self.assertTrue((PKG / "hooks" / hook).is_file()); self.assertIn(f"dyad/hooks/{hook}", text)
        wf = {p.name for p in (ROOT / ".github" / "workflows").glob("dyad-*.yml")}
        self.assertEqual({t.rsplit("/", 1)[-1] for t in re.findall(r"`(\.github/workflows/[^`]+)`", text)}, wf)

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
