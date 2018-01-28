import os
import re
import sys
from pathlib import Path
from typing import Dict, NamedTuple, Optional, Tuple

import py  # type: ignore

from toxn.util import CmdLineBufferPrinter, Loggers, run


class CouldNotFindInterpreter(ValueError):
    pass


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
    base_python_exe = get_interpreter(python, logger)
    logger.info('%s resolves as %s', python, base_python_exe)
    version, version_info = await get_python_info(base_python_exe, logger)
    return Python(python, base_python_exe, version, version_info)


async def get_python_info(base_python_exe: Path, logger: Loggers) -> Tuple[str, VersionInfo]:
    printer = CmdLineBufferPrinter(limit=None)
    await run([base_python_exe, "-c", "import sys; print(sys.version); print(tuple(sys.version_info))"],
              stdout=printer, logger=logger)
    version_info = eval(printer.elements.pop(), {}, {})
    version = '\n'.join(printer.elements)
    return version, version_info


WIN_32_MAP: Dict[str, Path] = {
    'python': Path(sys.executable)
}


def get_interpreter(name: str, logger: Loggers) -> Path:
    # noinspection PyCallByClass
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
        binary = WIN_32_MAP.get(name, None)
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
