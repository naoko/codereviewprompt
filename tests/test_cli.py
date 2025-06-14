import pytest
from click.testing import CliRunner
from codereviewprompt.cli import cli

def test_help_shows_run_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'run' in result.output

def test_run_stub_exits_with_1():
    runner = CliRunner()
    result = runner.invoke(cli, ['run'])
    # In a non-repo or with no changes, we expect a graceful no-op
    assert result.exit_code == 0
    assert 'No changes detected' in result.output