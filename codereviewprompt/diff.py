"""
Functions for extracting git diff hunks and surrounding context.
"""
import subprocess
import re
import os

def get_diff_hunks(base: str, unified: int = 0) -> dict[str, list[tuple[int, int]]]:
    """
    Run `git diff` against the given base (branch, tag, or commit) with specified unified context,
    and parse hunk headers to return a mapping of file paths to lists of (start, end) line ranges
    in the new version.
    """
    # Run git diff
    try:
        output = subprocess.check_output(
            ['git', 'diff', f'--unified={unified}', base],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except subprocess.CalledProcessError:
        return {}

    hunks: dict[str, list[tuple[int, int]]] = {}
    current_file: str | None = None
    # Regex to match a new-file path in diff header
    new_file_re = re.compile(r'^\+\+\+ [ab]/?(.*)')
    # Regex to match hunk headers, capturing new file start and length
    hunk_re = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@')

    for line in output.splitlines():
        # Detect file path
        if line.startswith('+++ '):
            m = new_file_re.match(line)
            if m:
                path = m.group(1)
                # /dev/null indicates deletion
                if path == '/dev/null':
                    current_file = None
                else:
                    current_file = path
                    hunks.setdefault(current_file, [])
            else:
                current_file = None
            continue

        # Parse hunk headers
        if line.startswith('@@ ') and current_file:
            m = hunk_re.match(line)
            if not m:
                continue
            start = int(m.group(1))
            length = int(m.group(2)) if m.group(2) is not None else 1
            # If no new lines (deletion), treat the hunk as a single-line at start
            if length == 0:
                end = start
            else:
                end = start + length - 1
            hunks[current_file].append((start, end))

    return hunks

def extract_context(
    file_path: str,
    hunks: list[tuple[int, int]],
    context_lines: int,
) -> list[dict]:
    """
    Given a file path and list of (start, end) line ranges (1-based), return a list of
    context snippets, each a dict with keys:
      - file_path: the file examined
      - hunk_start, hunk_end: original hunk range
      - context_start, context_end: snippet boundaries
      - snippet: the code snippet as a single string
    Extracts up to `context_lines` lines before and after each hunk.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read all lines from file (preserving line breaks)
    with open(file_path, encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    total = len(lines)
    contexts: list[dict] = []

    for start, end in hunks:
        # Determine context boundaries
        ctx_start = max(1, start - context_lines)
        ctx_end = min(total, end + context_lines)

        # Extract snippet (0-based indexing)
        snippet = ''.join(lines[ctx_start - 1 : ctx_end])

        contexts.append({
            'file_path': file_path,
            'hunk_start': start,
            'hunk_end': end,
            'context_start': ctx_start,
            'context_end': ctx_end,
            'snippet': snippet,
        })

    return contexts