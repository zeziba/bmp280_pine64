import os
import socketserver
import signal
import threading
import sys
from http.server import SimpleHTTPRequestHandler

try:
    os.chdir('/home/ubuntu/pybmp180/pyscript/data')
except NotADirectoryError:
    os.makedirs('/home/ubuntu/pybmp180/pyscript/data')
finally:
    os.chdir('/home/ubuntu/pybmp180/pyscript/data')
address = ''
port = 8000


class SignalWatch:
    kill = False

    def __init__(self):
        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

    def _exit(self, signum, frame):
        self.kill = True


signal_watch = SignalWatch()


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
        super().end_headers()


class TCPServer(socketserver.TCPServer):
    def run(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server_close()


def main():

    server = TCPServer((address, port), CORSRequestHandler)
    thread = threading.Thread(None, server.run)

    thread.start()

    while True:
        if signal_watch.kill:
            sys.exit(0)
        pass
