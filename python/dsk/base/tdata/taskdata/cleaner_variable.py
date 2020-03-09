import types
import re
from collections import namedtuple

#####################################################################
class ResultCommand(namedtuple('ResultCommand', 'success  newCommand addOn')):
    __slots__ = ()

def remove_extern_quote(vs):
    assert type(vs) in types.StringTypes
    if len(vs) < 2:
        return vs
    if (vs[0] == "'" and vs[-1] == "'") or (vs[0] == '"'  and vs[-1] =='"'):
        vs = vs[1:-1]
    return vs


def remove_extern_bracket(vs):
    assert type(vs) in types.StringTypes
    if len(vs) < 2:
        return vs
    if vs[0] == "[" and vs[-1] == "]":
        vs = vs[1:-1]
    return vs


def remove_extern_cbracket(vs):
    assert type(vs) in types.StringTypes
    if len(vs) < 2:
        return vs
    if vs[0] == "{" and vs[-1] == "}":
        vs = vs[1:-1]
    return vs


_GLOB = "(TP|TASK|TASKINFO|TASKINFO|RTD|CFD)"
ALL_KEYS = _GLOB.split("|")[1:-1]
######## clean command  function
class CleanCommand(object):

    _ii = "(s|r|d|f|x|lx)"
    def __init__(self):
        super(CleanCommand,self).__init__()
        allc = "%\(" + _GLOB + ".[\.\w\d\[\]\"\']*\)" + CleanCommand._ii
        self._p = re.compile(allc, re.DOTALL)
        self._found = []
    def reset(self):
        self._found = []
    def get_count(self):
        return len(self._found)
    def get_patern(self):
        return self._p
    def __call__(self,m):
        self._found.append(m.group())
        return "%" + m.group()[m.group().rfind(")")+1:]
    def get_python_syntax(self):
        if self.get_count() == 0:
            return ResultCommand(False,"","")
        clean = map(lambda x:x.replace("%(","").replace(")s",""),self._found)
        if self.get_count() == 1:
            return ResultCommand(True,"","% " + clean[0])
        return ResultCommand(True,"","% (" + ",".join(clean) + ")")

_globalCleanCommand = CleanCommand()

def do_clean_command(command):

    _globalCleanCommand.reset()
    cmd = _globalCleanCommand.get_patern().sub(_globalCleanCommand,command)
    res = _globalCleanCommand.get_python_syntax()
    if res.success:
        return ResultCommand(res.success,cmd,res.addOn)
    return res

######## clean function argument
class CleanArgument(object):
    _ii = "(s|r|d|f|x|lx)"
    def __init__(self):
        super(CleanArgument,self).__init__()
        all1 = "\'" + _GLOB + "[\.\w\d\[\]\"]*\'" # start/end with single quote
        self._p1 = re.compile(all1,re.DOTALL)
        all2 = '\"' + _GLOB + '[\.\w\d\[\]\']*\"' # start/end with double quote
        self._p2 = re.compile(all2,re.DOTALL)
    def get_patern_single_quote(self):
        return self._p1
    def get_patern_double_quote(self):
        return self._p2
    def __call__(self,m):
        return m.group()[1:-1] # clean up the quote

_globalCleanQuote = CleanArgument()

def clean_quote(astring):
    astring = _globalCleanQuote.get_patern_single_quote().sub(_globalCleanQuote,astring)
    return _globalCleanQuote.get_patern_double_quote().sub(_globalCleanQuote,astring)


def quote_if_needed(astring):
    for k in ALL_KEYS:
        if astring.startswith(k):
            return astring

    return "%r" % astring

def remove_over_quoted(vs):
    """Some expression in argument like 'RTD.ffff["string"] + "--caco"'
    are overquote.... needs to return RTD.ffff["string"] + "--caco" instead
    """
    # check first if this is the case
    vs1 = remove_extern_quote(vs)
    if vs1 == vs:
        return vs
    # if no more quote exist it needed to be quote
    if vs1.find("'") == -1 and vs1.find('"') == -1:
        return vs
    return vs1

