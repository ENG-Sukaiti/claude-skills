# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""WhatsApp for agents that can't use MCP tools directly: calls a running
WhatsApp MCP server (e.g. github.com/Albrrak773/whatsapp-mcp-server, run as a
daemon on http://127.0.0.1:8765/mcp) over its HTTP transport. Standard
library only; uv supplies a recent Python (macOS's own python3 is too old).

    sh scripts/run wa.py tools            # list the server's tools and their arguments
    sh scripts/run wa.py <tool> key=value ...   # call one

Values are parsed as JSON when they can be (limit=50, unread_only=true),
otherwise kept as text (query="مراجعة الميد").

Examples:
    wa.py whatsapp_status
    wa.py list_chats query=CS315
    wa.py search_messages query=midterm after=2026-11-01
    wa.py list_messages chat="Calculus 1234" limit=200
    wa.py download_media chat=<jid> message_id=<id>

Server address: $WHATSAPP_MCP_URL, else `[whatsapp] url` in the nearest
study-prep.toml, else http://127.0.0.1:8765/mcp. Bearer token, if the server
needs one: $WHATSAPP_MCP_TOKEN.
"""

import json
import os
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

PROTOCOL = "2025-06-18"


def server_url():
    if os.environ.get("WHATSAPP_MCP_URL"):
        return os.environ["WHATSAPP_MCP_URL"]
    home = Path(os.environ.get("STUDY_PREP_HOME", Path.home() / ".config/study-prep"))
    for d in [Path.cwd(), *Path.cwd().parents, home]:
        p = d / "study-prep.toml"
        if p.is_file():
            url = tomllib.loads(p.read_text()).get("whatsapp", {}).get("url")
            if url:
                return url
    return "http://127.0.0.1:8765/mcp"


class Client:
    def __init__(self, url):
        self.url, self.session, self.n = url, None, 0

    def post(self, payload):
        h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
             "MCP-Protocol-Version": PROTOCOL}
        if self.session:
            h["Mcp-Session-Id"] = self.session
        if os.environ.get("WHATSAPP_MCP_TOKEN"):
            h["Authorization"] = f"Bearer {os.environ['WHATSAPP_MCP_TOKEN']}"
        req = urllib.request.Request(self.url, json.dumps(payload).encode(), h, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                self.session = r.headers.get("Mcp-Session-Id") or self.session
                body, ctype = r.read().decode(), r.headers.get("Content-Type", "")
        except urllib.error.URLError as e:
            raise SystemExit(f"WhatsApp server not reachable at {self.url} ({getattr(e, 'reason', e)}). "
                             "Is it running? (e.g. `systemctl --user status whatsapp-mcp`)")
        if "id" not in payload or not body.strip():
            return None
        msgs = [json.loads(l[5:]) for l in body.splitlines() if l.startswith("data:")] \
            if "event-stream" in ctype else [json.loads(body)]
        for m in msgs:
            if m.get("id") == payload["id"]:
                if "error" in m:
                    raise SystemExit(f"error: {m['error'].get('message', m['error'])}")
                return m["result"]
        raise SystemExit("No answer from the server.")

    def call(self, method, params=None):
        self.n += 1
        return self.post({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}})

    def start(self):
        self.call("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
                                 "clientInfo": {"name": "study-prep-wa", "version": "1"}})
        self.post({"jsonrpc": "2.0", "method": "notifications/initialized"})


def value(v):
    try:
        return json.loads(v)
    except json.JSONDecodeError:
        return v


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    c = Client(server_url())
    c.start()
    if args[0] == "tools":
        for t in c.call("tools/list")["tools"]:
            props = t.get("inputSchema", {}).get("properties", {})
            print(f"{t['name']}({', '.join(props)})\n    {t.get('description', '').strip().splitlines()[0]}")
        return
    kw = dict(a.split("=", 1) for a in args[1:] if "=" in a)
    res = c.call("tools/call", {"name": args[0], "arguments": {k: value(v) for k, v in kw.items()}})
    for part in res.get("content", []):
        if part.get("type") == "text":
            print(part["text"])
        else:
            print(f"[{part.get('type')} {part.get('mimeType', '')}]")
    if res.get("isError"):
        sys.exit(1)


if __name__ == "__main__":
    main()
