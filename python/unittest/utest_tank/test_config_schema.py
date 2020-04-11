"""Test the current sgtk core configuration
"""
import pytest
import os
import sys
import getpass
from pprint import pprint

print "WithPython version \"%s\"" % (".".join(str(i) for i in sys.version_info[0:3]),)

#import sgtk.platform
root_tk = os.environ.get("TANK_CURRENT_PC","")
if root_tk in [None,""]:
    root_tk = "/Users/sgtk/dev/eric/devshow"  # this should be removed
    print "testing in a dev environment init to %s for now" % root_tk
    print "set your TANK_CURRENT_PC environment to your config to be tested"

if root_tk == "/u/sgtk/studio":
    raise Exception("For dev or td nothing should point to this config/ studio config")

try:
    import sgtk
except:
    python_path = os.path.abspath(os.path.join(root_tk, "install","core","python"))
    print "Adding sgtk location to python_path: %s" % python_path
    sys.path.insert(0,python_path)


from sgtk.pipelineconfig import PipelineConfiguration

# a config file
cf = PipelineConfiguration(root_tk)

def read_ignore_files(schema_config_path):
    """
    Reads ignore_files from root of schema if it exists.
    Returns a list of patterns to ignore.
    """
    ignore_files = []
    file_path = os.path.join(schema_config_path, "ignore_files")
    if os.path.exists(file_path):
        open_file = open(file_path, "r")
        try:
            for line in open_file.readlines():
                # skip comments
                if "#" in line:
                    line = line[:line.index("#")]
                line = line.strip()
                if line:
                    ignore_files.append(line)
        finally:
            open_file.close()
    return ignore_files

def test_schema_file_exist():
    """ check if all the xml file for definition exists """
    schema_config_path = cf.get_schema_config_location()
    print "Schema location",schema_config_path
    ignore_files = read_ignore_files(schema_config_path)
    print "ignore_files:",ignore_files