"""
Context extraction by symbol (using Python AST) with fallback to raw diff context.
"""
import os
import ast

from codereviewprompt.diff import extract_context


def extract_by_symbol(
    file_path: str,
    hunks: list[tuple[int, int]],
    context_lines: int,
) -> list[dict]:
    """
    For Python files, use AST to locate enclosing function/class definitions for each hunk,
    and extract full symbol blocks with additional context lines. Falls back to raw
    diff-based context for unsupported files or missing symbols.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Only Python AST-based extraction is supported for now
    _, ext = os.path.splitext(file_path)
    if ext.lower() != '.py':
        return []

    # Read lines
    with open(file_path, encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    total_lines = len(lines)

    # Parse AST
    try:
        tree = ast.parse(''.join(lines))
    except SyntaxError:
        # Cannot parse, fallback entirely
        return extract_context(file_path, hunks, context_lines)

    # Collect symbol ranges: functions, async functions, classes
    symbol_ranges: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = getattr(node, 'lineno', None)
            end = getattr(node, 'end_lineno', None)
            if start is None:
                continue
            if end is None:
                # Approximate end by deepest child lineno
                end = start
                for child in ast.walk(node):
                    if hasattr(child, 'lineno'):
                        end = max(end, child.lineno)
            symbol_ranges.append((start, end))

    contexts: list[dict] = []
    for hunk_start, hunk_end in hunks:
        # Find first symbol that encloses the hunk start
        match = next(
            ((s, e) for (s, e) in symbol_ranges if s <= hunk_start <= e),
            None,
        )
        if match:
            s, e = match
            ctx_start = max(1, s - context_lines)
            ctx_end = min(total_lines, e + context_lines)
            snippet = ''.join(lines[ctx_start - 1 : ctx_end])
            contexts.append({
                'file_path': file_path,
                'hunk_start': hunk_start,
                'hunk_end': hunk_end,
                'context_start': ctx_start,
                'context_end': ctx_end,
                'snippet': snippet,
            })
        else:
            # Fallback to raw diff context for this hunk
            contexts.extend(extract_context(file_path, [(hunk_start, hunk_end)], context_lines))

    return contexts