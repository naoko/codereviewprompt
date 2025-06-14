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

    # Step 3: compose prompt
    lines = []
    lines.append("# Code Review Prompt")
    lines.append("")
    if ticket:
        lines.append(f"**Ticket**: {ticket}")
        lines.append("")
    lines.append("## Context Snippets")
    lines.append("")
    for ctx in contexts:
        header = f"### {ctx['file_path']}:{ctx['context_start']}-{ctx['context_end']}"
        lines.append(header)
        lines.append('```')
        # strip trailing newline to avoid extra blank
        snippet = ctx['snippet'].rstrip('\n')
        lines.append(snippet)
        lines.append('```')
        lines.append("")

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

if __name__ == '__main__':  # pragma: no cover
    cli()