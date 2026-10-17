"""ledgerd/auth.py: the OAuth device flow against a stub HTTP server in the test (pending -> slow_down -> token;
the 0600 credential file in git's store form; nothing of the token on stdout), the refusal with the five
registration steps when no client id is configured, expired and denied endings, `status` and `logout`.
Importing the module runs its INVARIANTS (verifiable-code.md p5)."""
import http.server, json, stat, threading, unittest, urllib.parse
import support
from support import Case
if not support.MISSING:
    from ledgerd import auth

class Stub:
    """A GitHub stand-in: the device endpoint, a token endpoint whose answers are scripted, the user endpoint."""
    def __init__(self, answers: list[dict]):
        answers = list(answers); seen = []
        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a): pass
            def _json(self, code, body):
                data = json.dumps(body).encode()
                self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data)))
                if self.path == "/user":
                    self.send_header("X-OAuth-Scopes", "repo")
                self.end_headers(); self.wfile.write(data)
            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0)); form = urllib.parse.parse_qs(self.rfile.read(n).decode())
                seen.append((self.path, form))
                if self.path == "/device":
                    self._json(200, {"device_code": "dc-1", "user_code": "ABCD-1234", "verification_uri": "https://example.test/login/device", "interval": 1, "expires_in": 900})
                elif self.path == "/token":
                    self._json(200, answers.pop(0) if answers else {"error": "expired_token"})
                else:
                    self._json(404, {})
            def do_GET(self):
                seen.append((self.path, dict(self.headers)))
                ok = self.headers.get("Authorization") == "Bearer tok-secret-123"
                self._json(200 if ok else 401, {"login": "operator"} if ok else {})
        self.seen = seen
        self.server = http.server.HTTPServer(("127.0.0.1", 0), H)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        base = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.urls = {"device": base + "/device", "token": base + "/token", "user": base + "/user"}
    def stop(self):
        self.server.shutdown(); self.server.server_close()

class DeviceFlowTests(Case):
    def stub(self, answers) -> Stub:
        s = Stub(answers); self.addCleanup(s.stop); return s
    def test_pending_then_token_writes_a_0600_file_and_prints_no_token(self):
        state = self.scratch(); out = []; slept = []
        s = self.stub([{"error": "authorization_pending"}, {"error": "slow_down"}, {"access_token": "tok-secret-123", "scope": "repo", "token_type": "bearer"}])
        rc = auth.login(state, "client-1", urls=s.urls, out=out.append, sleep=slept.append)
        self.assertEqual(rc, 0, out)
        self.assertEqual(out[0], "Open https://example.test/login/device and enter the code ABCD-1234")
        self.assertNotIn("tok-secret-123", "\n".join(out), "the token is never printed")
        p = auth.credentials_path(state)
        self.assertEqual(p.read_text(), "https://x-access-token:tok-secret-123@github.com\n")
        self.assertEqual(stat.S_IMODE(p.stat().st_mode), 0o600)
        self.assertEqual(auth.token(state), "tok-secret-123")
        self.assertEqual(slept, [1, 1, 6], "the stated interval, widened by slow_down")
        self.assertEqual(s.seen[0][1]["scope"], ["repo"]); self.assertEqual(s.seen[1][1]["grant_type"], [auth.GRANT_TYPE])
        self.assertEqual(auth.health_label(state), "token")
    def test_no_client_id_refuses_with_the_five_steps(self):
        state = self.scratch(); out = []
        self.assertEqual(auth.login(state, None, out=out.append), 2)
        self.assertEqual(len([l for l in out if l.strip()[:2] in ("1.", "2.", "3.", "4.", "5.")]), 5)
        self.assertIn("Enable Device Flow", "\n".join(out)); self.assertFalse(auth.credentials_path(state).exists())
    def test_expired_and_denied_store_nothing(self):
        for answer, text in (({"error": "expired_token"}, "expired"), ({"error": "access_denied"}, "denied"), ({"error": "incorrect_client_credentials", "error_description": "x"}, "failed")):
            state = self.scratch(); out = []
            s = self.stub([answer])
            self.assertEqual(auth.login(state, "client-1", urls=s.urls, out=out.append, sleep=lambda n: None), 1)
            self.assertIn(text, "\n".join(out)); self.assertFalse(auth.credentials_path(state).exists())
    def test_status_and_logout(self):
        state = self.scratch(); s = self.stub([])
        self.assertEqual(auth.status(state, urls=s.urls), {"anonymous": True})
        auth.write_credentials(state, "tok-secret-123")
        st = auth.status(state, urls=s.urls)
        self.assertEqual((st["ok"], st["login"], st["scopes"], st["anonymous"]), (True, "operator", "repo", False))
        self.assertTrue(auth.logout(state)); self.assertFalse(auth.logout(state)); self.assertIsNone(auth.token(state))
        self.assertEqual(auth.health_label(state), "anonymous")
    def test_token_round_trip_quotes_special_characters(self):
        state = self.scratch(); auth.write_credentials(state, "a:b/c@d")
        self.assertEqual(auth.token(state), "a:b/c@d"); self.assertNotIn("a:b/c@d", auth.credentials_path(state).read_text())

if __name__ == "__main__":
    unittest.main()
