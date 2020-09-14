from emanate import cli, __version__, __author__


EXPECTED_VERSION = "Emanate v{} by {}.\n".format(__version__, __author__)


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
