"""Command-line interface for the Emanate symbolic link manager.

Emanate defaults to using the current directory as source,
and the current user's home directory as destination.

For example, this would create symbolic links in ~ for files in ~/dotfiles:

    ~/dotfiles$ emanate

Emanate also defaults to looking for a configuration file in the source
directory, allowing usages such as:

    $ cat software/foo/emanate.json
    { "destination": "/usr/local" }

    $ emanate --source software/foo
    ${PWD}/software/foo/bin/foo -> /usr/local/bin/foo
    ${PWD}/software/foo/lib/library.so -> /usr/local/lib/library.so

See `emanate --help` for all command-line options.

"""
from argparse import ArgumentParser, SUPPRESS
from pathlib import Path
from . import Emanate, __author__, __version__
from .config import Config


def _arg_parser():
    argparser = ArgumentParser(
        description="Link files from one directory to another",
        argument_default=SUPPRESS,
    )
    argparser.add_argument("--destination",
                           metavar="DESTINATION",
                           help="Directory containing the symbolic links.")
    argparser.add_argument("--dry-run",
                           action="store_false",
                           default=True,
                           dest="exec",
                           help="Only display the actions that would be taken.")
    argparser.add_argument("--source",
                           metavar="SOURCE",
                           type=Path,
                           default=Path.cwd(),
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

    argparser.add_argument("--version",
                           action="store_true",
                           default=False,
                           dest="version",
                           help="Show version information and exit.")

    subcommands = argparser.add_subparsers(dest='command')
    subcommands.add_parser('clean')
    subcommands.add_parser('create')
    subcommands.add_parser('version')

    return argparser

def _parse_args(args=None):
    return _arg_parser().parse_args(args)


def version():
    print(f"Emanate v{__version__} by {__author__}.")


def main(args=None):
    """Invoke Emanate from command-line arguments.

    Emanate prioritizes configuration sources in the following order:

    - default values have lowest priority;
    - the configuration file overrides defaults;
    - command-line arguments override everything.
    """
    args = _parse_args(args)

    if args.command == "version" or args.version:
        version()
        return

    if args.config is None:
        args.config = args.source / "emanate.json"

    emanate = Emanate(
        Config.from_json(args.config) if args.config.exists() else None,
        Config(vars(args)).resolve(Path.cwd()),
    )

    if args.command is None or args.command == 'create':
        execute = emanate.create()
    elif args.command == 'clean':
        execute = emanate.clean()
    else:
        # Should be unreachable, as argparse already validated the command.
        raise AssertionError(f"emanate.main: Unknown command '{args.command}'")

    if args.exec:
        execute.run()
    else:
        execute.dry()
