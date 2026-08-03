# pc-report

Rapport de monitoring pour une machine (Linux, macOS ou Windows).

## Description

Produit un résumé de la journée écoulée : CPU, RAM, disque, et top processus (`sysstat`/`sar` sous Linux ; scripts spécifiques sous macOS et Windows). Le rapport peut être livré automatiquement à **7h00** sur Telegram via un cron job Hermes.

## Organisation

Les scripts sont séparés par langue :

- `FR/` — versions françaises (`pc-daily-report.sh`, `pc-daily-report-mac.sh`, `pc-daily-report.ps1`)
- `en/` — versions anglaises (mêmes fichiers)

## Utilisation

```bash
# Exécution directe (français / Linux)
./FR/pc-daily-report.sh

# Version anglaise
./en/pc-daily-report.sh

# macOS : ./FR/pc-daily-report-mac.sh   |  Windows : pwsh -File ./FR/pc-daily-report.ps1

# Via cron job Hermes (no_agent mode — livré tel quel)
cronjob action=create \
  name="Rapport PC" \
  schedule="0 7 * * *" \
  script="FR/pc-daily-report.sh" \
  no_agent=true \
  deliver=origin
```

## Exemple de sortie

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 RAPPORT PC — kleinplex
  2026-06-29
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱ UPTIME & LOAD
up 11:05,  3 users,  load average: 0.69, 0.63, 0.57

── 🖥 CPU ──
▸ Moyenne — User: 4.9% | System: 1.0% | IOWait: 0.0% | Idle: 94.1%
▸ Top 3 pics CPU : ...

── 💾 RAM ──
▸ Utilisation moyenne : 7.0%  ...
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Fin du rapport
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Dépendances

Voir [`dependencies.md`](dependencies.md) pour la liste complète des dépendances.

## Cron job actif

- **Horaire :** `0 7 * * *` (tous les jours à 7h)
- **Mode :** `no_agent` (script pur, pas de LLM)
