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

def test_cli_build_langs_no_tree_sitter(monkeypatch):
    """If the tree_sitter binding lacks build_library, build-langs should fail with a clear error."""
    import tree_sitter
    monkeypatch.delattr(tree_sitter.Language, 'build_library', raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ['build-langs', 'python'])
    assert result.exit_code != 0
    assert 'does not support building language libraries' in result.output
    
def test_cli_build_langs_no_tree_sitter(monkeypatch):
    # Simulate missing build_library in tree_sitter.Language
    import tree_sitter
    monkeypatch.delattr(tree_sitter.Language, 'build_library', raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ['build-langs', 'python'])
    # Expect non-zero exit and message about missing tree-sitter binding
    assert result.exit_code != 0
    assert 'does not support building language libraries' in result.output