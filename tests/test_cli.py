import pytest
from click.testing import CliRunner
from codereviewprompt.cli import cli

def test_help_shows_run_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'run' in result.output

def test_run_default_copies_clipboard():
    runner = CliRunner()
    result = runner.invoke(cli, ['run'])
    # Default behavior in a repo: copy prompt to clipboard
    assert result.exit_code == 0
    assert 'Prompt copied to clipboard.' in result.output