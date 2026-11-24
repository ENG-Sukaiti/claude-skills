# /// script
# requires-python = ">=3.11"
# dependencies = ["requests>=2.31", "websocket-client>=1.7"]
# ///
"""Blackboard Learn from the command line, for any university.

    sh scripts/run bb.py <command> ...

Which Blackboard: --url, else $BLACKBOARD_URL, else `[blackboard] url` in the
nearest study-prep.toml (this folder or a parent), else
~/.config/study-prep/study-prep.toml.

Logging in. Two ways, picked by `[blackboard] login` in the config:

  login = "browser"   (default; any login: university portal, SSO, Nafath,
                       Microsoft, SMS codes...)
      `bb.py login` opens a browser window on Blackboard. The student logs in
      there as usual; the script notices, saves the session and closes the
      window. The window uses its own browser profile, so later, when
      Blackboard's session runs out, the script tries a hidden browser with
      that profile first: if the portal still remembers the student, that
      renews it with nobody involved.

  login = "password"  (Blackboard's own username/password page)
      The student puts BLACKBOARD_USER and BLACKBOARD_PASSWORD in
      ~/.config/study-prep/blackboard.env (chmod 600) themselves. The script
      logs in with them whenever the session runs out. If that fails it falls
      back to the browser.

Commands:
    login                         log in (opens a browser window unless the password works)
    status                        is the saved session alive
    courses                       courseId, available?, name
    tree <course>                 content tree: id, kind, title
    announcements <course>
    download <course> [contentId...] --to <dir>
                                  attachments of those items (folders: everything
                                  inside). No ids: every file in the course,
                                  keeping its folder structure.
    get <api path>                raw JSON, e.g. /learn/api/public/v1/users/me
    open [course|url]             open Blackboard in the logged-in browser profile

<course> is a courseId (_12345_1) or any part of the course name or code,
spacing and case ignored (e.g. CS315, "numerical methods").
"""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
CONFIG_DIR = Path(os.environ.get("STUDY_PREP_HOME", Path.home() / ".config/study-prep"))
DATA_DIR = Path(os.environ.get("STUDY_PREP_DATA", Path.home() / ".local/share/study-prep"))
PROFILE = DATA_DIR / "browser"        # the login browser's own profile; the student's main browser is untouched
CDP_PORT = int(os.environ.get("STUDY_PREP_CDP_PORT", "9333"))
ME = "/learn/api/public/v1/users/me"


class NeedLogin(Exception):
    pass


# ---------- config ----------

def find_config():
    for d in [Path.cwd(), *Path.cwd().parents]:
        if (d / "study-prep.toml").is_file():
            return d / "study-prep.toml"
    p = CONFIG_DIR / "study-prep.toml"
    return p if p.is_file() else None


def settings(url_arg):
    cfg = {}
    if (p := find_config()):
        cfg = tomllib.loads(p.read_text()).get("blackboard", {})
    url = (url_arg or os.environ.get("BLACKBOARD_URL") or cfg.get("url") or "").rstrip("/")
    if not url:
        raise SystemExit("No Blackboard URL. Set `[blackboard] url` in study-prep.toml, or pass --url.")
    if not url.startswith("http"):
        url = "https://" + url
    return url, cfg.get("login", "browser")


def cookie_file(lms):
    return CONFIG_DIR / f"blackboard-{urlparse(lms).netloc}.json"


# ---------- session ----------

def new_session():
    s = requests.Session()
    s.headers["User-Agent"] = UA
    return s


def set_cookies(s, cookies):
    for c in cookies:
        s.cookies.set(c["name"], c["value"], domain=c["domain"], path=c.get("path", "/"),
                      expires=c.get("expires") or None, secure=c.get("secure", False))


def dump_cookies(s):
    return [{"name": c.name, "value": c.value, "domain": c.domain, "path": c.path,
             "expires": c.expires, "secure": c.secure} for c in s.cookies]


