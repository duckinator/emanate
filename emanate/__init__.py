#!/usr/bin/env python3

# Example usage:
# TODO

import argparse
from fnmatch import fnmatch
import functools
import json
import os
from pathlib import Path
import sys

class Emanate:
    DEFAULT_IGNORE = [
            "*~",
            ".*~",
            ".*.sw?",
            "*/emanate.json",
            "*.emanate",
            ".*.emanate",
            "*/.git/*",
            "*/.gitignore",
            "*/.gitmodules",
            "*/__pycache__/*",
            ]

    @staticmethod
    def parse_args(argv):
        argparser = argparse.ArgumentParser(
                description="symlink files from one directory to another",
                argument_default=argparse.SUPPRESS)
        argparser.add_argument("--clean",
                action="store_true",
                default=False,
                help="Remove symlinks.")
        argparser.add_argument("--destination",
                default=Path.home(),
                metavar="DESTINATION",
                nargs="?",
                help="Directory to create and/or remove symlinks in.")
        argparser.add_argument("--no-confirm",
                action="store_true",
                default=False,
                help="Don't prompt before replacing a file.")
        argparser.add_argument("--config",
                metavar="CONFIG_FILE",
                default="emanate.json",
                help="Configuration file to use.")
        argparser.add_argument("--version",
                action="store_true",
                default=False,
                help="Show version information")
        args = argparser.parse_args(argv[1:])
        return args

    @staticmethod
    def parse_conf(file):
        if isinstance(file, io.IOBase):
            pass
        elif isinstance(file, Path):
            file = file.open()
        else:
            file = open(file, 'r')

        return json.load(file)

    def ignored_file(self, path_obj):
        path = str(path_obj.resolve())
        patterns = self.DEFAULT_IGNORE + self.config.get("ignore", [])
        match = functools.partial(fnmatch, path)
        return any(map(match, patterns))

    def valid_file(self, path_obj):
        if path_obj.is_dir():
            return False

        return not self.ignored_file(path_obj)

    def confirm(self, prompt):
        if self.config.no_confirm:
            return True

        result = None
        while not result in ["y", "n"]:
            print("{} [Y/n] ".format(prompt), end="", flush=True)
            result = sys.stdin.read(1)

        return (result == "y")

    def symlink_file(self, dest, path_obj):
        assert (not path_obj.is_absolute()), \
                "expected path_obj to be a relative path, got absolute path."

        src_file  = path_obj.resolve()
        dest_file = Path(dest, path_obj)
        prompt    = "{!r} already exists. Replace it?".format(str(dest_file))

        assert src_file.exists(), "expected {!r} to exist.".format(str(src_file))

        # If it's not a file, we just skip it.
        if src_file.exists() and not src_file.is_file():
            return True

        if dest_file.exists() and src_file.samefile(dest_file):
            return True

        if dest_file.exists() and not self.confirm(prompt):
            return False

        print("{!r} -> {!r}".format(str(src_file), str(dest_file)))

        dest_file.symlink_to(src_file)

        return src_file.samefile(dest_file)

    def symlink_all(self, dest, files):
        # symlinkfn is a partially-applied variant of symlink_file(),
        # whose first argument is always set to dest
        symlinkfn = functools.partial(self.symlink_file, dest)
        return list(map(symlinkfn, files))

    def clean_file(self, dest, config, path_obj):
        assert (not path_obj.is_absolute()), \
                "expected path_obj to be a relative path, got absolute path."

        src_file  = path_obj.resolve()
        dest_file = Path(dest, path_obj)

        if not dest_file.exists():
            return True

        print("{!r}".format(str(dest_file)))

        if src_file.samefile(dest_file):
            dest_file.unlink()

        return not dest_file.exists()

    def clean_all(self, dest, files):
        # cleanfn is a partially-applied variant of clean_file(),
        # whose first argument is set to dest
        cleanfn = functools.partial(self.clean_file, dest)
        return list(map(cleanfn, files))

    def run(self):
        dest  = Path(self.config.destination).expanduser().resolve()
        files = list(filter(self.valid_file, Path(".").glob("**/*")))

        if self.config.clean:
            self.clean_all(dest, files)
        else:
            self.symlink_all(dest, files)

    def __init__(self, argv=None, config=None):
        """Emanate obeys configuration source with the following priorities:
        - command-line arguments (argv) overrides anything else;
        - programmatic configuration (config) overrides the configuration file;
        - the configuration file has the least priority.
        """
        args = Emanate.parse_args(argv) if argv is not None else {}
        conf = Emanate.parse_conf(config) if config is not None else {}

        if args.config is not None and os.path.exists(args.config):
            conf = parse_conf(args.config).update(conf)

        conf.update(args)
        self.config = conf


def main():
    return Emanate(argv=sys.argv).run()

if __name__ == '__main__':
    exit(main())
