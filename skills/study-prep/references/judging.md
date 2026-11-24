# Judging what you found

## Contents
- Ranking claims about the exam
- Leaks
- Weighing past papers
- Topic list
- Question types

## Ranking claims about the exam

Rank by how close the source is to whoever writes the paper:

1. **Official.** A Blackboard announcement, the lecturer's own message (in a
   section group, forwarded by the student), the syllabus, or the lecturer
   talking about the exam in a recorded lecture.
2. **Leak.** A breakdown of the actual paper (see below).
3. **Student consensus** in the groups. Report it as hearsay.

An official scope and a leak can both exist: the scope says "chapters 1-4",
the leak says which slides. Keep both. State the final scope as lectures and
slide ranges, each with its source. When sources disagree (one says 7-8
true/false questions, another 5-6), show both side by side.

When the course has several sections, lecturers often write one shared
paper, each contributing a part, so the exam isn't only the student's own
lecturer's. A scope from another section's lecturer still counts.

## Leaks

Before many exams, a breakdown of the paper reaches students: the number of
questions, their type, the marks, sometimes the exact topics or slide
numbers. It usually starts with one section (a lecturer tells their own
students) and spreads through friends on WhatsApp, often as a screenshot.
When one exists it tends to match the real exam closely, so search for one
every time (terms in sources.md). Most exams have none. Quote a leak in full,
with who sent it and when. Examples of the shape:

> 1) MCQ: 10 questions, 5 marks
> 2) Short answer: model selection, a calculation, risk types, 5 marks
> 3) Lecture 7, slide 17: 10 marks

> Q1 multiple choice, 10 marks. Q2 the graphical method, 5 marks, max or min.
> Q3 simplex, 10 marks, usually maximisation.

## Weighing past papers

Most past papers are student-made: rebuilt from memory or photographed in
the exam hall. Some are the setter's own file with the model answer, shared
after the exam. Check with `pdf.py info`: an Author matching the lecturer and a
CreationDate a few days before the exam mean the setter's original, so its
answer key is how the setter marks, even where it looks wrong. A Word file's
Title is often left over from an old template; ignore it.

Two things set a paper's weight:

- **Age.** Last semester is worth much more than five years ago. Lectures and
  exam patterns change. An old paper isn't invalid, just weaker; if it's all
  there is, judge it on its content.
- **Same setter.** If whoever wrote it still sets the exam, the style rarely
  changes, so this can outweigh age: a five-year-old paper from the same
  coordinator is still strong. A new coordinator weakens even last
  semester's paper.

So find out who set each paper (its header, the answer key, or group talk
like "the coordinator is new"), and compare with this semester's lecturer
and coordinator; name both. Get the student's lecturer from Blackboard or
their section group. Check each paper's scope against this semester's
lectures. Check student answer keys against the slides and list the mistakes
you find. Student reconstructions also go wrong: duplicated questions,
tables with missing rows, a wrong formula on a cheat sheet.

## Topic list

Only when the student named an exam, and no leak already names the topics.

A scope like "lectures 1-7" can be 140 slides of uneven weight. Reduce it to
a short list of named topics the student can each look up, watch a ~20-minute
explanation of, practise, and be done. For each topic:

- the standard English name, as they'd type it into YouTube
  ("Newton-Raphson method", not "Newton's method, x1 and x2");
- priority: **high** (in every recent paper, or the lecturer said it's in),
  **medium** (some papers, or hinted), **low** (rare but in scope). Mention
  marks only when they tell the student something ("always a 5-mark
  question");
- what it takes: a formula to apply, or a method that needs real practice;
- where it is: file and PDF page in the course folder (the PDF page is what
  they type into the viewer; the number printed on the slide can differ);
- the evidence: which papers, what the lecturer said.

High priority first. If one topic builds on another, say what order to study
them in. Topics not worth the time go in one line after the list. If the
course doesn't split into topics this way (a reading or essay course), say so
and skip the list.

## Question types

The kind of paper decides the kind of studying: all MCQ, true/false,
problems, short answer, essay, code output. Use the same source order:
official, then leak, then past papers. From past papers, a small table of
paper x question type x marks, with how much each paper should count.
