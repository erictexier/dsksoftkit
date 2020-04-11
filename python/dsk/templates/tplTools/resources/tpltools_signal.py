_DATA='''from dsk.base.lib.signal_info import signalInfo
from dsk.base.resources.browser_signal import SINGLE_ARG

%(tool_signal_name)s = signalInfo('%(module_name)s_%(tool_fname)s',SINGLE_ARG)
'''