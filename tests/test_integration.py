import json
from pathlib import Path
from tempfile import TemporaryDirectory
from emanate import main


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
    with TemporaryDirectory() as tmpdir:
        # Setup the test environment
        tmpdir = Path(tmpdir)
        src = tmpdir.joinpath('src')
        dest = tmpdir.joinpath('dest')
        src.mkdir()
        src.joinpath('foo').touch()
        dest.mkdir()

        with src.joinpath('emanate.json').open(mode='w') as config:
            json.dump({
                'destination': '../dest',
            }, config)

        assert not dest.joinpath('foo').exists()
        main(['--source', str(src)])
        assert dest.joinpath('foo').samefile(src.joinpath('foo'))
        assert not dest.joinpath('emanate.json').exists()
