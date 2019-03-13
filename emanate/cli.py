"""Command-line interface for the Emanate symbolic link manager.

Examples:
    Emanate defaults to using the current directory as source,
    and the current user's home directory as destination::

        ~/.dotfiles $ emanate

    would create symbolic links in ~ for files in ~/.dotfiles

    Emanate also defaults to looking for a configuration file in the source
    directory, allowing usages such as::

        $ cat software/foo/emanate.json
        { 'destination': '/usr/local' }

        $ emanate --source software/foo
        ${PWD}/software/foo/bin/foo -> /usr/local/bin/foo
        ${PWD}/software/foo/lib/library.so -> /usr/local/lib/library.so

    See `emanate --help` for all command-line options.

"""
from argparse import ArgumentParser, SUPPRESS
from pathlib import Path
from . import Emanate, config


def _parse_args(args=None):
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

    subcommands = argparser.add_subparsers(dest='command')
    subcommands.add_parser('clean')
    subcommands.add_parser('create')

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

    emanate = Emanate(
        config.from_json(args.config) if args.config.exists() else None,
        config.resolve(vars(args)),
        src=vars(args).get("source", None),
    )

    if args.command is None or args.command == 'create':
        execute = emanate.create()
    elif args.command == 'clean':
        execute = emanate.clean()
    else:
        assert False

    if args.exec:
        execute.run()
    else:
        execute.dry()
