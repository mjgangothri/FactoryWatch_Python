import csv
import io
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND = os.path.join(ROOT, "frontend")
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.dirname(__file__))
from sensor_engine import analyze_readings  # noqa: E402

SAMPLE = [4, 1, 7, 3, 6, 11, 8, 2, 9, 5, 13, 4, 6, 10, 1, 7, 12, 3]


def json_bytes(payload):
    return json.dumps(payload).encode("utf-8")


class FactoryWatchHandler(BaseHTTPRequestHandler):
    def log_message(self, format_string, *args):
        return

    def _send(self, status, body, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/sample":
            self._send(200, json_bytes({"readings": SAMPLE}))
            return
        if path == "/api/health":
            self._send(200, json_bytes({"ok": True, "service": "FactoryWatch"}))
            return
        if path == "/api/download":
            self._send(200, json_bytes({"error": "Use POST /api/download with analysis payload"}))
            return
        relative = "index.html" if path == "/" else path.lstrip("/")
        safe_path = os.path.normpath(os.path.join(FRONTEND, relative))
        if not safe_path.startswith(FRONTEND) or not os.path.isfile(safe_path):
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        content_type = "text/html; charset=utf-8" if safe_path.endswith(".html") else "text/css; charset=utf-8" if safe_path.endswith(".css") else "application/javascript; charset=utf-8"
        with open(safe_path, "rb") as file:
            self._send(200, file.read(), content_type)

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            if path == "/api/analyze":
                result = analyze_readings(payload.get("readings"), int(payload.get("window_size")), float(payload.get("high_threshold")), float(payload.get("low_threshold")))
                self._send(200, json_bytes(result))
                return
            if path == "/api/download":
                rows = payload.get("windows", [])
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["Window", "Readings", "Maximum", "Minimum", "High Alert", "Low Alert", "Status"])
                for row in rows:
                    writer.writerow([row["window"], " ".join(str(value) for value in row["readings"]), row["maximum"], row["minimum"], row["high_alert"], row["low_alert"], row["status"]])
                self._send(200, output.getvalue().encode("utf-8"), "text/csv; charset=utf-8")
                return
            self._send(404, json_bytes({"error": "Unknown endpoint"}))
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            self._send(400, json_bytes({"error": str(error)}))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), FactoryWatchHandler)
    print(f"FactoryWatch running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nFactoryWatch stopped")
        server.server_close()
