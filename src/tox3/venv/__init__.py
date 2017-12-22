import logging
from pathlib import Path

from tox3.interpreters import get_interpreter
from tox3.util import run, PrintAndKeepLastLine


class Venv:

    @classmethod
    async def from_python(cls, python: str, dest_dir: Path, name: str):
        base_python_exe = get_interpreter(python)
        logging.info('use python %s', base_python_exe)

        logging.info('create venv %s at %r', name, dest_dir)
        env_dir = dest_dir / name

        script = Path(__file__).parent / '_venv.py'

        printer = PrintAndKeepLastLine(limit=2)
        await run(cmd=[str(base_python_exe), str(script), str(env_dir)], stdout=printer)
        return cls(printer.elements.pop(), printer.elements.pop())

    def __init__(self, executable, bin_path):
        self.executable = executable
        self.bin_path = bin_path
        logging.info('virtual environment executable ready at %r', executable)

    async def pip(self, deps, batch_name=''):
        if deps is not None:
            logging.info('pip install %s %r', batch_name, deps)
            await run([self.executable, '-m', 'pip', 'install', *deps])
