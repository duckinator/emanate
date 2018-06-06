import collections.abc
import json
from pathlib import Path


DEFAULTS = {
    'ignore': frozenset((
        "*~",
        ".*~",
        ".*.sw?",
        "*/emanate.json",
        "*.emanate",
        ".*.emanate",
        "*/.git",
        "*/.git/*",
        "*/.gitignore",
        "*/.gitmodules",
        "*/__pycache__",
        "*/__pycache__/*",
    )),

    'clean': False,
    'confirm': True,
    'destination': Path.home(),
    'source': Path.cwd(),
}

class AttrDict(dict):
    def __getattr__(self, name):
        if name not in self:
            raise AttributeError("{!r} object has no attribute {!r}".
                                 format(type(self).__name__, name))

        return self[name]

def merge(*configs):
    result = AttrDict()
    for config in configs:
        if config is not None:
            for key, value in config.items():
                if value is not None:
                    if key == 'ignore':
                        result[key] = result.get(key, frozenset()).union(value)
                    else:
                        result[key] = value

    return result

def from_json(file):
    if isinstance(file, str):
        return json.loads(file)
    else:
        return json.load(file)
