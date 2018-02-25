import os
import re
from pathlib import Path
from typing import Any, Dict, List

_pattern = re.compile(r'<(?P<keys>[\w.]+)(?P<value_1>:[^:]+)?(?P<value_2>:.+)?>')


def substitute(obj: Any, arg: str) -> Any:
    while True:
        matches = list(_pattern.finditer(arg))
        if not matches:
            return arg
        pieces: List[Any] = []
        pos = 0
        for match_obj in matches:
            match: Dict[str, str] = match_obj.groupdict()

            keys = match['keys']
            if keys == 'env':
                os_key = match.get('value_1')
                if os_key is None:
                    continue
                os_key = os_key[1:]
                if os_key in os.environ:
                    value: Any = os.environ[os_key]
                else:
                    default = match.get('value_2')
                    value = default[1:] if default is not None else ''
            else:
                value = obj
                for key in keys.split('.'):
                    try:
                        value = getattr(value, key, None)
                    except AttributeError:
                        value = None
                        break
                if value is None:
                    if 'value_1' not in match:
                        value = ''
                    else:
                        default = match.get('value_1')
                        value = '' if default is None else default[1:]

            start, end = match_obj.span()
            if end - start == len(arg):
                return value
            pieces.append(arg[pos: start])
            pieces.append(value)
            pos = end
        if pos == 0:  # no replacement, short it
            return arg
        pieces.append(arg[pos:])
        arg = ''.join(str(p) for p in pieces)


class Substitute:

    def _substitute(self, arg: str) -> Any:
        return substitute(self, arg)

    def __getattribute__(self, item: str) -> Any:
        result = super().__getattribute__(item)
        if isinstance(result, str):
            return self._substitute(result)
        elif isinstance(result, Path):
            return Path(self._substitute(str(result)))
        elif isinstance(result, list) and all(isinstance(i, str) for i in result):
            return [str(self._substitute(i)) for i in result]
        return result
