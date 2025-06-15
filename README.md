# code-review-prompt

> A zero‑hook CLI that turns your local `git diff` (plus optional Story/Jira text) into a Gemini‑ready code‑review prompt.

---
## What problem does this solve?

Manually assembling code review prompts—collecting diffs, extracting relevant context, and including ticket details—is time-consuming and error-prone. codereviewprompt automates this in one simple command.

## Who is this for?

- Developers performing code reviews or using AI assistants to critique code.
- Teams seeking consistency, speed, and reduced context-switching during reviews.

## Benefits of using codereviewprompt

- One-line CLI to generate a structured prompt with diff and contextual snippets.
- Context-aware extraction around changed symbols.
- Optional ticket ID inclusion (with story fetch integration planned).
- Token-budget smart: trims context to fit model limits.
- Fully local execution for code privacy.

---

## Installation

### End-user install (recommended)

If you don’t have `uv` installed, install it with the official installer:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install or update codereviewprompt from GitHub via `uv` (no virtualenv required):
```bash
uv pip install git+https://github.com/naoko/codereviewprompt.git          # first-time install
uv pip install --upgrade git+https://github.com/naoko/codereviewprompt.git  # update to latest version
```

(*Optional*: you can also install from PyPI with `pip install codereviewprompt`, but
we recommend using `uv` to avoid installing globally.)

### Developer setup

For working on the codebase (requires Git, Make, and `uv`):
```bash
git clone https://github.com/naoko/codereviewprompt.git
cd codereviewprompt
make requirements     # update requirements.txt
make init             # create .venv and install dependencies
```

---

## ✨ Key Features

* **One‑liner usage** – `codereviewprompt run` pulls, diffs, builds the prompt and copies it straight to your clipboard.
* **Context aware** – grabs full source for touched functions/classes using Tree‑sitter so Gemini sees enough code to reason about changes.
* **Ticket integration (optional)** – pass `--ticket JIRA‑1234` to embed the Story description automatically.
* **Token‑budget smart** – drops low‑priority context chunks if the prompt would exceed model limits.
* **Purely local** – no API keys; nothing leaves your machine until **you** paste the prompt into Gemini.

---

## 📦 Requirements

* Python **3.11+**
* Git installed and on `PATH`
* (Optional) access to Jira/Linear REST API & auth token

Python dependencies are pinned in `pyproject.toml` / `requirements.txt` and installed automatically.

---

## 🚀 Quick Start

Follow the [Installation](#installation) instructions above to set up the tool.
Then generate a code-review prompt:

```bash
codereviewprompt run --base main --ticket JIRA-1234 --out clipboard
```
Paste into Gemini 2.5 Pro and hit Enter to get feedback ✨

By default, codereviewprompt:

1. Fetches `origin/<base>` (default `main`).
2. Generates a **compact diff** (`--unified=0`).
3. Scans changed files with Tree‑sitter and extracts ±50 lines around each touched symbol.
4. Composes a markdown prompt containing:

   * Review rubric & severity guide
   * (Optional) Story/Ticket description
   * Diff + contextual snippets
5. Writes the prompt to your **clipboard** (or `stdout` / file).

---

## 🛠️ CLI Flags

| Flag              | Default     | Description                                 |
| ----------------- | ----------- | ------------------------------------------- |
| `--base`          | `main`      | Commit/branch/tag to diff against           |
| `--ticket`        | *none*      | Ticket ID to fetch via REST                 |
| `--context-lines` | `50`        | Lines of context around each touched symbol |
| `--out`           | `clipboard` | `clipboard`, `stdout`, or a file path       |
| `--model`         | `gemini`    | Reserved for future custom prompts          |

```bash
# Example: compare against a tag and print to stdout
codereviewprompt run --base v1.4.0 --out stdout
```

---

## 🧩 Configuration

Create `~/.config/codereviewprompt/config.yaml` (optional):

```yaml
jira:
  url: "https://mycompany.atlassian.net"
  token_env: JIRA_API_TOKEN  # read from env var at runtime
prompt:
  context_lines: 80          # default override
```

Any CLI flag overrides the config file at run‑time.

---

## 🧪 Development & Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## ⚙️ Makefile

Use the provided Makefile for common tasks:

* make requirements — compile `requirements.in` to `requirements.txt` (requires pip-tools).
* make init         — create a `.venv` via `uv` and install both production and dev dependencies.

Example:
```bash
make requirements
make init
```

Linting & formatting: `ruff check .` & `ruff format .`

---

## ➕ Roadmap

* Symbol-level context extraction (Python AST; Tree-sitter for other languages)
* Rich prompt templates: include full diffs, severity guide, and file grouping
* Inline diff annotations (map Gemini feedback back to line numbers)
* VS Code & JetBrains plugin wrappers
* Quality gates: exit non‑zero on detected **critical** issues (for CI use)
* Support for self‑hosted LLM endpoints (Code Llama, Qwen‑Code)

---

## 🤝 Contributing

1. Fork & clone
2. Create a feature branch
3. Run `pre-commit install`
4. Submit a PR – please include tests where reasonable!

## 🤖 Acknowledgements

This project’s code was generated with assistance from OpenAI’s ChatGPT via the Codex CLI tool.

---

## 📝 License

MIT © 2025 Naoko Reeves & contributors
