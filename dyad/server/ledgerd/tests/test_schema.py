"""ledgerd/schema.py: the ledger-schema contract (`schema_problem` in the shape of dyadlib.contract_problem), the
generic parsers a simple ledger declares its `load` with, and the `notes` fixture schema — the proof that a second
ledger is a module of a few declarative lines. Importing the module runs its INVARIANTS (verifiable-code.md p5)."""
import types, unittest
from pathlib import Path
import support
from support import Case
if not support.MISSING:
    from ledgerd import schema as S

def module(**kw) -> types.ModuleType:
    m = types.ModuleType("fixture_schema")
    base = {"NAME": "fx", "VERSION": 1, "STORES": ("a",), "TABLES": {"t": (("k", "v"), "k")}, "VIEWS": {"all": "SELECT * FROM t"},
            "RENDERED": ("all",), "load": lambda tree: {"t": []}, "INVARIANTS": []}
    for k, v in {**base, **kw}.items():
        setattr(m, k, v)
    for k in [k for k, v in kw.items() if v is None]:
        delattr(m, k)
    return m

class ContractTests(Case):
    def test_contract_names(self):
        self.assertEqual(S.SCHEMA_CONTRACT, ("NAME", "VERSION", "STORES", "TABLES", "VIEWS", "RENDERED", "load", "INVARIANTS"))
        self.assertEqual(S.SCHEMA_OPTIONAL, ("DEFAULT_VIEW", "DETAIL", "TREE_INVARIANTS"))
    def test_a_conforming_module_passes(self):
        self.assertIsNone(S.schema_problem(module()))
        self.assertIsNone(S.schema_problem(module(DEFAULT_VIEW="all", DETAIL={"t": "k"}, TABLES={"t": ((("k", "integer"), "v"), ("k", "v"))})))
    def test_missing_symbol_is_named(self):
        self.assertIn("lacks VIEWS, RENDERED", S.schema_problem(module(VIEWS=None, RENDERED=None)))
        self.assertIn("lacks load", S.schema_problem(module(load=None)))
    def test_shape_problems(self):
        self.assertIn("not an identifier", S.schema_problem(module(NAME="a b")))
        self.assertIn("STORES", S.schema_problem(module(STORES=("/abs",))))
        self.assertIn("STORES", S.schema_problem(module(STORES=())))
        self.assertIn("never 'meta'", S.schema_problem(module(TABLES={"meta": (("k",), "k")})))
        self.assertIn("primary key", S.schema_problem(module(TABLES={"t": (("k",), "zz")})))
        self.assertIn("distinct identifiers", S.schema_problem(module(TABLES={"t": (("k", "k"), "k")})))
        self.assertIn("column kinds", S.schema_problem(module(TABLES={"t": ((("k", "blob"),), "k")})))
        self.assertIn("share a table's name", S.schema_problem(module(VIEWS={"t": "SELECT 1"})))
        self.assertIn("RENDERED", S.schema_problem(module(RENDERED=("nope",))))
        self.assertIn("DEFAULT_VIEW", S.schema_problem(module(DEFAULT_VIEW="nope")))
        self.assertIn("DETAIL", S.schema_problem(module(DETAIL={"t": "zz"})))
        self.assertIn("load", S.schema_problem(module(load=3)))
    def test_helpers(self):
        m = module(TABLES={"t": ((("k", "integer"), "v"), ("k", "v"))}, DETAIL={"t": "v"})
        self.assertEqual(S.column_spec("v"), ("v", "text")); self.assertEqual(S.column_spec(("k", "integer")), ("k", "integer"))
        self.assertEqual(S.columns_of(m, "t"), ["k", "v"]); self.assertEqual(S.primary_key(m, "t"), ("k", "v"))
        self.assertEqual(S.default_view(m), "all"); self.assertEqual(S.default_view(module(RENDERED=(), VIEWS={"z": "SELECT 1", "a": "SELECT 2"})), "z")
        self.assertEqual(S.detail_of(m), {"t": "v"}); self.assertEqual(S.detail_of(module()), {})
        d = S.describe(m)
        self.assertEqual(d["tables"]["t"], {"columns": [["k", "integer"], ["v", "text"]], "primary_key": ["k", "v"]})
        self.assertEqual(d["default_view"], "all")

