# Sources: where things are and how to dig

## Contents
- Search terms
- Telegram
- WhatsApp
- Blackboard
- Shared drives
- Files you get back

## Search terms

Search in every language the student's groups use, and with every spelling.
Add the config's `[search] terms` and the course's `aliases`.

| Looking for | English | Arabic |
|---|---|---|
| Past exams | olds, past exam, previous exam, midterm, mid, final, quiz, exam 2025 | اولدات، نماذج، اسئلة سابقة، اختبار سابق، ميد، الميد، فاينل، النهائي، كويز |
| Exam scope / format | scope, chapters, included, excluded, format, MCQ, true false, marks | المطلوب، المقرر، تحديد، محذوف، الدرجات، اسئلة، خيارات، صح وخطأ، سلايد |
| The lecturer speaking | Dr, the doctor said, professor, announced, important, will come | الدكتور، الدكتورة، د.، قال، يقول، مهم، بيجي، راح يجي، ركزوا |
| Material | slides, lecture, summary, notes, solution, answer key | سلايدات، محاضرة، ملخص، حل، الحل، اجابات |

Course codes get written several ways (`CS315`, `CS 315`, `cs-315`): try
them. Numbers may be in Arabic-Indic digits (`٤٦١` = 461).

## Telegram

The student's own account through `tg.py` (a user login, so it reads full
history; a bot can't). Public groups and channels can be read without
joining; private ones need joining or an invite link.

```bash
tg.py chats <filter>                 # joined chats whose title contains <filter>
tg.py find <query>                   # public groups/channels by name
tg.py pinned <chat>                  # always read these first
tg.py read <chat> --since 2026-09-01 --limit 3000 > <tmp>/chat.txt
tg.py read <forum group> --topic <N> # one course's topic in a forum group
tg.py search "<term>" [--chat <chat>] [--files] [--since <date>]
tg.py download <chat> <msg_id>... --to <tmp>
tg.py download <t.me message link> --to <tmp>
tg.py join <t.me link or @name>
```

How to dig:

1. **Find the groups.** Search joined chats and public ones by course code,
   English name, local name, and the level/major ("level 7", "CS"). Typical
   finds: this semester's level group, a per-course group or channel, a
   section group, a student's personal channel of summaries, and **last
   year's cohort group for the same course**, which holds a whole semester
   of slides, past papers, outlines and tips.
2. **Pinned messages first.** Resource lists, drive links and announcements
   live there.
3. **Follow the forks.** Groups get replaced every semester, channels split
   off, posts link into other cohorts' groups. `tg.py` prints hidden "Click
   here" link targets in `<...>` at the end of a line. Collect them with
   `grep -o 't.me/[^ >]*'` and follow the course-related ones. Topic links
   (`t.me/<group>/<topic>/<msg>`) point into a forum group: read the whole
   topic with `--topic`.
4. **Noisy general groups:** dump the semester to a file with `read --since`
   and grep for the course code and names, then read the replies after each
   hit (`grep -A8`). Blank lines in `read` output are join notices; skip them.
5. **Files:** `read <chat> --files` lists only messages with attachments.

## WhatsApp

Read through a WhatsApp MCP server linked to the student's phone as a
companion device (read-only). Tools: `whatsapp_status`, `list_chats`,
`search_messages`, `list_messages`, `get_message_context`, `download_media`,
`request_older_history`. Without MCP tools, call the same ones with
`sh <skill>/scripts/run wa.py <tool> key=value ...`.

- **Check `whatsapp_status` first.** The archive holds only what synced since
  linking (plus the history the phone shared then). If a chat looks cut off,
  `request_older_history` asks the phone for more (phone must be online).
- **Section group:** what the lecturer said in class, schedule changes, quiz
  arrangements. Lecturers sometimes run their own group with slides and
  samples.
- **Level/major groups:** mixed; past papers and tips land here.
- **Direct chats with friends:** where leaked exam breakdowns usually arrive.
- **Leak search:** over the week before the exam, search the course code,
  every spelling of its name, and the scope/format terms above. Look at the
  images posted near each hit: breakdowns are often screenshots.
- **Old media expires** on WhatsApp's servers after a few weeks (download
  fails). Look for the same file on Telegram.

## Blackboard

The official source. `bb.py` uses Blackboard's REST API with the student's
own session, so it sees exactly what they see.

```bash
bb.py courses                          # courseId, available (Yes/No), name
bb.py announcements <course>
bb.py tree <course>                    # id, kind (folder/file/page/assign/test), title
bb.py download <course> --to <tmp>     # every attachment, folders kept
bb.py download <course> <id>... --to <tmp>
bb.py get /learn/api/public/v1/...     # anything else, raw JSON
bb.py open <course>                    # the course in a logged-in browser window
```

- `<course>` can be any part of the course name or code.
- A course showing `No` in `courses` is closed to the student (403 on
  everything); say so, and get its files from Telegram, where students
  usually mirror them.
- Announcements are the most official scope there is. Read all of them, not
  just the latest.
- Some content is a "page" with text and no file: `bb.py get
  /learn/api/public/v1/courses/<courseId>/contents/<id>` shows its body.

## Shared drives

Many departments have a student-built Google Drive of past exams. If the
config lists one (`[[drive]]`) and the student has rclone set up:

```bash
rclone lsf -R --format "pst" --drive-root-folder-id <folderId> <remote>
rclone copy --drive-root-folder-id <folderId> <remote>"<sub/path>" <tmp>
rclone lsjson --drive-root-folder-id <folderId> <remote>   # ids, to drill down
```

- `--max-age` filters by upload date, not the exam's date: read the term
  on the cover page.
- No rclone? Give the student the folder link and say which subfolders to
  grab. Don't install things on their behalf.

## Files you get back

- `file <name>` (built in on macOS and Linux) tells the real type of a file
  with a wrong or missing extension.
- Filenames from chats carry invisible direction marks (U+200E, U+2068/9)
  and sometimes no extension. Check types with `file`, and rename everything;
  never match on the raw name.
- The same exam often arrives several times (a typed answer key, phone
  photos solved and unsolved). Compare cover pages before counting it twice.
- Answers are sometimes blanked out with white blobs before sharing.
- Student copies sometimes map each question to a lecture and slide. Keep
  those notes.
