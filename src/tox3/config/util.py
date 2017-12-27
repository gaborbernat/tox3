import logging
import re

VERBOSITY_TO_LOG_LEVEL = {0: logging.ERROR,
                          1: logging.WARN,
                          2: logging.INFO,
                          3: logging.DEBUG}


class Substitute:
    pattern = re.compile(r'<(\w+)>')

    def _substitute(self, arg: str) -> str:
        matches = Substitute.pattern.finditer(arg)
        handled = set()
        for match in matches:
            try:
                key = match.group(1)
                if key in handled:
                    continue
                handled.add(key)
                value = self.__getattribute__(key)
                arg = arg.replace(f'<{key}>', value)
            except AttributeError:
                pass
        return arg

    def __getattribute__(self, item):
        result = super().__getattribute__(item)
        if isinstance(result, str):
            return self._substitute(result)
        elif isinstance(result, list):
            return [self._substitute(i) for i in result]
        return result
