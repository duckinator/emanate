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
                default=".",
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

    def ignored_file(self, config, path_obj):
        config_ignore = config.get("ignore", [])
        patterns = self.DEFAULT_IGNORE
        match = functools.partial(fnmatch, str(path_obj))
        return any(map(match, patterns))

    def valid_file(self, config, path_obj):
        return path_obj.is_file() and not (".git" in path_obj.parts) \
            and not self.ignored_file(config, path_obj)

    def run(self, argv):
        args    = self.parse_args(argv)
        dest    = Path(args.destination).expanduser().resolve()
        config  = json.loads(Path(args.config).read_text())
        # validfn is a partially-applied variant of valid_file(),
        # which has the first argument always set to `config`.
        validfn = functools.partial(self.valid_file, config)
        files   = list(filter(validfn, Path(".").iterdir()))

        pprint(dest)
        pprint(config)
        pprint(args)
        print(files)
        print("TODO.")

if __name__ == '__main__':
    exit(Emanate().run(sys.argv))
