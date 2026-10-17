"""ledgerd/core.py: the build (store -> tree -> load -> SQLite, atomically replaced; two builds at one commit give one
`iterdump()`; the `meta` table and no timestamp), the two write refusals (UPDATE, PRAGMA, two statements; the
authorizer refuses what the text fence lets through), the renderers (`--md` shape), the rendered views, saved
views, the refresh tick, and the server (uvicorn in a thread, stdlib urllib as the client): /health, /query,
/refresh after a new commit, /views/board, the /views PUT/GET/DELETE round-trip with a write-shaped SQL refused on
PUT, /board. Importing the module runs its INVARIANTS (verifiable-code.md p5)."""
import json, sqlite3, unittest
from pathlib import Path
import support
from support import Case, http
if not support.MISSING:
    from ledgerd import core, schema as S, store

def service_for(case: Case, repo: Path | None = None, git: bool = True, build: bool = True, **conf_extra):
    repo = repo or support.instance(case.scratch())
    state = case.scratch()
    conf = {"schema": "dwork", "schema_version": "1", "store": f"git+file://{repo}#main" if git else f"file://{repo}", "bind": "127.0.0.1", "port": "8731", "refresh_every": "60", **conf_extra}
    core.write_conf(state, conf)
    svc = core.Service(state, conf, supervisor="proc")
    if build:
        svc.build()
    return svc, repo

class ConfTests(Case):
    def test_conf_round_trip_in_fixed_order(self):
        state = self.scratch()
        p = core.write_conf(state, {"port": "1", "schema": "dwork", "store": "x", "bind": "127.0.0.1", "refresh_every": "60", "github_client_id": ""})
        self.assertEqual(p.read_text(), "schema: dwork\nstore: x\nbind: 127.0.0.1\nport: 1\nrefresh_every: 60\n")
        self.assertEqual(core.read_conf(state)["port"], "1"); self.assertEqual(core.ui_url(core.read_conf(state)), "http://127.0.0.1:1/")
        with self.assertRaises(FileNotFoundError):
            core.read_conf(self.scratch())

class FenceTests(Case):
    def test_read_statement(self):
        self.assertEqual(core.read_statement("  SELECT 1 ; "), "SELECT 1")
        self.assertEqual(core.read_statement("-- a comment\nWITH x AS (SELECT 1) SELECT * FROM x"), "-- a comment\nWITH x AS (SELECT 1) SELECT * FROM x")
        self.assertEqual(core.read_statement("SELECT 'a;b' AS s"), "SELECT 'a;b' AS s")
        for bad, why in (("UPDATE rows SET state = 'done'", "read-only"), ("PRAGMA table_info(rows)", "read-only"), ("SELECT 1; SELECT 2", "one statement"),
                         ("", "empty"), ("SELECT 'unterminated", "incomplete"), ("DELETE FROM rows", "read-only"), ("ATTACH 'x' AS y", "read-only")):
            with self.assertRaises(core.QueryError) as cm:
                core.read_statement(bad)
            self.assertIn(why, str(cm.exception), bad)
    def test_authorizer_refuses_what_the_text_fence_cannot_see(self):
        svc, _ = service_for(self, git=False)
        cx = core.open_ro(svc.db)
        self.assertEqual(cx.execute("SELECT count(*) FROM rows").fetchone()[0], 6)
        for sql in ("UPDATE rows SET state = 'done'", "PRAGMA journal_mode", "CREATE TABLE z (a)", "ATTACH ':memory:' AS m", "INSERT INTO meta VALUES ('a', 'b')"):
            with self.assertRaises(sqlite3.DatabaseError, msg=sql):
                cx.execute(sql)
        cx.close()
        with self.assertRaises(core.QueryError):
            core.run_query(svc.db, "SELECT * FROM no_such_table")

