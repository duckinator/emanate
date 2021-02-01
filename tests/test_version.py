from emanate import cli, __version__, __author__


EXPECTED_VERSION = f"Emanate v{__version__} by {__author__}.\n"


def test_version_command(capsys):
    cli.main(["version"])
    captured = capsys.readouterr()
    assert captured.out == EXPECTED_VERSION
    assert not captured.err

def test_version_flag(capsys):
    cli.main(["--version"])
    captured = capsys.readouterr()
    assert captured.out == EXPECTED_VERSION
    assert not captured.err
