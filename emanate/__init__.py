"""Emanate symbolic link manager.

Emanate is a command-line utility and Python library for managing symbolic
links in a fashion similar to Stow or Effuse.

Given a `source` and `destination` directory, Emanate can create or remove
symbolic links from the destination to each file in the source, mirroring
the directory structure and creating directories as needed.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Callable
import sys
from .config import Config

# Expose `emanate.version.__version__` as `emanate.__version__`.
from .version import __version__  # noqa: F401


#: Emanate's maintainer.
__author__ = "Ellen Marie Dash"

# __version__ is defined in version.py.


@dataclass(frozen=True)
class FilePair:
    """Pairs of source/destination file paths."""

    src: Path
    dest: Path

    def print_add(self):
        """Print a message when creating a link."""
        print(f"{str(self.src)!r} -> {str(self.dest)!r}")

    def print_del(self):
        """Print a message when deleting a link."""
        print(f"{str(self.dest)!r}")

    def del_symlink(self):
        """Delete a link."""
        if self.dest.samefile(self.src):
            self.dest.unlink()

        return not self.dest.exists()

    def add_symlink(self):
        """Add a link."""
        self.dest.symlink_to(self.src)
        return self.src.samefile(self.dest)


@dataclass(frozen=True)
class Execution:
    """Describe an Emanate execution.

    The user passes functions defining the operation that is applied, and a
    “printer” that's called upon changes; this is useful to provide "dry-run"
    functionality or report changes back to the user.
    """

    func: Callable[[FilePair], bool]
    printer: Callable[[FilePair], Any]
    ops: Iterable[FilePair]

    def run(self):
        """Run a prepared execution.

        Callable only once per Execution object.
        """
        for args in self.ops:
            if self.func(args):
                self.printer(args)

    def dry(self):
        """Print a dry-run of an execution."""
        for args in self.ops:
            self.printer(args)


class Emanate:
    """Provides the core functionality of Emanate.

    This class is configurable at initialization-time, by passing it a number
    of configuration objects, supporting programmatic use (from a configuration
    management tool, for instance) as well as wrapping it in a human interface
    (see emanate.main for a simple example).
    """

    def __init__(self, *configs):
        """Construct an Emanate instance from configuration dictionaries.

        The default values (as provided by Config.defaults()) are implicitly
        the first configuration object; latter configurations override earlier
        configurations (see Config.merge).

        The configs must define a source directory.
        """
        explicit_configs = Config.merge(*configs)
        self.conf = Config.defaults(explicit_configs.get('source')).merge(
            explicit_configs,
        )

    @property
    def dest(self):
        return self.conf.destination

    @staticmethod
    def _is_dir(path_obj):
        """Check whether a given path is a directory, but never raise an
        exception (such as Path(x).is_dir() may do).
        """
        try:
            return path_obj.is_dir()
        except OSError:
            return False

    def valid_file(self, path_obj):
        """Check whether a given path is covered by an ignore glob.

        As a side effect, if the path is a directory, it is created
        in the destination directory.
        """
        path = str(path_obj.absolute())
        ignore_patterns = []
        for pattern in self.conf.ignore:
            ignore_patterns.append(pattern)
            # If it's a directory, also ignore its contents.
            if Emanate._is_dir(pattern):
                ignore_patterns.append(pattern / "*")

        if any(fnmatch(path, str(pattern)) for pattern in ignore_patterns):
            return False

        if path_obj.is_dir():
            dest_path = self.dest / path_obj.relative_to(self.conf.source)
            dest_path.mkdir(exist_ok=True)
            return False

        return True

    def confirm_replace(self, dest_file):
        """Prompt the user before replacing a file.

        The prompt is skipped if the `confirm` configuration option is False.
        """
        prompt = f"{str(dest_file)!r} already exists. Replace it?"

        if not self.conf.confirm:
            return True

        result = None
        while result not in ["y", "n", "\n"]:
            print(f"{prompt} [Y/n] ", end="", flush=True)
            result = sys.stdin.read(1).lower()

        return result != "n"

    def _add_symlink(self, pair):
        # If the file exists and _isn't_ the symbolic link we're
        # trying to make, prompt the user to determine what to do.
        if pair.dest.exists():
            # If the user said no, skip the file.
            if not self.confirm_replace(pair.dest):
                return False
            Emanate.backup(pair.dest)

        return pair.add_symlink()

    @staticmethod
    def backup(dest_file):
        """Rename the file so we can safely write to the original path."""
        new_name = str(dest_file) + ".emanate"
        dest_file.rename(new_name)

    def _files(self):
        all_files = Path(self.conf.source).glob("**/*")
        for file in filter(self.valid_file, all_files):
            src  = file.absolute()
            dest = self.dest / file.relative_to(self.conf.source)
            yield FilePair(src, dest)

    def create(self):
        """Create symbolic links."""
        # Ignore files that are already linked.
        gen = filter(lambda p: not (p.dest.exists() and p.src.samefile(p.dest)),
                     self._files())

        return Execution(self._add_symlink,
                         FilePair.print_add,
                         gen)

    def clean(self):
        """Remove symbolic links."""
        # Skip non-existing files.
        gen = filter(lambda p: p.dest.exists(), self._files())

        return Execution(FilePair.del_symlink,
                         FilePair.print_del,
                         gen)
