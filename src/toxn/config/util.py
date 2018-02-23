import re
from pathlib import Path
from typing import Any, Dict, Set


class Substitute:
    _pattern = re.compile(r'<(?P<key>\w+)(?P<default>:.*)?>')

    def _substitute(self, arg: str) -> str:
        matches = Substitute._pattern.finditer(arg)
        handled: Set[str] = set()
        for match in matches:
            values: Dict[str, str] = match.groupdict()
            try:
                key = values['key']
                default = values.get('default')
                if key in handled:
                    continue
                handled.add(key)
                value = getattr(self, key, None)
                if value is None:
                    if 'default' not in values:
                        continue
                    else:
                        value = default
                if not isinstance(value, str):
                    value = str(value)
                arg = arg.replace(f'<{key}>', value)
            except AttributeError:
                pass
        return arg

    def __getattribute__(self, item: str) -> Any:
        result = super().__getattribute__(item)
        if isinstance(result, str):
            return str(self._substitute(result))
        elif isinstance(result, Path):
            return Path(self._substitute(str(result)))
        elif isinstance(result, list) and all(isinstance(i, str) for i in result):
            return [str(self._substitute(i)) for i in result]
        return result
