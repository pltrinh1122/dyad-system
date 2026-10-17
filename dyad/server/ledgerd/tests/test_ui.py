"""ledgerd/ui.py: the navigator served at `/` and its fragments — `/?view=` and `/?sql=` reproduce a page, the page
and every fragment reference no external URL (every src, href, hx-get, hx-post and action is a same-origin path:
the one mechanical check of "self-contained" the suite can make), the basic bar composed into SQL, sort and column
choice, the detail panel over DETAIL, export, save-as and delete through the form routes (bodies parsed without a
form library), the htmx file served from the tree. Importing the module runs its INVARIANTS (verifiable-code.md p5);
its TREE_INVARIANTS are run here."""
import hashlib, json, re, unittest, unittest.mock, urllib.parse
import support
from support import Case, http
import dyadlib
if not support.MISSING:
    from ledgerd import core, ui
    from test_core import service_for

_REF = re.compile(r"""\b(?:src|href|action|hx-get|hx-post|hx-put|hx-delete|hx-push-url)\s*=\s*["']([^"']*)["']""")

def refs(html: str) -> list[str]:
    return _REF.findall(html)

class UnitTests(Case):
    def test_tree_invariants_and_quoting(self):
        dyadlib.check_invariants(ui)
        self.assertEqual(ui.qi('a"b'), '"a""b"'); self.assertEqual(ui.ql("it's"), "'it''s'")
        self.assertEqual(ui.wrap("SELECT * FROM board;", ["id", "what"], "id", "desc"), 'SELECT "id", "what" FROM (SELECT * FROM board) ORDER BY "id" DESC')
        self.assertEqual(ui.wrap("SELECT 1", [], "", ""), "SELECT * FROM (SELECT 1)")
        self.assertEqual(ui.state_url("", "board", ["id"], "id", "asc"), "/?view=board&cols=id&sort=id&dir=asc")
        self.assertEqual(ui.state_url("SELECT 1", "", [], "", "asc"), "/?sql=SELECT+1")
    def test_compose(self):
        sql = ui.compose("board", ["id", "status", "what"], {"status": ["open", "planned"], "id": [""]}, {"what": "row"}, "x'y")
        self.assertEqual(sql, 'SELECT * FROM "board" WHERE "status" IN (\'open\', \'planned\') AND CAST("what" AS TEXT) LIKE \'%row%\' '
                              'AND (CAST("id" AS TEXT) LIKE \'%x\'\'y%\' OR CAST("status" AS TEXT) LIKE \'%x\'\'y%\' OR CAST("what" AS TEXT) LIKE \'%x\'\'y%\')')
        self.assertEqual(ui.compose("board", ["id"], {}, {}, ""), 'SELECT * FROM "board"')
    def test_filter_spec_and_run(self):
        svc, _ = service_for(self, git=False)
        spec = {f["name"]: f for f in ui.filter_spec(svc, "board")}
        self.assertEqual(spec["status"], {"name": "status", "kind": "select", "values": ["blocked", "open", "planned"]})
        with unittest.mock.patch.object(ui, "MAX_VALUE", 10):
            self.assertEqual({f["name"]: f["kind"] for f in ui.filter_spec(svc, "board")}["why"], "text", "long values get a contains box")
        r = ui.run(svc, "SELECT * FROM board", ["id"], "id", "desc")
        self.assertEqual((r["columns"], [x[0] for x in r["rows"]], r["error"]), (["id"], [6, 3, 2, 1], ""))
        self.assertEqual(ui.run(svc, "DROP TABLE rows", [], "", "")["error"][:9], "read-only")

