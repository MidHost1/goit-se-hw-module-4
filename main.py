from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import mimetypes
import threading
import socket
import urllib.parse
import json
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        file_path = Path(self.path.lstrip("/"))
        if self.path == "/":
            self.send_html_file('index.html')
        elif self.path == "/message":
            self.send_html_file('message.html')
        elif file_path.exists() and file_path.is_file():
            self.send_static(file_path)
        else:
            self.send_html_file('error.html', 404)
    
    
    def do_POST(self):
        if self.path == '/message':
            length = int(self.headers["Content-Length"])
            data = self.rfile.read(length)
            print(data)

            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.sendto(data, ("127.0.0.1", 5000))
            udp_sock.close()

            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        with open(filename, "rb") as f:
            self.wfile.write(f.read())
    
    def send_static(self, file_path: Path, status=200):
        self.send_response(status)

        mime_type, _ = mimetypes.guess_type(str(file_path))
        self.send_header("Content-Type", mime_type or "application/octet-stream")

        self.end_headers()
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())





def run_http():
    print("HTTP сервер запущено.")
    http = HTTPServer(('', 3000), HttpHandler)
    http.serve_forever()

def run_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 5000))
    print("UDP сервер запущено.")

    while True:
        data, addr = sock.recvfrom(1024)
        text = data.decode("utf-8")
        text = urllib.parse.unquote_plus(text)
        pairs = text.split("&")  # ["username= ", "message= "]
        payload_dict = {}
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)  # важливо: 1
                payload_dict[key] = value

        print(data, addr)
        print(payload_dict)

        storage_dir = Path("storage")
        storage_dir.mkdir(exist_ok=True)

        data_file = storage_dir / "data.json"
        
        try:
            with open(data_file, "r", encoding="utf-8") as fh:
                data_json = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
                data_json = {}

        timestamp = str(datetime.now())
        data_json[timestamp] = payload_dict

        with open(data_file, "w") as f:
            json.dump(data_json, f, indent=2)

if __name__ == '__main__':
    t1 = threading.Thread(target=run_http, daemon=True)
    t2 = threading.Thread(target=run_udp, daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

