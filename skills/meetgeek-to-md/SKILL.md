---
name: meetgeek-to-md
description: Convert a MeetGeek DOCX transcript export to a clean, well-formatted markdown file with corrected speaker attribution, agenda, and Key Takeaways. Use when given a .docx file exported from MeetGeek.
argument-hint: <path-to-docx>
allowed-tools: Bash Read Write
---

# MeetGeek DOCX → Markdown

Convert the MeetGeek DOCX file at `$ARGUMENTS` to a clean markdown transcript.

## Step 1: Extract text

Run this via Bash, substituting the actual file path:

```python
python3 -c "
import zipfile
from xml.etree import ElementTree as ET

with zipfile.ZipFile('DOCX_PATH') as z:
    xml = z.read('word/document.xml')

tree = ET.fromstring(xml)
ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
paragraphs = []
for para in tree.iter(f'{{{ns}}}p'):
    texts = []
    for t in para.iter(f'{{{ns}}}t'):
        if t.text:
            texts.append(t.text)
    paragraphs.append(''.join(texts))
print('\n'.join(paragraphs))
"
```

The output will be large — save it to a temp file and read from there.

## Step 2: Parse the MeetGeek structure

The raw text follows this pattern:

- **Line 1:** Title (e.g. "Jane Doe and John Wick")
- **Line 2:** "Metadata"
- **Line 3:** One long blob containing Title, Location, Date, Attendees, Link, and Agenda all concatenated
- **Line 4:** "MeetGeek Transcript"
- **Line 5:** The entire transcript as one long run-on paragraph

Parse out from the metadata blob:
- `Date:` → formatted as `YYYY-MM-DDTHH:MM:SSZ UTC`
- `Location:`
- `Attendees:`
- `Link:`
- `Agenda:` → everything from here to end of blob; split into individual agenda items. If no `Agenda:` field is present, skip the Agenda section entirely — do not fabricate agenda items.

Infer short display names for each participant from the Attendees field (e.g. "John Wick" → **John**, "Jane Doe" → **Jane**). Use these consistently throughout the output. If a participant appears as "Unknown User" in the transcript, infer their identity from context.

## Step 3: Fix speaker attribution

MeetGeek's raw transcript format:
```
SpeakerName - MM:SS text text SpeakerName - MM:SS text text
```

**Critical problem:** MeetGeek frequently splits mid-sentence across speaker labels. A new speaker label does not necessarily mean that speaker started talking — MeetGeek's voice detection switches mid-utterance constantly.

**Rules for reconstruction:**

1. If a speaker's section ends mid-sentence and the next speaker's section continues it grammatically, treat it as one speaker's utterance.
2. Trust meaning over raw attribution. If content clearly belongs to one participant (e.g. first-person statements about their own job search, their own health, their own dog), reassign it regardless of what MeetGeek says.
3. Short backchannels ("Yeah", "Right", "Okay", "Sure", "Totally") appearing mid-sentence in another speaker's flow are the *other* person — fold them in as natural conversation or omit.
4. When genuinely ambiguous, take the reading that produces the more coherent, complete sentence. When the override is uncertain (not obvious from context), add a CHECK comment (see Step 5).
5. When reassigning content from one speaker's block to another, use the timestamp from where that speaker *logically* began — not the DOCX block timestamp it was extracted from. If Jane's response is embedded in a John block labeled 03:07 but she clearly started at 03:55 (a later label in the same block), use 03:55.
6. When a closing question ("Does that help?", "Does that make sense?", "Are you with me?") appears at the start of a block attributed to the person being asked, treat it as the *other* speaker's question. Split as a separate turn and add a CHECK comment.

## Step 4: Format the output

```markdown
# [Title] — [Meeting Type]

## Metadata

- **Date:** ...
- **Location:** ...
- **Attendees:** ...
- **Link:** ...

---

## Agenda

- **[Item]** *(N min)* — description.

---

## Key Takeaways

- Bulleted summary of main points, decisions, and action items.

---

## Transcript

**Speaker** *(MM:SS)*
Text of utterance.

**Speaker** *(MM:SS)*
Text of utterance.

---

### [Section header when topic clearly shifts]

...
```

