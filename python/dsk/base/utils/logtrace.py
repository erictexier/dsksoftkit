# Written by Brendan O'Connor, brenocon@gmail.com, www.anyall.org
#  * Originally written Aug. 2005
#  * Posted to gist.github.com/16173 on Oct. 2008

#   Copyright (c) 2003-2006 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re, sys, types

"""
Have all your function & method calls automatically logged, in indented outline
form - unlike the stack snapshots in an interactive debugger, it tracks call
structure & stack depths across time!
It hooks into all function calls that you specify, and logs each time they're
called.  I find it especially useful when I don't know what's getting called
when, or need to continuously test for state changes.  (by hacking this file)
Originally inspired from the python cookbook:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/198078
Currently you can
 - tag functions or individual methods to be autologged
 - tag an entire class's methods to be autologged
 - tag an entire module's classes and functions to be autologged
TODO:
 - allow tagging of ALL modules in the program on startup?
CAVEATS:
 - certain classes barf when you logclass() them -- most notably,
   SWIG-generated wrappers, and perhaps others.
USAGE: see examples on the bottom of this file.
Viewing tips
============
If your terminal can't keep up, try xterm or putty, they seem to be highest
performance.  xterm is available for all platforms through X11...
Also try:    (RunChandler > log &); tail -f log
Also, you can  "less -R log"  afterward and get the colors correct.
If you have long lines, less -RS kills wrapping, enhancing readability. Also
can chop at formatAllArgs().
If you want long lines to be chopped realtime, try piping through less::
   RunChandler | less -RS
but then you have to hit 'space' lots to prevent chandler from freezing.
less's 'F' command is supposed to do this correctly but doesn't work for me.
"""


#@@@ should use the standard python logging system?
log = sys.stdout

# Globally incremented across function calls, so tracks stack depth
indent = 0
indStr = '  '


# ANSI escape codes for terminals.
#  X11 xterm: always works, all platforms
#  cygwin dosbox: run through |cat and then colors work
#  linux: works on console & gnome-terminal
#  mac: untested
import logging
import types
import pdb
from pprint import pformat
TRACE = pdb.set_trace

fmt = "%(name)s: %(indent)s%(funcNameExtra)s: %(message)s"
#fmt = "%(name)s %(levelnames): %(message)s"
debug_logger = logging.getLogger('TRC')
debug_handler = logging.StreamHandler()
debug_logger.addHandler(debug_handler)
debug_handler.setFormatter(logging.Formatter(fmt))
debug_logger.setLevel(logging.DEBUG)
debug_logger.propagate = False

indent = 0
indent_amount = 2

def logify(fn):
    '''Decorator for adding tracing messages to the call of a function'''
    #def debuglog2(fn):
    def new(*args, **kwargs):
        global indent
        global indent_amount
        extra = ".".join(map(str, [fn.__module__, fn.__name__]))
        indent_spaces = ' ' * indent
        debug_logger.debug("Start...", extra={'funcNameExtra': extra,
                                              'indent': indent_spaces})
        indent += indent_amount
        result = 'ERROR'
        try:
            debug_logger.debug('ARGK: %s' % pformat(kwargs))
            debug_logger.debug('ARG: %s' % pformat(args))
            result = fn(*args, **kwargs)
        finally:
            debug_logger.debug("End...", extra={'funcNameExtra': extra, 'indent': indent_spaces})
            indent = max(indent - indent_amount, 0)
        return result

    # Preserve the function's info onto new
    new.__doc__ = fn.__doc__
    new.__name__ = fn.__name__
    new.__module__ = fn.__module__
    new.__dict__.update(fn.__dict__)

    return new

def logtrace(funcOrClass):
    '''Decorator and function that sets up a function to be traced and changes a class
    so that its functions are traced
    '''
    if isinstance(funcOrClass, type):
        for name in dir(funcOrClass):
            func = getattr(funcOrClass, name)
            if callable(func) and hasattr(func, '__logify') and func.__logify:
                setattr(funcOrClass, name, logify(func))
                func.__dict__.pop('__logify')
    else:
        funcOrClass.__logify = True

    return funcOrClass

