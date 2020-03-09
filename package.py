name = "devsoftkit"

version = "1.0.1"

authors = [
    "erictexier"
]

description = \
    """
    Python-based devsoftkit package.
    """

tools = [
    "launch_auth"
]

requires = [
    "python-2.7"
]

uuid = "dsk.hello_world_py"

def commands():
    env.PYTHONPATH.append("{root}/python")
    env.PATH.append("{root}/bin")