import subprocess
import os
import sys
import time
from signal import SIGTERM


def process_get_output(cmd):
    """ cmd: list of what's make the command to run
    """

    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)
    if sys.platform == "win32":
        p.stdin.close()
    if p.wait() != 0:
        return ["ERROR BaseProcess1: %s" % " ".join(cmd)]
    res = p.stdout.readlines()
    p.stdout.close()
    return res


def process_nowait(cmd):
    """Cmd: list of what's make the process
    """
    return subprocess.Popen(cmd, close_fds=True)


class BaseProcess(object):
    def __init__(self):
        self._p = None
        self._cmd = ""

    def start(self, cmd):
        if isinstance(cmd, str):
            cmd = [cmd]
        self._cmd = cmd

        self._p = subprocess.Popen(cmd,
                                   stdin=None,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, close_fds=True)
        # shell=True,
        # close_fds=True)

    def end(self):
        """
            :return:
                empty string if failed,
        """

        if self._p.wait() != 0:
            print(["ERROR BaseProcess: %s" % " ".join(self._cmd)])
            print(self._p.stdout.readlines())
            return ["ERROR"]
        result = self._p.stdout.readlines()
        self._p.stdout.close()
        return result

    def launch_and_return(self, cmd):
        self.start(cmd)
        return self.end()


'''
see http://code.activestate.com/recipes/66012-fork-a-daemon-process-on-unix/
'''


def daemonize(stdin='/dev/null',
              stdout='/dev/null',
              stderr='/dev/null',
              pidFile=""):

    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit first parent.
    except OSError as e:
        sys.stderr.write('fork #1 failed: (%d) %s\n' % (e.errno, e.strerror))
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir(os.sep)
    os.umask(0)
    os.setsid()

    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit second parent.
    except OSError as e:
        sys.stderr.write('fork #2 failed: (%d) %s\n' % (e.errno, e.strerror))
        sys.exit(1)

    # Now I am a daemon!
    # Redirect standard file descriptors.
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)

    sys.stdout.flush()
    sys.stderr.flush()

    os.close(sys.stdin.fileno())
    os.close(sys.stdout.fileno())
    os.close(sys.stderr.fileno())

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    if pidFile:
        file(pidFile, 'w+').write("%s\n" % os.getpid())


class DeamonProcess(object):
    abortmsg = "Start aborted; pid file '%s' exists.\n"
    stopfailmsg = "Could not stop, pid file '%s' missing.\n"

    def __init__(self, **keys):
        super(DeamonProcess, self).__init__()
        # assign any overrides to self
        self.pidfile = ""
        self.pid = None
        self.stdout = '/dev/null'
        self.stderr = self.stdout
        self.stdin = '/dev/null'

        for n, v in keys.items():
            setattr(self, n, v)

        # setup pid number
        try:
            if self.pidfile != "":
                pf = file(self.pidfile, 'r')
                self.pid = int(pf.read().strip())
                pf.close()
        except IOError:
            self.pid = None

    def start(self):
        if self.pid and self.pidfile != "":
            sys.stderr.write(self.abortmsg % self.pidfile)
            sys.exit(1)
        daemonize(stdin=self.stdin,
                  stdout=self.stdout,
                  stderr=self.stderr,
                  pidFile=self.pidfile)
        return True

    def restart(self):
        if self.pid:
            self.stop()
        return self.start()

    def stop(self):
        if not self.pid:
            sys.stderr.write(self.stopfailmsg % self.pidfile)
            sys.exit(1)
        try:
            os.kill(self.pid, SIGTERM)
            time.sleep(1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                # sys.stdout.write(err+"\n")
                os.remove(self.pidfile)
            else:
                sys.stderr.write(err)
                sys.exit(1)
        self.pid = None
        return True


class ActionExample(DeamonProcess):
    '''This is an example main function run by the daemon.
    This prints a count and timestamp once per second.
    '''
    def doIt(self):
        sys.stdout.write('Daemon started with pid %d\n' % os.getpid())
        sys.stdout.write('Daemon stdout output\n')
        sys.stderr.write('Daemon stderr output\n')
        c = 0

        while c < 10:
            sys.stdout.write('%d: %s pid->%d\n' % (
                                        c,
                                        time.ctime(time.time()), os.getpid()))
            sys.stdout.flush()
            c = c + 1
            time.sleep(2)

if __name__ == '__main__':
    DeamonProcess.stdout = '/tmp/daemon.log'
    DeamonProcess.stderr = DeamonProcess.stdout
    action = ""
    try:
        action = sys.argv[1]
    except Exception as e:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)

    print("Running %s for daemon..." % action)

    # could replace ... with fixed options, or parse args from sys.argv
    a = ActionExample()
    method = getattr(a, action)
    method()
    if action != "stop":
        a.doIt()
    sys.exit(0)
