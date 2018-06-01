#!/usr/bin/env python3

# Example usage:
# TODO

import argparse
import sys
from pathlib import Path
from pprint import pprint

class Emanate:
    DEFAULT_EXCLUDE = [
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
                default="emanate.yml",
                help="Configuration file to use.")
        argparser.add_argument("--version",
                action="store_true",
                default=False,
                help="Show version information")
        args = argparser.parse_args(argv[1:])
        return args

    def path(self, raw_path):
        return Path(raw_path).expanduser().resolve()

    def run(self, argv):
        args        = self.parse_args(argv)
        destination = self.path(args.destination)
        config      = self.path(args.config)

        pprint(destination)
        pprint(config)
        pprint(args)
        print("TODO.")

if __name__ == '__main__':
    exit(Emanate().run(sys.argv))
