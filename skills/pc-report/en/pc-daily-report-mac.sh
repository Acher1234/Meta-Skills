#!/bin/bash
# Daily PC Monitoring Report — macOS
# Uses native tools (top, vm_stat, sysctl, df, ps) to summarize CPU, RAM, disk.
#
# macOS has no built-in 24h history like Linux sysstat/sar, so this is a
# point-in-time snapshot at run time. Output mirrors the Linux report format.

set -e

HOSTNAME=$(hostname -s)
TODAY=$(date '+%Y-%m-%d %H:%M')
NCPU=$(sysctl -n hw.ncpu)
MEM_BYTES=$(sysctl -n hw.memsize)
MEM_GIB=$(awk -v b="$MEM_BYTES" 'BEGIN{printf "%.1f", b/1024/1024/1024}')

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 DAILY REPORT — $HOSTNAME (macOS)"
echo "  $TODAY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "ℹ️  Snapshot at run time (macOS has no sar history)."
echo ""

# ── UP TIME & LOAD ──
echo "⏱ UPTIME & LOAD"
uptime | sed 's/^.*up/up/'
echo ""

# ── CPU ──
echo "── 🖥 CPU — $NCPU cores ──"
# Second sample from `top` is the accurate one (first is since-boot average).
CPU_LINE=$(top -l 2 -n 0 -s 1 2>/dev/null | grep "CPU usage" | tail -1)
CPU_USER=$(echo "$CPU_LINE" | awk -F'[:,]' '{gsub(/[^0-9.]/,"",$2); print $2}')
CPU_SYS=$(echo "$CPU_LINE" | awk -F'[:,]' '{gsub(/[^0-9.]/,"",$3); print $3}')
CPU_IDLE=$(echo "$CPU_LINE" | awk -F'[:,]' '{gsub(/[^0-9.]/,"",$4); print $4}')
echo "▸ Snapshot — User: ${CPU_USER}% | System: ${CPU_SYS}% | Idle: ${CPU_IDLE}%"
LOADAVG=$(sysctl -n vm.loadavg | tr -d '{}' | awk '{printf "1min: %s | 5min: %s | 15min: %s", $1, $2, $3}')
echo "▸ Load average — $LOADAVG"
echo ""

# ── RAM ──
echo "── 💾 RAM — ${MEM_GIB} GiB total ──"
# Compute used/available from vm_stat page counters.
eval "$(
    vm_stat | awk -v total="$MEM_BYTES" '
        /page size of/ { match($0, /[0-9]+/); ps = substr($0, RSTART, RLENGTH) }
        /Pages free/            { gsub(/\./,""); free=$3 }
        /Pages active/          { gsub(/\./,""); active=$3 }
        /Pages inactive/        { gsub(/\./,""); inactive=$3 }
        /Pages speculative/     { gsub(/\./,""); spec=$3 }
        /Pages wired down/      { gsub(/\./,""); wired=$4 }
        /occupied by compressor/{ gsub(/\./,""); comp=$5 }
        END {
            avail = (free + inactive + spec) * ps
            used  = total - avail
            printf "USED_PCT=%.1f\n", used/total*100
            printf "AVAIL_MB=%.0f\n", avail/1024/1024
            printf "USED_MB=%.0f\n",  used/1024/1024
            printf "WIRED_MB=%.0f\n", wired*ps/1024/1024
            printf "COMP_MB=%.0f\n",  comp*ps/1024/1024
        }'
)"
echo "▸ Usage: ${USED_PCT}%  (${USED_MB} MB used | ${AVAIL_MB} MB free)"
echo "▸ Wired: ${WIRED_MB} MB | Compressed: ${COMP_MB} MB"

# Swap usage.
SWAP=$(sysctl -n vm.swapusage 2>/dev/null)
[ -n "$SWAP" ] && echo "▸ Swap — $SWAP"
echo ""

# ── DISK ──
echo "── 💽 DISK ──"
df -h / | tail -1 | awk '{printf "▸ / (root) — Size: %s | Used: %s (%s) | Free: %s\n", $2, $3, $5, $4}'
# On APFS the real user data lives on the Data volume — report it when present.
if df -h /System/Volumes/Data >/dev/null 2>&1; then
    df -h /System/Volumes/Data | tail -1 | awk '{printf "▸ /System/Volumes/Data — Size: %s | Used: %s (%s) | Free: %s\n", $2, $3, $5, $4}'
fi
echo ""

# ── TOP PROCESSES ──
echo "── 🔄 PROCESSES ──"
echo "▸ Total: $(($(ps ax | wc -l) - 1)) processes"

echo "▸ Top CPU:"
ps aux -r 2>/dev/null | head -6 | awk 'NR>1{printf "  • PID %-5s %-18s %s%%\n", $2, $11, $3}'
echo "▸ Top MEM:"
ps aux -m 2>/dev/null | head -6 | awk 'NR>1{printf "  • PID %-5s %-18s %s%%\n", $2, $11, $4}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ End of report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
