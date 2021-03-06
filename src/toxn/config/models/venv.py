from pathlib import Path
from typing import List, NamedTuple, Tuple

from toxn.util import Loggers


class VEnvCreateParam(NamedTuple):
    recreate: bool
    dir: Path
    name: str
    python: str
    logger: Loggers

    @property
    def cache(self) -> Path:
        return self.dir / f'.{self.name}.tox.cache'


class VEnvParams(NamedTuple):
    root_dir: Path
    bin_path: Path
    executable: Path
    site_package: Path


class Install(NamedTuple):
    batch_name: str
    packages: List[str]
    base_cmd: List[str]
    use_develop: bool


VersionInfo = Tuple[int, int, int, str]


class Python(NamedTuple):
    python_name: str
    exe: Path
    version: str
    version_info: VersionInfo

    @property
    def major_version(self) -> int:
        return self.version_info[0]


class VEnv:

    def __init__(self, python: Python, params: VEnvParams, logger: Loggers) -> None:
        self.params: VEnvParams = params
        self.python: Python = python
        self.logger: Loggers = logger
        self.logger.info('virtual environment executable for %r ready at %r', self.python.python_name,
                         self.params.executable)
