"""Emanate symbolic link manager.

Emanate is a command-line utility and Python library for managing symbolic
links in a fashion similar to `stow` or `infuse`_.

Given a `source` and `destination` directory, `emanate` creates (or removes)
symbolic links from the destination to each file in the source, mirroring the
directory structure (and creating directories as needed).

In `clean` mode, emanate instead removes such symbolic links.

"""

from collections import namedtuple
from fnmatch import fnmatch
from pathlib import Path
import sys
from . import config


class FilePair(namedtuple('FilePair', ['src', 'dest'])):
    """Pairs of source/destination file paths."""

    def print_add(self):
        """Print a message when creating a link."""
        print("{!r} -> {!r}".format(str(self.src), str(self.dest)))

    def print_del(self):
        """Print a message when deleting a link."""
        print("{!r}".format(str(self.dest)))

    def del_symlink(self):
        """Delete a link."""
        if self.dest.samefile(self.src):
            self.dest.unlink()

        return not self.dest.exists()

    def add_symlink(self):
        """Add a link."""
        self.dest.symlink_to(self.src)
        return self.src.samefile(self.dest)


class Execution(list):
    """Describe an Emanate execution.

    Callable once, useful to provide “dry-run”
    functionality or report changes back to the user.
    """

    def __init__(self, func, printer, iterable):
        """Prepare an Emanate execution."""
        self.func = func
        self.printer = printer
        super().__init__(iterable)

    def run(self):
        """Run a prepared execution."""
        for args in self:
            if self.func(args):
                self.printer(args)

    def dry(self):
        """Print a dry-run of an execution."""
        for args in self:
            self.printer(args)


class Emanate:
    """Provide the core functionality of Emanate.

    This class is configurable at initialization-time, by passing it a number
    of configuration objects, supporting programmatic use (from a configuration
    management tool, for instance) as well as wrapping it in a human interface
    (see emanate.main for a simple example).
    """

    def __init__(self, *configs, src=None):
        """Construct an Emanate instance from configuration dictionaries.

        The default values (as provided by config.defaults()) are implicitly
        the first configuration object; latter configurations override earlier
        configurations (see config.merge).
        """
        self.config = config.merge(
            config.defaults(src),
            *configs,
        )
        self.dest = self.config.destination.resolve()

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

        As a side effect, if the path is a directory, is it created
        in the destination directory.
        """
        path = str(path_obj.absolute())
        ignore_patterns = [
            p / "*" if Emanate._is_dir(p) else p for p in self.config.ignore
        ]
        if any(fnmatch(path, str(pattern)) for pattern in ignore_patterns):
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

    def _add_symlink(self, pair):
        _, dest = pair

        # If the file exists and _isn't_ the symbolic link we're
        # trying to make, prompt the user to determine what to do.
        if dest.exists():
            # If the user said no, skip the file.
            if not self.confirm_replace(dest):
                return False
            Emanate.backup(dest)

        return pair.add_symlink()

    @staticmethod
    def backup(dest_file):
        """Rename the file so we can safely write to the original path."""
        new_name = str(dest_file) + ".emanate"
        dest_file.rename(new_name)

    def _files(self):
        all_files = Path(self.config.source).glob("**/*")
        for file in filter(self.valid_file, all_files):
            src  = file.absolute()
            dest = self.dest / file.relative_to(self.config.source)
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
