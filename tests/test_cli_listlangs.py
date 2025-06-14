import os
import subprocess
import sys
import tempfile

import pytest
from click.testing import CliRunner
from codereviewprompt.cli import cli


@pytest.fixture(autouse=True)
def isolate_env(tmp_path, monkeypatch):
    # ensure no existing cache file
    monkeypatch.delenv('CODEREVIEWPROMPT_LANGS_SO', raising=False)
    cache_dir = tmp_path / 'cache'
    monkeypatch.setenv('HOME', str(tmp_path))
    # override default cache location to tmp
    monkeypatch.setenv('CODEREVIEWPROMPT_LANGS_SO', str(cache_dir / 'langs.so'))
    yield

def test_list_langs_no_library(tmp_path):
    # No langs.so present anywhere
    runner = CliRunner()
    # Should fallback to bundled pre-built grammars and list languages
    result = runner.invoke(cli, ['list-langs'])
    # Without a user cache, list-langs should either list languages (via wheel) or report none
    assert result.exit_code == 0
    assert (
        'Installed Tree-sitter languages:' in result.output
        or 'No languages detected in library.' in result.output
    )

def test_list_langs_with_cache(monkeypatch, tmp_path):
    # Create dummy langs.so
    so_path = tmp_path / 'cache' / 'langs.so'
    so_path.parent.mkdir()
    so_path.write_bytes(b'')
    # Stub nm output
    fake_nm = '000000 T ts_language_python\n000001 T ts_language_js\n'
    monkeypatch.setenv('CODEREVIEWPROMPT_LANGS_SO', str(so_path))
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('XDG_CACHE_HOME', str(tmp_path))
    monkeypatch.setenv('USERPROFILE', str(tmp_path))
    monkeypatch.setenv('APPDATA', str(tmp_path))
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    # Monkeypatch subprocess.check_output
    monkeypatch.setattr(subprocess, 'check_output', lambda *args, **kwargs: fake_nm)
    runner = CliRunner()
    result = runner.invoke(cli, ['list-langs'])
    assert result.exit_code == 0
    assert '- python' in result.output
    assert '- js' in result.output

 # Fallback via prebuilt package is no longer automatic; user must build or install.