class LoadSchemaTests(Case):
    def test_shipped_dwork_loads_and_conforms(self):
        mod = S.load_schema("dwork")
        self.assertEqual(mod.NAME, "dwork"); self.assertIsNone(S.schema_problem(mod))
    def test_module_path_loads(self):
        d = self.scratch(); p = support.notes_schema(d)
        mod = S.load_schema(f"module:{p}")
        self.assertEqual(mod.NAME, "notes"); self.assertEqual(S.default_view(mod), "open_notes")
    def test_missing_contract_symbol_is_refused(self):
        d = self.scratch(); p = d / "bad.py"
        p.write_text("NAME, VERSION, STORES = 'bad', 1, ('x',)\nTABLES = {'t': (('k',), 'k')}\nVIEWS = {}\nRENDERED = ()\nINVARIANTS = []\n")   # no load
        with self.assertRaises(ValueError) as cm:
            S.load_schema(f"module:{p}")
        self.assertIn("lacks load", str(cm.exception))
    def test_unknown_names_are_refused(self):
        with self.assertRaises(ValueError):
            S.load_schema("no-such")
        with self.assertRaises(ValueError):
            S.load_schema("module:/nowhere/at/all.py")

class ParserTests(Case):
    def test_kv_lines(self):
        self.assertEqual(S.kv_lines("a: 1\n# c\n\nb: x: y\n"), {"a": "1", "b": "x: y"})
    def test_jsonl(self):
        self.assertEqual(S.jsonl('{"a": 1}\n\n{"b": 2}\n'), [{"a": 1}, {"b": 2}])
        with self.assertRaises(ValueError) as cm:
            S.jsonl('{"a": 1}\nnope\n')
        self.assertIn("line 2", str(cm.exception))
    def test_md_table(self):
        self.assertEqual(S.md_table("x\n| a | b |\n|---|---|\n| 1 | 2 |\n"), (["a", "b"], [["1", "2"]]))
    def test_md_sections(self):
        self.assertEqual(S.md_sections("# T\nintro\n\n## A\n\na1\n\n## B\nb1\n"), {"": "# T\nintro", "A": "a1", "B": "b1"})
        self.assertEqual(S.md_sections("## A\nx\n")[""] if "" in S.md_sections("## A\nx\n") else None, None)
    def test_first_sentence(self):
        self.assertEqual(S.first_sentence("Build the thing. Then more."), "Build the thing.")
        self.assertEqual(S.first_sentence("1. Write module a. Then test it."), "Write module a.")
        self.assertEqual(S.first_sentence("- a bullet\nover two lines"), "a bullet over two lines")
        self.assertEqual(S.first_sentence(""), "")
    def test_read_tree(self):
        d = self.scratch(); (d / "s").mkdir(); (d / "s" / "b.md").write_text("1"); (d / "s" / "a.md").write_text("2")
        self.assertEqual([p.name for p in S.read_tree(d, "s", "*.md")], ["a.md", "b.md"])
        self.assertEqual(S.read_tree(d, "missing"), [])

class NotesSchemaTests(Case):
    """The second ledger: three key: value files, one table, two views, the generic parsers — nothing of d-work."""
    def test_notes_loads_three_rows(self):
        d = self.scratch(); mod = S.load_schema(f"module:{support.notes_schema(d)}")
        data = mod.load(d)
        self.assertEqual([r["name"] for r in data["notes"]], ["alpha", "beta", "gamma"])
        self.assertEqual(data["notes"][0], {"name": "alpha", "title": "first note", "owner": "ann", "priority": "2"})
        self.assertNotIn("dwork", Path(mod.__file__).read_text()); self.assertNotIn("guards", Path(mod.__file__).read_text())

if __name__ == "__main__":
    unittest.main()