def save(lms, s):
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    f = cookie_file(lms)
    fd = os.open(f, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        json.dump({"saved_at": int(time.time()), "cookies": dump_cookies(s)}, fh)


def logged_in(lms, s):
    try:
        return s.get(lms + ME, headers={"Accept": "application/json"}, timeout=30).status_code == 200
    except requests.RequestException:
        return False


def session(lms, method):
    """A logged-in session; renews quietly when it can."""
    s = new_session()
    f = cookie_file(lms)
    if f.exists():
        set_cookies(s, json.loads(f.read_text())["cookies"])
        if logged_in(lms, s):
            return s
    if method == "password" and (s2 := password_login(lms)):
        save(lms, s2)
        print("(Blackboard session renewed with the saved password)", file=sys.stderr)
        return s2
    if PROFILE.exists() and (s2 := browser_login(lms, headless=True, timeout=45)):
        save(lms, s2)
        print("(Blackboard session renewed through the browser profile)", file=sys.stderr)
        return s2
    raise NeedLogin("Not logged in to Blackboard. Run `bb.py login`: it opens a browser window, "
                    "and the student logs in there.")


# ---------- password login (Blackboard's own login page) ----------

class _Forms(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms, self._form = [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self._form = {"action": a.get("action") or "", "method": (a.get("method") or "get").lower(), "inputs": []}
            self.forms.append(self._form)
        elif tag == "input" and self._form is not None and a.get("name"):
            self._form["inputs"].append({"name": a["name"], "type": (a.get("type") or "text").lower(),
                                         "value": a.get("value") or ""})

    def handle_endtag(self, tag):
        if tag == "form":
            self._form = None


def password_login(lms):
    env = CONFIG_DIR / "blackboard.env"
    vals = {}
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip().strip('"').strip("'")
    user = os.environ.get("BLACKBOARD_USER") or vals.get("BLACKBOARD_USER")
    pw = os.environ.get("BLACKBOARD_PASSWORD") or vals.get("BLACKBOARD_PASSWORD")
    if not (user and pw):
        return None
    s = new_session()
    r = s.get(lms + "/webapps/login/", timeout=30)
    p = _Forms()
    p.feed(r.text)
    form = next((f for f in p.forms if any(i["name"] == "user_id" for i in f["inputs"])), None)
    if not form:
        print("(password login: no Blackboard login form found; this site probably logs in "
              "through a portal, so use login = \"browser\")", file=sys.stderr)
        return None
    data = {i["name"]: i["value"] for i in form["inputs"] if i["type"] not in ("submit", "button", "image")}
    data.update({"user_id": user, "password": pw})
    s.post(urljoin(r.url, form["action"] or r.url), data=data, headers={"Referer": r.url}, timeout=30)
    if logged_in(lms, s):
        return s
    print("(password login: Blackboard refused the saved username/password)", file=sys.stderr)
    return None


# ---------- browser login (any login method) ----------

def browser_exe():
    if os.environ.get("STUDY_PREP_BROWSER"):
        return os.environ["STUDY_PREP_BROWSER"]
    for b in ("google-chrome-stable", "google-chrome", "chromium", "chromium-browser", "brave", "brave-browser",
              "microsoft-edge", "microsoft-edge-stable"):
        if (p := shutil.which(b)):
            return p
    for app in ("Google Chrome", "Chromium", "Brave Browser", "Microsoft Edge"):  # macOS
        for root in (Path("/Applications"), Path.home() / "Applications"):
            p = root / f"{app}.app/Contents/MacOS/{app}"
            if p.is_file():
                return str(p)
    raise SystemExit("No Chromium-based browser found (Chrome, Chromium, Brave or Edge). Install one, or set "
                     "STUDY_PREP_BROWSER to its executable. (Safari and Firefox can't be driven this way.)")


def cdp_version():
    try:
        return requests.get(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=1).json()
    except requests.RequestException:
        return None


class CDP:
    def __init__(self):
        import websocket
        self.ws = websocket.create_connection(cdp_version()["webSocketDebuggerUrl"], timeout=15,
                                              suppress_origin=True)  # Chromium rejects DevTools sockets with an Origin
        self.n = 0

    def call(self, method, params=None):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params or {}}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})


