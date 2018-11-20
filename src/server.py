import os
import socketserver
from http.server import SimpleHTTPRequestHandler

os.chdir('/home/ubuntu/pybmp180/pyscript')
address = ''
port = 8000


class CORSRequestHandler (SimpleHTTPRequestHandler):
    def __int__(self, *args, **kwargs):
        super().__init__(*args, directory=address, **kwargs)

    def do_GET(self):
        super(CORSRequestHandler, self).do_GET()

    def do_OPTIONS(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header("Access-Control-Allow-Headers", "dataType, accept, authorization")

    def end_headers(self):
        self.do_OPTIONS()
        SimpleHTTPRequestHandler.end_headers(self)


httpd = socketserver.TCPServer((address, port), CORSRequestHandler)
httpd.serve_forever()
