import os
import re
from pathlib import Path
from typing import Any, Dict, List

_pattern = re.compile(r'<(?P<key>\w+)(?P<value_1>:[^:]+)?(?P<value_2>:.+)?>')


def substitute(obj: Any, arg: str) -> str:
    while True:
        matches = list(_pattern.finditer(arg))
        if not matches:
            return arg
        pieces: List[Any] = []
        pos = 0
        for match_obj in matches:
            match: Dict[str, str] = match_obj.groupdict()

            key = match['key']
            if key == 'env':
                os_key = match.get('value_1')
                if os_key is None:
                    continue
                os_key = os_key[1:]
                if os_key in os.environ:
                    value = os.environ[os_key]
                else:
                    default = match.get('value_2')
                    value = default[1:] if default is not None else ''
            else:
                try:
                    value = getattr(obj, key, None)
                except AttributeError:
                    continue
                if value is None:
                    if 'value_1' not in match:
                        value = ''
                    else:
                        default = match.get('value_1')
                        value = '' if default is None else default[1:]

            start, end = match_obj.span()
            pieces.append(arg[pos: start])
            pieces.append(value)
            pos = end
        if pos == 0:  # no replacement, short it
            return arg
        pieces.append(arg[pos:])
        arg = ''.join(str(p) for p in pieces)


class Substitute:

    def _substitute(self, arg: str) -> str:
        return substitute(self, arg)

    def __getattribute__(self, item: str) -> Any:
        result = super().__getattribute__(item)
        if isinstance(result, str):
            return str(self._substitute(result))
        elif isinstance(result, Path):
            return Path(self._substitute(str(result)))
        elif isinstance(result, list) and all(isinstance(i, str) for i in result):
            return [str(self._substitute(i)) for i in result]
        return result
