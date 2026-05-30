# claude-code-timeline

An interactive, offline timeline viewer for Claude Code session transcripts. Added here for experimentation.

**Source:** [simonw/tools](https://github.com/simonw/tools/blob/c8e1d009bee9093ea67250cc47e5783ceb01fc62/claude-code-timeline.html) on GitHub.

**License:** Apache-2.0. The `LICENSE` file here is the upstream copy, carried over verbatim.

### Usage

Open the file directly in a browser — no server needed. Load a session file via:

- **File picker or drag-and-drop** — select a `.jsonl` file
- **Paste** — paste raw JSONL content
- **URL fetch** — provide a CORS-enabled URL to a `.jsonl` file

Sessions live at `~/.claude/projects/`.

### What you can do

- Browse every message, tool call, and tool result in a session as a scrollable timeline
- Filter by role (`user` / `assistant`), message type, and content type
- Search across message text, tool names, and working directories
- Toggle between local timezone and UTC
- Click into individual events for full detail, including file snapshots with formatted previews of text, code blocks, and embedded images
- Export any event's raw data as JSON