def start_browser(url, headless):
    """Start the login browser, or reuse it if it's already running. Returns
    the process we started, or None if it was already running."""
    if cdp_version():
        CDP().call("Target.createTarget", {"url": url})
        return None
    PROFILE.mkdir(mode=0o700, parents=True, exist_ok=True)
    args = [browser_exe(), f"--user-data-dir={PROFILE}", f"--remote-debugging-port={CDP_PORT}",
            "--no-first-run", "--no-default-browser-check"]
    if headless:
        args.append("--headless=new")
    proc = subprocess.Popen(args + [url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    for _ in range(100):
        if cdp_version():
            return proc
        time.sleep(0.2)
    proc.terminate()
    raise SystemExit("The browser started, but its DevTools port never answered.")


def browser_login(lms, headless, timeout):
    proc = start_browser(lms + "/ultra/stream", headless)
    deadline = time.time() + timeout
    try:
        while time.time() < deadline:
            time.sleep(2 if headless else 3)
            try:
                cookies = CDP().call("Storage.getCookies")["cookies"]
            except Exception:
                if not cdp_version():
                    return None  # the window was closed
                continue
            s = new_session()
            set_cookies(s, cookies)
            if logged_in(lms, s):
                return s
        return None
    finally:
        if proc or headless:
            try:
                CDP().call("Browser.close")
            except Exception:
                if proc:
                    proc.terminate()


# ---------- API helpers ----------

def get_json(lms, s, path, **params):
    r = s.get(urljoin(lms, path), params=params, headers={"Accept": "application/json"}, timeout=60)
    r.raise_for_status()
    return r.json()


def paged(lms, s, path, **params):
    out = []
    while path:
        d = get_json(lms, s, path, **params)
        out += d.get("results", [])
        path, params = d.get("paging", {}).get("nextPage"), {}
    return out


def memberships(lms, s):
    uid = get_json(lms, s, ME)["id"]
    return paged(lms, s, f"/learn/api/public/v1/users/{uid}/courses", expand="course", limit=100)


def norm(x):
    return re.sub(r"[\s_\-|]+", "", x or "").upper()


def course_id(lms, s, ref):
    if re.fullmatch(r"_\d+_\d+", ref):
        return ref
    want = norm(ref)
    ms = memberships(lms, s)
    hits = [m for m in ms if want in norm(m["course"].get("name")) or want in norm(m["course"].get("courseId"))]
    live = [m for m in hits if m.get("availability", {}).get("available") == "Yes"]
    hits = live if len(live) >= 1 and len(hits) > 1 else hits
    if len(hits) != 1:
        names = "; ".join(f"{m['courseId']} {m['course'].get('name')}" for m in hits) or "none"
        raise SystemExit(f"'{ref}' matches {len(hits)} courses ({names}). Use the courseId.")
    return hits[0]["courseId"]


KIND = {"resource/x-bb-folder": "folder", "resource/x-bb-lesson": "module", "resource/x-bb-document": "page",
        "resource/x-bb-file": "file", "resource/x-bb-courselink": "link", "resource/x-bb-externallink": "url",
        "resource/x-bb-assignment": "assign", "resource/x-bb-asmt-test-link": "test"}


def kind(item):
    h = item.get("contentHandler") or ""
    return KIND.get(h if isinstance(h, str) else h.get("id", ""), "?")


def contents(lms, s, cid):
    """Every content item of a course, each with parentId."""
    try:  # the Ultra UI's own endpoint: whole tree in one call
        return paged(lms, s, f"/learn/api/v1/courses/{cid}/contents", recursive="true",
                     fields="id,title,contentHandler,parentId")
    except requests.HTTPError:
        pass
    out = []

    def walk(path, parent):
        for i in paged(lms, s, path):
            i["parentId"] = parent
            out.append(i)
            if i.get("hasChildren"):
                walk(f"/learn/api/public/v1/courses/{cid}/contents/{i['id']}/children", i["id"])
    walk(f"/learn/api/public/v1/courses/{cid}/contents", None)
    return out


def safe(name):
    name = re.sub(r"[‎‏‪-‮⁦-⁩]", "", name)  # invisible direction marks
    return re.sub(r'[/\\:*?"<>|]+', "-", name).strip() or "untitled"


# ---------- commands ----------

def cmd_login(a, lms, method):
    if method == "password" and (s := password_login(lms)):
        save(lms, s)
    else:
        print("A browser window is opening on Blackboard. Log in there the way you normally do;"
              " it closes by itself once you're in (10 minutes max).", flush=True)
        s = browser_login(lms, headless=False, timeout=600)
        if not s:
            raise SystemExit("No login seen (window closed, or timed out). Run `bb.py login` again.")
        save(lms, s)
    me = get_json(lms, s, ME)
    print(f"Logged in to {urlparse(lms).netloc} as {me.get('userName')}. Session saved to {cookie_file(lms)}.")


def cmd_status(a, lms, method):
    f = cookie_file(lms)
    print(f"site: {lms}\nlogin method: {method}\nsaved session: "
          + (time.strftime("%Y-%m-%d %H:%M", time.localtime(json.loads(f.read_text())["saved_at"])) if f.exists() else "none"))
    try:
        s = session(lms, method)
    except NeedLogin as e:
        raise SystemExit(f"Blackboard: not logged in. {e}")
    print(f"Blackboard: logged in as {get_json(lms, s, ME).get('userName')}")


def cmd_courses(a, lms, method):
    for m in memberships(lms, session(lms, method)):
        avail = m.get("availability", {}).get("available", "?")
        print(m["courseId"], avail, re.sub(r"\s+", " ", m["course"].get("name", "")), sep="\t")


def cmd_tree(a, lms, method):
    s = session(lms, method)
    cid = course_id(lms, s, a.course)
    items = contents(lms, s, cid)
    ids = {i["id"] for i in items}
    kids = {}
    for i in items:
        kids.setdefault(i.get("parentId") if i.get("parentId") in ids else None, []).append(i)

    def walk(pid, depth):
        for i in kids.get(pid, []):
            print(f"{'  ' * depth}{i['id']}  {kind(i):<6}  {i.get('title', '')}")
            walk(i["id"], depth + 1)
    print(f"# {cid}")
    walk(None, 0)


def cmd_announcements(a, lms, method):
    s = session(lms, method)
    cid = course_id(lms, s, a.course)
    for n in paged(lms, s, f"/learn/api/public/v1/courses/{cid}/announcements"):
        body = html.unescape(re.sub(r"<[^>]+>", " ", n.get("body") or ""))
        print(f"== {(n.get('created') or '')[:10]}  {n.get('title', '')}\n{re.sub(r'\s+', ' ', body).strip()}\n")


def cmd_download(a, lms, method):
    s = session(lms, method)
    cid = course_id(lms, s, a.course)
    items = contents(lms, s, cid)
    by_id = {i["id"]: i for i in items}
    kids = {}
    for i in items:
        kids.setdefault(i.get("parentId"), []).append(i)

    def rel_dir(i):  # folder path of an item inside the course
        parts, p = [], i.get("parentId")
        while p in by_id:
            parts.append(safe(by_id[p].get("title", "")))
            p = by_id[p].get("parentId")
        return Path(*reversed(parts)) if parts else Path()

    def under(root):
        out, stack = [], [root]
        while stack:
            i = stack.pop()
            out.append(i)
            stack += kids.get(i["id"], [])
        return out

    picked = [i for r in a.content for i in under(by_id.get(r) or {"id": r, "title": r})] if a.content else items
    root = Path(a.to)
    n = 0
    for i in picked:
        if kind(i) in ("folder", "module", "link", "url"):
            continue
        base = f"/learn/api/public/v1/courses/{cid}/contents/{i['id']}/attachments"
        try:
            atts = get_json(lms, s, base).get("results", [])
        except requests.HTTPError:
            continue
        for att in atts:
            dest = root / (rel_dir(i) if not a.content else Path()) / safe(Path(att["fileName"]).name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with s.get(urljoin(lms, f"{base}/{att['id']}/download"), stream=True, timeout=120) as r:
                r.raise_for_status()
                size = int(r.headers.get("Content-Length") or -1)
                if dest.exists() and dest.stat().st_size == size:
                    print(f"{dest}\t(already there)")
                    continue
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(1 << 16):
                        f.write(chunk)
            n += 1
            print(f"{dest}\t{i.get('title', '')}")
    print(f"{n} file(s) downloaded", file=sys.stderr)


def cmd_get(a, lms, method):
    print(json.dumps(get_json(lms, session(lms, method), a.path), ensure_ascii=False, indent=1))


def cmd_open(a, lms, method):
    s = session(lms, method)
    target = a.target or f"{lms}/ultra/stream"
    if not target.startswith("http"):
        target = f"{lms}/ultra/courses/{course_id(lms, s, target)}/outline"
    start_browser("about:blank", headless=False)
    cdp = CDP()
    cdp.call("Storage.setCookies", {"cookies": [
        {"name": c.name, "value": c.value, "domain": c.domain, "path": c.path, "secure": bool(c.secure),
         "httpOnly": True, **({"expires": c.expires} if c.expires else {})} for c in s.cookies]})
    cdp.call("Target.createTarget", {"url": target})
    print(f"Opened {target}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", help="Blackboard address, e.g. https://lms.example.edu")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login").set_defaults(f=cmd_login)
    sub.add_parser("status").set_defaults(f=cmd_status)
    sub.add_parser("courses").set_defaults(f=cmd_courses)
    for name, f in (("tree", cmd_tree), ("announcements", cmd_announcements)):
        sp = sub.add_parser(name)
        sp.add_argument("course")
        sp.set_defaults(f=f)
    sp = sub.add_parser("download")
    sp.add_argument("course")
    sp.add_argument("content", nargs="*")
    sp.add_argument("--to", required=True)
    sp.set_defaults(f=cmd_download)
    sp = sub.add_parser("get")
    sp.add_argument("path")
    sp.set_defaults(f=cmd_get)
    sp = sub.add_parser("open")
    sp.add_argument("target", nargs="?")
    sp.set_defaults(f=cmd_open)
    a = p.parse_args()
    lms, method = settings(a.url)
    try:
        a.f(a, lms, method)
    except NeedLogin as e:
        raise SystemExit(str(e))
    except requests.HTTPError as e:
        hint = " (403 usually means the course is closed to you: check `bb.py courses`)" \
            if e.response.status_code == 403 else ""
        raise SystemExit(f"HTTP {e.response.status_code} for {e.request.url.split('?')[0]}{hint}")


if __name__ == "__main__":
    main()
