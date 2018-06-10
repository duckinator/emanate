#!/usr/bin/env python3

# Example usage:
# TODO

from argparse import ArgumentParser, SUPPRESS
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

        The default values (as provided by config.defaults()) are implicitely
        the first configuration object; latter configurations override earlier
        configurations (see config.merge).
        """
        self.config   = config.merge(config.defaults(), *configs)
        self.dest     = self.config.destination.resolve()

        if self.config.clean:
            self.function = self._del_symlink
        else:
            self.function = self._add_symlink

    def valid_file(self, path_obj):
        """Check whether a given path is covered by an ignore glob.

        As a side effect, if the path is a directory, is it created
        in the destination directory.
        """
        path = str(path_obj.resolve())
        if any(fnmatch(path, pattern) for pattern in self.config.ignore):
            return False

        if path_obj.is_dir():
            Path(self.dest, path_obj).mkdir(exist_ok=True)
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

    def _add_symlink(self, path_obj):
        src_file  = path_obj.resolve()
        dest_file = self.dest / path_obj.relative_to(self.config.source)

        # If the symlink is already in place, skip it.
        if dest_file.exists() and src_file.samefile(dest_file):
            return True

        # If the file exists and _isn't_ the symlink we're trying to make,
        # prompt the user to determine what to do.
        if dest_file.exists():
            # If the user said no, skip the file.
            if not self.confirm_replace(dest_file):
                return False
            Emanate.backup(dest_file)

        print("{!r} -> {!r}".format(str(src_file), str(dest_file)))

        dest_file.symlink_to(src_file)

        return src_file.samefile(dest_file)

    def _del_symlink(self, path_obj):
        src_file  = path_obj.resolve()
        dest_file = Path(self.dest, path_obj)

        print("{!r}".format(str(dest_file)))

        if dest_file.exists() and src_file.samefile(dest_file):
            dest_file.unlink()

        return not dest_file.exists()

    def run(self):
        """Execute Emanate as configured."""
        all_files = Path(self.config.source).glob("**/*")
        for file in filter(self.valid_file, all_files):
            self.function(file)


def _parse_args(args=None):
    argparser = ArgumentParser(
        description="symlink files from one directory to another",
        argument_default=SUPPRESS,
    )
    argparser.add_argument("--clean", help="Remove symlinks.")
    argparser.add_argument("--destination",
                           metavar="DESTINATION",
                           help="Directory to create and remove symlinks in.")
    argparser.add_argument("--source",
                           metavar="SOURCE",
                           type=Path,
                           help="Directory holding the files to symlink.")
    argparser.add_argument("--no-confirm",
                           action="store_false",
                           dest="confirm",
                           help="Don't prompt before replacing a file.")
    argparser.add_argument("--config",
                           metavar="CONFIG_FILE",
                           default=None,
                           type=Path,
                           help="Configuration file to use.")

    return argparser.parse_args(args)


def main(args=None):
    """Invoke Emanate from command-line arguments.

    Emanate prioritizes configuration sources in the following order:
    - default values have lowest priority;
    - the configuration file overrides defaults;
    - command-line arguments override everything.
    """
    args = _parse_args(args)
    if args.config is None:
        if 'source' in args:
            args.config = args.source / "emanate.json"
        else:
            args.config = Path.cwd() / "emanate.json"

    return Emanate(
        config.from_json(args.config) if args.config.exists() else None,
        config.resolve(vars(args)),
    ).run()


if __name__ == '__main__':
    exit(main())