class PageTests(Case):
    def setUp(self):
        self.svc, self.repo = service_for(self, git=False)
        self.s = support.serve(self, core.create_app(self.svc))
    def test_page_opens_on_the_default_view_and_references_no_external_url(self):
        code, html, _ = http(self.s.base, "/")
        self.assertEqual(code, 200)
        self.assertIn("<title>ledgerd: dwork</title>", html); self.assertIn('<script src="/static/htmx.min.js"></script>', html)
        self.assertIn("first open row", html); self.assertIn("Basic: filter <code>board</code>", html); self.assertIn("asof dir:", html)
        found = refs(html); self.assertTrue(found)
        for r in found:
            self.assertTrue(r == "#" or (r.startswith("/") and not r.startswith("//")), r)
        self.assertNotIn("http://", html.replace("http://127.0.0.1", "").replace("http://www.apple.com", "")); self.assertNotIn("https://", html)
        for path in ("/ui/sidebar", "/ui/results?sql=SELECT+*+FROM+backlog", "/ui/detail?value=2", "/ui/filter?view=board&f_status=open"):
            code, frag, _ = http(self.s.base, path); self.assertEqual(code, 200, path)
            for r in refs(frag):
                self.assertTrue(r == "#" or (r.startswith("/") and not r.startswith("//")), (path, r))
    def test_view_and_sql_urls_reproduce_the_page(self):
        code, html, _ = http(self.s.base, "/?view=backlog")
        self.assertEqual(code, 200); self.assertIn("a backlog row", html); self.assertNotIn("first open row", html.split('<div id="results">')[1]); self.assertIn('<li class="active"><a href="/?view=backlog">', html)
        code, html, _ = http(self.s.base, "/?" + urllib.parse.urlencode({"sql": "SELECT id, title FROM rows WHERE state = 'done'"}))
        results = html.split('<div id="results">')[1]
        self.assertEqual(code, 200); self.assertIn("a done row", results); self.assertNotIn("first open row", results); self.assertIn("SELECT id, title FROM rows WHERE state = &#39;done&#39;", html)
        code, html, _ = http(self.s.base, "/?view=no-such-view"); self.assertEqual(code, 200); self.assertIn("first open row", html)   # falls back to the default
        code, html, _ = http(self.s.base, "/?" + urllib.parse.urlencode({"sql": "DROP TABLE rows"})); self.assertEqual(code, 200); self.assertIn('class="error"', html)
    def test_results_sort_columns_and_push_url(self):
        code, frag, hdr = http(self.s.base, "/ui/results?" + urllib.parse.urlencode([("sql", "SELECT * FROM board"), ("sort", "id"), ("dir", "desc"), ("cols", "id"), ("cols", "what")]))
        self.assertEqual(code, 200)
        self.assertEqual(hdr.get("hx-push-url") or hdr.get("HX-Push-Url"), "/?sql=SELECT+%2A+FROM+board&cols=id&cols=what&sort=id&dir=desc")
        cells = re.findall(r"<td>(\d+)</td>", frag); self.assertEqual(cells, ["6", "3", "2", "1"])
        self.assertNotIn("<th><a", frag.split("</thead>")[0].replace('<th><a href="#" hx-get="/ui/results?', ""))   # only the two chosen columns
        self.assertEqual(frag.count("<th>"), 2); self.assertIn("4 of 4", frag); self.assertIn('hx-get="/ui/detail?value=6"', frag)
    def test_filter_composes_sql_and_shows_it(self):
        code, frag, _ = http(self.s.base, "/ui/filter?" + urllib.parse.urlencode([("view", "board"), ("f_status", "open"), ("q", "accreted")]))
        self.assertEqual(code, 200); self.assertIn("an accreted row", frag); self.assertNotIn("first open row", frag)
        self.assertIn('id="sql-shown" hx-swap-oob="true"', frag); self.assertIn("WHERE &#34;status&#34; IN (&#39;open&#39;)", frag)
        self.assertEqual(http(self.s.base, "/ui/filter?view=nope")[0], 404)
    def test_detail_panel_over_detail_tables(self):
        code, frag, _ = http(self.s.base, "/ui/detail?value=2")
        self.assertEqual(code, 200)
        for table in self.svc.schema.DETAIL:
            self.assertIn(f"<h3>{table} ", frag)
        self.assertIn("a planned row with a plan", frag); self.assertIn("Build the thing the Operator asked for.", frag); self.assertIn("do the thing", frag); self.assertIn("seat-a", frag)
    def test_export(self):
        code, body, hdr = http(self.s.base, "/ui/export?format=md&sql=SELECT+id%2C+what+FROM+backlog")
        self.assertEqual(code, 200); self.assertEqual(body, "| id | what |\n|---|---|\n| 4 | a backlog row |\n"); self.assertIn("attachment", hdr.get("content-disposition", hdr.get("Content-Disposition", "")))
        code, body, _ = http(self.s.base, "/ui/export?format=csv&sql=SELECT+id+FROM+backlog"); self.assertEqual(body, "id\n4\n")
        self.assertEqual(http(self.s.base, "/ui/export?format=xml&sql=SELECT+1")[0], 400); self.assertEqual(http(self.s.base, "/ui/export?format=md&sql=DROP+TABLE+x")[0], 400)
    def test_save_and_delete_through_the_form_routes(self):
        form = urllib.parse.urlencode([("name", "mine"), ("sql", "SELECT id, what FROM board"), ("cols", "id"), ("cols", "what"), ("sort", "id asc")]).encode()
        code, frag, _ = http(self.s.base, "/ui/views", raw=form, method="POST")
        self.assertEqual(code, 200); self.assertIn("saved view mine", frag); self.assertIn('<a href="/?view=mine">mine</a>', frag)
        self.assertEqual(core.read_view(self.svc.state, "mine")["columns"], "id what")
        code, html, _ = http(self.s.base, "/?view=mine"); self.assertIn("SELECT id, what FROM board", html)
        code, frag, _ = http(self.s.base, "/ui/views", raw=urllib.parse.urlencode({"name": "evil", "sql": "DELETE FROM rows"}).encode(), method="POST")
        self.assertEqual(code, 200); self.assertIn("not saved: read-only", frag); self.assertEqual(core.saved_views(self.svc.state), ["mine"])
        code, frag, _ = http(self.s.base, "/ui/views/mine/delete", raw=b"", method="POST"); self.assertIn("deleted mine", frag); self.assertEqual(core.saved_views(self.svc.state), [])
    def test_htmx_is_served_from_the_tree_and_matches_the_manifest(self):
        code, body, hdr = http(self.s.base, "/static/htmx.min.js")
        self.assertEqual(code, 200); self.assertTrue(body.startswith("var htmx=")); self.assertIn("javascript", hdr.get("content-type", hdr.get("Content-Type", "")))
        digest = hashlib.sha256((ui.STATIC_DIR / ui.HTMX).read_bytes()).hexdigest()
        manifest = (support.PKG / "infrastructure" / "INFRASTRUCTURE.md").read_text()
        row = next(r for r in dyadlib.table_rows(manifest) if dyadlib.plain(r[0]).strip() == "htmx")
        self.assertIn(digest, row[2], "the vendored file is the one the manifest row names"); self.assertIn("2.0.4", row[2]); self.assertIn('version:"2.0.4"', body)

if __name__ == "__main__":
    unittest.main()
