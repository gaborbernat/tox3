import logging
from pathlib import Path
import venv

from tox3.util import run


class EnvB(venv.EnvBuilder):
    executable = None
    bin_path = None

    def post_setup(self, context):
        self.executable = context.env_exe
        self.bin_path = context.bin_path


class Venv:

    def __init__(self, dest_dir: Path, name: str):
        logging.info('create venv %s at %r', name, dest_dir)
        env_dir = dest_dir / name

        venv.create(env_dir, with_pip=True)
        env_build = EnvB(with_pip=True)
        env_build.create(env_dir)

        self.executable = env_build.executable
        self.bin_path = env_build.bin_path
        logging.info('virtual environment executable ready at %r', self.executable)

    async def pip(self, deps, batch_name=''):
        if deps is not None:
            logging.info('pip install %s %r', batch_name, deps)
            await run([self.executable, '-m', 'pip', 'install', *deps])
