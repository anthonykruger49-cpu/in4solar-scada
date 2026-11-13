import http.server
import os
import sys
import webbrowser
from threading import Timer

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

os.chdir(get_resource_path("."))

# Built-in fallback HTML dashboard if index.html is missing
FALLBACK_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>In4Solar SCADA Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #111; color: #0f0; text-align: center; padding-top: 50px; }
        h1 { color: #ff0; }
        .card { background: #222; border: 2px solid #0f0; display: inline-block; padding: 20px; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>In4Solar SCADA Active</h1>
        <p>Telemetry Polling & Switchgear Control Online</p>
    </div>
</body>
</html>
"""

class SCADARequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            if os.path.exists('index.html'):
                self.path = '/index.html'
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(FALLBACK_HTML.encode('utf-8'))
                return
        return super().do_GET()

def run(server_class=http.server.HTTPServer, handler_class=SCADARequestHandler, port=8085):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f"in4solar SCADA Dashboard live at http://0.0.0.0:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
