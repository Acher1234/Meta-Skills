#!/usr/bin/env python3
"""Read inbound messages from Hermes gateway logs (WhatsApp / Telegram / both).

Parses every `inbound message: platform=<p> ...` line in gateway.log
(+ rotated files) and prints them in a readable, date-grouped format.
Includes messages the bot may not have replied to.

Platform selection (in priority order):
  1. CLI flag  --platform whatsapp|telegram|all
  2. Env var   MSG_PLATFORM=whatsapp|telegram|all
  3. Default   whatsapp (backward compatible)

Media handling: when a message is a received image (`[image received]` or an
empty msg with a nearby image file), the script locates the actual file in
`~/.hermes/cache/images/` by matching the message timestamp to the file's
modification time, and prints the absolute path.

Usage:
  python3 read_whatsapp.py [--platform whatsapp|telegram|all] [--days N]
                           [--user "Name"] [--chat ID] [--raw] [--limit N]
"""
import argparse
import glob
import os
import re
from datetime import datetime, timedelta

LOG_DIR = "/root/.hermes/logs"
IMG_DIR = os.path.expanduser("~/.hermes/cache/images")
PLATFORMS = ("whatsapp", "telegram")
DEFAULT_PLATFORM = os.environ.get("MSG_PLATFORM", "whatsapp")

# Line: 2026-07-20 19:13:08,684 ... platform=whatsapp user=X chat=Y msg='...' reply_to_id=...
INBOUND_RE = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
    r'.*?platform=(?P<platform>\w+)\s+'
    r'user=(?P<user>.*?)\s+'
    r'chat=(?P<chat>\S+)\s+'
    r"msg='(?P<msg>.*?)'\s+reply_to_id="
)

# Markers that indicate a media (image) message rather than plain text
MEDIA_MARKERS = ("[image received]", "[video received]", "[audio received]",
                 "[sticker received]", "[document received]", "[ptt received]")


def is_media(msg):
    """Return True if the message is a media placeholder."""
    return any(marker in msg for marker in MEDIA_MARKERS) or msg.strip() == ""


def _closest_image(ts_dt, window=180):
    """Find the image file in IMG_DIR whose mtime is closest to ts_dt (within window sec)."""
    if not os.path.isdir(IMG_DIR):
        return None
    best = None
    best_delta = None
    try:
        for name in os.listdir(IMG_DIR):
            if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
                continue
            path = os.path.join(IMG_DIR, name)
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            delta = abs((ts_dt - mtime).total_seconds())
            if delta <= window and (best_delta is None or delta < best_delta):
                best = (path, name, mtime)
                best_delta = delta
    except OSError:
        return None
    return best


def load_logs(days, platforms):
    files = sorted(glob.glob(os.path.join(LOG_DIR, "gateway.log*")),
                   key=lambda p: os.path.getmtime(p), reverse=True)
    cutoff = datetime.now() - timedelta(days=days) if days else None
    selectors = [f"platform={p}" for p in platforms]
    messages = []
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if "inbound" not in line or not any(s in line for s in selectors):
                        continue
                    m = INBOUND_RE.search(line)
                    if not m:
                        continue
                    if m.group("platform") not in platforms:
                        continue
                    try:
                        ts_dt = datetime.strptime(m.group("ts"), "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        continue
                    if cutoff and ts_dt < cutoff:
                        continue
                    msg = m.group("msg")
                    entry = {
                        "ts": m.group("ts"), "ts_dt": ts_dt,
                        "platform": m.group("platform"),
                        "user": m.group("user").strip(),
                        "chat": m.group("chat"), "msg": msg,
                        "media": is_media(msg), "image_path": None,
                    }
                    if entry["media"]:
                        img = _closest_image(ts_dt)
                        if img:
                            entry["image_path"] = img[0]
                    messages.append(entry)
        except OSError:
            continue
    messages.sort(key=lambda x: x["ts"])
    return messages


def _resolve_platforms(arg):
    """Combine CLI arg + env var + default into a sorted list of platforms."""
    val = (arg or DEFAULT_PLATFORM or "whatsapp").lower().strip()
    if val in ("all", "both"):
        return list(PLATFORMS)
    if val == "w":
        return ["whatsapp"]
    if val == "t":
        return ["telegram"]
    if val in PLATFORMS:
        return [val]
    # unknown -> fall back to default safely
    return ["whatsapp"]


def main():
    ap = argparse.ArgumentParser(
        description="Lire les messages reçus dans les logs gateway (whatsapp/telegram/all)")
    ap.add_argument("--platform", default=None,
                    help="whatsapp | telegram | all (défaut: $MSG_PLATFORM ou whatsapp)")
    ap.add_argument("--days", type=int, default=None, help="Ne garder que les N derniers jours")
    ap.add_argument("--user", default=None, help="Filtrer par nom d'utilisateur (sous-chaîne)")
    ap.add_argument("--chat", default=None, help="Filtrer par chat (sous-chaîne)")
    ap.add_argument("--raw", action="store_true", help="Afficher le format brut un-par-ligne")
    ap.add_argument("--limit", type=int, default=200, help="Nombre max de messages affichés (200)")
    args = ap.parse_args()

    platforms = _resolve_platforms(args.platform)
    msgs = load_logs(args.days, platforms)
    if args.user:
        msgs = [m for m in msgs if args.user.lower() in m["user"].lower()]
    if args.chat:
        msgs = [m for m in msgs if args.chat in m["chat"]]

    n_media = sum(1 for m in msgs if m["media"])

    if args.raw:
        for m in msgs:
            line = f"{m['ts']} | {m['platform']} | {m['user']} | {m['chat']} | {m['msg']}"
            if m["image_path"]:
                line += f" | 📁 {m['image_path']}"
            print(line)
        print(f"\nTotal: {len(msgs)} dont {n_media} média")
        return

    current_date = None
    for m in msgs[-args.limit:]:
        day = m["ts"][:10]
        if day != current_date:
            print(f"\n### {day}")
            current_date = day
        icon = "🟢" if m["platform"] == "whatsapp" else "🔵"
        label = m["msg"][:200] if m["msg"] else "(média sans légende)"
        print(f"**{m['ts'][11:16]}** {icon} — *{m['user']}* : {label}")
        if m["image_path"]:
            print(f"   📁 `{m['image_path']}`")
    print(f"\n---\n📊 Total : {len(msgs)} message(s), dont {n_media} média")


if __name__ == "__main__":
    main()