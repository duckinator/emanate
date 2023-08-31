"""Emanate's configuration module.

`emanate.config` defines Emanate's defaults, along with helpers for working
with configuration objects, loading them from JSON files, and dealing with
relative paths.
"""

import functools
import json
from pathlib import Path
from collections.abc import Iterable

from frozendict import frozendict


PATHS = frozenset(('destination', 'source',))
PATH_SETS = frozenset(('ignore',))
PATH_KEYS = PATHS.union(PATH_SETS)


class Config(frozendict):
    """Simple wrapper around dict, allowing accessing values as attributes."""

    def __getattr__(self, name):
        """Provide the contents of self as attributes."""
        if name not in self:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {name!r}",
            )

        return self[name]

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

        def _resolve(path):
            return rel_to / Path(path).expanduser()

        return self.copy(**{
            key: _resolve(v) if key in PATHS else frozenset(map(_resolve, v))
            for (key, v) in self.items()
            if key in PATH_KEYS
        })

    def merge(*configs, strict_resolve=True):  # pylint: disable=no-method-argument,no-self-argument
        """Merge several Config objects.

        Later configurations override previous ones,
        and the `ignore` attributes are merged (according to set union).
        """
        # NOTE: There is no `self` argument because it is part of `configs`.

        def _merge_one(config, other):
            assert isinstance(config, Config)
            assert isinstance(other, Config)
            assert config.resolved

            if strict_resolve and not other.resolved:
                raise ValueError("Merging a non-resolved configuration")

            return config.copy(**other, **{
                key: config[key].union(other[key])
                for key in PATH_SETS
                if key in config and key in other
            })

        return functools.reduce(_merge_one, filter(None, configs), Config())

    @classmethod
    def from_json(cls, path):
        """Load an Emanate configuration from a file.

        Takes a `pathlib.Path` object designating a JSON configuration file,
        loads it, and resolve paths relative to the file.
        """
        assert isinstance(path, Path)

        with path.open() as file:
            return cls(json.load(file)).resolve(path.parent.resolve())

    @property
    def resolved(self):
        """Check that all path options in a configuration object are absolute."""
        for key in PATHS:
            if key not in self:
                continue

            path = self[key]
            if not isinstance(path, Path):
                raise TypeError(
                    f"Configuration key '{key}' should contain a Path, "
                    f"got a '{type(path).__name__}': '{path!r}'"
                )

            if not self[key].is_absolute():
                return False

        for key in PATH_SETS:
            if key not in self:
                continue

            assert isinstance(self[key], Iterable)
            for path in self[key]:
                if not isinstance(path, Path):
                    raise TypeError(
                        f"Configuration key '{key}' should be a set of Paths, "
                        f"got a '{type(path).__name__}': '{path!r}'"
                    )

                if not path.is_absolute():
                    return False

        return True
