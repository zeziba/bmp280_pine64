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
    A generic daemon class.
    Usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, pidfile=join(__base__, 'bmp180.pid')):
        self.pidfile = pidfile

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        atexit.register(self.onstop)
        signal(SIGTERM, lambda signum, stack_frame: exit())

        # write pidfile
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write("%s\n" % pid)

    def onstop(self):
        self.quit()
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            print(self.pidfile)
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\nPID:{}\n".format(pid)
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        Should be override, is run after the class is dameonized
        :return:
        """
        pass

    def quit(self):
        """
        Should be overridden, is used to quit the daemon
        :return:
        """
        pass


class BMP180(Daemon):
    def __init__(self, pid=join(__base__, "bmp180.service")):
        super().__init__(pid)
        self.signal_watch = m.signal_watch


    def run(self):
        self.server = m
        self.signal_watch = m.signal_watch
        self.BACKUP = m.BACKUP
        self.server.main()

    def quit(self):
        self.signal_watch.kill = True


def main():
    _daemon = BMP180()
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            _daemon.start()
            _daemon.backup()
        elif sys.argv[1] == "stop":
            _daemon.quit()
        elif sys.argv[1] == "backup":
            import database
            with database.DatabaseManager() as db:
                db.BACKUP()
    else:
        print("Usage: start | stop | backup")


if __name__ == "__main__":
    main()
