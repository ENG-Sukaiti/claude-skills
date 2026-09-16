# Profile: uni

## Destination

Under `Dashboard` there is a `## 🎓 Uni` section holding two pages:

```
Dashboard → 🎓 Uni → 🎓 Sophomore Year → Level 5 / Level 6 (KFUPM) → <Course or Assignment>
Dashboard → 🎓 Uni → 🟦 GDG → <Area or Feature>
```

- **Coursework** goes under the current level page inside `Sophomore Year`.
  Cached as `uni_root` (= Sophomore Year) in `notion-ids.json`.
- **GDG club work** — the scores platform, its three repos, anything for the
  club rather than for a grade — goes under `GDG`, cached as `gdg`.
  Confirmed 2026-09-13.

`GDG` is a **hub page and must stay one** — never add a page directly to it.
It has three sections, and everything goes in one of them:

| Sub-hub | Cached as | Holds |
|---|---|---|
| `🏛️ Architecture` | `gdg_architecture` | How the system works *today*. Reference docs kept current with `main`. |
| `✨ Features` | `gdg_features` | One page per feature — proposed, in progress or shipped, incl. the thinking and the open questions. |
| `🛠️ Improvements` | `gdg_improvements` | One page per improvement — performance, refactors, UX polish, tech-debt paydown. Making an existing thing better, not a new feature. Added 2026-09-16. |

If a new GDG page is neither, ask him where it should live and add a row here.
Confirmed 2026-09-14.

Inside Architecture there is a second kind of doc: `🚶 Feature Walkthroughs`
(cached `gdg_walkthroughs`) — one page per admin feature, walked click → DB
with code snippets, branching to shared-service pages under `🔀 Branches`
(cached `gdg_walkthrough_branches`). Convention: a `🔀` callout reading
**Branch → [page]** — one line on what it does here — *Come back at step N.*
A new admin feature gets a walkthrough page there; a new shared service gets a
branch page. He asked for these to stay simple — no "you already know the
system" tone. Added 2026-09-16.

Local material lives under `~/gSync/Uni/` (`Freshmen`, `Sophomore`, `PYP`);
GDG code lives under `~/gSync/Dev/GDG/`.

## Page title

The project or assignment name. Prefix with the course code when there is one,
e.g. `CSE332 — AVL Tree Visualiser`.

## Required sections — starting point, refine with use

1. **What it is** — the assignment or project, in two or three sentences, plus
   the course and what's actually being asked for.
2. **Approach** — how he decided to tackle it, and what he rejected.
3. **To-do** — checklist of remaining work. Include the **due date** if known.
4. **Notes & gotchas** — things learned the hard way, worth having at exam time.
5. **Files** — new files created, with a one-line purpose each. Skip the
   repos/branches table unless the project is actually under git.

Coursework is often not a git repo. When it isn't, skip git-derived sections
rather than fabricating them, and list files from the filesystem instead.
