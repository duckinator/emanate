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

    def parse_args(self, argv):
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

    def valid_file(self, config, path_obj):
        if path_obj.is_dir():
            return False

        path = str(path_obj.resolve())
        patterns = self.DEFAULT_IGNORE + config.get("ignore", [])
        return not any(fnmatch(path, p) for p in patterns)

    def confirm(self, prompt):
        result = None
        while not result in ["y", "n"]:
            print("{} [Y/n] ".format(prompt), end="", flush=True)
            result = sys.stdin.read(1).lower()

        return (result == "y")

    def symlink_file(self, dest, no_confirm, config, path_obj):
        assert (not path_obj.is_absolute()), \
                "expected path_obj to be a relative path, got absolute path."

        src_file  = path_obj.resolve()
        dest_file = Path(dest, path_obj)
        prompt    = "{!r} already exists. Replace it?".format(str(dest_file))

        assert src_file.exists(), "expected {!r} to exist.".format(str(src_file))

        # If the symlink is already in place, skip it.
        if dest_file.exists() and src_file.samefile(dest_file):
            return True

        # If it's not a file, skip it.
        if src_file.exists() and not src_file.is_file():
            return False

        # If it's a file and not already a symlink, prompt the user to
        # overwrite it.
        if dest_file.exists():
            if no_confirm or self.confirm(prompt):
                # If they confirm, overwrite it.
                dest_file.unlink()
            else:
                # If they don't confirm, simply return here.
                return False

        print("{!r} -> {!r}".format(str(src_file), str(dest_file)))

        dest_file.symlink_to(src_file)

        return src_file.samefile(dest_file)

    def symlink_all(self, dest, args, config, files):
        # symlinkfn is a partially-applied variant of symlink_file(),
        # which has the first 3 arguments always set to:
        #     dest, args.no_confirm, config
        symlinkfn = functools.partial(self.symlink_file, dest, args.no_confirm, config)
        return list(map(symlinkfn, files))

    def clean_file(self, dest, config, path_obj):
        assert (not path_obj.is_absolute()), \
                "expected path_obj to be a relative path, got absolute path."

        src_file  = path_obj.resolve()
        dest_file = Path(dest, path_obj)

        print("{!r}".format(str(dest_file)))

        if dest_file.exists() and src_file.samefile(dest_file):
            dest_file.unlink()

        return not dest_file.exists()

    def clean_all(self, dest, config, files):
        # cleanfn is a partially-applied variant of clean_file(),
        # which has the first 3 arguments always set to:
        #     dest, args.no_confirm, config
        cleanfn = functools.partial(self.clean_file, dest, config)
        return list(map(cleanfn, files))

    def run(self, argv):
        args = self.parse_args(argv)
        dest = Path(args.destination).expanduser().resolve()

        config_file = Path(args.config)
        if config_file.exists():
            config = json.loads(config_file.read_text())
        else:
            config = {}

        all_files = Path(".").glob("**/*")
        validfn = lambda path_obj: self.valid_file(config, path_obj)
        files = list(filter(validfn, all_files))

        if args.clean:
            self.clean_all(dest, config, files)
        else:
            self.symlink_all(dest, args, config, files)

def main():
    return Emanate().run(sys.argv)

if __name__ == '__main__':
    exit(main())
