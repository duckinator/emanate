#!/usr/bin/env python3

# Example usage:
# TODO

from .config import Config
from argparse import ArgumentParser
from fnmatch import fnmatch
from pathlib import Path
import sys

class Emanate:
    def __init__(self, config=None):
        if config is None:
            self.config = Config()
        else:
            self.config = config

        self.dest     = Path(self.config.destination).expanduser().resolve()
        self.function = self.del_symlink if config.clean else self.add_symlink

    def valid_file(self, path_obj):
        path = str(path_obj.resolve())
        if any(fnmatch(path, pattern) for pattern in self.config.ignore):
            return False

        if path_obj.is_dir():
            Path(self.dest, path_obj).mkdir(exist_ok=True)
            return False

        return True

    def confirm_replace(self, dest_file):
        prompt = "{!r} already exists. Replace it?".format(str(dest_file))

        if not self.config.confirm:
            return True

        result = None
        while not result in ["y", "n", "\n"]:
            print("{} [Y/n] ".format(prompt), end="", flush=True)
            result = sys.stdin.read(1).lower()

        return (result != "n")

    def backup(self, dest_file):
        # Rename the file so we can safely write to the original path.
        new_name = str(dest_file) + ".emanate"
        dest_file.rename(new_name)

    def add_symlink(self, path_obj):
        src_file  = path_obj.resolve()
        dest_file = Path(self.dest, path_obj)

        # If the symlink is already in place, skip it.
        if dest_file.exists() and src_file.samefile(dest_file):
            return True

        # If the file exists and _isn't_ the symlink we're trying to make,
        # prompt the user to determine what to do.
        if dest_file.exists():
            # If the user said no, skip the file.
            if not self.confirm_replace(dest_file):
                return False
            self.backup(dest_file)

        print("{!r} -> {!r}".format(str(src_file), str(dest_file)))

        dest_file.symlink_to(src_file)

        return src_file.samefile(dest_file)

    def del_symlink(self, path_obj):
        src_file  = path_obj.resolve()
        dest_file = Path(self.dest, path_obj)

        print("{!r}".format(str(dest_file)))

        if dest_file.exists() and src_file.samefile(dest_file):
            dest_file.unlink()

        return not dest_file.exists()

    def run(self):
        all_files = Path(".").glob("**/*")
        files = filter(self.valid_file, all_files)
        list(map(self.function, files))


def parse_args(args=None):
    argparser = ArgumentParser(
        description="symlink files from one directory to another")
    argparser.add_argument("--clean",
                           action="store_true",
                           default=False,
                           help="Remove symlinks.")
    argparser.add_argument("--destination",
                           default=Path.home(),
                           metavar="DESTINATION",
                           help="Directory to create and remove symlinks in.")
    argparser.add_argument("--no-confirm",
                           action="store_true",
                           default=False,
                           help="Don't prompt before replacing a file.")
    argparser.add_argument("--config",
                           metavar="CONFIG_FILE",
                           default="emanate.json",
                           type=Path,
                           help="Configuration file to use.")

    return argparser.parse_args(args)


def main():
    """Emanate prioritizes configuration sources in the following order:
    - default values have lowest priority;
    - the configuration file overrides defaults;
    - command-line arguments override everything."""
    args = parse_args()
    cli_config = Config(
        clean=args.clean,
        destination=args.destination,
        confirm=not args.no_confirm,
    )

    config = Config.merge(
        Config.from_json(args.config.open()) if args.config.exists() else None,
        cli_config
    )

    return Emanate(config).run()

if __name__ == '__main__':
    exit(main())
