# pc-report

Monitoring report for a host (Linux, macOS, or Windows).

French version: [`README-FR.md`](README-FR.md)

## Description

Produces a summary of the past day: CPU, RAM, disk, and top processes (via `sysstat`/`sar` on Linux; platform-specific scripts on macOS and Windows). The report can be delivered automatically at **07:00** on Telegram via a Hermes cron job.

## Layout

Scripts are split by language:

- `FR/` — French versions (`pc-daily-report.sh`, `pc-daily-report-mac.sh`, `pc-daily-report.ps1`)
- `en/` — English versions (same filenames)

## Usage

```bash
# Direct run (English / Linux)
./en/pc-daily-report.sh

# French version
./FR/pc-daily-report.sh

# macOS: ./en/pc-daily-report-mac.sh   |  Windows: pwsh -File ./en/pc-daily-report.ps1

# Via Hermes cron job (no_agent mode — delivered as-is)
cronjob action=create \
  name="PC report" \
  schedule="0 7 * * *" \
  script="en/pc-daily-report.sh" \
  no_agent=true \
  deliver=origin
```

## Sample output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 PC REPORT — kleinplex
  2026-06-29
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱ UPTIME & LOAD
up 11:05,  3 users,  load average: 0.69, 0.63, 0.57

── 🖥 CPU ──
▸ Average — User: 4.9% | System: 1.0% | IOWait: 0.0% | Idle: 94.1%
▸ Top 3 CPU peaks: ...

── 💾 RAM ──
▸ Average usage: 7.0%  ...
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ End of report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Dependencies

See [`dependencies.md`](dependencies.md) for the full dependency list.

## Active cron job

- **Schedule:** `0 7 * * *` (every day at 07:00)
- **Mode:** `no_agent` (plain script, no LLM)
