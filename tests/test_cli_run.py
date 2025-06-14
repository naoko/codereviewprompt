import os
import subprocess

import pytest
from click.testing import CliRunner
from codereviewprompt.cli import cli


@pytest.fixture(autouse=True)
def preserve_cwd(tmp_path, monkeypatch):
    """Ensure tests run in isolated temp dirs without affecting real cwd."""
    orig_cwd = os.getcwd()
    # Jump into a temp dir for each test
    os.chdir(tmp_path)
    yield
    os.chdir(orig_cwd)

def init_repo_with_change(tmp_path):
    # Create a repo dir and initialize
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    os.chdir(repo_dir)
    # git init and minimal config
    subprocess.run(["git", "init"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)
    # initial commit
    file_path = repo_dir / "foo.txt"
    file_path.write_text("a\nb\nc\n")
    subprocess.run(["git", "add", "foo.txt"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", "initial"], check=True, stdout=subprocess.DEVNULL)
    # modify file: insert 'x' after 'a'
    file_path.write_text("a\nx\nb\nc\n")
    return repo_dir

def test_run_outputs_context(tmp_path):
    # Setup repo with a change
    repo = init_repo_with_change(tmp_path)
    # Invoke CLI in that repo
    runner = CliRunner()
    # Run CLI from inside the repo (init_repo has chdir'd)
    result = runner.invoke(
        cli,
        ['run', '--base', 'HEAD', '--context-lines', '1', '--out', 'stdout'],
    )
    assert result.exit_code == 0
    output = result.output
    # Should mention the file and context range 1-3
    # Should include the rubric header
    assert '## Review Rubric & Severity Guide' in output
    assert '**Critical**' in output
    # Should include diff section
    assert '## Diff' in output
    assert '```diff' in output
    # Diff should show the inserted 'x'
    assert '+x' in output
    # Context snippets as before
    assert 'foo.txt:1-3' in output
    assert 'a\nx\nb' in output

def test_run_no_changes(tmp_path):
    # Initialize empty repo
    repo_dir = tmp_path / "emptyrepo"
    repo_dir.mkdir()
    os.chdir(repo_dir)
    subprocess.run(["git", "init"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)
    # No commits or changes
    runner = CliRunner()
    # In an empty or no-commit repo
    result = runner.invoke(cli, ['run', '--base', 'HEAD'])
    assert result.exit_code == 0
    assert 'No changes detected' in result.output