"""Emanate's configuration module.

`emanate.config` defines Emanate's defaults, along with helpers for working
with configuration objects, loading them from JSON files, and dealing with
relative paths.
"""

import functools
import json
from pathlib import Path
from collections.abc import Iterable


def defaults(src=None):
    """Return Emanate's default configuration.

    config.defaults() resolves the default using the values
    of Path.home() and Path.cwd() at the time it was called.
    """
    if src is None:
        src = Path.cwd()
    base_ignores = resolve({
        'ignore': frozenset((
            "*~",
            ".*~",
            ".*.sw?",
            "emanate.json",
            "*/emanate.json",
            ".emanate",
            ".*.emanate",
            ".git/",
            ".gitignore",
            ".gitmodules",
            "__pycache__/",
        )),
    }, cwd=src.resolve())
    return AttrDict({
        **base_ignores,
        'confirm': True,
        'destination': Path.home(),
        'source': Path.cwd(),
    })


class AttrDict(dict):
    """Simple wrapper around dict, allowing accessing values as attributes."""

    def __getattr__(self, name):
        """Provide the contents of self as attributes."""
        if name not in self:
            raise AttributeError("{!r} object has no attribute {!r}".
                                 format(type(self).__name__, name))

        return self[name]

    def copy(self):
        """Return a new AttrDict, with the same contents as self."""
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

    Later configurations override previous ones,
    and the `ignore` attributes are merged (according to set union).
    """
    configs = [c for c in configs if c is not None]

    if strict_resolve:
        assert all(map(is_resolved, configs))

    return functools.reduce(_merge_one, configs, AttrDict())


CONFIG_PATHS = ('destination', 'source', 'ignore')


def is_resolved(config):
    """Check that all path options in a configuration object are absolute."""
    for key in CONFIG_PATHS:
        if key in config:
            if isinstance(config[key], (Path)):
                value = config[key]
            elif isinstance(config[key], Iterable):
                return all([is_resolved({key: p}) for p in config[key]])
            if not isinstance(value, Path) or not value.is_absolute():
                return False

    return True


def resolve(config, cwd=None):
    """Convert path options to pathlib.Path objects, and resolve relative paths.

    Returns a new configuration dict-like, similar to its input, with all paths
    attributes converted to `pathlib` objects, and relative paths resolved
    relatively to `cwd`.
    """
    if cwd is None:
        cwd = Path.cwd()

    assert isinstance(cwd, Path)
    assert cwd.is_absolute()
    result = AttrDict(config)

    for key in CONFIG_PATHS:
        if key not in result:
            continue

        if isinstance(result[key], str):
            result[key] = Path(result[key])

        elif isinstance(result[key], Iterable):
            result[key] = [resolve({key: p}, cwd)[key] for p in result[key]]

        if isinstance(result[key], Path) and not result[key].is_absolute():
            result[key] = cwd / result[key].expanduser()

    return result


def from_json(path):
    """Load an Emanate configuration from a file.

    Takes a `pathlib.Path` object designating a JSON configuration file,
    loads it, and resolve paths relative to the file.
    """
    assert isinstance(path, Path)

    with path.open() as file:
        return resolve(json.load(file), cwd=path.parent.resolve())
