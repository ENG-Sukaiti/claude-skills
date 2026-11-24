---
name: study-prep
description: Gathers what a university student needs to study a course, from their own Telegram, WhatsApp and Blackboard. Finds the course's groups and channels, pulls past exams ("olds"), slides and announcements into the course folder, picks out what the lecturer said matters (scope, exam format, leaked breakdowns), and reports what it found and where. Also watches a lecture recording or any video the student points to and reports anything important said in it. Use when the student says they are about to study a course or have an exam coming, e.g. "I'm going to study CS315, do the thing", "midterm tomorrow in MATH317", "get me ready for the final", "grab the olds for X", or "watch this video and tell me if anything important was said", even without the word "prep".
---

# Study prep

The student is about to study a course and wants everything in one place,
fast: this semester's material, past exams, and anything the lecturer said
about the exam. Your job is to gather it from the student's own accounts,
file it in their course folder, and tell them what you found. Don't write
study material (summaries, practice exams) unless asked.

Every command below runs a script from this skill's `scripts/` folder. Write
`<skill>` for the folder this file is in.

```bash
sh <skill>/scripts/run tg.py ...          # Telegram
sh <skill>/scripts/run bb.py ...          # Blackboard
sh <skill>/scripts/run wa.py ...          # WhatsApp, only if you have no WhatsApp MCP tools
sh <skill>/scripts/run pdf.py ...         # PDF text, metadata, page images
sh <skill>/scripts/run transcribe.py ...  # speech in a recording to text
sh <skill>/scripts/run frames.py ...      # what's on screen in a video
```

