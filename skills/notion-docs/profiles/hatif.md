# Profile: hatif (work)

## Destination

```
Dashboard → Work → Hatif → Features → <Feature Name>
                                       └── Bugs   (sub-page)
```

Resolve `Features` by searching Notion under the Hatif page. Cache the id as
`hatif_features` in `notion-ids.json`.

## Page title

Exactly the feature name. No prefixes, no dates, no ticket numbers unless asked.

## Required sections — in this order, every time

1. **Description** — what the feature does, why it was needed, who it's for.
   Two to five sentences. Written so he can read it in six months and recover
   the context — not a restatement of the title.

2. **Approach** — the design decision actually taken, and briefly what was
   rejected and why. The highest-value section. If the approach changed
   mid-implementation, record the change, not just where it landed.

3. **To-do** — a Notion to-do checklist tracking where the work stands, so he
   can resume after a break. Keep it current: tick items as they land, add
   newly discovered work. This is the resume point.

4. **Repos & branches** — the most important section. Every repo the feature
   touched and the branch created in each:

   | Repo | Branch | Notes |
   |------|--------|-------|
   | Backend | `feat/xyz` | API + migration |
   | voxa-dashboard | `feat/xyz-ui` | settings screen |

   From git, never from memory. Three repos touched → three rows.

5. **Files added** — every *new* file the feature introduced, with a one-line
   purpose each. New files only; modified files are noise unless he asks.
   `git -C <repo> status --porcelain` for uncommitted,
   `git -C <repo> diff --name-status <base>...HEAD | grep '^A'` for committed.

6. **Bugs** — a sub-page named `Bugs` under the feature page: a running list of
   bugs in this feature. Each entry: what happens, how to reproduce, status
   (open / fixed). Create the sub-page even when empty, so the first bug has
   somewhere to go.

## Scope

Repos under `~/gSync/Dev/Hatif/` — currently `Backend`, `voxa-dashboard`,
`voxa-mobile` — and any repo with a `Voxasa` remote. This list will grow; any
new repo appearing there is in scope automatically. Never require this list to
be updated before documenting a new repo.
