"""Console script for codereviewprompt."""
import sys
import click

@click.group()
def cli():
    """codereviewprompt CLI."""
    pass

@cli.command()
@click.option('--base', default='main', show_default=True,
              help='Commit/branch/tag to diff against')
@click.option('--ticket', default=None,
              help='Ticket ID to fetch via REST')
@click.option('--context-lines', default=50, show_default=True, type=int,
              help='Lines of context around each touched symbol')
@click.option('--out', default='clipboard', show_default=True,
              help='clipboard, stdout, or a file path')
@click.option('--model', default='gemini', show_default=True,
              help='Reserved for future custom prompts')
def run(base, ticket, context_lines, out, model):
    """Generate a code-review prompt based on local git diff and context extraction."""
    # Step 1: compute diff hunks against the base
    from codereviewprompt.diff import get_diff_hunks, extract_context

    hunks_map = get_diff_hunks(base, unified=0)
    if not hunks_map:
        click.echo("No changes detected.")
        return

    # Step 2: extract context snippets for each hunk
    contexts = []
    # Step 2: extract context snippets for each hunk, preferring symbol-based when available
    from codereviewprompt.context import extract_by_symbol
    for file_path, hunks in hunks_map.items():
        if not hunks:
            continue
        try:
            # Try AST-based symbol extraction for Python
            snippets = extract_by_symbol(file_path, hunks, context_lines)
        except FileNotFoundError:
            # Skip deleted or missing files
            continue
        # Fallback to raw diff context if no symbol snippets
        if not snippets:
            snippets = extract_context(file_path, hunks, context_lines)
        contexts.extend(snippets)

    if not contexts:
        click.echo("No context available for the detected changes.")
        return

    # Step 3: compose prompt with rubric, diff, and context snippets
    lines: list[str] = []
    lines.append('# Code Review Prompt')
    lines.append('')
    # Rubric & severity guide
    lines.append('## Review Rubric & Severity Guide')
    lines.append('')
    lines.append('**Critical**: security vulnerabilities, data loss, crashes.')
    lines.append('**Major**: logic errors, performance regressions, incorrect functionality.')
    lines.append('**Minor**: code readability, maintainability, edge cases.')
    lines.append('**Style**: formatting, naming, comments.')
    lines.append('')
    # Optional ticket info
    if ticket:
        lines.append(f'**Ticket**: {ticket}')
        lines.append('')
    # Full diff
    lines.append('## Diff')
    lines.append('')
    lines.append('```diff')
    # Retrieve raw git diff; handle errors explicitly
    import subprocess
    try:
        diff_text = subprocess.check_output(
            ['git', 'diff', f'--unified=0', base],
            stderr=subprocess.PIPE,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        diff_text = ''
    # Include raw diff lines
    for l in diff_text.rstrip().splitlines():
        lines.append(l)
    lines.append('```')
    lines.append('')
    # Contextual snippets grouped by file
    lines.append('## Context Snippets')
    lines.append('')
    for ctx in contexts:
        header = f"### {ctx['file_path']}:{ctx['context_start']}-{ctx['context_end']}"
        lines.append(header)
        lines.append('```')
        snippet = ctx['snippet'].rstrip('\n')
        lines.append(snippet)
        lines.append('```')
        lines.append('')
    prompt = '\n'.join(lines)

    # Step 4: output
    if out == 'stdout':
        click.echo(prompt)
    elif out == 'clipboard':
        try:
            import pyperclip

            pyperclip.copy(prompt)
            click.echo("Prompt copied to clipboard.")
        except ImportError:
            click.echo("pyperclip not installed; cannot copy to clipboard.")
    else:
        # treat 'out' as a file path
        try:
            with open(out, 'w', encoding='utf-8') as f:
                f.write(prompt)
            click.echo(f"Prompt written to {out}")
        except OSError as e:
            click.echo(f"Failed to write prompt to {out}: {e}")

# Move entrypoint below all command definitions
  
@cli.command('list-langs')
def list_langs():  # pragma: no cover
    """List Tree-sitter languages embedded in the shared library."""
    import os
    import sys
    import subprocess
    # Determine library path (env override, cache default)
    so_path = os.environ.get(
        'CODEREVIEWPROMPT_LANGS_SO',
        os.path.expanduser('~/.cache/codereviewprompt/langs.so')
    )
    # Auto-fallback: try wheel-provided shared lib from tree-sitter-languages
    if not os.path.exists(so_path):
        try:
            from importlib.metadata import distribution, files, PackageNotFoundError
            dist = distribution('tree-sitter-languages')
            for f in files('tree-sitter-languages'):
                if f.name.endswith('.so'):
                    candidate = str(dist.locate_file(f))
                    if os.path.exists(candidate):
                        so_path = candidate
                        break
        except Exception:
            pass
    if not os.path.exists(so_path):
        click.echo(
            f"Language library not found at {so_path}."
            " Please install the 'tree-sitter-languages' package or run"
            " `codereviewprompt build-langs <languages...>`"
        )
        sys.exit(1)
    try:
        output = subprocess.check_output(
            ['nm', so_path], stderr=subprocess.DEVNULL, text=True
        )
    except subprocess.CalledProcessError:
        click.echo("Failed to inspect language library.")
        sys.exit(1)
    langs = set()
    for line in output.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3 and parts[2].startswith('ts_language_'):
            langs.add(parts[2].split('ts_language_')[1])
    if not langs:
        click.echo("No languages detected in library.")
        return
    click.echo("Installed Tree-sitter languages:")
    for lang in sorted(langs):
        click.echo(f"- {lang}")

@cli.command('build-langs')
@click.argument('languages', nargs=-1, required=True)
@click.option(
    '--repo-prefix', default='https://github.com/tree-sitter/tree-sitter-',
    help='Git repo prefix for Tree-sitter grammar repos'
)
@click.option(
    '--output', default=None,
    help='Path to output shared library (defaults to cache location)'
)
def build_langs_cmd(languages, repo_prefix, output):  # pragma: no cover
    """Clone and compile Tree-sitter grammars into a shared library."""
    args: list[str] = []
    args += ['--repo-prefix', repo_prefix]
    if output:
        args += ['--output', output]
    args += list(languages)
    try:
        from codereviewprompt.build_langs import main
    except ImportError:
        click.echo('build_langs module not found; cannot compile grammars.')
        sys.exit(1)
    main(args)

"""Entry point: invoke the CLI when run as a script."""
# Invoke CLI after all commands are registered
if __name__ == '__main__':  # pragma: no cover
    cli()

  