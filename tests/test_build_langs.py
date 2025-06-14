import sys
import pytest

import tree_sitter
from codereviewprompt import build_langs

class DummyLanguage:
    pass

def test_missing_build_library(monkeypatch, capsys):
    # Remove build_library if present
    monkeypatch.delattr(tree_sitter.Language, 'build_library', raising=False)
    # Call main with minimal args
    with pytest.raises(SystemExit) as exc:
        build_langs.main(['python'])
    # Should exit with code 1 and print an error about missing build_library
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert 'does not support building language libraries' in captured.out

def test_help_message(capsys):
    # Running with --help should display usage and exit
    with pytest.raises(SystemExit) as exc:
        build_langs.main(['--help'])
    # argparse exits with code 0 on --help
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert 'Build Tree-sitter language library' in out or 'usage:' in out