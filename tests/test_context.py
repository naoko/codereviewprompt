import ast
from codereviewprompt.context import extract_by_symbol
from codereviewprompt.diff import extract_context


def test_extract_by_symbol_python_function(tmp_path):
    # Create a Python file with two functions
    content = [
        'def foo():\n',
        '    x = 1\n',
        '    y = 2\n',
        '\n',
        'def bar():\n',
        '    pass\n',
    ]
    file_path = tmp_path / 'example.py'
    file_path.write_text(''.join(content))

    # Hunk inside foo (line 3)
    hunks = [(3, 3)]
    contexts = extract_by_symbol(str(file_path), hunks, context_lines=0)
    # Should extract only the foo function (lines 1-3)
    assert len(contexts) == 1
    ctx = contexts[0]
    assert ctx['file_path'] == str(file_path)
    assert ctx['hunk_start'] == 3
    assert ctx['hunk_end'] == 3
    assert ctx['context_start'] == 1
    assert ctx['context_end'] == 3
    expected = ''.join(content[0:3])
    assert ctx['snippet'] == expected

def test_extract_by_symbol_python_class(tmp_path):
    # Create Python file with a class
    content = [
        'class A:\n',
        '    def m(self):\n',
        '        return 42\n',
        '\n',
        'def other():\n',
        '    pass\n',
    ]
    file_path = tmp_path / 'cls.py'
    file_path.write_text(''.join(content))

    # Hunk inside method m (line 3)
    hunks = [(3, 3)]
    contexts = extract_by_symbol(str(file_path), hunks, context_lines=0)
    # Should extract class A block (lines 1-3)
    assert len(contexts) == 1
    ctx = contexts[0]
    assert ctx['context_start'] == 1
    assert ctx['context_end'] == 3
    expected = ''.join(content[0:3])
    assert ctx['snippet'] == expected

def test_extract_by_symbol_fallback_non_python(tmp_path):
    # Non-Python file should return empty list
    file_path = tmp_path / 'data.txt'
    file_path.write_text('foo\nbar\n')
    contexts = extract_by_symbol(str(file_path), [(1, 1)], context_lines=10)
    assert contexts == []

def test_extract_by_symbol_syntax_error(tmp_path):
    # Syntax error Python file falls back to raw diff context
    content = [
        'def bad():\n',
        '    x =\n',  # invalid syntax
    ]
    file_path = tmp_path / 'bad.py'
    file_path.write_text(''.join(content))
    # Single hunk
    hunks = [(2, 2)]
    contexts = extract_by_symbol(str(file_path), hunks, context_lines=1)
    # Fallback to raw extract_context: expect context around line 2
    assert contexts
    ctx = contexts[0]
    # context_start should be 1 (2-1)
    assert ctx['context_start'] == 1
    # snippet should include both lines
    assert 'def bad()' in ctx['snippet']