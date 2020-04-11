from dsk.base.utils import logtrace
##################################################
#  new class
# class definition
class myclassname1(object):
    def __init__(self):
        super(myclassname1, self).__init__()
        from dsk.base.tdata.taskdata.tp_variable import TpVariable,ProcessVar

        # instance
        self.CFD = TpVariable()
        self.CFD.set_with_dict({u'debug': True, u'prefefile': u'cfdfoo'})
        self.RTD = TpVariable()
        self.RTD.set_with_dict({u'debug': False, u'showname': u'devshow'})
        self.TP = ProcessVar()
        ##########end init

    def doIt(self,RTD=None,CFD=None,TP=None):
        CFD = self.CFD.overwrite(CFD)
        RTD = self.RTD.overwrite(RTD)
        TP = self.TP.overwrite(TP)



        #
        # firstTask -- this is a comment
        #
        import dskenv.api.dsk_naming
        a = dskenv.api.dsk_naming.DskNaming()


        #
        # secondTask
        #
        show=RTD.showname
        print a
        print a.get_base_project_config(show)
        print a.get_base_version_pack(show)
        print RTD
        print RTD.get_as_dict()
        print CFD.get_as_dict()
        print TP.get_as_dict()

myclassname1 = logtrace.logclass(myclassname1)

#########################
objectProc = myclassname1()
objectProc.doIt()
        