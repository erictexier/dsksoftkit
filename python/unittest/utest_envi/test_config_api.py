import pytest
import os
from dskenv import dskenv_constants

from dskenv.api.dsk_naming import DskNaming
proj = "dev_show"
apath = os.path.join(os.sep,
                     dskenv_constants.DSK_MOUNTED_ROOT,
                     dskenv_constants.DSK_DEV_AREA,
                     'eric',
                     dskenv_constants.DSK_CONFIGURATION_FOLDER,
                     dskenv_constants.DSK_ENVI_FOLDER)

def test_maya_config():

    x = DskNaming.configuration(apath,
                                project_name = proj,
                                app_name = "maya",
                                sgtk_path = "",
                                with_base = True)
    assert len(x) == 2

    x = DskNaming.configuration(apath,
                                project_name = proj,
                                app_name = "maya",
                                sgtk_path = "/Users/sgtk/dev/eric/dont",
                                with_base = True)

    assert len(x) == 2

    x = DskNaming.configuration(apath,
                                project_name = proj,
                                app_name = "maya",
                                sgtk_path = "/Users/sgtk/dev/eric/dont",
                                with_base = False)

    assert len(x) == 2

@pytest.mark.skipif(True, reason="too long to wait")
def test_outline_zlaunch():
    import os
    application_exec = "maya"
    application_tag = "maya"
    os.environ['DSK_ENGINE'] = application_tag

    x = DskNaming.configuration("/u/dev/DskWS/devenvETEXIER",
                                project_name = proj,
                                app_name = "maya",
                                sgtk_path = "/u/sgtk/dev/eric/dont",
                                with_base = True)

    # add app and Deamonize flag to all envi command
    last = x[-1]
    last.append("-a %s" % application_exec)
    last.append("-Deamon")
    log_file = DskNaming.generic_launch_log_file(application_tag)
    envicommands = list() # add log file to all file
    for i in x:
        i.append("-l %s" % log_file)
        envicommands.append(" ".join(i))

    launchfile = DskNaming.build_launch_bash(envicommands,
                                             apath,
                                             app_tag = application_tag
                                             )
    print("\nlaunchfile %r\n" % launchfile)
    print(open(launchfile,"r").read())
    DskNaming.launch_batch_file(launchfile)


@pytest.mark.skipif(False, reason="too long to wait")
def test_outline_wrapped_api():
    import os
    application_exec = "maya"
    application_tag = "maya"
    os.environ['DSK_ENGINE'] = application_tag

    x = DskNaming.configuration(apath,
                                project_name = proj,
                                app_name = "maya",
                                sgtk_path = "/u/sgtk/dev/eric/dont",
                                with_base = True)
    log_file = DskNaming.generic_launch_log_file(application_tag)
    x = DskNaming.do_log(x, log_file)
    x = DskNaming.do_app(x, application_exec)
    x = DskNaming.do_debug(x)

    print(x)
    #    envicommands.append(" ".join(i))

    launchfile = DskNaming.build_launch_bash(x,
                                             apath,
                                             app_tag = application_tag
                                             )
    print("\nlaunchfile %r\n" % launchfile)
    print(open(launchfile,"r").read())
    DskNaming.launch_batch_file(launchfile)


@pytest.mark.skipif(True, reason="too long to wait")
def test_outline_zlaunch_from_scratch():
    import os
    application_exec = "maya"
    application_tag = "maya"

    os.environ['DSK_ENGINE'] = application_tag

    x = DskNaming.configuration(apath,
                                project_name = proj,
                                app_name = "maya",
                                sgtk_path = "/u/sgtk/dev/eric/dont",
                                with_base = True)


    print "x->",x

    # add app and Deamonize flag to all envi command
    last = x[-1]
    last.append("-a %s" % application_exec)
    last.append("-Deamon")
    log_file = DskNaming.generic_launch_log_file(application_tag)
    #x = DskNaming.do_log(x,log_file)
    envicommands = list() # add log file to all file
    for i in x:
        i.append("-l %s" % log_file)
        envicommands.append(" ".join(i))

    launchfile = DskNaming.build_launch_bash(envicommands,
                                             apath,
                                             app_tag = application_tag,
                                             add_default_env = None) # <-------
    print("\nlaunchfile %r\n" % launchfile)
    print(open(launchfile,"r").read())
    # real launch
    #DskNaming.launch_batch_file_with_console(launchfile,clean_tmp_dir = True)
    #DskNaming.launch_batch_file_with_console(launchfile,console='konsole')
    #DskNaming.launch_batch_file_with_console(launchfile,console='gnome-terminal')