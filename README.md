# code-review-prompt

> A zero‑hook CLI that turns your local `git diff` into a Gemini‑ready code‑review prompt.

---
## What problem does this solve?

Manually assembling code review prompts—collecting diffs, extracting relevant context—is time-consuming and error-prone. codereviewprompt automates this in one simple command.

## Who is this for?

- Developers performing code reviews or using AI assistants to critique code.
- Teams seeking consistency, speed, and reduced context-switching during reviews.

## Benefits of using codereviewprompt

- One-line CLI to generate a structured prompt with diff and contextual snippets.
- Context-aware extraction around changed symbols.
- Token-budget smart: trims context to fit model limits.
- Fully local execution for code privacy.

---

### Install 
Setup `uv`
```bash
brew install uv
uv tool update-shell
```

Install
```bash
uv tool install git+https://github.com/naoko/codereviewprompt.git    
```

To update in future use `uv tool upgrade codereviewprompt`


### Usage
Navigate to your code repository and run the tool:

```bash
cd ~/projects/my-code-project
codereviewprompt run
```

By default, the generated prompt (including diff and context snippets) is copied to your clipboard.

Primary workflows:

1. Review your local uncommitted or staged changes:

   ```bash
   codereviewprompt run
   ```

2. Review a feature or remote branch against main:

   ```bash
   git fetch origin <feature-branch>
   git checkout <feature-branch>
   codereviewprompt run --base main
   ```

## Development / Local Usage

If you have not installed the package, you can run the CLI directly from the source directory by adding `src` to your `PYTHONPATH`:

```bash
cd path/to/codereview-prompt
PYTHONPATH=src python -m codereviewprompt.cli run [OPTIONS]
```

Alternatively, install the package in editable mode to register the console script:

```bash
pip install --upgrade --editable .
codereviewprompt run [OPTIONS]
```