class BuildTests(Case):
    def test_build_twice_from_one_commit_is_one_dump_and_holds_meta(self):
        svc, repo = service_for(self)
        dump = lambda: "\n".join(sqlite3.connect(f"file:{svc.db}?mode=ro", uri=True).iterdump())   # a plain ro connection: iterdump itself reads PRAGMAs the authorizer denies
        pin = svc.pin; dump1 = dump()
        svc.build(); dump2 = dump()
        self.assertEqual(dump1, dump2); self.assertEqual(svc.pin, pin)
        cols, rows = svc.query("SELECT key, value FROM meta ORDER BY key")
        self.assertEqual(rows, [["built_from", pin], ["schema", "dwork"], ["schema_version", "1"]])
        self.assertNotIn("2026-", dump1.split("INSERT INTO \"meta\"")[1][:200]); self.assertFalse(svc.db.with_name(svc.db.name + ".tmp").exists())
        self.assertEqual(core.built_from(svc.db), pin); self.assertEqual(svc.pin_label(), f"git:{pin}")
    def test_dir_store_builds_too(self):
        svc, repo = service_for(self, git=False)
        self.assertTrue(svc.pin_label().startswith("dir:")); self.assertEqual(svc.query("SELECT count(*) FROM rows")[1], [[6]])
        self.assertEqual(core.counts(svc.db, svc.schema)[0], len(svc.schema.TABLES))
    def test_normalize_and_kinds(self):
        mod = S.load_schema("dwork")
        rows = core.normalize(mod, "rows", [{"id": "10", "title": "b"}, {"id": "2", "title": "a"}, {"id": None, "title": "z"}])
        self.assertEqual([r["id"] for r in rows], [2, 10, None]); self.assertEqual(set(rows[0]), set(S.columns_of(mod, "rows")))
        self.assertEqual(core._coerce("", "integer"), None); self.assertEqual(core._coerce("x1", "integer"), "x1"); self.assertEqual(core._coerce(3, "text"), "3")
    def test_reflect_and_schema_describe(self):
        svc, _ = service_for(self, git=False)
        r = core.reflect(svc.db)
        self.assertEqual(set(r["tables"]), set(svc.schema.TABLES) | {"meta"}); self.assertEqual(set(r["views"]), set(svc.schema.VIEWS))
        self.assertEqual([c["name"] for c in r["tables"]["rows"]], list(S.columns_of(svc.schema, "rows")))
    def test_notes_schema_builds_and_serves(self):
        """Any ledger: the notes schema over its three files, the same core."""
        d = self.scratch(); p = support.notes_schema(d); state = self.scratch()
        conf = {"schema": f"module:{p}", "store": f"file://{d}", "bind": "127.0.0.1", "port": "1", "refresh_every": "5"}
        svc = core.Service(state, conf); svc.build()
        self.assertEqual(svc.query("SELECT name, owner FROM open_notes")[1], [["gamma", "bob"], ["alpha", "ann"]])
        self.assertEqual(svc.query("SELECT * FROM owners")[1], [["", 1], ["ann", 1], ["bob", 1]])
        self.assertEqual(svc.query("SELECT priority FROM notes WHERE name = 'gamma'")[1], [[3]], "an integer column")
        self.assertEqual(sorted(p.name for p in core.views_dir(state).iterdir()), ["open_notes.md", "open_notes.txt"])

class RenderTests(Case):
    def test_md_and_txt_and_csv(self):
        cols, rows = ["id", "what"], [[1, "a | b"], [2, None]]
        self.assertEqual(core.render_md(cols, rows), "| id | what |\n|---|---|\n| 1 | a \\| b |\n| 2 |  |\n")
        self.assertEqual(core.render_txt(cols, rows), "id  what\n--  -----\n1   a | b\n2\n")
        self.assertEqual(core.render_csv(cols, rows), "id,what\n1,a | b\n2,\n")
    def test_rendered_views_are_byte_identical_and_headed_by_the_pin(self):
        svc, _ = service_for(self)
        files = svc.render_all(); texts = {p.name: p.read_text() for p in files}
        svc.render_all()
        self.assertEqual({p.name: p.read_text() for p in files}, texts)
        self.assertTrue(texts["board.md"].startswith(f"# board (built from git:{svc.pin}; schema dwork 1)\n\n| id | status | what |"))
        self.assertIn("backlog.txt", texts); self.assertIn("unheld.md", texts)
        self.assertEqual(svc.rendered("board", ".md"), texts["board.md"]); self.assertIsNone(svc.rendered("nope", ".md")); self.assertIsNone(svc.rendered("board", ".html"))

class SavedViewTests(Case):
    def test_save_read_delete_and_refusals(self):
        svc, _ = service_for(self, git=False)
        p = core.save_view(svc.state, svc.db, svc.schema, "mine", "SELECT id, what FROM board;", "id what", "id asc")
        self.assertEqual(p.read_text(), "name: mine\nsql: SELECT id, what FROM board\ncolumns: id what\nsort: id asc\n")
        self.assertEqual(core.saved_views(svc.state), ["mine"]); self.assertEqual(core.read_view(svc.state, "mine")["sql"], "SELECT id, what FROM board")
        for name, sql, why in (("mine", "DELETE FROM rows", "read-only"), ("board", "SELECT 1", "schema's"), ("bad name", "SELECT 1", "view name"), ("x", "SELECT * FROM nowhere", "no such table")):
            with self.assertRaises(core.QueryError) as cm:
                core.save_view(svc.state, svc.db, svc.schema, name, sql)
            self.assertIn(why, str(cm.exception), name)
        self.assertTrue(core.delete_view(svc.state, "mine")); self.assertFalse(core.delete_view(svc.state, "mine")); self.assertEqual(core.saved_views(svc.state), [])
        self.assertFalse(core.delete_view(svc.state, "../etc"))

