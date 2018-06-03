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
from pprint import pprint

class Emanate:
    DEFAULT_IGNORE = [
            "*~",
            ".*~",
            ".*.sw?",
            "emanate.yml",
            "*.emanate",
            ".*.emanate",
            ".git",
            ".gitignore",
            ".gitmodules",
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

    def ignored_file(self, config, path):
        path = str(path)
        patterns = self.DEFAULT_IGNORE + config.get("ignore", [])
        match = functools.partial(fnmatch, path)
        return any(map(match, patterns))

    def valid_file(self, config, path_obj):
        return path_obj.is_file() and not (".git" in path_obj.parts) \
            and not self.ignored_file(config, path_obj)

    def confirm(self, prompt, no_confirm):
        if no_confirm:
            return True

        result = None
        while not result in ["y", "n"]:
            print("{} [Y/n] ".format(prompt), end="", flush=True)
            result = sys.stdin.read(1)

        return (result == "y")

    def file_exists_and_not_identical(self, src_file, dest_file):
        return dest_file.exists() #and ???

    def symlink_file(self, dest, no_confirm, config, path_obj):
        assert (not path_obj.is_absolute()), \
            "expected path_obj to be a relative path, got absolute path."

        src_file  = path_obj
        dest_file = Path(dest, path_obj)
        prompt    = "{!r} already exists. Replace it?".format(str(dest_file))

        if self.file_exists_and_not_identical(src_file, dest_file) and \
            not self.confirm(prompt, no_confirm):
                return False


        print("{!r} -> {!r}".format(str(src_file), str(dest_file)))
        return True

    def run(self, argv):
        args    = self.parse_args(argv)
        dest    = Path(args.destination).expanduser().resolve()
        config  = json.loads(Path(args.config).read_text())

        # validfn is a partially-applied variant of valid_file(),
        # which has the first argument always set to `config`.
        validfn = functools.partial(self.valid_file, config)
        files   = list(filter(validfn, Path(".").iterdir()))

        # symlinkfn is a partially-applied variant of symlink_file(),
        # which has the first 3 arguments always set to:
        #     dest, args.no_confirm, config
        symlinkfn = functools.partial(self.symlink_file, dest, args.no_confirm, config)
        list(map(symlinkfn, files))

if __name__ == '__main__':
    exit(Emanate().run(sys.argv))
