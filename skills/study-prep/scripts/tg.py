# /// script
# requires-python = ">=3.11"
# dependencies = ["telethon>=1.36"]
# ///
"""Telegram for study agents: read, search and download from student groups
and channels through the student's own account (a user client: bots can't
read chat history).

    sh scripts/run tg.py <command> ...

The login lives in ~/.config/study-prep/telegram.env (mode 600). Create it
once with `tg.py login`, run by the student in a real terminal: it asks for
the api_id/api_hash from https://my.telegram.org (API development tools),
the phone number, the code Telegram sends, and the 2FA password if set.

Commands:
    login                           one-time login (interactive, the student runs it)
    status                          is the login working, and as whom
    chats [filter]                  joined chats: id, type, title (filter: part of the title)
    find <query> [--limit N]        public groups/channels by name, joined or not
    read <chat> [--limit N] [--since YYYY-MM-DD] [--files] [--topic ID]
                                    messages oldest-first; --files = only ones with a file;
                                    --topic = one topic of a forum group (the N in t.me/group/N/msg)
    search <query> [--chat <chat>] [--limit N] [--files] [--since YYYY-MM-DD]
                                    one chat, or every chat when --chat is omitted
    pinned <chat>                   the chat's pinned messages
    download <chat> <msg_id>... --to <dir>
    download <t.me message link> --to <dir>
                                    e.g. a lecture video the student pasted
    join <t.me link or @username>   join a group or channel (invite links too)

<chat> is a numeric id (from `chats`), a @username, or a t.me link.
Every message line ends with its t.me link, for citing.
Apart from `join`, nothing is ever sent, edited, deleted or marked as read.
"""

import argparse
import getpass
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import InputMessagesFilterPinned

ENV_FILE = Path(os.environ.get("STUDY_PREP_HOME", Path.home() / ".config/study-prep")) / "telegram.env"
DEVICE = "study-prep (Telethon)"  # how the login shows up in Telegram > Settings > Devices


def load_env():
    if ENV_FILE.exists():
        for kv in ENV_FILE.read_text().splitlines():
            if "=" in kv:
                k, v = kv.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    missing = [k for k in ("TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_SESSION") if not os.environ.get(k)]
    if missing:
        raise SystemExit(f"Telegram isn't logged in ({ENV_FILE} has no {', '.join(missing)}). The student runs, "
                         f"in a real terminal: sh {Path(__file__).resolve().parent}/run tg.py login")


