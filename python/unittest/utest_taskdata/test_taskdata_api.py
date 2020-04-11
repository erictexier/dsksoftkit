from dsk.base.tdata.taskdata.gen_task import GenTask
from dsk.base.tdata.taskdata.genpy_task import GenPyTask
from dsk.base.tdata.taskdata.gengroup_task import GenGroupTask
from dsk.base.tdata.taskdata.genexternal_task import GenMayaTask,GenExternalTask
from dsk.base.tdata.taskdata.genpackage_task import GenPackageTask

from dsk.base.tdata.taskdata.tp_variable import TpVariable

from dsk.base.tdata.taskdata.taskdata_api import TaskDataApi

ashowname = 'dev_show'


def test_taskdata_api():
    t1 = GenPyTask()
    t1.setName("firstTask")
    assert t1.getTypeName()
    assert None == t1.set_comment("this is a comment")
    assert t1.get_argument_string() == ""
    assert t1.get_attribute_names() != ""
    assert isinstance(t1.get_attribute_names(), list)
    assert t1.get_lock_up()
    #print t1.get_lock_up()
    assert t1.is_script() == False
    assert t1.set("module","dskenv.api.dsk_naming") == True
    assert t1.set("command","DskNaming")
    assert t1.set("output","a")

    t2 = GenPyTask()
    t2.setName("secondTask")
    assert t2.set("handler","exec") == True
    full_text = list()
    full_text.append("show=RTD.showname\nprint a\nprint a.get_base_project_config(show)\nprint a.get_base_version_pack(show)\nprint RTD")
    full_text.append("print RTD.get_as_dict()")
    full_text.append("print CFD.get_as_dict()")
    full_text.append("print TP.get_as_dict()")
    assert t2.set("command","\n".join(full_text))

    rtd = TpVariable()
    rtd.showname = ashowname
    rtd.debug = False
    cfd = TpVariable()
    cfd.prefefile = "cfdfoo"
    cfd.debug = True


    g = GenGroupTask()
    g.setName("doIt")
    g.setVariable(rtd, cfd)
    g.addChild(t1)
    g.addChild(t2)
    value = TaskDataApi.dumps_to_python(loadedTp = g,
                                        className = "myclassname1",
                                        skipComment = False,
                                        doTaskPackage = False,
                                        doTrace=True,
                                        searchPath=None,
                                        mainType="instance")
    #print value


    open("foo.py","w").write(value)
    #exec(value)
    code = compile(value, '<string>', 'exec')
    ns = {}
    exec code in ns
    assert ns['objectProc'].RTD.showname == ashowname


