from pathlib import Path
from typing import List, NamedTuple

from tox3.util import Loggers


class VEnvCreateParam(NamedTuple):
    recreate: bool
    dest_dir: Path
    name: str
    python: str
    logger: Loggers

    @property
    def dir(self) -> Path:
        return self.dest_dir / self.name

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
