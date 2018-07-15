#!/usr/bin/env python3
"""Emanate symbolic link manager.

Emanate is a command-line utility and Python library for managing symbolic
links in a fashion similar to `stow` or `infuse`_.

Given a `source` and `destination` directory, `emanate` creates (or removes)
symbolic links from the destination to each file in the source, mirroring the
directory structure (and creating directories as needed).

In `clean` mode, emanate instead removes such symbolic links.

"""

from fnmatch import fnmatch
from pathlib import Path
import sys
from . import config


class Emanate:
    """Provide the core functionality of Emanate.

    This class is configurable at initialization-time, by passing it a number
    of configuration objects, supporting programmatic use (from a configuration
    management tool, for instance) as well as wrapping it in a human interface
    (see emanate.main for a simple example).
    """

    def __init__(self, *configs):
        """Construct an Emanate instance from configuration dictionaries.

        The default values (as provided by config.defaults()) are implicitly
        the first configuration object; latter configurations override earlier
        configurations (see config.merge).
        """
        self.config   = config.merge(config.defaults(), *configs)
        self.dest     = self.config.destination.resolve()

    def valid_file(self, path_obj):
        """Check whether a given path is covered by an ignore glob.

        As a side effect, if the path is a directory, is it created
        in the destination directory.
        """
        path = str(path_obj.resolve())
        if any(fnmatch(path, pattern) for pattern in self.config.ignore):
            return False

        if path_obj.is_dir():
            dest_path = self.dest / path_obj.relative_to(self.config.source)
            dest_path.mkdir(exist_ok=True)
            return False

        return True

    def confirm_replace(self, dest_file):
        """Prompt the user before replacing a file.

        The prompt is skipped if the `confirm` configuration option is False.
        """
        prompt = "{!r} already exists. Replace it?".format(str(dest_file))

        if not self.config.confirm:
            return True

        result = None
        while result not in ["y", "n", "\n"]:
            print("{} [Y/n] ".format(prompt), end="", flush=True)
            result = sys.stdin.read(1).lower()

        return result != "n"

    @staticmethod
    def backup(dest_file):
        """Rename the file so we can safely write to the original path."""
        new_name = str(dest_file) + ".emanate"
        dest_file.rename(new_name)

    def _add_symlink(self, src, dest):
        # If the symbolic link is already in place, skip it.
        if dest.exists() and src.samefile(dest):
            return True

        # If the file exists and _isn't_ the symbolic link we're
        # trying to make, prompt the user to determine what to do.
        if dest.exists():
            # If the user said no, skip the file.
            if not self.confirm_replace(dest):
                return False
            Emanate.backup(dest)

        print("{!r} -> {!r}".format(str(src), str(dest)))
        dest.symlink_to(src)
        return src.samefile(dest)

    @staticmethod
    def _del_symlink(src, dest):
        if not dest.exists():
            return True

        print("{!r}".format(str(dest)))
        if dest.samefile(src):
            dest.unlink()

        return not dest.exists()

    class Execution(list):
        """Describe an Emanate execution.

        Callable once, useful to provide “dry-run”
        functionality or report changes back to the user.
        """

        def __init__(self, func, iterable):
            """Prepare an Emanate execution."""
            self.func = func
            super().__init__(iterable)

        def run(self):
            """Run a prepared execution."""
            for args in self:
                self.func(*args)

    def _files(self):
        all_files = Path(self.config.source).glob("**/*")
        for file in filter(self.valid_file, all_files):
            src  = file.resolve()
            dest = self.dest / file.relative_to(self.config.source)
            yield src, dest

    def create(self):
        """Create symbolic links."""
        return Emanate.Execution(self._add_symlink, self._files())

    def clean(self):
        """Remove symbolic links."""
        return Emanate.Execution(self._del_symlink, self._files())
