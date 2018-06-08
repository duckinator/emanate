import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import contextmanager
import emanate


def main(*pargs):
    args = map(lambda x: x if isinstance(x, str) else str(x), pargs)
    emanate.main(args)


@contextmanager
def cd(path):
    if isinstance(path, Path):
        path = str(path)

    cwd = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(str(cwd))


@contextmanager
def directory_tree(obj):
    def mktree(path, obj):
        assert isinstance(path, Path)
        # File by content
        if isinstance(obj, str):
            with path.open(mode='w') as file:
                file.write(obj)

        # Directory
        elif 'type' not in obj:
            path.mkdir(exist_ok=True)
            for name, child in obj.items():
                mktree(path / name, child)

        elif obj['type'] == 'link':
            path.symlink_to(obj['target'])

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        if obj:
            mktree(tmpdir, obj)
        yield tmpdir


def helper(tree=None, source='src', options=lambda _: []):
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
                },
                'dest': {},
            },
            options=lambda tmpdir: ['--dest', tmpdir / 'dest'],
    ):
        assert (tmpdir / 'dest' / 'foo').samefile(tmpdir / 'src'  / 'foo')


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
