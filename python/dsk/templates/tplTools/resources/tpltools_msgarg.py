_DATA='''from dsk.base.lib.msg_arg import MsgArg

class Msg%(TplToolsClassRoot)s(MsgArg):
    def __init__(self,widfrom,grp):
        super(Msg%(TplToolsClassRoot)s, self).__init__(widfrom,grp)
'''