def logtrace_class(cls):
    '''Changes a class so that all of its methods are traced'''
    if isinstance(cls, type):
        for name in dir(cls):
            func = getattr(cls, name)
            if callable(func) and type(func) == types.MethodType:
                setattr(cls, name, logify(func))
    return cls

BLACK     =        "\033[0;30m"
BLUE      =        "\033[0;34m"
GREEN     =        "\033[0;32m"
CYAN      =       "\033[0;36m"
RED       =        "\033[0;31m"
PURPLE    =        "\033[0;35m"
BROWN     =        "\033[0;33m"
GRAY      =        "\033[0;37m"
BOLDGRAY  =       "\033[1;30m"
BOLDBLUE     =   "\033[1;34m"
BOLDGREEN    =   "\033[1;32m"
BOLDCYAN     =   "\033[1;36m"
BOLDRED      =   "\033[1;31m"
BOLDPURPLE   =   "\033[1;35m"
BOLDYELLOW   =         "\033[1;33m"
WHITE     =        "\033[1;37m"

NORMAL = "\033[0m"


def indentlog(message):
    global log, indStr, indent
    print("%s%s" %(indStr*indent, message), file=log)
    log.flush()

def shortstr(obj):
    """
    Where to put gritty heuristics to make an object appear in most useful
    form. defaults to __str__.
    """
    if "wx." in str(obj.__class__)  or  obj.__class__.__name__.startswith("wx"):
        shortclassname = obj.__class__.__name__
        ##shortclassname = str(obj.__class__).split('.')[-1]
        if hasattr(obj, "blockItem") and hasattr(obj.blockItem, "blockName"):
            moreInfo = "block:'%s'" %obj.blockItem.blockName
        else:
            moreInfo = "at %d" %id(obj)
        return "<%s %s>" % (shortclassname, moreInfo)
    else:
        return str(obj)

def formatAllArgs(args, kwds):
    """
    makes a nice string representation of all the arguments
    """
    allargs = []
    for item in args:
        allargs.append('%s' % shortstr(item))
    for key,item in list(kwds.items()):
        allargs.append('%s=%s' % (key,shortstr(item)))
    formattedArgs = ', '.join(allargs)
    if len(formattedArgs) > 150:
        return formattedArgs[:146] + " ..."
    return formattedArgs




def logfunction(theFunction, displayName=None):
    """a decorator."""
    if not displayName: displayName = theFunction.__name__

    def _wrapper(*args, **kwds):
        global indent
        argstr = formatAllArgs(args, kwds)

        # Log the entry into the function
        indentlog("%s%s%s  (%s) " % (BOLDRED,displayName,NORMAL, argstr))
        log.flush()

        indent += 1
        returnval = theFunction(*args,**kwds)
        indent -= 1

        # Log return
        ##indentlog("return: %s"% shortstr(returnval)
        return returnval
    return _wrapper

def logmethod(theMethod, displayName=None):
    """use this for class or instance methods, it formats with the object out front."""
    if not displayName: displayName = theMethod.__name__
    def _methodWrapper(self, *args, **kwds):
        "Use this one for instance or class methods"
        global indent

        argstr = formatAllArgs(args, kwds)
        selfstr = shortstr(self)

        #print >> log,"%s%s.  %s  (%s) " % (indStr*indent,selfstr,methodname,argstr)
        indentlog("%s.%s%s%s  (%s) " % (selfstr,  BOLDRED,theMethod.__name__,NORMAL, argstr))
        log.flush()

        indent += 1

        if theMethod.__name__ == 'OnSize':
            indentlog("position, size = %s%s %s%s" %(BOLDBLUE, self.GetPosition(), self.GetSize(), NORMAL))

        returnval = theMethod(self, *args,**kwds)

        indent -= 1

        return returnval
    return _methodWrapper


