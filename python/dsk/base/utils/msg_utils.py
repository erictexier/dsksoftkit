import sys
import logging
import string


####################################

class MsgUtils(object):
    _logger = ""
    _wlogger = None
    _doFlush = False
    # convenient to call the log.write wrapper
    _callerWraper = None

    # convenient for detail call 
    _levelWraper = None


    def __init__(self):
        if MsgUtils._callerWraper == None:
            MsgUtils._callerWraper = {'debug':MsgUtils.debug,
                                      'error':MsgUtils.error,
                                      'info':MsgUtils.info,
                                      'warning':MsgUtils.warning}
        if MsgUtils._levelWraper == None:
            MsgUtils._levelWraper = {0:MsgUtils.whoami0, # none (default
                                     1:MsgUtils.line_number, #  (line_number)
                                     2:MsgUtils.caller_name, # function 
                                     3:MsgUtils.whoami1, # function (line_number)
                                     4:MsgUtils.whoami2} # module function (line_number)

    @staticmethod
    def set_logger(logger):
        assert type(logger) in (str,)
        MsgUtils._logger = logger

    @staticmethod
    def get_stream():
        return logging.getLogger(MsgUtils._logger)

    @staticmethod
    def whoami0(frame):
        return ""

    @staticmethod
    def line_number(frame):
        return "line(%d)" % sys._getframe(frame).f_lineno

    @staticmethod
    def caller_name(frame):
        return "from %s" % sys._getframe(frame).f_code.co_name

    @staticmethod
    def whoami1(frame):
        return "%s (%d)" % (sys._getframe(frame).f_code.co_name,
                                        sys._getframe(frame).f_lineno)

    @staticmethod
    def whoami2(frame):
        return "%s %s (%d)" % (sys._getframe(frame).f_code.co_filename,
                                             sys._getframe(frame).f_code.co_name,
                                             sys._getframe(frame).f_lineno)

    ##################
    @staticmethod
    def error(amsg,*extra,**kdata):
        if 'd' in kdata:
            index = kdata['d']
            msg = "%s - %s" % (MsgUtils._levelWraper[index](2),amsg)
        else:
            msg = amsg
        if extra != ():
            msg = msg + ", " + string.join(extra) 

        if MsgUtils._logger:
            logging.getLogger(MsgUtils._logger).error(msg)
        else:
            print(("ERROR: %s" % msg))

        if MsgUtils._doFlush and hasattr(sys.stdout,"flush"):sys.stdout.flush()

    ##################
    @staticmethod
    def debug(amsg,*extra,**kdata):
        if 'd' in kdata:
            index = kdata['d']
            msg = "%s - %s" % (MsgUtils._levelWraper[index](2),amsg)
        else:
            msg = amsg
        if extra != ():
            msg = msg + ", " + string.join(extra) 

        if MsgUtils._logger:
            logging.getLogger(MsgUtils._logger).debug(msg)
        else:
            print(("DEBUG: %s" % msg))

        if MsgUtils._doFlush and hasattr(sys.stdout,"flush"):sys.stdout.flush()

    ##################
    @staticmethod
    def warning(amsg,*extra,**kdata):
        if 'd' in kdata:
            index = kdata['d']
            msg = "%s - %s" % (MsgUtils._levelWraper[index](2),amsg)
        else:
            msg = amsg
        if extra != ():
            msg = msg + ", " + string.join(extra) 

        if MsgUtils._logger:
            logging.getLogger(MsgUtils._logger).warning(msg)
        else:
            print(("WARNING: %s" % msg))
        if MsgUtils._doFlush and hasattr(sys.stdout,"flush"):sys.stdout.flush()
    ##################
    @staticmethod
    def info(amsg,*extra,**kdata):
        if 'd' in kdata:
            index = kdata['d']
            msg = "%s - %s" % (MsgUtils._levelWraper[index](2),amsg)
        else:
            msg = amsg
        if extra != ():
            msg = msg + ", " + string.join(extra) 
        
        if MsgUtils._logger:
            logging.getLogger(MsgUtils._logger).info(msg)
        else:
            print(("INFO: %s" % msg))
        if MsgUtils._doFlush and hasattr(sys.stdout,"flush"):sys.stdout.flush()

    ##################
    @staticmethod
    def msg(data):
        # generic print
        if MsgUtils._logger:
            logging.getLogger(MsgUtils._logger).info(data)
        else:
            print(data)

    ##################
    @staticmethod
    def write(data,amode='debug'):
        """ to mimic the api of log
        """
        MsgUtils._callerWraper[amode](data)

# this is for initialisation for some class member, keep it
singleMsgUtils=MsgUtils()