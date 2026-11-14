import hmac
import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs

import Emote_API as service

# Credentials are configured in Vercel Project Settings -> Environment Variables.
service.BOT_UID = os.getenv("BOT_UID", "").strip()
service.BOT_PASSWORD = os.getenv("BOT_PASSWORD", "").strip()
API_SECRET = os.getenv("API_SECRET", "").strip()


class handler(BaseHTTPRequestHandler):
    def _reply(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path not in ("/api/rishu", "/api/rishu/"):
            return self._reply(404, {"ok": False, "error": "Not found"})

        if not API_SECRET:
            return self._reply(503, {"ok": False, "error": "API_SECRET is not configured"})
        supplied = self.headers.get("x-api-key", "")
        if not hmac.compare_digest(supplied, API_SECRET):
            return self._reply(401, {"ok": False, "error": "Unauthorized"})

        if not service.BOT_UID or not service.BOT_PASSWORD:
            return self._reply(503, {"ok": False, "error": "BOT_UID or BOT_PASSWORD is not configured"})

        params = parse_qs(parsed.query)
        team_code = (params.get("Tc", [""])[0] or "").strip()
        emote_value = (params.get("Emote_id", [""])[0] or "").strip()
        target_value = (
            params.get("Target_Uid", [""])[0]
            or params.get("Target_uid", [""])[0]
            or params.get("target_uid", [""])[0]
        ).strip()

        if not team_code.isdigit():
            return self._reply(400, {"ok": False, "error": "Tc must be a numeric team code"})
        if not emote_value:
            emote_value = str(service.DEFAULT_EMOTE_ID)
        if not emote_value.isdigit():
            return self._reply(400, {"ok": False, "error": "Emote_id must be numeric"})
        if target_value and not target_value.isdigit():
            return self._reply(400, {"ok": False, "error": "Target_Uid must be numeric"})

        try:
            # The source already serializes API operations with its own lock.
            result = service.run_api_emote(
                team_code,
                int(emote_value),
                int(target_value) if target_value else None,
            )
            return self._reply(200, result)
        except Exception as exc:
            # Avoid returning credentials or internal tracebacks to callers.
            print("[api] request failed:", repr(exc))
            return self._reply(500, {"ok": False, "error": "Emote request failed; inspect Vercel Runtime Logs"})
