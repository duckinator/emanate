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
            "*/.git",
            "*/.git/*",
            "*/.gitignore",
            "*/.gitmodules",
            "*/__pycache__",
            "*/__pycache__/*",
            ]

    def __init__(self, argv):
        args   = self.parse_args(argv)
        config = self.load_config(args.config)
        self.dest   = Path(args.destination).expanduser().resolve()
        self.ignore = self.DEFAULT_IGNORE + config.get("ignore", [])
        self.no_confirm = args.no_confirm

        if args.clean:
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
                help="Directory to create and/or remove symlinks in.")
        argparser.add_argument("--no-confirm",
                action="store_true",
                default=False,
                help="Don't prompt before replacing a file.")
        argparser.add_argument("--config",
                metavar="CONFIG_FILE",
                default="emanate.json",
                help="Configuration file to use.")
        return argparser.parse_args(argv[1:])

    def valid_file(self, path_obj):
        path = str(path_obj.resolve())
        if any(fnmatch(path, pattern) for pattern in self.ignore):
            return False

        if path_obj.is_dir():
            Path(self.dest, path_obj).mkdir(exist_ok=True)
            return False

        return True

    def confirm_replace(self, dest_file):
        prompt = "{!r} already exists. Replace it?".format(str(dest_file))

        if self.no_confirm:
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

    def load_config(self, filename):
        config_file = Path(filename)
        if config_file.exists():
            return json.loads(config_file.read_text())
        else:
            return {}

    def run(self):
        all_files = Path(".").glob("**/*")
        files = filter(self.valid_file, all_files)
        list(map(self.function, files))

def main():
    return Emanate(sys.argv).run()

if __name__ == '__main__':
    exit(main())
