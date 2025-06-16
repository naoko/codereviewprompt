"""
Context extraction by symbol (using Tree-sitter or Python AST) with fallback to raw diff context.
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
    For Python files, use Tree-sitter to locate enclosing function/class definitions
    for each hunk, and extract full symbol blocks with additional context lines.
    Falls back to raw diff-based context for unsupported files or missing symbols.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    _, ext = os.path.splitext(file_path)
    if ext.lower() != '.py':
        return []

    # Read source lines
    with open(file_path, encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    total_lines = len(lines)
    source = ''.join(lines).encode('utf8')

    # Collect symbol ranges: try Tree-sitter first, then Python AST
    symbol_ranges: list[tuple[int, int]] = []
    try:
        from tree_sitter import Parser
        from tree_sitter_languages import get_language

        # Load Python language via tree-sitter-languages
        PY_LANGUAGE = get_language('python')
        parser = Parser()
        parser.language = PY_LANGUAGE
        tree = parser.parse(source)
        # Traverse Tree-sitter tree for symbols
        def traverse(node):
            if node.type in ('function_definition', 'class_definition'):
                s = node.start_point[0] + 1
                e = node.end_point[0] + 1
                symbol_ranges.append((s, e))
            for child in node.children:
                traverse(child)
        traverse(tree.root_node)
    except Exception:
        symbol_ranges = []
    # Fallback to AST if no symbols found
    if not symbol_ranges:
        try:
            tree = ast.parse(''.join(lines))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    s = getattr(node, 'lineno', None)
                    e = getattr(node, 'end_lineno', None)
                    if s is None:
                        continue
                    if e is None:
                        e = s
                        for child in ast.walk(node):
                            if hasattr(child, 'lineno'):
                                e = max(e, child.lineno)
                    symbol_ranges.append((s, e))
        except SyntaxError:
            # Fallback entirely to raw diff context
            return extract_context(file_path, hunks, context_lines)

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