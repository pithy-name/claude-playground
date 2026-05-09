# meetgeek-to-md

Converts a MeetGeek DOCX transcript export into a clean, readable markdown file. This is a Claude Code skill — invoking it via `/meetgeek-to-md` runs a multi-step automated process defined in [SKILL.md](SKILL.md).

## Usage

```
/meetgeek-to-md <path-to-docx>
```

Example:
```
/meetgeek-to-md "Meetings/Jane+Doe+and+John+Wick_sentences_2026-04-10T18_30_00Z.docx"
```

### Prerequisites

- Python 3 (used to extract text from the DOCX)
- The input must be a `.docx` file exported directly from MeetGeek

---

## Input format

This skill expects a `.docx` file exported directly from MeetGeek's transcript feature. The DOCX must follow MeetGeek's standard 5-line structure:

1. Title (e.g. "Jane Doe and John Wick")
2. The word "Metadata"
3. A single long blob containing: title, location, date, attendees, meeting link, and agenda — all concatenated
4. The words "MeetGeek Transcript"
5. The entire transcript as one long run-on paragraph, with speaker names and timestamps embedded inline

**Do not run this skill on other DOCX files** (homework documents, reference files, etc.) — the extraction logic assumes the MeetGeek format and will produce incorrect output on anything else.

### Known MeetGeek quirk: speaker misattribution

MeetGeek's voice detection frequently splits sentences mid-word and attributes fragments to the wrong speaker. This skill applies heuristics to reconstruct correct attribution — grammatical continuity, first-person context, and semantic coherence all take precedence over the raw speaker labels.

When attribution is genuinely ambiguous, the skill adds an inline `<!-- CHECK -->` comment so you can review it (see [Inline annotations](#inline-annotations) below).

### What if sections are missing?

- **No agenda found:** skill skips the Agenda section entirely — it does not fabricate agenda items.
- **Empty transcript:** skill will fail gracefully with no output written.

---

## What it produces

A markdown file saved to the same directory as the input DOCX, containing:

- **Meeting details** — date, location, attendees, meeting link
- **Agenda** — parsed from the MeetGeek metadata blob and formatted as a list
- **Key Takeaways** — bulleted synthesis of main points, decisions, and action items (generated, not extracted verbatim from transcript)
- **Transcript** — speaker turns with timestamps, organized under topic section headers

The transcript is not filtered or censored. All exchanges are preserved — including digressions, off-topic asides, and pricing or tooling discussions — because the full record has value.

---

## Output filename

The filename is derived from the meeting date, participant first names, and inferred meeting type:

```
YYMMDD_Participant1+Participant2_meeting-type.md
```

Examples:
| Date in transcript | Participants | Meeting type | Output |
|--------------------|--------------|--------------|--------|
| 2026-04-10T18:30:00Z | Jane Doe, John Wick | coaching-session | `260410_Jane+John_coaching-session.md` |
| 2025-12-03T19:00:00Z | Jane Doe, John Wick | team-sync | `251203_Jane+John_team-sync.md` |

If a file with the same name already exists, the skill appends `_2`, `_3`, etc. before `.md` rather than overwriting.

---

## Inline annotations

The output uses HTML comments (invisible in rendered markdown, readable when editing) to flag two kinds of uncertainty:

**Uncertain speaker attribution** — when the skill overrides MeetGeek's speaker labels with low confidence:
```markdown
<!-- CHECK: uncertain whether this is Jane or John — MeetGeek split mid-sentence -->
**Jane** *(29:09)*
Text of utterance.
```

**ASR word correction** — when the skill substitutes a word that appears garbled by speech recognition. Every substitution, no matter how obvious, is flagged — no silent corrections:
```markdown
**Jane** *(04:26)*
He seems lethargic. <!-- ASR: original "empty" → corrected to "lethargic" — verify against audio -->
```

After saving, the skill will surface all flagged items for your review and remove resolved comments once you respond. You can also add `<!-- CHECK: ... -->` annotations yourself anywhere in the output file to request a follow-up attribution pass.

---

## Future improvements

- **Format flexibility:** V1 assumes MeetGeek's exact 5-line DOCX structure. Future versions should detect and adapt to variations in export format (different MeetGeek versions, other meeting tools with similar output).
- **Partial structure handling:** gracefully skip or infer missing sections rather than failing silently.
- **Rename "Metadata" section:** the output currently uses "Metadata" as the section header for meeting details — inherited from MeetGeek's own label. This is ambiguous; a clearer name (e.g. "Meeting Details") would improve readability.