Always go through `run`. It works the same on macOS and Linux, and the
student doesn't need to install or know anything: the first time, it
installs `uv` by itself (no admin password; tell the student "installing a
small tool that runs the scripts, one time"), and `uv` fetches a recent
Python and each script's packages on first use, so a first run takes a
minute longer. Don't call the system `python3` (macOS ships 3.9, too old) or
system tools like `pdftotext`/`ffmpeg`, which most Macs don't have. Below,
`tg.py ...` is short for `sh <skill>/scripts/run tg.py ...`.

## Ground rules

- **Read-only.** Never post, react, vote, or mark anything read in any chat.
  Joining a group or channel to read it is fine unless the config says
  `join = false`.
- **Cite everything.** Every claim from a chat carries its link (`tg.py`
  prints a `t.me` link on every line) or, for WhatsApp, the chat name and
  date. Students don't take group chatter on trust; they want to check it.
- **Download into a fresh empty temp folder**, then rename into the course
  folder. Done means `ls` shows the file in place.
- **Never handle passwords.** Logins are things the student does (a browser
  window, a terminal prompt). Never ask for a password in chat, and never
  read the credential files.
- **One broken source never stops the run.** If a source isn't set up or its
  login expired, skip it, carry on with the rest, and say in the report what
  was skipped and the one command that fixes it.

## Workflow

```
- [ ] 0. Config and sources ready
- [ ] 1. Course pinned down
- [ ] 2. Telegram
- [ ] 3. WhatsApp
- [ ] 4. Blackboard
- [ ] 5. Other sources (shared drives, recordings)
- [ ] 6. Sorted and judged
- [ ] 7. Report
```

### 0. Config and sources

Look for `study-prep.toml` in the current folder or a parent, else
`~/.config/study-prep/study-prep.toml`. It holds the student's university,
Blackboard address and login method, their general groups, and their folder
layout. **If there's none, this is a first run: follow
[references/setup.md](references/setup.md)** to ask the student a few
questions and write it. Then check every source at once:

```bash
sh <skill>/scripts/run tg.py status
sh <skill>/scripts/run bb.py status
# WhatsApp: the whatsapp_status MCP tool, or: sh <skill>/scripts/run wa.py whatsapp_status
```

If Blackboard isn't logged in, run `bb.py login` in the background and tell
the student "a browser window opened on Blackboard, log in there as usual",
then carry on with Telegram while they do. Telegram's login needs codes typed
into a terminal, so the student runs that one themselves (setup.md).

### 1. The course

Work out the course code, its names (English and local spellings; students
misspell them, so search several), its course folder (match on the code; if
there's none, create one following the layout in the config), and, if the
student mentioned one, the exam and its date. Read the course folder first:
what's already there doesn't need fetching again.

### 2. Telegram

Where course material and past exams usually are. Details and search terms
in [references/sources.md](references/sources.md#telegram).

1. Find the groups: `tg.py chats <code>` and `tg.py chats <name>` for joined
   ones, `tg.py find <code>` for public ones, plus the general groups in the
   config. Last year's cohort group for the same course is often the richest.
2. Read each candidate's **pinned messages** first, then this semester's
   messages. Follow every invite link, `t.me/` mention and "Click here" link
   that looks like course material: resources scatter across groups,
   channels and forum topics.
3. Search for past exams and for what the lecturer said (terms in
   sources.md), and download the files you want.

### 3. WhatsApp

Section groups (what the lecturer said in class, schedule changes), level
groups, and direct chats with friends, where leaked exam breakdowns usually
arrive. Use the WhatsApp MCP tools if you have them (`search_messages`,
`list_messages`, `get_message_context`, `download_media`); otherwise the same
tools through `wa.py`. The archive only holds what has synced: check
`whatsapp_status` first and say if coverage is thin. Search terms in
[references/sources.md](references/sources.md#whatsapp).

### 4. Blackboard

The official source: slides, homework, and the lecturer's announcements.

```bash
bb.py courses                         # find the course; "No" = closed to the student
bb.py announcements <course>          # read every one: scope, exam dates, changes
bb.py tree <course>                   # what's there
bb.py download <course> --to <tmp>    # everything, folder structure kept
bb.py download <course> <id>... --to <tmp>   # or just some items/folders
```

Take this semester's slides, homework and quizzes, then rename into the
course folder. Old semesters' homework is usually set by someone else to a
different scope; skip it.

### 5. Other sources

- **Shared drives** from the config (`[[drive]]`): past exams students
  collected over the years. rclone recipe in sources.md.
- **Lecture recordings.** When an exam is within a week, the last lecture
  before it often has the lecturer talking about the exam. Transcribe it (see
  "A video" below) if one exists. Otherwise skip; it's slow.

### 6. Sort and judge

- Name past exams `Past <Midterm|Final|Quiz N> (<term>, <year>).pdf`, newest
  first. Put the same exam's copies (typed key, phone photos, solved and
  unsolved) together; they're one exam, not three.
- Read each one: `pdf.py info` (pages with a text layer, author, dates),
  then `pdf.py text` for typed PDFs. Scans and phone photos have no text
  layer: `pdf.py render <file> --to <tmp>` and look at the page images
  yourself (OCR does badly on angled phone photos). Save the text to the
  course's OCR folder so nobody redoes it.
- Weigh every past paper and every claim about the exam using
  [references/judging.md](references/judging.md): official beats leak beats
  rumour; a paper's age and setter decide its weight.
- If the student named an exam with a big scope, cut it down to the topics
  that actually get examined (judging.md, "Topic list").

### 7. Report

Answer in chat, then save the same text as `Study prep <YYYY-MM-DD>.md` in
the course's notes folder. Lead with what matters, keep it short, link every
file (absolute path in angle brackets, since names have spaces:
`[Midterm 2025](</home/.../Past Exams/Past Midterm (Fall, 2025).pdf>)`) and
every message.

```
## <Course> — what I gathered

**Heads up:** <the one or two things that matter most: a leaked breakdown,
the lecturer's scope, an exam date change. Skip if nothing stands out.>

**Past exams:** <N> papers, <newest>-<oldest>.
- <M> from <Telegram group> (<links>), <K> from <WhatsApp chat>, <J> from the shared drive.
- Strongest: <paper>, because <same setter / last semester>.

**What the lecturer said:** (official first, then leaks, then rumour)
- <quote or close paraphrase> — <source link, date>

**Blackboard:** <N> files downloaded (<what>), <N> announcements read; <the
ones that matter, one line each>.

**What to focus on:** <only if there's an exam: the topic list or the scope,
short.>

**Couldn't get:** <skipped sources with the fix command, files that wouldn't
download, groups that need an invite.>
```

Say each fact once. State confidence in a word ("confirmed by the lecturer",
"leak", "rumour") rather than a paragraph. When two sources disagree, show
both side by side instead of picking one.

## A video ("watch this and tell me if anything important was said")

The student points at a recording: a file, a Telegram link, a WhatsApp video.

1. Get it into a temp folder: a file path as is; a `t.me` link with
   `tg.py download <link> --to <tmp>`; WhatsApp with `download_media`.
2. Transcribe:
   `transcribe.py <video> <tmp>/talk.txt --language <code>`.
   It runs Whisper locally (no cloud, no key; the first run downloads the
   model), in 10-minute chunks in parallel, and writes the first chunk to
   `talk.txt.part0` as soon as it's done. Roughly 50 minutes for an hour of
   audio on a laptop CPU with the default `medium` model; `--model small` is
   much faster and fine for clear English; `--device cuda` on an NVIDIA GPU.
   Run it in the background and read `part0` first: exam talk is usually at
   the start or the very end.
3. Things written or shown on screen: grab frames with
   `frames.py <video> --to <tmp> --at 12:40`, or first a contact sheet to
   find the moment: `frames.py <video> --to <tmp> --every 240 --sheet`.
4. Report what matters for the exam with timestamps (`[12:40]`): scope,
   what's in or out, question format, "this will come up", hints, deadlines.
   Quote the lecturer's own words, translated if needed. If nothing
   important was said, say so in one line. Save the transcript to the
   course's OCR folder as `<video name> (transcript).txt`.
