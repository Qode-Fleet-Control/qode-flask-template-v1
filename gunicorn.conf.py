"""Gunicorn settings, read automatically from ./gunicorn.conf.py by every `gunicorn`
start of this app (the Docker image, compose.yaml and fleet.conf's START_CMD)."""

import json

from gunicorn.glogging import Logger

# KEEP THIS: one log line per request (status + duration) is what the workspace Monitoring tab charts.
# Each finished request writes ONE JSON line to stdout, e.g.
#   {"method": "GET", "path": "/", "status": 200, "durationMs": 3.1, "ua": "curl/8.5.0"}
# No query string, bodies, cookies or Authorization headers are logged.
accesslog = "-"


class JsonAccessLogger(Logger):
    def access(self, resp, req, environ, request_time):
        status = resp.status
        if isinstance(status, str):
            status = status.split(None, 1)[0]
        try:
            status = int(status)
        except (TypeError, ValueError):
            status = 0
        line = {
            "method": environ.get("REQUEST_METHOD"),
            "path": environ.get("PATH_INFO"),
            "status": status,
            "durationMs": round(request_time.total_seconds() * 1000, 1),
            "ua": environ.get("HTTP_USER_AGENT", ""),
        }
        try:
            self.access_log.info(json.dumps(line))
        except Exception:
            self.exception("request log line failed")


logger_class = JsonAccessLogger
