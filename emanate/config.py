"""Emanate's configuration module.

emanate.config defines Emanate's defaults, along with helpers for working with
config objects, loading them from JSON files, and dealing with relative paths.
"""

import functools
import json
from pathlib import Path


def defaults():
    return {
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
    """Simple wrapper around dict, allowing accessing values as attributes."""

    def __getattr__(self, name):
        if name not in self:
            raise AttributeError("{!r} object has no attribute {!r}".
                                 format(type(self).__name__, name))

        return self[name]

    def copy(self):
        return AttrDict(self)


def _merge_one(config, dict_like):
    assert isinstance(config, AttrDict)
    assert dict_like is not None

    config = config.copy()
    for key, value in dict_like.items():
        if value is None:
            continue

        if key == 'ignore':
            config[key] = config.get(key, frozenset()).union(value)
        else:
            config[key] = value

    return config


def merge(*configs, strict_resolve=True):
    """Merge a sequence of configuration dict-like objects.

    Later configs overide previous ones, and the `ignore` attributes are
    merged (according to set union).
    """
    configs = [c for c in configs if c is not None]

    if strict_resolve:
        assert all(map(is_resolved, configs))

    return functools.reduce(_merge_one, configs, AttrDict())


CONFIG_PATHS = ('destination', 'source')


def is_resolved(config):
    """Check that all path options in a config object are absolute Paths."""
    for key in CONFIG_PATHS:
        if key in config:
            value = config[key]
            if not isinstance(value, Path) or not value.is_absolute():
                return False

    return True


def resolve(config, cwd=None):
    """Convert path options to pathlib.Path objects, and resolve relative paths.

    Returns a new config dict-like, similar to its input, with all paths
    attributes converted to pathlib objects, and relative paths resolved
    relatively to `cwd`.
    """
    if cwd is None:
        cwd = Path.cwd()

    assert isinstance(cwd, Path)
    assert cwd.is_absolute()
    result = config.copy()

    for key in CONFIG_PATHS:
        if key not in result:
            continue

        if isinstance(result[key], str):
            result[key] = Path(result[key])

        if not result[key].is_absolute():
            result[key] = cwd / result[key].expanduser()

    return result


def from_json(path):
    """Load an Emanate configuration from a file.

    Takes a pathlib.Path object designating a JSON configuration file,
    loads it, and resolve paths relative to the filepath.
    """
    assert isinstance(path, Path)
    return resolve(json.load(path.open()), cwd=path.parent.resolve())