class RefreshTests(Case):
    def test_tick_rebuilds_only_when_the_pin_moved(self):
        svc, repo = service_for(self)
        self.assertEqual(svc.tick()["rebuilt"], False); self.assertTrue(svc.last_fetch_ok)
        mtime = svc.db.stat().st_mtime_ns
        head = support.add_row(repo, 7, "a new row")
        r = svc.tick()
        self.assertEqual((r["rebuilt"], r["pin"]), (True, f"git:{head}")); self.assertNotEqual(svc.db.stat().st_mtime_ns, mtime)
        self.assertEqual(svc.query("SELECT count(*) FROM rows")[1], [[7]]); self.assertEqual(svc.ticks, 2)
    def test_failed_fetch_keeps_the_last_build(self):
        svc, repo = service_for(self)
        pin = svc.pin
        svc.store.ref = "no-such-ref"
        r = svc.tick()
        self.assertFalse(r["last_fetch_ok"]); self.assertIn("RuntimeError", r["error"]); self.assertEqual(svc.pin, pin)
        self.assertEqual(svc.health()["last_fetch_ok"], False); self.assertEqual(svc.query("SELECT count(*) FROM rows")[1], [[6]])
    def test_health_fields(self):
        svc, _ = service_for(self)
        h = svc.health()
        for k in ("ok", "built_from", "pin", "schema", "schema_version", "store", "tables", "rows", "refresh_every", "ticks", "last_fetch_ok", "last_error", "supervisor", "auth", "ui_url"):
            self.assertIn(k, h)
        self.assertEqual((h["ok"], h["schema"], h["refresh_every"], h["supervisor"], h["auth"], h["ui_url"]), (True, "dwork", 60, "proc", "anonymous", "http://127.0.0.1:8731/"))

class ServerTests(Case):
    def test_routes(self):
        svc, repo = service_for(self)
        s = support.serve(self, core.create_app(svc))
        code, body, _ = http(s.base, "/health"); h = json.loads(body)
        self.assertEqual((code, h["ok"], h["built_from"]), (200, True, svc.pin))
        code, body, _ = http(s.base, "/query", {"sql": "SELECT id, status FROM board ORDER BY id"})
        self.assertEqual(code, 200); r = json.loads(body)
        self.assertEqual(r["rows"], [[1, "open"], [2, "planned"], [3, "blocked"], [6, "open"]]); self.assertEqual(r["pin"], f"git:{svc.pin}")
        for bad in ("UPDATE rows SET state = 'x'", "PRAGMA table_info(rows)", "SELECT 1; SELECT 2"):
            code, body, _ = http(s.base, "/query", {"sql": bad}); self.assertEqual(code, 400, bad); self.assertIn("detail", body)
        code, body, _ = http(s.base, "/query", {"nosql": 1}); self.assertEqual(code, 422)
        code, body, _ = http(s.base, "/views/board.md"); self.assertEqual(code, 200); self.assertTrue(body.startswith("# board (built from git:"))
        code, body, hdr = http(s.base, "/board"); self.assertEqual(code, 200); self.assertIn("text/plain", hdr.get("content-type", hdr.get("Content-Type", ""))); self.assertIn("first open row", body)
        code, body, _ = http(s.base, "/schema"); self.assertEqual(code, 200); self.assertEqual(json.loads(body)["name"], "dwork"); self.assertIn("reflected", body)
        head = support.add_row(repo, 8, "after a new commit")
        code, body, _ = http(s.base, "/refresh", method="POST"); self.assertEqual(code, 200); self.assertEqual(json.loads(body), {"pin": f"git:{head}", "rebuilt": True, "last_fetch_ok": True, "error": ""})
        self.assertEqual(json.loads(http(s.base, "/health")[1])["built_from"], head)
        self.assertEqual(json.loads(http(s.base, "/query", {"sql": "SELECT count(*) FROM rows"})[1])["rows"], [[7]])
        self.assertIn("after a new commit", http(s.base, "/views/board.txt")[1])
    def test_views_round_trip(self):
        svc, _ = service_for(self, git=False)
        s = support.serve(self, core.create_app(svc))
        code, body, _ = http(s.base, "/views"); self.assertEqual(code, 200); self.assertEqual(json.loads(body), {"schema": ["board", "backlog", "unheld"], "rendered": ["board", "backlog", "unheld"], "saved": [], "default": "board"})
        code, body, _ = http(s.base, "/views/mine", {"sql": "SELECT id, what FROM board", "columns": ["id"], "sort": "id desc"}, method="PUT"); self.assertEqual(code, 201)
        code, body, _ = http(s.base, "/views/mine", {"sql": "SELECT id FROM board"}, method="PUT"); self.assertEqual(code, 200)
        code, body, _ = http(s.base, "/views/mine"); self.assertEqual(json.loads(body), {"name": "mine", "sql": "SELECT id FROM board", "columns": [], "sort": "", "saved": True})
        code, body, _ = http(s.base, "/views/bad", {"sql": "DELETE FROM rows"}, method="PUT"); self.assertEqual(code, 400); self.assertIn("read-only", body)
        code, body, _ = http(s.base, "/views/board", {"sql": "SELECT 1"}, method="PUT"); self.assertEqual(code, 400)
        self.assertEqual(json.loads(http(s.base, "/views")[1])["saved"], ["mine"])
        code, body, _ = http(s.base, "/views/board"); self.assertEqual(json.loads(body)["saved"], False)
        code, body, _ = http(s.base, "/views/mine", method="DELETE"); self.assertEqual(code, 200)
        code, body, _ = http(s.base, "/views/mine", method="DELETE"); self.assertEqual(code, 404)
        code, body, _ = http(s.base, "/views/nothing"); self.assertEqual(code, 404)

if __name__ == "__main__":
    unittest.main()
