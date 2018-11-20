import os
from http.server import SimpleHTTPRequestHandler, HTTPServer, test

os.chdir('/home/ubuntu/pybmp180/pyscript')
address = ''
port = 8000


class CORSRequestHandler (SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


server_address = (address, port)
httpd = HTTPServer(server_address, CORSRequestHandler)
httpd.serve_forever()