def login():
    print("Get api_id and api_hash at https://my.telegram.org -> API development tools.")
    api_id = int(input("api_id: ").strip())
    api_hash = getpass.getpass("api_hash (hidden): ").strip()
    with TelegramClient(StringSession(), api_id, api_hash, device_model=DEVICE) as client:
        client.start(password=lambda: getpass.getpass("2FA password (hidden, blank if none): "))
        me = client.get_me()
        session = client.session.save()
    ENV_FILE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(ENV_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(f"TELEGRAM_API_ID={api_id}\nTELEGRAM_API_HASH={api_hash}\nTELEGRAM_SESSION={session}\n")
    print(f"Logged in as {me.first_name} (@{me.username}). Saved to {ENV_FILE}.\n"
          f"It shows in Telegram > Settings > Devices as \"{DEVICE}\"; revoke it there any time.")


def link(m):
    """t.me link to a message. /c/ links open for members only; basic
    (non-super) groups have no message links."""
    username = getattr(m.chat, "username", None)
    if username:
        return f"https://t.me/{username}/{m.id}"
    if str(m.chat_id).startswith("-100"):
        return f"https://t.me/c/{str(m.chat_id)[4:]}/{m.id}"
    return "(no link)"


def line(m):
    when = m.date.strftime("%Y-%m-%d %H:%M")
    who = getattr(m.sender, "first_name", None) or getattr(m.sender, "title", None) or "?"
    file = ""
    if m.file:
        file = f" [file: {m.file.name or m.file.mime_type} {(m.file.size or 0) / 1e6:.1f}MB]"
    text = (m.message or "").replace("\n", " / ")
    links = [e.url for e in (m.entities or []) if getattr(e, "url", None)]  # "Click here" links hide here
    if links:
        text += " <" + " ".join(links) + ">"
    return f"#{m.id} {when} {who}:{file} {text}  {link(m)}"


def since_of(s):
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc) if s else None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login")
    sub.add_parser("status")
    c = sub.add_parser("chats"); c.add_argument("filter", nargs="?")
    f = sub.add_parser("find"); f.add_argument("query"); f.add_argument("--limit", type=int, default=20)
    r = sub.add_parser("read"); r.add_argument("chat"); r.add_argument("--limit", type=int, default=100)
    r.add_argument("--since"); r.add_argument("--files", action="store_true"); r.add_argument("--topic", type=int)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--chat")
    s.add_argument("--limit", type=int, default=50); s.add_argument("--files", action="store_true"); s.add_argument("--since")
    sub.add_parser("pinned").add_argument("chat")
    d = sub.add_parser("download"); d.add_argument("chat"); d.add_argument("ids", nargs="*", type=int)
    d.add_argument("--to", required=True)
    sub.add_parser("join").add_argument("target")
    a = p.parse_args()

    if a.cmd == "login":
        return login()
    load_env()
    client = TelegramClient(StringSession(os.environ["TELEGRAM_SESSION"]), int(os.environ["TELEGRAM_API_ID"]),
                            os.environ["TELEGRAM_API_HASH"], device_model=DEVICE)

    def chat(ref):
        """Resolve a chat. A fresh session knows no numeric ids until it has
        seen the dialogs, so load them and retry once."""
        ref = ref.removeprefix("https://").removeprefix("t.me/").removeprefix("@") if not ref.lstrip("-").isdigit() else int(ref)
        try:
            return client.get_input_entity(ref)
        except ValueError:
            client.get_dialogs()
            return client.get_input_entity(ref)

    with client:
        if not client.is_user_authorized():
            raise SystemExit("The Telegram login stopped working (revoked or expired). The student reruns `tg.py login`.")
        if a.cmd == "status":
            me = client.get_me()
            print(f"Telegram: logged in as {me.first_name} (@{me.username})")

        elif a.cmd == "chats":
            for dlg in client.iter_dialogs():
                if a.filter and a.filter.lower() not in dlg.name.lower():
                    continue
                kind = "channel" if dlg.is_channel and not dlg.is_group else "group" if dlg.is_group else "user"
                print(f"{dlg.id}\t{kind}\t{dlg.name}")

        elif a.cmd == "find":
            res = client(SearchRequest(q=a.query, limit=a.limit))
            for ch in res.chats:
                kind = "group" if getattr(ch, "megagroup", False) else "channel" if hasattr(ch, "broadcast") else "group"
                handle = f"@{ch.username}" if getattr(ch, "username", None) else "(private)"
                joined = "" if getattr(ch, "left", True) else "\tjoined"
                print(f"-100{ch.id}\t{kind}\t{handle}\t{getattr(ch, 'participants_count', '') or ''}\t{ch.title}{joined}")

        elif a.cmd == "read":
            since = since_of(a.since)
            kw = {"offset_date": since, "reverse": True} if since else {}
            if a.topic:
                kw["reply_to"] = a.topic
            msgs = [m for m in client.iter_messages(chat(a.chat), limit=a.limit, **kw) if not a.files or m.file]
            if not since:
                msgs.reverse()
            for m in msgs:
                print(line(m))

        elif a.cmd == "search":
            since = since_of(a.since)
            target = chat(a.chat) if a.chat else None
            for m in client.iter_messages(target, search=a.query, limit=a.limit):
                if since and m.date < since:
                    break
                if a.files and not m.file:
                    continue
                prefix = "" if a.chat else f"[{m.chat_id} {getattr(m.chat, 'title', None) or getattr(m.chat, 'first_name', '')}] "
                print(prefix + line(m))

        elif a.cmd == "pinned":
            for m in reversed(list(client.iter_messages(chat(a.chat), filter=InputMessagesFilterPinned))):
                print(line(m))

        elif a.cmd == "download":
            if not a.ids:  # a message link: t.me/<name>/<id>, t.me/c/<id>/<msg>, t.me/<name>/<topic>/<msg>
                parts = a.chat.split("?")[0].rstrip("/").removeprefix("https://").removeprefix("t.me/").split("/")
                if len(parts) < 2 or not parts[-1].isdigit():
                    raise SystemExit("Give message ids, or a t.me link that ends in a message number.")
                a.chat, a.ids = (f"-100{parts[1]}" if parts[0] == "c" else parts[0]), [int(parts[-1])]
            os.makedirs(a.to, exist_ok=True)
            for m in client.get_messages(chat(a.chat), ids=a.ids):
                if m and m.file:
                    print(client.download_media(m, file=a.to.rstrip("/") + "/"))
                else:
                    print(f"#{m.id if m else '?'}: no file", file=sys.stderr)

        elif a.cmd == "join":
            t = a.target.removeprefix("https://").removeprefix("t.me/").removeprefix("@")
            if t.startswith("+") or t.startswith("joinchat/"):
                res = client(ImportChatInviteRequest(t.split("/")[-1].lstrip("+")))
            else:
                res = client(JoinChannelRequest(t))
            ch = res.chats[0]
            print(f"joined {ch.title}  id -100{ch.id}")


if __name__ == "__main__":
    main()
