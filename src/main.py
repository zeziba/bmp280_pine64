#!/usr/bin/env python3

import atexit
import os
import sys
import time
from os.path import join
from signal import signal, SIGTERM

sys.path.append('/home/ubuntu/pybmp180/pyscript')

import _main as m

__base__ = '/var/run'


class Daemon:
    """
    Pass me something...
    """

    def __init__(self, pidfile, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"):
        self.stderr = stderr
        self.stdout = stdout
        self.stdin = stdin
        self.pid_file = pidfile

    def __sys_exit__(self, msg):
        sys.stderr.write(msg)
        sys.exit(1)

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            self.__sys_exit__("fork: #1 failed: {} {}".format(e.errno, e.strerror))

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            self.__sys_exit__("fork: #2 failed: {} {}".format(e.errno, e.strerror))

        sys.stdout.flush()
        sys.stderr.flush()

        if not os.path.exists(self.stdin):
            with open(self.stdin, "w+") as stdin:
                pass

        if not os.path.exists(self.stdin):
            with open(self.stdout, "w+") as stdout:
                pass

        if not os.path.exists(self.stderr):
            with open(self.stderr, "w+") as stderr:
                pass

        si = open(self.stdin, "r")
        so = open(self.stdout, "a+")
        se = open(self.stderr, "a+")

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.remove_pidfile)
        pid = str(os.getpid())
        with open(self.pid_file, "w+") as f:
            f.write("{}\n".format(pid))

    def remove_pidfile(self):
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)

    def start(self):
        try:
            with open(self.pid_file, "r") as pidfile:
                pid = int(pidfile.read().strip())
        except IOError:
            pid = None

        if pid:
            try:
                os.kill(self.pid_file, 0)  # Checks if a process is running under the pid
            except OSError:
                self.__sys_exit__("pidfile {} already exists. Daemon already running!\n".format(self.pid_file))
            finally:
                self.remove_pidfile()
                sys.stdout.write("pidfile {} already exists. Daemon not running, deleting pid.\n".format(self.pid_file))

        sys.stdout.write("Starting processes")

        self.daemonize()
        self.run()

    def stop(self):
        try:
            with open(self.pid_file, "r") as pidfile:
                pid = int(pidfile.read().strip())
        except IOError:
            pid = None

        if not pid:
            sys.stderr.write("pidfile {} does not exist. Daemon not running?\n".format(self.pid_file))
            return

        self.remove_pidfile()
        time.sleep(2)

        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(1)
        except OSError as err:
            err = str(err)
            if err.find('No such process') > 0:
                self.__sys_exit__("{}\n".format(err))

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        pass


class BMP180(Daemon):
    def __init__(self, pid=join(__base__, "bmp180.service"),
                 stdin="/home/ubuntu/bmpin", stdout="/home/ubuntu/bmpout", stderr="/home/ubuntu/bmperr"):
        super().__init__(pid, stdin, stdout, stderr)
        self.server = m

    def run(self):
        self.server.main()

    def quit(self):
        self.server.signal_watch.kill = True


def main():
    _daemon = BMP180()
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            _daemon.start()
        elif sys.argv[1] == "stop":
            _daemon.quit()
            time.sleep(0.5)
            _daemon.stop()
        elif sys.argv[1] == "backup":
            import database
            with database.DatabaseManager() as db:
                db.BACKUP()
        elif sys.argv[1] == "restart":
            _daemon.quit()
            time.sleep(0.5)
            _daemon.stop()
            time.sleep(0.5)
            _daemon.start()
    else:
        print("Usage: start | stop | backup | restart")


if __name__ == "__main__":
    main()
