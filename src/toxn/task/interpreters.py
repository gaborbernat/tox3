"""
Interpreters have two main keys:

- name (by default python, but can be overwritten to other, e.g. pypy),
- version (uses PEP-440 version scheme - https://www.python.org/dev/peps/pep-0440/#version-scheme).

In order to specify a tasks python interpreter one uses PEP-440 version constraint format
(https://www.python.org/dev/peps/pep-0440/#version-specifiers). In case of a range specifier
the latest available Python will be used (in spirit of newer -> faster).


The lookup strategy for versions is as follows, in this order:

- use the systems shell to acquire the interpreter (e.g. try to invoke {name}{version_part}) in the shell
  (looks in systems underlying PATH specification; note on Windows symlinks won PATH will not work, but
  ``bat`` proxy files do)
- on Windows will look under ``[CDZ]:\\<folder>\\python.exe``,
- the current invoked Python interpreter used to invoke tox.
"""
import os
import re
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import py  # type: ignore
from packaging.requirements import Requirement

from toxn.config.models.venv import Python, VersionInfo
from toxn.util import CmdLineBufferPrinter, Loggers, run


class CouldNotFindInterpreter(ValueError):
    pass


async def find_python(python: str, logger: Loggers) -> Python:
    base_python_exe = get_interpreter(python, logger)
    logger.info('%s resolves as %s', python, base_python_exe)
    return await get_python_info(base_python_exe, logger)


async def get_python_info(base_python_exe: Path, logger: Loggers) -> Python:
    printer = CmdLineBufferPrinter(limit=None)
    await run([str(base_python_exe), "-c",
               "import sys; print(repr( (sys.executable, sys.version, tuple(sys.version_info))) )"],
              stdout=printer, logger=logger)
    exec_path, version, info = eval(printer.elements.pop(), {}, {})
    return Python(Path(exec_path), version, VersionInfo(*info[:5]))


python_req = re.compile(r'(?P<op>[<>=])(?P<val>[0-9.]+)')


async def find_interpreter(req: Requirement, logger: Loggers) -> Python:
    """

    :param req: the requirement for the interpreter to locate
    :return: the path to an interpreter that satisfies the requirement
    :raises CouldNotFindInterpreter: if not interpreter matching the requirement could be found
    """
    if req.url:
        res = urlparse(req.url)
        if res.scheme == 'file' and res.hostname == 'localhost':
            path = Path(res.path)
            if path.exists() and path.is_file():
                return await get_python_info(path, logger)
            raise CouldNotFindInterpreter(f'specified path {req.url} does not exist')
        raise CouldNotFindInterpreter(f'invalid url of {req.url}')
    else:
        pass


def get_interpreter(name: str, logger: Loggers) -> Path:
    """For a requirement string, get the correct interpreter.

    :param name:
    :param logger:
    :return:
    """

    # noinspection PyCallByClass
    requires = name.split(',')
    for req in requires:
        req = re.sub(r"\s+", "", req, flags=re.UNICODE)

    binary_str = py.path.local.sysfind(name)
    if binary_str is not None:
        return Path(binary_str)

    match = re.match(r"python(\d)\.(\d+)", name)
    binary = None
    if match and sys.platform == "win32":
        major, minor = match.groups()
        pattern = re.compile(f'python{major}{minor}', re.IGNORECASE)
        # The standard names are in predictable places.
        drives = ['C', 'D', 'Z']
        for drive in drives:
            base = Path(f'{drive}:\\')
            for folder in base.iterdir():
                if pattern.match(folder.name):
                    binary = folder / 'python.exe'
                    if binary.exists():
                        return binary
                    else:
                        binary = None
        if binary is None:
            binary = locate_via_py(logger, major, minor)
    else:
        binary = sys.executable
    if binary is not None and binary.exists():
        return binary

    if binary is None:
        raise CouldNotFindInterpreter('could not find {}, sys path {!r}'.format(name, os.environ.get('PATH')))
    return Path(binary)


def locate_via_py(logger: Loggers, v_maj: str, v_min: str) -> Optional[Path]:
    ver = "-%s.%s" % (v_maj, v_min)
    py_exe = py.path.local.sysfind('py')
    if py_exe is not None:
        printer = CmdLineBufferPrinter(limit=1)
        result = run([py_exe, ver, '-c', "import sys; print(sys.executable)"], stdout=printer, logger=logger,
                     exit_on_fail=False)
        if result:
            return Path(printer.last)
    return None
