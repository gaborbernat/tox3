import re
from pathlib import Path
from typing import Any, Dict, List


class Substitute:
    _pattern = re.compile(r'<(?P<key>\w+)(?P<default>:.*)?>')

    def _substitute(self, arg: str) -> str:
        while True:
            matches = list(Substitute._pattern.finditer(arg))
            if not matches:
                return arg
            pieces: List[Any] = []
            pos = 0
            for match in matches:
                values: Dict[str, str] = match.groupdict()

                key = values['key']
                try:
                    value = getattr(self, key, None)
                except AttributeError:
                    continue
                if value is None:
                    if 'default' not in values:
                        continue
                    else:
                        default = values.get('default')
                        value = '' if default is None else default[1:]

                start, end = match.span()
                pieces.append(arg[pos: start])
                pieces.append(value)
                pos = end
            if pos == 0:  # no replacement, short it
                return arg
            pieces.append(arg[pos:])
            arg = ''.join(str(p) for p in pieces)

    def __getattribute__(self, item: str) -> Any:
        result = super().__getattribute__(item)
        if isinstance(result, str):
            return str(self._substitute(result))
        elif isinstance(result, Path):
            return Path(self._substitute(str(result)))
        elif isinstance(result, list) and all(isinstance(i, str) for i in result):
            return [str(self._substitute(i)) for i in result]
        return result
