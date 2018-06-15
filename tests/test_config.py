import json
from emanate import config
from pathlib import Path
from utils import cd, directory_tree, home


def test_json_resolution():
    with directory_tree({
            'src': {
                'emanate.json': json.dumps(
                    {"source": ".", "destination": "../dest"},
                ),
            },
    }) as tmpdir:

        config_cwd = config.from_json(tmpdir / 'src' / 'emanate.json')
        assert config.is_resolved(config_cwd)

        with cd(tmpdir):
            config_tmp = config.from_json(Path('src') / 'emanate.json')
            assert config.is_resolved(config_tmp)

        with cd(tmpdir / 'src'):
            config_src = config.from_json(Path('emanate.json'))
            assert config.is_resolved(config_src)

        assert config_cwd == config_tmp == config_src
        assert config_cwd.destination.is_absolute()
        assert config_cwd.source.is_absolute()


def test_defaults():
    assert config.defaults().destination == Path.home()
    assert config.defaults().source == Path.cwd()

    with directory_tree({}) as tmpdir:
        with cd(tmpdir):
            assert config.defaults().source == Path.cwd() == tmpdir

        with home(tmpdir):
            assert config.defaults().destination == Path.home() == tmpdir
