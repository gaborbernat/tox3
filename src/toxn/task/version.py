import re
from enum import IntFlag
from typing import List, NamedTuple


class VersionOperator(IntFlag):
    COMPATIBLE = 0
    EQ = 1
    NEQ = 2
    GT = 3
    LT = 4
    GT_EQ = 5
    LESS_EQ = 6
    ARBITRARY_EQ = 6


class Version:
    PATTERN = re.compile('')

    def __init__(self, version: str):
        self._version = version


class VersionRequirement(NamedTuple):
    operator: VersionOperator
    version: Version


class VersionSpecify(NamedTuple):
    requirements: List[VersionRequirement]  # the requirements are and together
