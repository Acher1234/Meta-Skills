# fathom — Fathom meeting fetcher

Fetches meetings, transcripts, AI summaries, and action items from the Fathom API via a bundled Python CLI. Shared code under Meta-Skills; per-workspace `.env` for `FATHOM_API_KEY`.

## Credentials

`FATHOM_API_KEY` lives next to the registered skill (`$CURRENT_SKILL_DIRECTORY`), resolved via `scripts/skill_env.py` → `SkillCred("fathom", [".env"])`.

```bash
export CURRENT_SKILL_DIRECTORY="/path/to/registered/fathom"
python scripts/fetch.py --list
```

## Usage

```bash
python scripts/fetch.py --list
python scripts/fetch.py --today
python scripts/fetch.py --since 2025-01-01
python scripts/fetch.py --id abc123
python scripts/fetch.py --id abc123 --download-video
```

## Files

| File | Role |
|------|------|
| `SKILL.md` | Skill instructions for agents |
| `scripts/fetch.py` | CLI (list / get / today / since) |
| `scripts/utils.py` | Fathom API client + markdown formatting |
| `scripts/skill_env.py` | SkillCred + `SkillEnv` (`FATHOM_API_KEY`) |
| `scripts/download_video.py` | HLS → MP4 downloader (ffmpeg) |
| `.env.example` | Template for `FATHOM_API_KEY` |
| `requirements.txt` | Python dependencies |
| `ORIGIN.md` | Upstream source |
