import logging
from pathlib import Path
from typing import NamedTuple, Tuple

import py

from .util import CmdLineBufferPrinter, run


class Python(NamedTuple):
    python_name: str
    exe: Path
    version: str
    version_info: Tuple[int, int, int, str]

    @property
    def major_version(self) -> int:
        return self.version_info[0]


async def find_python(python: str) -> Python:
    base_python_exe = get_interpreter(python)
    logging.info('use python %s', base_python_exe)
    version, version_info = await get_python_info(base_python_exe)
    return Python(python, base_python_exe, version, version_info)


async def get_python_info(base_python_exe):
    printer = CmdLineBufferPrinter(limit=2)
    await run([base_python_exe, "-c", "import sys; print(sys.version); print(tuple(sys.version_info))"],
              stdout=printer)
    version_info = eval(printer.elements.pop(), {}, {})
    version = printer.elements.pop()
    return version, version_info


def get_interpreter(name: str) -> Path:
    binary = py.path.local.sysfind(name)
    return Path(binary)
