import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from test import analyze, decide_mood, recommend

PORT = 8000
BASE = os.path.dirname(os.path.abspath(__file__))


def _read(*parts):
    with open(os.path.join(BASE, *parts), encoding="utf-8") as f:
        return f.read()


# HTML/CSS/JS live in their own files (templates/ and static/), loaded once here.
INDEX = _read("templates", "index.html")
RESULT = _read("templates", "result.html")
SONG_ROW = _read("templates", "song_row.html")
STYLE_CSS = _read("static", "style.css")


def _fill(template, **values):
    """Replace %%TOKEN%% placeholders with the given values."""
    for key, value in values.items():
        template = template.replace("%%" + key + "%%", str(value))
    return template


def render(text=""):
    if not text.strip():
        return _fill(INDEX, TEXT="", RESULT="")

    analysis = analyze(text)
    mood = decide_mood(analysis)
    songs_html = "".join(
        _fill(SONG_ROW, N=i, TITLE=t, ARTIST=a, GENRE=g, MELODY=m)
        for i, (t, a, g, m) in enumerate(recommend(mood), 1)
    )
    result = _fill(
        RESULT,
        MOOD=mood,
        SENTIMENT=analysis["sentiment"],
        EMOTION=analysis["emotion"],
        SONGS=songs_html,
    )
    # TEXT last so any %% in user input isn't treated as a placeholder.
    return _fill(INDEX, RESULT=result, TEXT=text.replace("<", "&lt;"))


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, content_type="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(render())
        elif self.path == "/style.css":
            self._send(STYLE_CSS, "text/css; charset=utf-8")
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        fields = parse_qs(data)
        text = fields.get("text", [""])[0]
        self._send(render(text))

    def log_message(self, *args):
        pass


def start_server():
    for port in range(PORT, PORT + 20):
        try:
            return HTTPServer(("127.0.0.1", port), Handler), port
        except OSError:
            continue
    raise OSError("No free port found between 8000 and 8019.")


def main():
    server, port = start_server()
    url = f"http://localhost:{port}"
    print(f"\n  Mood App is running!")
    print(f"  Open this in your browser:  {url}\n")
    print("  Press Ctrl+C here to stop.\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
