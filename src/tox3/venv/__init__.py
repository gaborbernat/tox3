import logging
import re
import shutil
from pathlib import Path

import sys
import virtualenv

from tox3.interpreters import get_interpreter
from tox3.util import run, Buffer


class Venv:

    @classmethod
    async def from_python(cls, python: str, dest_dir: Path, name: str, recreate: bool):
        base_python_exe = get_interpreter(python)
        logging.info('use python %s', base_python_exe)

        printer = Buffer(limit=2)
        await run([str(base_python_exe), "-c", "import sys; print(sys.version); print(tuple(sys.version_info))"],
                  stdout=printer)
        version_info = eval(printer.elements.pop(), {}, {})
        version = printer.elements.pop()

        logging.info('create venv %s at %r with %s', name, dest_dir, version)
        env_dir = dest_dir / name
        if recreate and env_dir.exists():
            logging.debug('remove %r', env_dir)
            shutil.rmtree(env_dir)

        if version_info[0] < 3:
            printer = Buffer(limit=None)
            await run([sys.executable, '-m', 'virtualenv', '--no-download', '--python',
                       str(base_python_exe), str(env_dir)],
                      stdout=printer)
            pattern = re.compile(r'New python executable in (.*)')
            for line in printer.elements:
                logging.info(line)
                match = re.match(pattern, line)
                if match:
                    executable = Path(match.group(1))
                    bin_path = executable.parent
                    break
            else:
                raise Exception('could not find executable')
        else:
            script = Path(__file__).parent / '_venv.py'
            await run(cmd=[str(base_python_exe), str(script), str(env_dir)], stdout=printer)
            executable, bin_path = Path(printer.elements.pop()), Path(printer.elements.pop())
        return cls(executable, bin_path, version, version_info)

    def __init__(self, executable, bin_path, version, version_info):
        self.executable = executable
        self.bin_path = bin_path
        self.version = version
        self.version_info = version_info
        logging.info('virtual environment executable ready at %r', executable)

    async def pip(self, deps, batch_name=''):
        if deps is not None:
            logging.info('pip install %s %r', batch_name, deps)
            await run([str(self.executable), '-m', 'pip', 'install', *deps])
