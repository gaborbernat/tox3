import py


def get_interpreter(name):
    binary = py.path.local.sysfind(name)
    return binary
