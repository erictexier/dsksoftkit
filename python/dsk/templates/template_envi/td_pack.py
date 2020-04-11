DATA_PACK ="""import os
showname = "%(project_name)s"
sgtk_td_base = "%(git_clone_area)s"

# set the studio td local
set_path("SGTKRELEASE","{}/SgtkStudio".format(sgtk_td_base))
set_path("SGTKFLAG","")

# set the show td local
set_path("PROD_TD_ROOT",   "{}/prod-td-{}".format(sgtk_td_base,showname))
add_path("PYTHON_PRE_PATH","{}/prod-td-{}/maya/scripts/python".format(sgtk_td_base,showname))
add_path("PYTHON_PRE_PATH","{}/prod-td-{}/lib".format(sgtk_td_base,showname))
"""