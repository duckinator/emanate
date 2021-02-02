import json
from pathlib import Path

from utils import chdir, directory_tree, home
from emanate import config
from emanate.config import Config


def test_json_resolution():
    with directory_tree({
            'src': {
                'emanate.json': json.dumps(
                    {"source": ".", "destination": "../dest"},
                ),
            },
    }) as tmpdir:

        config_cwd = Config.from_json(tmpdir / 'src' / 'emanate.json')
        assert config.is_resolved(config_cwd)

        with chdir(tmpdir):
            config_tmp = Config.from_json(Path('src') / 'emanate.json')
            assert config.is_resolved(config_tmp)

        with chdir(tmpdir / 'src'):
            config_src = Config.from_json(Path('emanate.json'))
            assert config.is_resolved(config_src)

        assert config_cwd == config_tmp == config_src
        assert config_cwd.destination.is_absolute()
        assert config_cwd.source.is_absolute()


def test_defaults():
    for path in (Path.cwd(), Path.home()):
        default = Config.defaults(path)
        assert default.destination == Path.home()
        assert 'source' not in default

    with directory_tree({}) as tmpdir:
        with home(tmpdir):
            default = Config.defaults(tmpdir)
            # The home directory should have changed.
            assert Path.home().samefile(tmpdir)
            # Emanate's default destination should be the new home directory.
            assert default.destination.samefile(tmpdir)
            assert 'source' not in default
