#!/bin/bash
# Daily PC Monitoring Report
# Uses sysstat (sar) to summarize CPU, RAM, disk usage for the past 24h

set -e

HOSTNAME=$(hostname)
TODAY=$(date '+%Y-%m-%d')
SADIR=${SADIR:-/var/log/sysstat}
SARFILE=$(ls -t "$SADIR"/sa?? 2>/dev/null | head -1)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 RAPPORT QUOTIDIEN — $HOSTNAME"
echo "  $TODAY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── UP TIME & LOAD ──
echo "⏱ UPTIME & LOAD"
uptime | sed 's/^.*up/up/'
echo ""

# ── CPU ──
echo "── 🖥 CPU — 8 cœurs ARM ──"
# Data lines: time(1) AM/PM(2) all(3) %user(4) %nice(5) %system(6) %iowait(7) %steal(8) %idle(9)
# Average   : Average(1) all(2) %user(3) %nice(4) %system(5) %iowait(6) %steal(7) %idle(8)
AVG_USER=$(sar -u -f "$SARFILE" 2>/dev/null | awk '/^Average/{printf "%.1f%%", $3}')
AVG_SYS=$(sar -u -f "$SARFILE" 2>/dev/null | awk '/^Average/{printf "%.1f%%", $5}')
AVG_IDLE=$(sar -u -f "$SARFILE" 2>/dev/null | awk '/^Average/{printf "%.1f%%", $8}')
AVG_IOW=$(sar -u -f "$SARFILE" 2>/dev/null | awk '/^Average/{printf "%.1f%%", $6}')

echo "▸ Moyenne — User: $AVG_USER | System: $AVG_SYS | IOWait: $AVG_IOW | Idle: $AVG_IDLE"

# Peak CPU (user+system) from data lines
CPU_DATA=$(sar -u -f "$SARFILE" 2>/dev/null | grep -E '^[0-9]' | awk 'NR>1 && $4+0==$4{total=$4+$6; print total, $1, $2}')
echo "▸ Top 3 pics CPU :"
echo "$CPU_DATA" | sort -rn | head -3 | while read -r total time ampm; do
    printf "  • %.1f%% à %s %s\n" "$total" "$time" "$ampm"
done

# Min idle
IDLE_DATA=$(sar -u -f "$SARFILE" 2>/dev/null | grep -E '^[0-9]' | awk 'NR>1 && $9+0==$9{print $9, $1, $2}')
MIN_IDLE=$(echo "$IDLE_DATA" | sort -n | head -1 | awk '{printf "%.1f%% à %s %s (charge max)", $1, $2, $3}')
echo "▸ Idle minimum : $MIN_IDLE"
echo ""

# ── RAM ──
echo "── 💾 RAM — 5.7 GiB total ──"
# Data lines: time(1) AM/PM(2) kbmemfree(3) kbavail(4) kbmemused(5) %memused(6) ...
# Average   : Average(1) kbmemfree(2) kbavail(3) kbmemused(4) %memused(5) ...
AVG_MEM=$(sar -r -f "$SARFILE" 2>/dev/null | awk '/^Average/{printf "%.1f%%", $5}')
AVG_AVAIL=$(sar -r -f "$SARFILE" 2>/dev/null | awk '/^Average/{printf "%.0f MB", $3/1024}')

echo "▸ Utilisation moyenne : $AVG_MEM  ($AVG_AVAIL dispo)"

RAM_DATA=$(sar -r -f "$SARFILE" 2>/dev/null | grep -E '^[0-9]' | awk 'NR>1 && $6+0==$6{print $6, $1, $2}')
echo "▸ Pic mémoire (top 3) :"
echo "$RAM_DATA" | sort -rn | head -3 | while read -r pct time ampm; do
    printf "  • %.1f%% à %s %s\n" "$pct" "$time" "$ampm"
done

echo "▸ Plus bas :"
echo "$RAM_DATA" | sort -n | head -1 | while read -r pct time ampm; do
    printf "  • %.1f%% à %s %s\n" "$pct" "$time" "$ampm"
done

free -h | grep -E '^Mem:|^Swap:' | while read -r line; do
    label=$(echo "$line" | awk '{print $1}' | tr -d ':')
    total=$(echo "$line" | awk '{print $2}')
    used=$(echo "$line" | awk '{print $3}')
    free=$(echo "$line" | awk '{print $4}')
    echo "▸ $label — Total: $total | Used: $used | Free: $free"
done
echo ""

# ── DISK ──
echo "── 💽 DISQUE ──"
df -h /home/data/disk1 2>/dev/null | tail -1 | awk '{printf "▸ /home/data/disk1 (6 To) — Taille: %s | Used: %s (%s) | Free: %s\n", $2, $3, $5, $4}'
df -h / | tail -1 | awk '{printf "▸ / (root) — Taille: %s | Used: %s (%s) | Free: %s\n", $2, $3, $5, $4}'
echo ""

# ── TOP PROCESSES ──
echo "── 🔄 PROCESSUS ──"
echo "▸ Total : $(ps aux | wc -l) processus"

echo "▸ Top CPU :"
ps aux --sort=-%cpu 2>/dev/null | head -6 | awk 'NR>1{printf "  • PID %-5s %-18s %s%%\n", $2, $11, $3}'
echo "▸ Top MEM :"
ps aux --sort=-%mem 2>/dev/null | head -6 | awk 'NR>1{printf "  • PID %-5s %-18s %s%%\n", $2, $11, $4}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Fin du rapport"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
