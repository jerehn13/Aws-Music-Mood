"""WSGI entry point for AWS Elastic Beanstalk.

Elastic Beanstalk's Python platform looks for a callable named `application`.
This reuses the same render() used by the local server, so the deployed app
behaves identically to running webapp.py locally.
"""

from urllib.parse import parse_qs

from webapp import render, STYLE_CSS


def application(environ, start_response):
    if environ.get("PATH_INFO") == "/style.css":
        data = STYLE_CSS.encode("utf-8")
        start_response("200 OK", [
            ("Content-Type", "text/css; charset=utf-8"),
            ("Content-Length", str(len(data))),
        ])
        return [data]

    if environ.get("REQUEST_METHOD") == "POST":
        try:
            size = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            size = 0
        body = environ["wsgi.input"].read(size).decode("utf-8")
        text = parse_qs(body).get("text", [""])[0]
        html = render(text)
    else:
        html = render()

    data = html.encode("utf-8")
    start_response("200 OK", [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(data))),
    ])
    return [data]
