# Profile: hatif (work)

## Destination

```
Dashboard → Work → Hatif → Features → <Feature Name>
                                       ├── 🧭 Plan
                                       ├── 🛠️ Implementation
                                       ├── 🐛 Bugs
                                       └── 🗂️ History
```

Resolve `Features` by searching Notion under the Hatif page. Cache the id as
`hatif_features` in `notion-ids.json`, and cache each feature root and its
sub-pages too (`hatif_<feature>`, `hatif_<feature>_plan`, …).

## Page title

Exactly the feature name. No prefixes, no dates, no ticket numbers unless asked.

## Layout — a parent page with sub-pages

Every feature is a parent page (see *Page layout* in `SKILL.md`, changed on
28 Sep 2026). Nothing long lives on the root.

**Feature root, in this order:**

1. **Description** — what the feature does, why it was needed, who it's for.
   Two to five sentences, written so he can recover the context in six months.
2. **Status callout** — dated; shippable or not, and what blocks it; open PRs.
3. **To-do** — open items only, as real to-do checkboxes. The resume point.
   Finished items move to History.
4. **Repos & branches** — every repo touched and the branch in each, from git,
   never from memory. Active branches only; retired ones go to History.

   | Repo | Branch | Notes |
   |------|--------|-------|
   | Backend | `feat/xyz` | API + migration |

5. **Sub-page links** — Plan, Implementation, Bugs, History, and any extras.

**🧭 Plan** — the approach actually taken, what was rejected and why, and the
open design questions still blocking the work. The highest-value page. If the
approach changed mid-way, record the change, not just where it landed.

**🛠️ Implementation** — what was built in each repo (endpoints, key classes),
**files added** (new files only, one line each —
`git -C <repo> diff --name-status <base>...HEAD | grep '^A'`, plus
`git status --porcelain` for uncommitted), and open review findings.

**🐛 Bugs** — created even when empty. Each bug is its own sub-page (see
`SKILL.md`). Exception: a feature under a project root (e.g. *Desktop app*)
uses that project's Bugs page.

**🗂️ History** — finished to-dos, retired branches, earlier attempts.

**Once a feature grows into a project** — several features, runbooks, reference
material — restructure it to the project layout in `SKILL.md`. *Desktop app*
is the worked example.

## Scope

Repos under `<vault>/Dev/Hatif/` — currently `Backend`, `voxa-dashboard`,
`voxa-mobile` — and any repo with a `Voxasa` remote. This list will grow; any
new repo appearing there is in scope automatically. Never require this list to
be updated before documenting a new repo.
