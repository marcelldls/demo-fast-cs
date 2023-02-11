import subprocess
import sys

from demo_fast_cs import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "demo_fast_cs", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
