import sys

from dsk.base.utils import shotgun_utils
import threading


class TimeoutError(Exception):
    pass


def timelimit(timeout):

    def internal(function):

        def internal2(*args, **kw):

            class Calculator(threading.Thread):

                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()[0]

            c = Calculator()
            c.start()
            c.join(timeout)
            if c.isAlive():
                raise TimeoutError
            if c.error:
                raise c.error
            return c.result
        return internal2
    return internal


def connect_to_shotgun(sg_server=None,
                       sg_script_name=None,
                       sg_script_key=None):
    return shotgun_utils.connect()


@timelimit(5)
def connect_to_shotgun_time_out(sg_server=None,
                                sg_script_name=None,
                                sg_script_key=None):
    return shotgun_utils.connect()
