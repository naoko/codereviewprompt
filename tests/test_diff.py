import os
import subprocess
import pytest

from codereviewprompt.diff import get_diff_hunks, extract_context

def test_extract_context_simple(tmp_path):
    # Create a test file with 10 lines
    lines = [f"line{i}" for i in range(1, 11)]
    file_path = tmp_path / "test.txt"
    file_path.write_text("\n".join(lines) + "\n")

    # Single-line hunk in the middle
    hunks = [(3, 3)]
    contexts = extract_context(str(file_path), hunks, context_lines=2)
    assert len(contexts) == 1
    ctx = contexts[0]
    assert ctx['file_path'] == str(file_path)
    assert ctx['hunk_start'] == 3
    assert ctx['hunk_end'] == 3
    assert ctx['context_start'] == 1  # 3 - 2 = 1
    assert ctx['context_end'] == 5    # 3 + 2 = 5
    expected = """
line1
line2
line3
line4
line5
""".lstrip()
    assert ctx['snippet'] == expected

    # Hunk near end of file
    hunks2 = [(10, 10)]
    contexts2 = extract_context(str(file_path), hunks2, context_lines=3)
    ctx2 = contexts2[0]
    assert ctx2['context_start'] == 7  # 10 - 3
    assert ctx2['context_end'] == 10   # EOF
    expected2 = """
line7
line8
line9
line10
""".lstrip()
    assert ctx2['snippet'] == expected2

def test_get_diff_hunks(tmp_path):
    # Initialize a new git repo
    repo = tmp_path / "repo"
    repo.mkdir()
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        subprocess.run(["git", "init"], check=True, stdout=subprocess.DEVNULL)
        # Configure user for commit
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)

        # Create initial file and commit
        foo = repo / "foo.txt"
        foo.write_text("a\nb\nc\n")
        subprocess.run(["git", "add", "foo.txt"], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "initial"], check=True, stdout=subprocess.DEVNULL)

        # Modify file: insert 'x' between b and c
        foo.write_text("a\nb\nx\nc\n")

        # Get diff hunks against HEAD
        hunks = get_diff_hunks('HEAD')
        assert 'foo.txt' in hunks
        file_hunks = hunks['foo.txt']
        # Expect one hunk at the inserted line (line 3)
        assert isinstance(file_hunks, list)
        assert len(file_hunks) == 1
        start, end = file_hunks[0]
        assert start == 3
        assert end == 3
    finally:
        os.chdir(cwd)