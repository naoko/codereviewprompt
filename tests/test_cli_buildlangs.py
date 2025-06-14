import sys
from click.testing import CliRunner
import pytest

from codereviewprompt.cli import cli

def test_build_langs_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['build-langs', '--help'])
    assert result.exit_code == 0
    assert 'Clone and compile Tree-sitter grammars' in result.output

def test_build_langs_missing_args():
    runner = CliRunner()
    # No languages provided
    result = runner.invoke(cli, ['build-langs'])
    # argparse should exit with code 2 for missing required arguments
    assert result.exit_code != 0
    assert 'Usage:' in result.output