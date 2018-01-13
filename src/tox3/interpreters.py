import os
from pathlib import Path
from typing import NamedTuple, Tuple

import py  # type: ignore

from .util import CmdLineBufferPrinter, Loggers, run

VersionInfo = Tuple[int, int, int, str]


class Python(NamedTuple):
    python_name: str
    exe: Path
    version: str
    version_info: VersionInfo

    @property
    def major_version(self) -> int:
        return self.version_info[0]


async def find_python(python: str, logger: Loggers) -> Python:
    base_python_exe = get_interpreter(python)
    logger.info('use python %s (as %s)', base_python_exe, python)
    version, version_info = await get_python_info(base_python_exe, logger)
    return Python(python, base_python_exe, version, version_info)


async def get_python_info(base_python_exe: Path, logger: Loggers) -> Tuple[str, VersionInfo]:
    printer = CmdLineBufferPrinter(limit=None)
    await run([base_python_exe, "-c", "import sys; print(sys.version); print(tuple(sys.version_info))"],
              stdout=printer, logger=logger)
    version_info = eval(printer.elements.pop(), {}, {})
    version = '\n'.join(printer.elements)
    return version, version_info


def get_interpreter(name: str) -> Path:
    # noinspection PyCallByClass
    binary = py.path.local.sysfind(name)
    if binary is None:
        raise RuntimeError('could not find {}, sys path {!r}'.format(name, os.environ.get('PATH')))
    return Path(binary)
