"""
Build a shared library of Tree-sitter grammars for the CLI to use.

Usage:
  python -m codereviewprompt.build_langs c python javascript typescript go
"""
import os
import sys
import tempfile
import subprocess
import shutil

from tree_sitter import Language


def main(args=None):
    import argparse
    parser = argparse.ArgumentParser(
        description="Build Tree-sitter language library for codereviewprompt"
    )
    parser.add_argument(
        'languages', nargs='+',
        help='List of language names to include (e.g., python, javascript)'
    )
    parser.add_argument(
        '-o', '--output',
        default=os.path.expanduser('~/.cache/codereviewprompt/langs.so'),
        help='Path to write the compiled shared library'
    )
    parser.add_argument(
        '--repo-prefix',
        default='https://github.com/tree-sitter/tree-sitter-',
        help='GitHub prefix for language grammar repos'
    )
    opts = parser.parse_args(args=args)

    # Verify that the Language.build_library API is available
    if not hasattr(Language, 'build_library'):
        print(
            "Error: your installed tree-sitter binding does not support building language libraries.\n"
            "This usually means the tree-sitter C library and headers were missing at install time.\n"
            "On macOS, install via: brew install tree-sitter\n"
            "On Debian/Ubuntu: sudo apt-get install libtree-sitter-dev\n"
            "Then reinstall the Python binding from source:\n"
            "  pip uninstall tree-sitter\n"
            "  pip install --no-binary=:all: tree-sitter>=0.20\n"
        )
        sys.exit(1)
    # Prepare temporary directory for cloning grammar repos
    tempdir = tempfile.mkdtemp(prefix='crp-grammars-')
    repos = []
    try:
        for lang in opts.languages:
            repo_url = opts.repo_prefix + lang + '.git'
            dest = os.path.join(tempdir, f'tree-sitter-{lang}')
            print(f'Cloning {repo_url}...')
            subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, dest],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            repos.append(dest)

        # Ensure output directory exists
        out_dir = os.path.dirname(opts.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # Build the shared library
        print(f'Building language library at {opts.output}...')
        Language.build_library(
            opts.output,
            repos,
        )
        print('Build complete.')
        print(f'Library written to: {opts.output}')
    finally:
        # Clean up
        shutil.rmtree(tempdir)


if __name__ == '__main__':  # pragma: no cover
    main()
