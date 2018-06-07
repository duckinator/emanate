import json
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import contextmanager
from emanate import main


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
        mktree(tmpdir, obj)
        yield tmpdir


def test_config_relative_path():
    """Test paths relative to the configuration file.

    Creates the following hierarchy, and calls `emanate --source tmpdir/src`:
    tmpdir
    ├── dest
    └── src
        ├── foo
        └── emanate.json

    This test then asserts that tmpdir/dest/foo exists, and that
    tmpdir/dest/emanate.json does not.
    """
    with directory_tree({
            'src': {
                'foo': '',
                'emanate.json': json.dumps({'destination': '../dest'}),
            },
            'dest': {},
    }) as tmpdir:
        dest_foo = tmpdir / 'dest' / 'foo'

        assert not dest_foo.exists()
        main(['--source', str(tmpdir / 'src')])
        assert dest_foo.samefile(tmpdir / 'src'  / 'foo')
        assert not (tmpdir / 'dest' / 'emanate.json').exists()


def test_no_config():
    """Test emanate without configuration file. (See issue #8)

    Creates the following hierarchy, and calls
    `emanate --source tmpdir/src --dest tmpdir/dest`:
    tmpdir
    ├── dest
    └── src
        └── foo

    This test then asserts that tmpdir/dest/foo exists.
    """
    with directory_tree({
            'src': {
                'foo': '',
            },
            'dest': {},
    }) as tmpdir:
        dest_foo = tmpdir / 'dest' / 'foo'

        assert not dest_foo.exists()
        main([
            '--source', str(tmpdir / 'src'),
            '--dest', str(tmpdir / 'dest'),
        ])
        assert dest_foo.samefile(tmpdir / 'src'  / 'foo')
