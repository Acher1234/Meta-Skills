# fathom — Fathom meeting fetcher

Fetches meetings, transcripts, AI summaries, and action items from the Fathom API via a bundled Python CLI. Shared code under Meta-Skills; per-workspace `.env` for `FATHOM_API_KEY`.


## Credentials — `.env` by location

`FATHOM_API_KEY` lives next to the registered skill (not shared), under `$CURRENT_SKILL_DIRECTORY`, resolved via `common.skill_cred` (`SkillCred("fathom", [".env"])`).

## Usage

```bash
python scripts/fetch.py --list                 # recent meetings
python scripts/fetch.py --today                # today's meetings
python scripts/fetch.py --since 2025-01-01     # since a date
python scripts/fetch.py --id abc123            # specific meeting
python scripts/fetch.py --id abc123 --download-video
```

## Files

| File | Role |
|------|------|
| `SKILL.md` | Skill instructions for agents |
| `scripts/fetch.py` | CLI (list / get / today / since) |
| `scripts/utils.py` | Fathom API client + markdown formatting (loads `.env` via `SkillCred`) |
| `scripts/download_video.py` | HLS → MP4 downloader (ffmpeg) |
| `scripts/_skill_home.py` | Thin wrapper around `SkillCred` / `.env` path |
| `.env.example` | Template for `FATHOM_API_KEY` |
| `requirements.txt` | Python dependencies |
| `ORIGIN.md` | Upstream source |
