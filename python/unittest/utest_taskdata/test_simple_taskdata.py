import pytest
import base64
from dsk.base.tdata.taskdata.gen_task import GenTask
from dsk.base.tdata.taskdata.genpy_task import GenPyTask
from dsk.base.tdata.taskdata.genpyimport_task import GenPyImportTask
from dsk.base.tdata.taskdata.gengroup_task import GenGroupTask
from dsk.base.tdata.taskdata.gennope_task import GenNopeTask
from dsk.base.tdata.taskdata.genexternal_task import GenExternalTask
from dsk.base.tdata.taskdata.genpackage_task import GenPackageTask
from dsk.base.tdata.taskdata.genmel_task import GenMelTask

@pytest.mark.skipif(True, reason="too long to wait")
def test_pytask():
    """ create a PyTask """
    t = GenPyTask()
    t.setName("firstTask")
    assert t.getTypeName()
    assert None == t.set_comment("this is a comment")
    assert t.get_comment() == "this is a comment"
    lockup = t.get_lock_up()
    #for l in  lockup:
    #    print l
    assert t.isEnable()
    assert 'module' in lockup
    assert 'handler' in lockup

    assert t.set("module","dskenv.api.envi_api") == True

    assert t.get_argument_string() == ""
    assert t.get_attribute_names() != ""
    assert isinstance(t.get_attribute_names(), list)
    assert t.is_script() == False
    #print "1",GenPyTask._LockupPyAttr['handler'].get(t,'handler')
    assert t.set("handler","exec") == True
    assert t.is_script() == True

    #print "2",GenPyTask._LockupPyAttr['handler'].get(t,'handler')
    #print "3",GenPyTask._LockupPyAttr['command'].get(t,'command')

    #print "4",t.get_attribute_name_and_type()
    #print "5",t.get_attribute_name_and_typeUI()

@pytest.mark.skipif(False, reason="too long to wait")
def test_group():
    """Simple creation 2 task, serialize, deserialize
    """
    t1 = GenPyTask()
    t1.setName("firstTask2")
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
    assert t2.set("command","show='dev_show'\nprint a\nprint a.get_base_project_config(show)\nprint a.get_base_version_pack(show)")
    #g = GenPyTask()
    g = GenGroupTask()
    g.setName("TaskList")
    g.addChild(t1)
    g.addChild(t2)
    streamlist, taskpackage = GenTask.to_python_one_package(g,
                                                            "myclassname",
                                                            False,
                                                            False,
                                                            [],
                                                            packName="")
    #print taskpackage
    vallist = []
    for s in streamlist:
        val = s.getvalue()
        print val
        vallist.append(val)
    x = g.Serialize("tasks.xml")
    x = base64.encodestring(x)
    #print "serializeaaaa->",x,"<-"
    x = base64.decodestring(x)
    dx = GenTask().Deserialize(x)
    newone = dx.load(-1)[0]

    streamlist2, taskpackage = GenTask.to_python_one_package(newone,
                                                             "myclassname",
                                                             False,
                                                             False,
                                                             [],
                                                             packName="")
    vallist2 = []
    for s in streamlist2:
        val = s.getvalue()
        vallist2.append(val)

    for s1,s2 in zip(vallist,vallist2):
        assert s1 == s2
