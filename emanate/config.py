"""Emanate's configuration module.

`emanate.config` defines Emanate's defaults, along with helpers for working
with configuration objects, loading them from JSON files, and dealing with
relative paths.
"""

import functools
import json
from pathlib import Path
from collections.abc import Iterable


CONFIG_PATHS = ('destination', 'source', 'ignore')


class Config(dict):
    """Simple wrapper around dict, allowing accessing values as attributes."""

    def __getattr__(self, name):
        """Provide the contents of self as attributes."""
        if name not in self:
            raise AttributeError("{!r} object has no attribute {!r}".
                                 format(type(self).__name__, name))

        return self[name]

    def copy(self):
        """Return a new Config, with the same contents as self."""
        return Config(self)

    @classmethod
    def defaults(cls, src):
        """Return Emanate's default configuration.

        Config.defaults() resolves the default using the value
        of Path.home() at the time it was called.
        """
        return cls({
            'confirm': True,
            'destination': Path.home(),
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
        }).resolve(src.absolute())

    def resolve(self, rel_to):
        """Convert path to absolute pathlib.Path objects.

        Returns a new Config object, similar to its input, with all
        paths attributes converted to `pathlib` objects, and relative paths
        resolved relatively to `relative_to`.
        """
        assert isinstance(rel_to, Path)
        assert rel_to.is_absolute()
        result = self.copy()

        for key in CONFIG_PATHS:
            if key not in result:
                continue

            if isinstance(result[key], (str, Path)):
                result[key] = rel_to / Path(result[key]).expanduser()

            elif isinstance(result[key], Iterable):
                result[key] = [rel_to / Path(p).expanduser() for p in result[key]]

        return result


    def merge(*configs, strict_resolve=True):  # pylint: disable=no-method-argument
        """Merge several Config objects.

        Later configurations override previous ones,
        and the `ignore` attributes are merged (according to set union).
        """
        f_configs = [c for c in configs if c is not None]

        if strict_resolve:
            assert all(map(is_resolved, f_configs))

        def _merge_one(config, dict_like):
            assert isinstance(config, Config)
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

        return functools.reduce(_merge_one, f_configs, Config())

    @classmethod
    def from_json(cls, path):
        """Load an Emanate configuration from a file.

        Takes a `pathlib.Path` object designating a JSON configuration file,
        loads it, and resolve paths relative to the file.
        """
        assert isinstance(path, Path)

        with path.open() as file:
            return cls(json.load(file)).resolve(path.parent.resolve())


def is_resolved(config):
    """Check that all path options in a configuration object are absolute."""
    for key in CONFIG_PATHS:
        if key not in config:
            continue

        if isinstance(config[key], Path):
            return config[key].is_absolute()
        if isinstance(config[key], Iterable):
            for path in config[key]:
                if not isinstance(path, Path):
                    raise TypeError(
                        f"Configuration key '{key}' should contain Paths, "
                        f"got a '{type(path).__name__}': '{path!r}'"
                    )
                if not path.is_absolute():
                    return False

        raise TypeError(
            f"Configuration key '{key}' should be a (list of) Path(s), "
            f"got a '{type(key).__name__}': '{config[key]!r}'"
        )

    return True
