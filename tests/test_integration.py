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
    """Test paths relative to the configuration file."""
    with directory_tree({
            'src': {
                'foo': '',
                'emanate.json': json.dumps({'destination': '../dest'}),
            },
            'dest': {},
    }) as tmpdir:
        dest_foo = tmpdir / 'dest' / 'foo'

        main(['--source', str(tmpdir / 'src')])
        assert dest_foo.samefile(tmpdir / 'src'  / 'foo')
        assert not (tmpdir / 'dest' / 'emanate.json').exists()


def test_no_config():
    """Test emanate without configuration file.

    This is a reproducing testcase for issue #8.
    """
    with directory_tree({
            'src': {
                'foo': '',
            },
            'dest': {},
    }) as tmpdir:
        dest_foo = tmpdir / 'dest' / 'foo'

        main([
            '--source', str(tmpdir / 'src'),
            '--dest', str(tmpdir / 'dest'),
        ])
        assert dest_foo.samefile(tmpdir / 'src'  / 'foo')


def test_empty_config():
    """Test emanate with an empty configuration file."""
    with directory_tree({
            'src': {
                'foo': '',
                'emanate.json': '{}',
            },
            'dest': {},
    }) as tmpdir:
        dest_foo = tmpdir / 'dest' / 'foo'

        main([
            '--source', str(tmpdir / 'src'),
            '--dest', str(tmpdir / 'dest'),
        ])
        assert dest_foo.samefile(tmpdir / 'src'  / 'foo')
        assert not (tmpdir / 'dest'  / 'emanate.json').exists()
