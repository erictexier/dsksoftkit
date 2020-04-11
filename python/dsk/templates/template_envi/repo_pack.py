DATA_PACK ="""import os
base_release = "%(rootname)s"
version = ""


add_path("PYTHONPATH",os.path.join(base_release, version, "python"))
#add_path("PATH",os.path.join(base_release, version, "python","bin"))
"""