def logclass(cls, methodsAsFunctions=False,
             logMatch=".*", logNotMatch="asdfnomatch"):
    """
    A class "decorator". But python doesn't support decorator syntax for
    classes, so do it manually::

        class C(object):
           ...
        C = logclass(C)

        :param methodsAsFunctions: set to True if you always want methodname first
            in the display.  Probably breaks if you're using class/staticmethods?

    """

    allow = lambda s: re.match(logMatch, s) and not re.match(logNotMatch, s) and \
          s not in ('__str__','__repr__')

    namesToCheck = list(cls.__dict__.keys())

    for name in namesToCheck:
        if not allow(name): continue
        # unbound methods show up as mere functions in the values of
        # cls.__dict__,so we have to go through getattr
        value = getattr(cls, name)

        if methodsAsFunctions and callable(value):
            setattr(cls, name, logfunction(value))
        elif isinstance(value, types.MethodType):
            #a normal instance method
            if value.__self__ == None:
                setattr(cls, name, logmethod(value))

            #class & static method are more complex.
            #a class method
            elif value.__self__ == cls:
                w = logmethod(value.__func__,
                              displayName="%s.%s" %(cls.__name__, value.__name__))
                setattr(cls, name, classmethod(w))
            else: assert False

        #a static method
        elif isinstance(value, types.FunctionType):
            w = logfunction(value,
                            displayName="%s.%s" %(cls.__name__, value.__name__))
            setattr(cls, name, staticmethod(w))
    return cls

class LogMetaClass(type):
    """
    Alternative to logclass(), you set this as a class's __metaclass__.

    It will not work if the metaclass has already been overridden (e.g.
    schema.Item or zope.interface (used in Twisted)

    Also, it should fail for class/staticmethods, that hasnt been added here
    yet.
    """

    def __new__(cls,classname,bases,classdict):
        logmatch = re.compile(classdict.get('logMatch','.*'))
        lognotmatch = re.compile(classdict.get('logNotMatch', 'nevermatchthisstringasdfasdf'))

        for attr,item in list(classdict.items()):
            if callable(item) and logmatch.match(attr) and not lognotmatch.match(attr):
                classdict['_H_%s'%attr] = item    # rebind the method
                classdict[attr] = logmethod(item) # replace method by wrapper

        return type.__new__(cls,classname,bases,classdict)
# ---------------------------- Tests and examples ----------------------------

if __name__=='__main__':
    print(); print("------------------- single function logging ---------------")
    @logfunction
    def test():
        return 42

    test()

    print(); print("------------------- single method logging -----------------")
    class Test1(object):
        def __init__(self):
            self.a = 10

        @logmethod
        def add(self,a,b): return a+b

        @logmethod
        def fac(self,val):
            if val == 1:
                return 1
            else:
                return val * self.fac(val-1)

        @logfunction
        def fac2(self, val):
            if val == 1:
                return 1
            else:
                return val * self.fac2(val-1)

    t = Test1()
    t.add(5,6)
    t.fac(4)
    print("--- tagged as @logfunction, doesn't understand 'self' is special:")
    t.fac2(4)


    print(); print("""-------------------- class "decorator" usage ------------------""")
    class Test2(object):
        #will be ignored
        def __init__(self):
            self.a = 10
        def ignoreThis(self): pass


        def add(self,a,b):return a+b
        def fac(self,val):
            if val == 1:
                return 1
            else:
                return val * self.fac(val-1)

    Test2 = logclass(Test2, logMatch='fac|add')

    t2 = Test2()
    t2.add(5,6)
    t2.fac(4)
    t2.ignoreThis()


    print(); print("-------------------- metaclass usage ------------------")
    class Test3(object, metaclass=LogMetaClass):
        logNotMatch = 'ignoreThis'

        def __init__(self): pass

        def fac(self,val):
            if val == 1:
                return 1
            else:
                return val * self.fac(val-1)
        def ignoreThis(self): pass
    t3 = Test3()
    t3.fac(4)
    t3.ignoreThis()

    print(); print("-------------- testing static & classmethods --------------")
    class Test4(object):
        @classmethod
        def cm(cls, a, b):
            print(cls)
            return a+b

        def im(self, a, b):
            print(self)
            return a+b

        @staticmethod
        def sm(a,b): return a+b

    Test4 = logclass(Test4)

    Test4.cm(4,3)
    Test4.sm(4,3)

    t4 = Test4()
    t4.im(4,3)
    t4.sm(4,3)
    t4.cm(4,3)
