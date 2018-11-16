import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

os.chdir('/home/ubuntu/pybmp180/pyscript')
server_address = ('', 8000)
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
httpd.serve_forever()
