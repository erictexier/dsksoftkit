from collections import namedtuple
from dsk.base.widgets.simpleqt import QtT

SIGNAL = QtT.QtCore.SIGNAL

class baseSig(object):
    @property
    def asTuple(self):
        return self.name,self.arg
 
class signalInfoT(namedtuple('signalInfo', "name arg signature"),baseSig):
    __slots__ = ()


def signalInfo(name,arg,sign=None):
    if sign == None:
        return signalInfoT(name,arg,"%s(%s)" % (name,arg))
    else:
        return signalInfoT(name,arg,sign)

  

class SignalClass(QtT.QtCore.QObject):
    """ Wrap tupple into a subclass of QObject
    """
    def __init__(self, xsignal):
        super(SignalClass,self).__init__()
        self.xsignal = xsignal
        self.doneName = xsignal.name+"Done"
    @property
    def asTuple(self):
        return self.xsignal.name,self.xsignal.arg

def make_signal_instance(xsignal,
                         doc="factory generated (base)"):

    if xsignal.arg != None:
        asig = SIGNAL(xsignal.arg)
    else:
        asig = SIGNAL()
    aclass = type(xsignal.name,
                  (SignalClass,),
                  {'sig': asig,    # class attribute                                                            
                   '__doc__':doc,
                   '__slots__':()
                   })

    a = aclass(xsignal)
    return a
