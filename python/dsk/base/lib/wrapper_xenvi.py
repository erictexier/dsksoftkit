import os
import sys
import argparse

TAG_LAUNCH = '_enviwrapper'


try:
    from dskenv.api.dsk_naming import DskNaming
except ImportError:
    sys.exit(0)

class WrapperXenvi(object):
    def __init__(self):
        super(WrapperXenvi, self).__init__()

    def execute(self,
                envi_config,
                project_name,
                application,
                with_system = False,
                with_farm = False,
                do_log = True,
                user_login = "",
                user_file = "",
                dry_run=False,
                do_verbose=False,
                launch_as_python=True):
        """Generic launch for envi

        :param envi_config: a valid config directory
        :param project_name: ex: dev_show
        :param application: ex: maya,Nuke ...
        :param with_system: default = False
        :param with_farm: default(False), insert a deadline pack
        :param do_log: default = True
        :param user_login: default = "" loging of a user with home package
        :param user_file: default = ""
        :param dry_run: default=False
        :param do_verbose: default=False
        :param launch_as_python:  default=False otherwise launch in python

        """
        application_exec = application
        application_tag = application_exec+TAG_LAUNCH
        os.environ['DSK_ENGINE'] = application_tag.lower()

        log_file = ""
        if do_log:
            log_file = DskNaming.generic_launch_log_file(application_tag)


        add_history = True

        # config
        x = [[]]
        if os.environ.get('SKIP_ENVI_CONFIG',"") != "":
            #dump_value_cache(project_name,[])
            sys.stderr.write("SKIP_ENVI_CONFIG set: Skipping envi, reading history")
            add_history = False
            x = DskNaming.get_history_command(with_app = True, remove_app = True)

        else:
            #Envi.load_base_show(project_name, user_file)
            x = DskNaming.project_configuration(envi_config,
                                                project_name = project_name,
                                                with_system = with_system,
                                                user_file = user_file,
                                                user_login = user_login)

            if do_log:
                x = DskNaming.do_log(x, log_file)

            # first show execution execute
            DskNaming.do_execute(x,envi_config)
            if do_verbose == True or dry_run == True:
                for xx in x:
                    sys.stdout.write("envi %s\n" % " ".join(xx))

            # this will return the default set of config and pack based on convention
            # you can also provide or add your own set of config and pack
            # this is just
            x = DskNaming.configuration(envi_config,
                                        project_name = project_name,
                                        app_name = application_exec,
                                        with_sgtk = False,
                                        sgtk_path = "",
                                        user_login = user_login,
                                        with_base = False,
                                        with_td = False)

        if do_verbose == True:
            out = sys.stderr.write
            out("Using config in %s\n" % envi_config)
            out("Launching %r for project %r\n" % (application_exec,project_name))
            if user_login != "":
                out("Warning, envi will use %r home data\n" % user_login)


        if with_farm == True:
            # Extra package
            if do_verbose == True:
                sys.stdout.write("adding deadline\n")
            x = DskNaming.do_extrapackage(x, ["-p deadline"])


        # application
        #x = DskNaming.do_app(x, application_exec)



        #if you don't wantloging  comment out the following lines
        if do_log:
            if do_verbose == True:
                sys.stdout.write("launch will be logging to %s\n" % log_file)

            x = DskNaming.do_log(x, log_file)

        if do_verbose == True or dry_run == True:
            for xx in x:
                sys.stdout.write("envi %s\n" % " ".join(xx))

        if dry_run == False:
            if launch_as_python == True:
                DskNaming.do_execute(x, envi_config)
            else:
                launchfile = DskNaming.build_launch_bash(x,
                                                         envi_config,
                                                         app_tag = application_tag,
                                                         add_history = add_history,
                                                         split_launch=True
                                                         )
                if do_verbose:
                    sys.stdout.write("".join(open(launchfile,"a+").readlines()))
                    sys.stdout.write("\n")
                DskNaming.launch_batch_file(launchfile)
            return True
