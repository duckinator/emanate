import json
import emanate
import tempfile
from pathlib import Path
from utils import cd, directory_tree, home


def main(*pargs):
    """Converts arguments, prints them and the cwd, then calls emanate.main."""
    args = [x if isinstance(x, str) else str(x) for x in pargs]
    print('cwd:', Path.cwd())
    print('emanate', *args)
    emanate.main(args)


def helper(tree=None, source='src', options=lambda _: []):
    """Run main in clean environments, with various '--source' options.

    Each invocation is done against a separate, temporary directory.
    main is currently run 3 times:
    - from the current working directory, with `--source tmpdir/src`;
    - from `tmpdir`, with `--source src`;
    - from `tmpdir/src`, without --source argument.
    """
    homedir = Path(tempfile.mkdtemp())
    with home(homedir):
        with directory_tree(tree) as tmpdir:
            main('--source', tmpdir / source, *options(tmpdir))
            yield tmpdir

        with directory_tree(tree) as tmpdir:
            with cd(tmpdir):
                main('--source', source, *options(tmpdir))
                yield tmpdir

        with directory_tree(tree) as tmpdir:
            with cd(tmpdir / source):
                main(*options(tmpdir))
                yield tmpdir

    # Implicitely asserts that `homedir` is empty
    homedir.rmdir()


def test_config_relative_path():
    """Test paths relative to the configuration file."""
    for tmpdir in helper(
            tree={
                'src': {
                    'foo': '',
                    'emanate.json': json.dumps({'destination': '../dest'}),
                },
                'dest': {},
            }):
        assert (tmpdir / 'dest' / 'foo').samefile(tmpdir / 'src'  / 'foo')
        assert not (tmpdir / 'dest' / 'emanate.json').exists()


def test_no_config():
    """Test emanate without configuration file.

    This is a reproducing testcase for issue #8.
    """
    for tmpdir in helper(
            tree={
                'src': {
                    'foo': '',
                    'bar': {'baz': ''},
                },
                'dest': {},
            },
            options=lambda tmpdir: ['--dest', tmpdir / 'dest'],
    ):
        assert (tmpdir / 'dest' / 'foo').samefile(tmpdir / 'src'  / 'foo')
        assert (tmpdir / 'dest' / 'bar' / 'baz').samefile(
            tmpdir / 'src'  / 'bar' / 'baz',
        )


def test_empty_config():
    """Test emanate with an empty configuration file."""
    for tmpdir in helper(
            tree={
                'src': {
                    'foo': '',
                    'emanate.json': '{}',
                },
                'dest': {},
            },
            options=lambda tmpdir: ['--dest', tmpdir / 'dest'],
    ):
        assert (tmpdir / 'dest' / 'foo').samefile(tmpdir / 'src'  / 'foo')
        assert not (tmpdir / 'dest'  / 'emanate.json').exists()
