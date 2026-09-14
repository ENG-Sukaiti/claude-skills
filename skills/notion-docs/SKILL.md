---
name: notion-docs
description: Document project work into Ibrahim's Notion. Use when starting, resuming, or wrapping up a piece of work in any project - Hatif/work features, uni coursework and projects, or personal side projects - and when asked to write it up, log it, create or update its Notion page, add to its to-do, or record a bug. Triggers - "new feature", "start feature", "document this", "write this up", "log it to Notion", "update the page", "found a bug", "add to the todo", "make a page for this".
---

# Documenting work into Notion

Ibrahim keeps a Notion page for the things he works on. This skill decides
**where** a page goes and **what** it must contain.

> **These instructions are deliberately flexible and expected to change.**
> When Ibrahim asks for a different format, an extra section, a new context, or
> a different destination — edit these files in place. Nothing here is fixed.
> Say what you changed afterwards.

## Step 1 — work out which profile applies

Match on git remote first (most reliable), then on path. First match wins.

| Signal | Profile |
|---|---|
| git remote org is `Voxasa`, or path under `~/gSync/Dev/Hatif/` | `hatif` |
| path under `~/gSync/Uni/`, or the work is coursework/a university project | `uni` |
| git remote org is `ENG-Sukaiti`, or any other path under `~/gSync/Dev/` | `personal` |
| nothing matches | **ask him** which it is, then add a row here |

Resolve with real commands, not assumptions:

```sh
git -C <repo> remote get-url origin     # → org
git -C <repo> rev-parse --abbrev-ref HEAD
```

## Step 2 — read that profile

Read `profiles/<profile>.md` in this skill directory. It holds the Notion
destination, the page-title convention, and the required sections for that
context. **The profile is authoritative** — this file only routes.

Profiles available: `hatif`, `uni`, `personal`.

## Universal rules — all profiles

- **Verify from the repo, never from memory.** Branch names, file lists, and
  repo names come from git commands run at that moment.
- **Update, don't duplicate.** Search the destination for an existing page
  before creating one. If it exists, edit it.
- **Ask before inventing.** If the "why" behind a decision isn't clear from the
  code and the conversation, ask. A plausible-but-wrong rationale is worse than
  a blank one.
- **Never document secrets.** No tokens, keys, connection strings, `.env`
  contents, or customer data.
- **Use real Notion blocks**, not markdown pasted into a paragraph: code blocks
  with the language set, real to-do checkboxes, real tables, real callouts.
  The page should be pleasant to read in Notion.
- **No colours.** Leave headings, callouts, and tables at Notion's default
  colour. Do not set `color=` / `{color="..."}` on anything. Ibrahim asked for
  this explicitly — he will ask for a colour when he wants one. Icons, emoji,
  and structure carry the visual hierarchy instead.
- **Emoji on headings.** Prefix every `##` and `###` with one emoji chosen for
  what that section is about — Ibrahim reads them as indicators when scanning a
  long page. Same for the bold labels that head a grouped checklist. One emoji,
  never two, and pick a specific one over a generic one: 📦 for packaging, 💧
  for a hydration problem, 🧟 for a zombie process. This is on top of the page
  icon, which is still always set.
- **Say when you're writing to Notion.** Don't do it silently mid-task.
- **Expect custom extras.** He'll ask for per-item additions — an HTML page
  describing the feature, a diagram, a code block, API samples. Add them
  *after* the profile's required sections, which always stay and stay in order.

## Visual formatting — every element must earn its place

**Default to plain.** Headings, prose, lists. A page of clear paragraphs is a
good page. Reach for a visual element only when it does something prose cannot,
and when it does not, leave it out. Bloat is the failure mode here, not
plainness — a diagram that restates a list makes a page *worse*.

The test for every element: **remove it and re-read. If the page says the same
thing without it, it was decoration — leave it out.**

| Element | Use it when | Do NOT use it when |
|---|---|---|
| **Mermaid diagram** | Something moves through stages, or parts connect in a shape that isn't a straight line. A reader would otherwise have to re-read the paragraph to reconstruct the topology. | The thing is a sequence of steps (numbered list is better), a two-or-three-item hierarchy, or anything one sentence covers. **Max one or two per page.** |
| **Callout** | It changes what the reader *does*: a gotcha, a trap, a constraint that isn't obvious, a status line. | It is ordinary emphasis, or its content amounts to "this is important". Roughly one per major section, never two adjacent. |
| **Toggle (`<details>`)** | The content is genuinely optional — background, rationale, an aside many readers will skip. | The content is required reading. Never hide something the reader needs. |
| **Side-by-side callouts in columns** | Two to four genuinely parallel items of equal weight, being compared. | It is really just a list. A list is fine. |
| **Table** | Three or more rows across two or more real dimensions. | Two rows, or one dimension. Write a sentence. |
| **Table of contents** | The page has six or more `##` sections. | Anything shorter. |
| **Cover image** | A landmark page someone will return to repeatedly. | Routine pages. Most feature pages do not get one. |
| **Code block** | Any command, path, file tree, or output. | — Cheap and always correct. Use freely, and set the language. |
| **Page icon** | Always. One emoji, chosen to be recognisable at a glance in the sidebar. | — |

### Calibration — the two poles

- **Rich end:** *Claude ↔ Notion Auto-Documentation* (Dashboard root). It earned
  cover, ToC, two diagrams, several callouts and toggles because it is a
  long-lived reference explaining an unfamiliar concept with real topology, and
  it will be re-read many times.
- **Plain end:** a routine feature page — a heading, a few paragraphs, a
  checklist, a table of repos and branches. **No diagram, no cover, no ToC.**
  This is what most pages should look like.

Scale the effort to how long the page will live and how often it will be
re-read. Most pages sit at the plain end. If unsure, go plainer — Ibrahim will
ask for more.

### Bloat checks before saving

- Two visual elements adjacent with no prose between them → at least one is decoration.
- A diagram that could be a numbered list → make it a numbered list.
- A callout that only says something is important → delete it, or make the point in the sentence.
- More than two diagrams → you are almost certainly padding.

## Page id caching

Resolve destination pages by **searching** Notion, not by hardcoded URLs.
Cache what you find in `~/gSync/.claude-shared/notion-ids.json`:

```json
{ "hatif_features": "<page-id>", "uni_root": "<page-id>" }
```

Read that file first; only search when an id is missing or stale.

## Adding a new context later

When Ibrahim starts documenting a new kind of work:

1. Copy `profiles/personal.md` to `profiles/<name>.md` and edit it.
2. Add a routing row to the table in Step 1.
3. Nothing else. No bootstrap change, no per-repo file, no re-linking.