def test_taskdata_api_group():
    t1 = GenPyTask()
    t1.setName("firstTask")
    assert t1.getTypeName()
    assert None == t1.set_comment("this is a comment")
    assert t1.get_argument_string() == ""
    assert t1.get_attribute_names() != ""
    assert isinstance(t1.get_attribute_names(), list)
    assert t1.get_lock_up()
    #print t1.get_lock_up()
    assert t1.is_script() == False
    assert t1.set("module","dskenv.api.dsk_naming") == True
    assert t1.set("command","DskNaming")
    assert t1.set("output","a")

    t2 = GenPyTask()
    t2.setName("secondTask")
    assert t2.set("handler","exec") == True
    full_text = list()
    full_text.append("show=RTD.showname\nprint a\nprint a.get_base_project_config(show)\nprint a.get_base_version_pack(show)\nprint RTD")
    full_text.append("print RTD.get_as_dict()")
    full_text.append("print CFD.get_as_dict()")
    full_text.append("print TP.get_as_dict()")
    assert t2.set("command","\n".join(full_text))


    t3 = GenPyTask()
    t3.setName("firstTask")
    assert t3.getTypeName()
    assert None == t3.set_comment("this is a comment")
    assert t3.get_argument_string() == ""
    assert t3.get_attribute_names() != ""
    assert isinstance(t3.get_attribute_names(), list)
    assert t3.get_lock_up()
    #print t3.get_lock_up()
    assert t3.is_script() == False
    assert t3.set("module","dskenv.api.dsk_naming") == True
    assert t3.set("command","DskNaming")
    assert t3.set("output","a")

    t4 = GenPyTask()
    t4.setName("secondTask")
    assert t4.set("handler","exec") == True
    full_text = list()
    full_text.append("show=RTD.showname\nprint a\nprint a.get_base_project_config(show)\nprint a.get_base_version_pack(show)\nprint RTD")
    full_text.append("print RTD.get_as_dict()")
    full_text.append("print CFD.get_as_dict()")
    full_text.append("print TP.get_as_dict()")
    assert t4.set("command","\n".join(full_text))



    rtd = TpVariable()
    rtd.showname = ashowname
    rtd.debug = False
    cfd = TpVariable()
    cfd.prefefile = "cfdfoo"
    cfd.debug = True


    g = GenGroupTask()
    g.setName("MainGroup")
    g.setVariable(rtd, cfd)
    g.addChild(t1)
    g.addChild(t2)

    g2 = GenGroupTask()
    g2.setName("doIt2")
    g2.setVariable(rtd, cfd)
    g2.addChild(t3)
    g2.addChild(t4)

    g.addChild(g2)


    tmaya = GenExternalTask()
    tmaya.setName("amayatask")
    assert tmaya.set("preExec","print 'before maya'\nprint 'befor maya second line'")
    assert tmaya.set("postExec","print 'after maya'")
    assert tmaya.set("block",True)
    assert tmaya.set("daemon",True)
    g2.addChild(tmaya)


    # task in maya 1
    taskinmaya = GenPyTask()
    taskinmaya.setName("firstTaskinmaya")
    assert taskinmaya.getTypeName()
    assert None == taskinmaya.set_comment("this is in maya")
    assert taskinmaya.get_argument_string() == ""
    assert taskinmaya.get_attribute_names() != ""
    assert isinstance(taskinmaya.get_attribute_names(), list)
    assert taskinmaya.get_lock_up()
    #print taskinmaya.get_lock_up()
    assert taskinmaya.is_script() == False
    assert taskinmaya.set("module","dskenv.api.dsk_naming") == True
    assert taskinmaya.set("command","DskNaming")
    assert taskinmaya.set("output","a")
    tmaya.addChild(taskinmaya)

    # task in maya 2
    taskinmaya2 = GenPyTask()
    taskinmaya2.setName("second Taskinmaya")
    assert taskinmaya2.getTypeName()
    assert None == taskinmaya2.set_comment("this is in maya2")
    assert taskinmaya2.get_argument_string() == ""
    assert taskinmaya2.get_attribute_names() != ""
    assert isinstance(taskinmaya2.get_attribute_names(), list)
    assert taskinmaya2.get_lock_up()
    #print taskinmaya.get_lock_up()
    assert taskinmaya2.is_script() == False
    assert taskinmaya2.set("module","dskenv.api.dsk_naming33") == True
    assert taskinmaya2.set("command","DskNaming")
    assert taskinmaya2.set("output","a")
    tmaya.addChild(taskinmaya2)



    tpackage = GenPackageTask()
    tpackage.setName("apackage")
    tpackage.set("file","/mnt/dev/eric/packages/devsoftkit/python/unittest/utest_taskdata/doIt.tpp.gz")
    g2.addChild(tpackage)


    value = TaskDataApi.dumps_to_python(loadedTp = g,
                                        className = "myclassname",
                                        skipComment = False,
                                        doTaskPackage = False,
                                        doTrace=True,
                                        searchPath="",
                                        mainType="instance")
    #print value

    open("foo2.py","w").write(value)
    """
    #exec(value)
    code = compile(value, '<string>', 'exec')
    ns = {}
    exec code in ns
    assert ns['objectProc'].RTD.showname == ashowname
    """
    TaskDataApi.save_tp(g)



