import argparse
import re
from typing import Optional

from tox3.venv import Venv, Python
from .core import CoreToxConfig
from ..project import BuildSystem, FileConf


class EnvConfig(CoreToxConfig):
    def __init__(self,
                 _options: argparse.Namespace,
                 build_system: BuildSystem,
                 file: FileConf,
                 name: str):
        super().__init__(_options, build_system, file)
        self.name = name
        # generated by running
        self.base_python: Optional[Python] = None  # interpreter resolution
        self.venv: Optional[Venv] = None  # virtualenv generation

    @property
    def python(self) -> str:
        key = 'basepython'
        if key in self._file:
            return self._file[key]
        match = re.match(r'py(\d)(\d)', self.name)
        if match:
            return 'python{}.{}'.format(match.group(1), match.group(2))
        raise ValueError('no base python for {}'.format(self.name))

    @property
    def recreate(self) -> bool:
        return self._options.__getattribute__('recreate')

    @property
    def build_wheel(self) -> bool:
        return self._file.get('build_wheel', True)

    @property
    def build_type(self) -> str:
        return 'wheel' if self.build_wheel else 'sdist'

    @property
    def envsitepackagesdir(self):
        return self.venv.core.site_package

    @property
    def envbindir(self):
        return self.venv.core.bin_path

    @property
    def envdir(self):
        return self.venv.core.root_dir

    @property
    def envpython(self):
        return self.venv.core.executable

    @property
    def envname(self):
        return self.name