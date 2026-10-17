"""ledgerd: GitHub authentication by the OAuth device flow, kernel only (stdlib `urllib`, no `gh`; plan #336
revision 7). `login` asks GitHub for a device code (`POST <device>`), prints the one line the Operator
needs — `Open <verification_uri> and enter the code <user_code>` — and polls `POST <token>` with the
device-code grant at the interval GitHub states (`authorization_pending` keeps polling, `slow_down`
widens the interval, `expired_token` and `access_denied` stop) until the Operator has logged in on any
device; the token is then written to `<state>/credentials` in git's credential-store form
(`https://x-access-token:<token>@github.com`), mode 0600, and never printed. `status` asks
`GET <user>` with the token; `logout` deletes the file (it revokes nothing on GitHub's side — the
Operator revokes a grant there). The flow needs the client id of an OAuth App the Operator registered
once with Device Flow enabled; `init --github-client-id` stores it in the conf, and without one `login`
refuses with the five registration steps. The three endpoint URLs are an argument so a test points
them at a stub server. Kernel: Python 3.12+.
"""
import sys
if sys.version_info < (3, 12):
    sys.exit("auth.py: Python 3.12+ required")
import json, os, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
COMPONENT = Path(__file__).resolve().parents[1]
for _p in (str(COMPONENT), str(COMPONENT.parents[1] / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dyadlib

GITHUB_URLS = {"device": "https://github.com/login/device/code",
               "token": "https://github.com/login/oauth/access_token",
               "user": "https://api.github.com/user"}
GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"
DEFAULT_SCOPE = "repo"                                      # what a private ledger's fetch needs; a public one needs none
CREDENTIALS = "credentials"                                  # `<state>/credentials` (store.py reads it)
CREDENTIAL_HOST = "github.com"
CREDENTIAL_USER = "x-access-token"
PENDING, SLOW_DOWN, EXPIRED, DENIED = "authorization_pending", "slow_down", "expired_token", "access_denied"
SLOW_DOWN_STEP = 5                                           # seconds GitHub asks to add on slow_down
MIN_INTERVAL = 1
REGISTRATION_STEPS = (
    "1. GitHub -> Settings -> Developer settings -> OAuth Apps -> New OAuth App",
    "2. Application name: dyad-ledgerd; Homepage URL: any; Authorization callback URL: not needed",
    "3. Tick 'Enable Device Flow' and register the application",
    "4. Copy the Client ID (public by design; never the client secret, which the device flow does not use)",
    "5. dyad ledger init --state <dir> ... --github-client-id <Client ID> --force   (then: dyad ledger auth login --state <dir>)",
)

INVARIANTS: list[dyadlib.Invariant] = [   # crafts/syseng/rules/invariants.md: pure, enforced at import
    ("urls-are-the-three-endpoints", lambda: set(GITHUB_URLS) == {"device", "token", "user"} and all(u.startswith("https://") for u in GITHUB_URLS.values())),
    ("grant-is-the-device-code-grant", lambda: GRANT_TYPE.endswith(":device_code")),
    ("flow-states-distinct", lambda: len({PENDING, SLOW_DOWN, EXPIRED, DENIED}) == 4),
    ("five-registration-steps", lambda: len(REGISTRATION_STEPS) == 5 and all(s[0] == str(i + 1) for i, s in enumerate(REGISTRATION_STEPS))),
    ("intervals-positive", lambda: MIN_INTERVAL > 0 and SLOW_DOWN_STEP > 0),
]

def credentials_path(state: Path) -> Path:
    return Path(state) / CREDENTIALS

def credential_line(token: str) -> str:
    return f"https://{CREDENTIAL_USER}:{urllib.parse.quote(token, safe='')}@{CREDENTIAL_HOST}\n"

def write_credentials(state: Path, token: str) -> Path:
    """The one write of the token: the file is created 0600 before the token enters it."""
    p = credentials_path(state); p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(credential_line(token))
    os.chmod(p, 0o600)
    return p

def token(state: Path) -> str | None:
    """The stored token, or None: the credential-store line's password field, unquoted."""
    p = credentials_path(state)
    if not p.is_file():
        return None
    for line in p.read_text().splitlines():
        line = line.strip()
        if line.startswith("https://") and "@" in line:
            userinfo = line[len("https://"):].rsplit("@", 1)[0]
            if ":" in userinfo:
                return urllib.parse.unquote(userinfo.split(":", 1)[1])
    return None

def _post(url: str, fields: dict, timeout: int = 30) -> dict:
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=data, headers={"Accept": "application/json", "User-Agent": "dyad-ledgerd"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
    try:
        return json.loads(body)
    except ValueError:
        return {"error": "bad_response", "error_description": body[:200]}

def _get(url: str, tok: str, timeout: int = 30) -> tuple[int, dict, dict]:
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "dyad-ledgerd", "Authorization": f"Bearer {tok}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or "{}"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, {}, dict(e.headers)

def login(state: Path, client_id: str | None, scope: str = DEFAULT_SCOPE, urls: dict | None = None,
          out=print, sleep=time.sleep, max_wait: int = 15 * 60) -> int:
    """The device flow, foreground. Returns 0 with the token stored, 2 when no client id is configured (the
    registration steps printed), 1 when the flow ended without a token (expired, denied, or an error). The
    token is never printed, never returned."""
    urls = {**GITHUB_URLS, **(urls or {})}
    if not client_id:
        out("auth login needs the client id of an OAuth App with Device Flow enabled (none in ledgerd.conf):")
        for step in REGISTRATION_STEPS:
            out(f"  {step}")
        return 2
    start = _post(urls["device"], {"client_id": client_id, "scope": scope})
    if "device_code" not in start:
        out(f"device code request failed: {start.get('error', '?')}: {start.get('error_description', '')}".rstrip(": "))
        return 1
    out(f"Open {start.get('verification_uri', '?')} and enter the code {start.get('user_code', '?')}")
    interval = max(int(start.get("interval", 5)), MIN_INTERVAL)
    expires = int(start.get("expires_in", max_wait))
    waited = 0
    while waited < min(expires, max_wait):
        sleep(interval); waited += interval
        r = _post(urls["token"], {"client_id": client_id, "device_code": start["device_code"], "grant_type": GRANT_TYPE})
        if r.get("access_token"):
            p = write_credentials(state, r["access_token"])
            out(f"logged in: token stored at {p} (mode 0600); scopes: {r.get('scope', '') or '(none reported)'}")
            return 0
        err = r.get("error")
        if err == PENDING:
            continue
        if err == SLOW_DOWN:
            interval += SLOW_DOWN_STEP; continue
        if err == EXPIRED:
            out("the code expired before the login completed; run `dyad ledger auth login` again for a new code"); return 1
        if err == DENIED:
            out("the login was denied on GitHub's side; nothing stored"); return 1
        out(f"token request failed: {err or '?'}: {r.get('error_description', '')}".rstrip(": ")); return 1
    out("the code expired before the login completed; run `dyad ledger auth login` again for a new code")
    return 1

def status(state: Path, urls: dict | None = None) -> dict:
    """{login, scopes, ok} for the stored token, or {anonymous: True} without one; never the token."""
    urls = {**GITHUB_URLS, **(urls or {})}
    tok = token(state)
    if not tok:
        return {"anonymous": True}
    code, body, headers = _get(urls["user"], tok)
    scopes = headers.get("X-OAuth-Scopes") or headers.get("x-oauth-scopes") or ""
    return {"anonymous": False, "ok": code == 200, "login": body.get("login", ""), "scopes": scopes, "http": code}

def logout(state: Path) -> bool:
    """Delete the credential file; True when one was there. Revokes nothing on GitHub."""
    p = credentials_path(state)
    if p.is_file():
        p.unlink(); return True
    return False

def health_label(state: Path) -> str:
    """What `/health` reports as `auth`: `<login>` once a status call has succeeded is the CLI's to show;
    here, without a network call, `token` or `anonymous`."""
    return "token" if token(state) else "anonymous"

dyadlib.enforce(INVARIANTS, __name__)   # Rule-12 p1: the fail-loud check, at import, after the list's last binding
