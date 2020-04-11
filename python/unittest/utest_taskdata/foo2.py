from dsk.base.utils import logtrace
##################################################
#  new class
# class definition
class myclassname(object):
    def __init__(self):
        super(myclassname, self).__init__()
        from dsk.base.tdata.taskdata.tp_variable import TpVariable,ProcessVar

        # instance
        self.CFD = TpVariable()
        self.CFD.set_with_dict({u'debug': True, u'prefefile': u'cfdfoo'})
        self.RTD = TpVariable()
        self.RTD.set_with_dict({u'debug': False, u'showname': u'devshow'})
        self.TP = ProcessVar()
        ##########end init

    def MainGroup(self,RTD=None,CFD=None,TP=None):
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


        #
        # doIt2
        #
        self.doIt2(RTD,CFD,TP)


    ##############################
    def doIt2(self,RTD,CFD,TP):


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


        #
        # amayatask
        #
        print 'before maya'
        print 'befor maya second line'
        self.amayatask(RTD,CFD,TP)
        print 'after maya'


        #
        # apackage
        #
        #TaskPackage turn off
        return


    ##############################
    def amayatask(self,RTD,CFD,TP):

        def remote_amayatask(RTD,CFD,TP):


            #
            # firstTaskinmaya -- this is in maya
            #
            import dskenv.api.dsk_naming
            a = dskenv.api.dsk_naming.DskNaming()


            #
            # second Taskinmaya -- this is in maya2
            #
            import dskenv.api.dsk_naming33
            a = dskenv.api.dsk_naming33.DskNaming()
        
        if TP.is_remote():
            TP.set_remote(False)
            return remote_amayatask(RTD,CFD,TP)
        else:
            from dsk.base.lib.wrapper_xenvi import WrapperxEnvi
                #-->bool(True) wait
        #-->bool(True) daemon
        #-->print 'after maya' postExec


myclassname = logtrace.logclass(myclassname)

#########################
objectProc = myclassname()
objectProc.doIt()
        