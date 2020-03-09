import types
from dsk.base.tdata.taskdata.gen_task import GenTask,AttrDescription,RequiredFieldError

class GenPackageTask(GenTask):
    _attr_PackageTask = [AttrDescription('file',types.StringType, 'simpleLineEdit', GenTask.zone,GenTask.set_zone,True),
                         AttrDescription('preExec',types.StringType, 'multipleLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,False),
                         AttrDescription('postExec',types.StringType, 'multipleLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,False)
                         ]
    _LockupPackageAttr = dict()
    for i in _attr_PackageTask:
        _LockupPackageAttr[i.name] = i

    def __init__(self):
        super(GenPackageTask, self).__init__()

    @classmethod
    def get_lock_up(cls):
        return cls._LockupPackageAttr

    def update_with(self,atask,lockup = None,attribList=None):
        super(GenPackageTask, self).update_with(atask,
                                                GenPackageTask._LockupPackageAttr,
                                                GenPackageTask._attr_PackageTask)

    def to_python(self,stream,acontext):
        from dsk.base.tdata.taskdata.taskdata_api import TaskDataApi
        super(GenPackageTask, self).to_python(stream,acontext)
        tab = acontext['tab']
        if acontext.has_key('doTaskPackage') and acontext['doTaskPackage'] == False:
            stream.write("%s#TaskPackage turn off\n" % tab)
            return
        afile  = GenPackageTask._LockupPackageAttr['file'].get(self,'file')
        preExec  = GenPackageTask._LockupPackageAttr['preExec'].get(self,'preExec')
        postExec  = GenPackageTask._LockupPackageAttr['postExec'].get(self,'postExec')
        if postExec == "":
            postExec = None
        if afile == None or afile == "":
            raise RequiredFieldError("cannot build the taskPackage without a file")

        if preExec != None:
            sc = preExec.split("\n")
            for i in sc:
                stream.write("%s%s\n" % (tab,i))
        # to valid the TASK interface
        stream.write("%sTASK = n = %s()\n" % (tab,
                                              TaskDataApi.get_class_name_from_package(afile))) # make TASK accessible for preExec

        stream.write("%sn.doIt(RTD,CFD,TP)\n" % tab)

        if postExec != None:
            sc = postExec.split("\n")
            for i in sc:
                stream.write("%s%s\n" % (tab,i))

        # update the package loaded
        if not afile in acontext['taskPackageLoaded']:
            acontext['taskPackage'].append(afile)