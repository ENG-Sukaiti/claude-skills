# claude-skills

My personal Claude Code skills and global config, version-controlled and moved
between devices with git.

## Layout

```
CLAUDE.md              # global instructions, symlinked to ~/.claude/CLAUDE.md
bootstrap.sh           # per-device setup; idempotent, Linux + macOS
skills/
  notion-docs/         # documents work into Notion (see its SKILL.md)
```

`bootstrap.sh` symlinks `CLAUDE.md` and **every** directory under `skills/`
into `~/.claude/`. Adding a skill needs no change to the script.

## New device

```bash
git clone git@github.com:ENG-Sukaiti/claude-skills.git
cd claude-skills && ./bootstrap.sh
```

Then `/mcp` → `notion` → approve in the browser, and restart Claude Code
(MCP servers are enumerated once at session startup, so one registered
mid-session stays invisible to that session).

The script resolves its own location, so it works from wherever you clone it.

## Adding a skill

1. `mkdir skills/<name>` with a `SKILL.md` carrying `name` + `description`
   frontmatter. The description is the trigger — make it specific, and list the
   phrases that should fire it.
2. Commit and push.
3. On each device: `git pull`, then `./bootstrap.sh` to link the new one.

Existing skills update on `git pull` alone — the symlinks already point here.

## Why git and not file sync

These files used to ride the gSync → Google Drive sync. That has two problems:
a broken sync means no skills, and there is no history when a skill starts
misbehaving. Git gives both, and `git pull` is explicit about when config
changes land.

Consequence: this directory now contains a `.git`, so the rclone job skips it
(`--exclude-if-present=.git/HEAD`). GitHub carries it instead. That is the
intended trade, and the same rule every other repo follows.

## Related

The team equivalent is [`Voxasa/hatif-claude-skills`](https://github.com/Voxasa/hatif-claude-skills),
which has a generalized version of `notion-docs` (PR #23). This repo is the
personal one: my own paths, my own Notion hierarchy, my own profiles.
