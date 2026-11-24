# First run: setting a student up

Do this once per student, when there's no `study-prep.toml`. Keep it short:
only Blackboard is needed to start, every other source can be added later,
and a run works with whatever is set up.

## 1. Ask

Ask these together, in one message:

1. Which university, and where do you keep your course files? (A folder with
   one subfolder per course. If they have none, suggest `~/Study/<term>/`.)
2. What's your Blackboard address? (What's in the browser bar when you're on
   it, e.g. `https://lms.example.edu`.)
3. **How do you log in to Blackboard?**
   - a) A username and password on Blackboard's own page, nothing else.
   - b) Through the university's portal or single sign-on (username and
     password on a university page, maybe a code or a phone approval:
     Microsoft Authenticator, Nafath, SMS...).
   - Not sure? b) works for everyone.
4. Which Telegram and WhatsApp groups are for your level or major? (Names or
   links are enough; course groups get found automatically.) Do you use
   either at all?
5. Any shared Drive of past exams your classmates use? (A link.)

Then copy `<skill>/assets/study-prep.example.toml` to `study-prep.toml` in
their course folder root, and fill it in: answer 3 a) is `login =
"password"`, b) is `login = "browser"`. Put anything else they tell you about
how their university works (term numbering, sections) in `notes`.

## 2. Tools

Nothing for the student to install. `scripts/run` installs `uv` the first
time if it's missing, and `uv` brings Python and every package. The one
outside need: for Blackboard's browser login, a Chromium-based browser
(Chrome, Chromium, Brave or Edge; Safari and Firefox can't be driven). Most
students have Chrome; if they have none, tell them to install Chrome.
Everything works the same on macOS and Linux.

## 3. Logins

Each one the student does themselves; you never see a password.

**Blackboard.** Run `bb.py login` (in the background if your agent can).
- `browser`: a browser window opens on Blackboard (its own profile, so their
  main browser is untouched). They log in as usual; the window closes by
  itself once they're in. Later, when the session runs out, `bb.py` tries
  the same profile in a hidden window first, which works as long as the
  portal still remembers them; otherwise it asks for the window again.
- `password`: they create `~/.config/study-prep/blackboard.env` themselves:
  ```
  BLACKBOARD_USER=their-username
  BLACKBOARD_PASSWORD=their-password
  ```
  then `chmod 600 ~/.config/study-prep/blackboard.env`. `bb.py` logs in with
  it whenever needed. If Blackboard's page turns out not to be a plain
  username/password form, `bb.py` says so: switch to `browser`.

**Telegram** (optional). Needs a terminal, because Telegram sends a code to
their phone. Tell them to:
1. Open https://my.telegram.org, log in, go to *API development tools*,
   create an app (any name), and keep the `api_id` and `api_hash`.
2. In a terminal: `sh <skill>/scripts/run tg.py login` (give them the
   full path, ready to paste). It asks for those two values, their phone number, the
   code, and their 2FA password if set, then saves the login to
   `~/.config/study-prep/telegram.env`.

It's a full login to their account, shown in Telegram under Settings →
Devices as "study-prep (Telethon)"; they can revoke it there any time.
Claude Code users can type `! sh <path>/run tg.py login` to run it in the session.

**WhatsApp** (optional). Needs a WhatsApp MCP server linked to their phone,
e.g. https://github.com/Albrrak773/whatsapp-mcp-server (read-only; build it,
`make service`, then scan the QR code at http://127.0.0.1:8765/). Register it
with their agent:
- Claude Code: `claude mcp add --transport http whatsapp http://127.0.0.1:8765/mcp`
- OpenCode: `opencode mcp add --global --url http://127.0.0.1:8765/mcp whatsapp`
- Codex: `codex mcp add whatsapp --url http://127.0.0.1:8765/mcp`
- Anything else: nothing to register; use `wa.py`.

**Shared drive** (optional). rclone with a Google Drive remote
(`rclone config`, type `drive`). Without it, skip the drive.

## 4. Check

Run the three status checks from SKILL.md step 0 and tell the student, in
one line each, what works and what's left.
