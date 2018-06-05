import collections.abc
import json
from pathlib import Path


DEFAULT_SETTINGS = {
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
}


# Boilerplate stolen from Cumin:
#   https://github.com/astronouth7303/cumin/blob/master/cumin/config.py
class Config(collections.abc.MutableMapping):
    """
    Configuration that just initializes itself from default values.
    """

    def __init__(self, **kwargs):
        if not kwargs:
            self._data = {}
        else:
            self._data = kwargs

    def __getitem__(self, key):
        return self._data.get(key, DEFAULT_SETTINGS.get(key))

    def __setitem__(self, key, data):
        self._data[key] = data

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        yield from self._data

    def __len__(self):
        return len(self._data)

    def __getattr__(self, name):
        if name not in self:
            raise AttributeError("{!r} object has no attribute {!r}".
                                 format(type(self).__name__, name))

        return self[name]

    @staticmethod
    def merge(*pargs):
        result = Config()
        for arg in pargs:
            if arg is not None:
                result.update(arg)

        return result

    def update(self, other):
        for key, value in other.items():
            if key == 'ignore':
                self[key] = self[key].union(value)
            else:
                self[key] = value

    @staticmethod
    def from_defaults():
        return Config()

    @staticmethod
    def from_json(file):
        if isinstance(file, str):
            data = json.loads(file)
        else:
            data = json.load(file)

        result = Config()
        result.update(data)
        return result
