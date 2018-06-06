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


CONFIG_PATHS = ('destination', 'source')

def is_resolved(config):
    for key in CONFIG_PATHS:
        if key in config:
            value = config[key]
            if not isinstance(value, Path) or not value.is_absolute():
                return False

    return True

def resolve(config, cwd=Path.cwd()):
    assert isinstance(cwd, Path)
    assert cwd.is_absolute()
    result = config.copy()

    for key in CONFIG_PATHS:
        if key in result:
            if isinstance(result[key], str):
                result[key] = Path(result[key])

            if not result[key].is_absolute():
                result[key] = cwd / result[key].expanduser()

    return result

def from_json(path):
    assert isinstance(path, Path)
    return resolve(json.load(path.open()), cwd=path.parent)
