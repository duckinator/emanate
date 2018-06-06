from argparse import ArgumentParser, SUPPRESS

def parse_args(args=None):
    argparser = ArgumentParser(
        description="symlink files from one directory to another",
        argument_default=SUPPRESS
    )
    argparser.add_argument("--clean", help="Remove symlinks.")
    argparser.add_argument("--destination",
                           metavar="DESTINATION",
                           help="Directory to create and remove symlinks in.")
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

    return argparser.parse_args(args)