**Formatting rules:**
- Speaker header: `**Name** *(MM:SS)*`
- One blank line between speaker turns
- Add `---` + `### Header` when the conversation shifts to a new topic
- Merge consecutive paragraphs from the same speaker on the same topic into one block
- Clean up transcript noise: false starts, repeated fillers ("you know you know"), cut-off words — preserve meaning and voice, don't over-sanitize
- **Do not drop exchanges.** Within a turn, cleaning filler words and false starts is fine. But do not omit entire conversational blocks — including digressions, off-topic asides, pricing discussions, tooling decisions, and uncomfortable moments. If a block of conversation happened, it belongs in the transcript.

## Step 5: Inline annotation convention

Use HTML comments (invisible in rendered markdown, readable when editing) to flag two kinds of uncertainty:

**Uncertain attribution** — when you override DOCX speaker attribution with low confidence:
```markdown
<!-- CHECK: uncertain whether this is Jane or John — MeetGeek split mid-sentence -->
**Jane** *(29:09)*
Text of utterance.
```

**ASR word correction** — when you substitute a word that appears garbled by speech recognition. **No silent corrections.** Every substitution, no matter how obvious, requires the inline comment. The user cannot verify what was actually said without it.
```markdown
**Jane** *(04:26)*
He seems lethargic. <!-- ASR: original "empty" → corrected to "lethargic" — verify against audio -->
```

Confident overrides (e.g., "Unknown User" → an attendee whose identity is obvious from context) don't need a CHECK comment. The user may also add `<!-- CHECK: ... -->` comments directly in the file to flag lines for you to revisit on a subsequent pass.

## Step 6: Name and save the output file

Save to the same directory as the input DOCX. Derive the output filename from the meeting date found in the transcript's `Date:` field (parsed in Step 2), participant display names, and inferred meeting type.

**Date prefix:** `YYMMDD` derived from the `Date:` field in the transcript text (e.g. `2026-04-10T18:30:00Z` → `260410`). Do not use the input filename or filesystem metadata.

**Meeting type:** infer from context — MeetGeek title, agenda, or transcript content. Use 2–3 words max, lowercase, spaces replaced with hyphens. Examples: `coaching-session`, `interview`, `team-sync`, `kickoff`.

**Separator:** underscore `_` between each component.

| Date field in transcript | Participants | Inferred type | Output |
|--------------------------|--------------|---------------|--------|
| 2026-04-10T18:30:00Z | Jane Doe, John Wick | coaching-session | `260410_Jane+John_coaching-session.md` |
| 2025-12-03T19:00:00Z | Jane Doe, John Wick | team-sync | `251203_Jane+John_team-sync.md` |

General pattern: `[YYMMDD]_[Participant1]+[Participant2]_[meeting-type].md`

If a file with that name already exists, never overwrite it. Append `_2`, `_3`, etc. before the `.md` extension until a free name is found (e.g. `260410_Jane+John_coaching-session_2.md`).

## Step 7: Interactive uncertainty review

After saving, scan the output file for any `<!-- CHECK -->` or `<!-- ASR -->` comments. If any exist, use the AskUserQuestion tool to present them all in one structured question — numbered list, one item per flagged line, with enough context (timestamp, speaker, the flagged text) for the user to make a call. Example format:

> I flagged a few uncertainties in the transcript. Please review:
>
> 1. **42:04** — MeetGeek attributes "So is this making sense?" to Jane, but I assigned it to John (John had been speaking continuously). Keep as John, or revert to Jane?
> 2. **04:26** — ASR had "He seems empty" — I corrected to "lethargic." Confirm, or did you hear something else?

Update the file based on the user's responses and remove the resolved comments. Do not use AskUserQuestion if there are no flagged items.
