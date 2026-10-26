# Profile: uni

## Destination

Under `Dashboard` there is a `## 🎓 Uni` section holding one hub page, `🎓 Uni`
(cached `uni_hub`). Everything university lives inside it:

```
Dashboard → 🎓 Uni → 📚 Years  → 📘 Sophomore Year → Level 5 / Level 6 (KFUPM) → <Course> → Lab → Lab N
                                → 📗 Junior Year    → 7️⃣ Level 7 (semester dashboard)
                                                       └── 🗄️ Behind the scenes → Courses · Tasks · Exams · Notes · Study log
                   → 🤝 Clubs  → 🟦 GDG → <Area or Feature>
```

- **Coursework** goes under the current year page, then the current level.
  Year pages: `uni_sophomore`, `uni_junior` (cached in `notion-ids.json`).
  A new academic year gets a new year page under `## 📚 Years` on the hub,
  with a `📙`-style book icon. Past years are left as they are.
- **The current level page is a semester dashboard, not a list of sub-pages.**
  Since 2026-10-26, `uni_level7` holds: a summary callout, course links,
  heads-up notes, a colour-coded weekly timetable, then linked views of five
  databases. The databases themselves live in its `🗄️ Behind the scenes`
  sub-page. Never add plain sub-pages to the level page; add rows instead:
  | Database | Cached as | A row is |
  |---|---|---|
  | `Courses` | `uni_l7_courses` | one course. The course page *is* the course notebook (Page tab); its Tasks/Exams/Notes/Study tabs fill from relations. Rollups give Progress, Grade so far, Open tasks, Exams left, Study hours. |
  | `Tasks` | `uni_l7_tasks` | an assignment, lab report, quiz, study to-do. Set `Course`, `Due`, `Type`; `Weight` + `Score` feed the grade. |
  | `Exams` | `uni_l7_exams` | a midterm, final or quiz. `When` is a datetime in Asia/Riyadh. |
  | `Notes` | `uni_l7_notes` | lecture/lab notes, summaries, cheat sheets. |
  | `Study log` | `uni_l7_study` | one study session, in minutes. |
  Coursework write-ups (an assignment or lab) become a `Notes` or `Tasks` row
  linked to its course, with the required sections below as the row's body.
  Existing per-course sub-pages such as the CS341 `Lab` page stay inside the
  course page. Course numbers follow the uni portal: الرسم بالحاسب (graphics,
  OpenGL labs) is **CS341**, not CS342 — CS342 is Visual Programming.
  When a new semester starts, build the same dashboard for it rather than a
  bare level page. Colours avoid red-vs-green meaning (he is colourblind).
- **GDG club work** — the scores platform, its three repos, anything for the
  club rather than for a grade — goes under `GDG`, cached as `gdg`, which sits
  under `## 🤝 Clubs` on the hub. Confirmed 2026-09-13, moved 2026-10-14.

`GDG` is a **hub page and must stay one** — never add a page directly to it.
It has four sections, and everything goes in one of them:

| Sub-hub | Cached as | Holds |
|---|---|---|
| `🏛️ Architecture` | `gdg_architecture` | How the system works *today*. Reference docs kept current with `main`. |
| `✨ Features` | `gdg_features` | One page per feature — proposed, in progress or shipped, incl. the thinking and the open questions. |
| `🛠️ Improvements` | `gdg_improvements` | One page per improvement — performance, refactors, UX polish, tech-debt paydown. Making an existing thing better, not a new feature. Added 2026-09-16. |
| `🐛 Incidents` | `gdg_incidents` | One page per production incident — what the user saw, the exact log line and digest/request id, root cause, fix (PR), and how to find it faster next time. Title by symptom, not by fix. Added 2026-09-21. |

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

Local material lives under `<vault>/Uni/` (`Freshmen`, `Sophomore`, `PYP`);
GDG code lives under `<vault>/Dev/GDG/`.

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
