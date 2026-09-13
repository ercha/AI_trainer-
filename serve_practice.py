from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import sys


class UTF8Handler(SimpleHTTPRequestHandler):
    extensions_map = SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map.update({
        ".html": "text/html; charset=utf-8",
        ".htm": "text/html; charset=utf-8",
        ".md": "text/plain; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
        ".csv": "text/csv; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
    })


if __name__ == "__main__":
    port = 7000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    server = ThreadingHTTPServer(("127.0.0.1", port), UTF8Handler)
    print(f"AI Trainer server: http://127.0.0.1:{port}/practice.html")
    print("Markdown/text files are served explicitly as UTF-8.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
