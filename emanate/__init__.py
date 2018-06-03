#!/usr/bin/env python3

# Example usage:
# TODO

from argparse import ArgumentParser
from fnmatch import fnmatch
import json
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

    def __init__(self, argv):
        self.args   = self.parse_args(argv)
        self.dest   = Path(self.args.destination).expanduser().resolve()
        self.config = self.load_config(self.args.config)

        if self.args.clean:
            self.function = self.del_symlink
        else:
            self.function = self.add_symlink

    def parse_args(self, argv):
        argparser = ArgumentParser(
                description="symlink files from one directory to another")
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
        return argparser.parse_args(argv[1:])

    def valid_file(self, path_obj, config=None):
        if config is None:
            config = self.config

        assert (not path_obj.is_absolute()), \
                "expected path_obj to be a relative path, got absolute path."

        if path_obj.is_dir():
            return False

        path = str(path_obj.resolve())
        patterns = self.DEFAULT_IGNORE + config.get("ignore", [])
        return not any(fnmatch(path, p) for p in patterns)

    def confirm(self, prompt):
        if self.args.no_confirm:
            return True

        result = None
        while not result in ["y", "n", "\n"]:
            print("{} [Y/n] ".format(prompt), end="", flush=True)
            result = sys.stdin.read(1).lower()

        return (result != "n")

    def add_symlink(self, dest, config, path_obj):
        src_file  = path_obj.resolve()
        dest_file = Path(dest, path_obj)
        prompt    = "{!r} already exists. Replace it?".format(str(dest_file))

        assert src_file.exists(), "expected {!r} to exist.".format(str(src_file))

        # If the symlink is already in place, skip it.
        if dest_file.exists() and src_file.samefile(dest_file):
            return True

        # If it's a file and not already a symlink, prompt the user to
        # overwrite it.
        if dest_file.exists():
            if self.confirm(prompt):
                # If they confirm, rename the the file.
                new_name = str(dest_file) + ".emanate"
                dest_file.rename(new_name)
            else:
                # If they don't confirm, simply return here.
                return False

        print("{!r} -> {!r}".format(str(src_file), str(dest_file)))

        dest_file.symlink_to(src_file)

        return src_file.samefile(dest_file)

    def del_symlink(self, dest, config, path_obj):
        src_file  = path_obj.resolve()
        dest_file = Path(dest, path_obj)

        print("{!r}".format(str(dest_file)))

        if dest_file.exists() and src_file.samefile(dest_file):
            dest_file.unlink()

        return not dest_file.exists()

    def load_config(self, filename):
        config_file = Path(filename)
        if config_file.exists():
            return json.loads(config_file.read_text())
        else:
            return {}

    def run(self):
        all_files = Path(".").glob("**/*")
        files = list(filter(self.valid_file, all_files))
        list(self.function(self.dest, self.config, f) for f in files)

def main():
    return Emanate(sys.argv).run()

if __name__ == '__main__':
    exit(main())
