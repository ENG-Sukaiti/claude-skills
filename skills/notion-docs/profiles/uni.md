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
