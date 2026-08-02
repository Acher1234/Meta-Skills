---
name: fathom
description: >-
  Fetch meetings, transcripts, AI summaries, and action items from the Fathom
  API via the bundled Python CLI (scripts/fetch.py). Shared CLI code; per-
  workspace .env resolved by location. Use when the user asks to get Fathom
  recordings, sync meeting transcripts, fetch recent calls, or invokes
  /fathom_*.
disable-model-invocation: true
---

# fathom — Fathom meeting fetcher

Fetches meeting data directly from the Fathom API: transcripts, AI summaries, action items, participant info, and (optionally) the video recording.

Shared CLI under Meta-Skills; per-workspace `.env` for `FATHOM_API_KEY` (see [`ORIGIN.md`](ORIGIN.md) for upstream source).

## When to use

Trigger phrases: "get my Fathom meetings", "sync meeting transcripts", "fetch today's calls", "download Fathom recording", `/fathom_list`, `/fathom_today`, `/fathom_since`, `/fathom_get`.

## Working directory (shared code)

The CLI code (`scripts/`) is shared once per machine — nothing is re-cloned per project. Prefer (in order):

| Target | Path |
|--------|------|
| **Canonical (after Meta-Skills clone)** | `~/.meta-skills/skills/fathom` |
| **Cursor** (full tree install) | `~/.cursor/skills/fathom` |
| **Claude Code** (full tree install) | `~/.claude/skills/fathom` |
| **Hermes — all profiles** | `~/.hermes/skills/fathom` |
| **Hermes — this profile** | `${HERMES_HOME}/skills/fathom` |

Always `cd` into the working directory before running, and use relative paths: `python scripts/fetch.py …`. Python deps use the shared venv (`~/.meta-skills/.venv/bin/python`); install them once with `bash ~/.meta-skills/install.sh pip init .` from the skill folder (or `pip install -r requirements.txt`).

## Credentials — `.env` resolved by location

The `.env` (holding `FATHOM_API_KEY`) is **not shared** — it lives next to the *registered* skill / workspace so each Cursor project or Hermes profile can use a different Fathom account. `scripts/utils.py` resolves it through `common/skill_home.py` (`SkillHome("fathom").env_path()`).

| Scope | `.env` path |
|-------|-------------|
| **Cursor — this project** | `./.cursor/skills/fathom/.env` |
| **Cursor — global** | `~/.cursor/skills/fathom/.env` |
| **Claude Code — this project** | `./.claude/skills/fathom/.env` |
| **Claude Code — global** | `~/.claude/skills/fathom/.env` |
| **Workspace root** (fallback) | `./.env` (must contain `FATHOM_*`) |
| **Hermes — this profile** | `${HERMES_HOME}/skills/fathom/.env` |
| **Override** | `FATHOM_ENV_PATH=/path/to/.env` |

Resolution order: registered skill dir → workspace `./.env` → global tool skill → Hermes profile. If `common/skill_home.py` is not importable (standalone use), the scripts fall back to a local `.env` next to `scripts/` or the skill root.

**Set it up** (copy the template into the chosen destination and fill it in):

```bash
cp .env.example ~/.cursor/skills/fathom/.env   # or your workspace / Hermes path
# edit the file: FATHOM_API_KEY=...
```

Show which `.env` is resolved from the current location:

```bash
python3 scripts/_skill_home.py   # prints the resolved .env path
```

## Usage

If you `cd` into the shared library (or a global install) to run, the code can no
longer see your project's `.env` via the cwd. **Export `CURRENT_SKILL_DIRECTORY`
to the registered skill dir** (the one that holds `.env`) before running —
`SkillCred` uses it to resolve credentials (falls back to the process cwd if unset).

```bash
export CURRENT_SKILL_DIRECTORY="$PWD/.cursor/skills/fathom"  # or your install path
cd ~/.meta-skills/skills/fathom
python scripts/fetch.py [options]
```

### Commands

| Command | Description |
|---------|-------------|
| `--list` | List recent meetings with IDs |
| `--id <recording_id>` | Fetch specific meeting by recording ID |
| `--today` | Fetch all meetings from today |
| `--since <YYYY-MM-DD>` | Fetch meetings since date |

### Options

| Option | Description |
|--------|-------------|
| `--analyze` | Run transcript-analyzer on fetched meetings |
| `--download-video` | Download video recording (requires ffmpeg) |
| `--output <dir>` / `-o` | Output directory (default: `<skill-location>/meetings`, created if missing) |
| `--limit <n>` | Max meetings to list (default: 10) |

## Slash commands

| Slash | CLI | Description |
|-------|-----|-------------|
| `/fathom_list` | `python scripts/fetch.py --list` | List recent meetings |
| `/fathom_today` | `python scripts/fetch.py --today` | Fetch today's meetings |
| `/fathom_since` | `python scripts/fetch.py --since YYYY-MM-DD` | Fetch since a date |
| `/fathom_get` | `python scripts/fetch.py --id RECORDING_ID` | Fetch a specific meeting |
| `/fathom_env` | `python scripts/_skill_home.py` | Print the resolved `.env` path |

## Examples

```bash
# List recent meetings
python scripts/fetch.py --list

# Fetch today's meetings
python scripts/fetch.py --today

# Fetch and analyze
python scripts/fetch.py --today --analyze

# Fetch since a date
python scripts/fetch.py --since 2025-01-01

# Fetch a specific meeting
python scripts/fetch.py --id abc123def456

# Download the video with the meeting
python scripts/fetch.py --id abc123def456 --download-video
```

## Output format

Each meeting is saved as markdown with YAML frontmatter:

```markdown
---
fathom_id: <id>
title: "Meeting Title"
date: YYYY-MM-DD
participants: [list]
duration: HH:MM
fathom_url: <url>
share_url: <url>
---

# Meeting Title

## Summary
{AI-generated summary from Fathom}

## Action Items
- [ ] Item 1 (@assignee)
- [ ] Item 2

## Transcript
**Speaker Name**: What they said...
```

File naming: `YYYYMMDD-meeting-title-slug.md` (e.g. `20250106-weekly-standup.md`).

## Prerequisites

- Python deps (shared venv): `bash install.sh pip init fathom` — installs `requests` + `python-dotenv`.
- Video download (optional): `ffmpeg` / `ffprobe` on PATH (`brew install ffmpeg` on macOS, `apt install ffmpeg` on Linux).

## Integration

- **transcript-analyzer**: `--analyze` runs the analyzer on fetched transcripts (if the skill is installed at `~/.claude/skills/transcript-analyzer`).
- **download_video.py**: `--download-video` downloads the recording (HLS → MP4), validates with `ffprobe`, and retries up to 3 times. Videos are saved as `.mp4` next to the meeting markdown.

## Files

| File | Role |
|------|------|
| `SKILL.md` | This file |
| `scripts/fetch.py` | CLI entrypoint (list / get / today / since) |
| `scripts/utils.py` | Fathom API client + markdown formatting; loads `.env` via shared `common/skill_home.py` |
| `scripts/download_video.py` | HLS → MP4 downloader (ffmpeg) |
| `scripts/_skill_home.py` | Resolves shared lib + per-workspace `.env`; prints the `.env` path when run |
| `.env.example` | Template for `FATHOM_API_KEY` |
| `ORIGIN.md` | Upstream source |
| `requirements.txt` | Python dependencies |

## Notes

- Never commit the real `.env` or `FATHOM_API_KEY`. One Fathom account per workspace is the intended setup.
- API base: `https://api.fathom.ai/external/v1` (rate limited ~60/min; the client self-throttles).
