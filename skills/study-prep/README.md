# study-prep

An agent skill for university students. Tell your coding agent

> I'm going to study CS315, do the thing

and it goes through **your own** Telegram, WhatsApp and Blackboard. It finds
the course's groups and channels, pulls past exams ("olds"), slides and
announcements into your course folder, and picks out what the lecturer said
matters: the exam scope, its format, and any leaked breakdown. Then it tells
you what it got and from where. Point it at a lecture recording ("watch this
and tell me if anything important was said") and it transcribes it locally
and reports what matters, with timestamps.

Works with any university that uses Blackboard, on **macOS and Linux**, with
Claude Code, OpenCode, Codex, or any agent that reads `SKILL.md` skills.
Nothing to install by hand: the agent installs what it needs on first use.

## Install

It lives in a repo with other skills; these install **only study-prep**.

**Easiest: ask your agent.** Paste this into Claude Code, OpenCode or Codex:

> Install only the `study-prep` agent skill from
> https://github.com/ENG-Sukaiti/claude-skills (the folder `skills/study-prep`),
> globally, for this agent. Use `npx skills add ENG-Sukaiti/claude-skills@study-prep -g -y`
> if Node is installed; otherwise sparse-clone just that folder to
> `~/.agents/skills/study-prep` and, for Claude Code, symlink it into
> `~/.claude/skills/study-prep`. Tell me when it's ready.

Then restart the agent and say "I'm going to study <course>, do the thing".

**Or one command** (needs Node):

```bash
npx skills add ENG-Sukaiti/claude-skills@study-prep -g -y
```

**Or with git only** (fetches just this folder, and `git pull` updates it):

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/ENG-Sukaiti/claude-skills ~/.local/share/study-prep-src
git -C ~/.local/share/study-prep-src sparse-checkout set skills/study-prep
mkdir -p ~/.agents/skills ~/.claude/skills
ln -s ~/.local/share/study-prep-src/skills/study-prep ~/.agents/skills/study-prep
ln -s ~/.local/share/study-prep-src/skills/study-prep ~/.claude/skills/study-prep   # Claude Code
```

Update later with `npx skills update study-prep`, or
`git -C ~/.local/share/study-prep-src pull`. On a Mac that has never used
git, the first `git` command offers to install Apple's developer tools:
accept, then run it again.

`~/.agents/skills/` is read by OpenCode, Codex and other agents;
`~/.claude/skills/` by Claude Code. Agents that don't load skills: point
them at `SKILL.md`.

## First run

Just ask for something. The agent sees there's no config yet, asks you a few
questions (your university, your Blackboard address, how you log in to it,
your level's groups), and writes `study-prep.toml` in your study folder. Then
it walks you through the logins:

- **Blackboard** (required): a browser window opens and you log in the way
  you always do: username and password, your university portal, Microsoft,
  Nafath, an SMS code, whatever it is. Needs Chrome, Chromium, Brave or Edge.
- **Telegram** (optional): a one-time login in a terminal with a code from
  your phone, using an API key you create at my.telegram.org.
- **WhatsApp** (optional): needs a read-only WhatsApp MCP server linked to
  your phone, such as
  [whatsapp-mcp-server](https://github.com/Albrrak773/whatsapp-mcp-server).
- **Shared Google Drive of past exams** (optional): through rclone.

Logins are saved on your computer only (`~/.config/study-prep/`, readable
only by you). The agent never sees your passwords, and it never posts,
reacts or marks anything as read in your chats.

## What's inside

```
SKILL.md                      the workflow the agent follows
references/setup.md           first-run questions and logins
references/sources.md         how to dig in each source, search terms (English + Arabic)
references/judging.md         ranking leaks vs rumours, weighing past papers, topic lists
assets/study-prep.example.toml
scripts/run                   runs a script, installing uv first if needed
scripts/bb.py                 Blackboard: courses, announcements, content tree, downloads
scripts/tg.py                 Telegram: find groups, read, search, download, pinned
scripts/wa.py                 WhatsApp MCP server from the command line, for agents without MCP
scripts/pdf.py                PDF text, metadata, page images
scripts/transcribe.py         local Whisper transcription, any language
scripts/frames.py             video frames and contact sheets
```

## Credits

Built on the study setup of [Albrrak773](https://github.com/Albrrak773): the
Telegram and Blackboard scripts, the transcription script, and the exam-prep
workflow started there.
