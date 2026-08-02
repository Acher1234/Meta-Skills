#!/usr/bin/env python3
"""Local OAuth redirect catcher for Google Workspace setup.

Google redirects here after consent. The page shows the auth code so the user
can paste it into the agent (``setup.py --auth-code CODE``).

Usage::

    python http-local.py
    python http-local.py --port 8765
    python http-local.py --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

import argparse
import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def _page(title: str, body: str) -> bytes:
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #0f1419;
      --fg: #e7ecf1;
      --muted: #8b9aab;
      --code: #1a2330;
      --accent: #3d8bfd;
      --ok: #3ecf8e;
      --err: #f07178;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      background:
        radial-gradient(1200px 600px at 10% -10%, #1b2a40 0%, transparent 55%),
        radial-gradient(900px 500px at 100% 0%, #243018 0%, transparent 50%),
        var(--bg);
      color: var(--fg);
      display: grid;
      place-items: center;
      padding: 2rem;
    }}
    main {{
      width: min(40rem, 100%);
    }}
    h1 {{
      font-family: "IBM Plex Serif", Georgia, serif;
      font-weight: 600;
      font-size: 1.75rem;
      margin: 0 0 0.35rem;
      letter-spacing: -0.02em;
    }}
    p {{
      color: var(--muted);
      margin: 0 0 1.25rem;
      line-height: 1.45;
    }}
    .code-block {{
      background: var(--code);
      border: 1px solid #2a3848;
      border-radius: 10px;
      padding: 1rem 1.1rem;
      font-family: "IBM Plex Mono", ui-monospace, monospace;
      font-size: 0.95rem;
      word-break: break-all;
      line-height: 1.5;
      user-select: all;
    }}
    .ok .code-block {{ border-color: color-mix(in srgb, var(--ok) 45%, #2a3848); }}
    .err .code-block {{ border-color: color-mix(in srgb, var(--err) 45%, #2a3848); }}
    button {{
      margin-top: 1rem;
      appearance: none;
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: #fff;
      font: inherit;
      font-weight: 600;
      padding: 0.65rem 1rem;
      cursor: pointer;
    }}
    button:hover {{ filter: brightness(1.08); }}
    .hint {{
      margin-top: 1.25rem;
      font-size: 0.9rem;
    }}
    kbd {{
      font-family: "IBM Plex Mono", ui-monospace, monospace;
      background: #1a2330;
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
  <main class="{'ok' if 'Auth code' in title else 'err' if 'failed' in title.lower() or 'Error' in title else ''}">
    {body}
  </main>
</body>
</html>
"""
    return doc.encode("utf-8")


def _success_html(code: str, state: str | None, scope: str | None) -> bytes:
    safe = html.escape(code)
    state_line = (
        f'<p class="hint">state: <kbd>{html.escape(state)}</kbd></p>' if state else ""
    )
    scope_line = (
        f'<p class="hint">scopes granted — paste the code above into the agent.</p>'
        if scope
        else '<p class="hint">Copy the code and paste it into the agent chat.</p>'
    )
    body = f"""
    <h1>Auth code ready</h1>
    <p>Paste this code into the LLM / agent so it can finish OAuth.</p>
    <div class="code-block" id="code">{safe}</div>
    <button type="button" id="copy">Copy code</button>
    {scope_line}
    {state_line}
    <script>
      const btn = document.getElementById("copy");
      const el = document.getElementById("code");
      btn.addEventListener("click", async () => {{
        const text = el.textContent || "";
        try {{
          await navigator.clipboard.writeText(text);
          btn.textContent = "Copied";
        }} catch {{
          const range = document.createRange();
          range.selectNodeContents(el);
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
          btn.textContent = "Select & copy (⌘/Ctrl+C)";
        }}
      }});
    </script>
    """
    return _page("Auth code", body)


def _error_html(error: str, description: str | None) -> bytes:
    detail = html.escape(description or error)
    body = f"""
    <h1>Authorization failed</h1>
    <p>Google returned an error instead of an auth code.</p>
    <div class="code-block">{detail}</div>
    <p class="hint">Close this tab and run <kbd>--auth-url</kbd> again.</p>
    """
    return _page("Authorization failed", body)


def _waiting_html(redirect_uri: str) -> bytes:
    body = f"""
    <h1>Waiting for Google</h1>
    <p>OAuth redirect URI for the Cloud Console:</p>
    <div class="code-block">{html.escape(redirect_uri)}</div>
    <p class="hint">After you approve access, Google will land here with the code.</p>
    """
    return _page("Waiting for Google", body)


class OAuthHandler(BaseHTTPRequestHandler):
    redirect_uri: str = ""

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[http-local] {self.address_string()} {fmt % args}\n")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in ("/", "/callback", "/oauth2/callback"):
            self.send_error(404, "Not found")
            return

        qs = parse_qs(parsed.query)
        code = (qs.get("code") or [None])[0]
        error = (qs.get("error") or [None])[0]
        state = (qs.get("state") or [None])[0]
        scope = (qs.get("scope") or [None])[0]
        desc = (qs.get("error_description") or [None])[0]

        if error:
            body = _error_html(error, desc)
            status = 400
        elif code:
            body = _success_html(code, state, scope)
            status = 200
            print(f"CODE={code}", flush=True)
            if state:
                print(f"STATE={state}", flush=True)
        else:
            body = _waiting_html(self.redirect_uri)
            status = 200

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Localhost HTTP server that shows the Google OAuth code for the agent."
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Bind address (default {DEFAULT_HOST})")
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port (default {DEFAULT_PORT})",
    )
    args = parser.parse_args(argv)

    redirect_uri = f"http://localhost:{args.port}/"
    OAuthHandler.redirect_uri = redirect_uri

    server = ThreadingHTTPServer((args.host, args.port), OAuthHandler)
    print(f"Listening on http://{args.host}:{args.port}/", flush=True)
    print(f"Redirect URI: {redirect_uri}", flush=True)
    print("Open the Google consent URL; the code will appear here and as CODE=… on stdout.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
