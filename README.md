# code-review-prompt

> A zero‑hook CLI that turns your local `git diff` (plus optional Story/Jira text) into a Gemini‑ready code‑review prompt.

---

## Installation

### Clone & bootstrap (recommended)

```bash
git clone https://github.com/naoko/codereviewprompt.git
cd codereviewprompt
make requirements
make init
```
You can then list or build grammars:
```bash
# Inspect existing shared library
codereviewprompt list-langs

# Build grammars for languages
codereviewprompt build-langs python javascript go
```

### Install via `uv` (alternate)

```bash
uv pip install git+https://github.com/naoko/codereviewprompt.git
```

### Manual install (fallback)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
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

## 🌳 Building Tree‑sitter Languages

codereviewprompt needs a compiled shared library containing the grammars you care about:

```bash
# One‑time build (C compiler required)
python -m codereviewprompt.build_langs c python javascript typescript go
```

This produces `~/.cache/codereviewprompt/langs.so` which the CLI will reuse.

### Pre-built grammars

codereviewprompt now includes the `tree-sitter-languages` package as a dependency, so prebuilt grammars are installed automatically. After installation, the shared library will be placed in:
```
~/.cache/codereviewprompt/langs.so
```
You can inspect available grammars with:
```bash
codereviewprompt list-langs
```

### Listing installed languages

Once you have a compiled `langs.so`, you can list the embedded grammars by inspecting its exported symbols. For example:
```bash
# List all Tree-sitter language symbols in the shared library
nm ~/.cache/codereviewprompt/langs.so 2>/dev/null \
  | grep ts_language_ \
  | sed 's/.*ts_language_//'
```
This will print names like `python`, `javascript`, `go`, etc., corresponding to the languages you built into the library.

Alternatively, use the built-in CLI command:
```bash
codereviewprompt list-langs
```
This will inspect the shared library (by default at `~/.cache/codereviewprompt/langs.so`) and list embedded languages.
You can override the library path with the `CODEREVIEWPROMPT_LANGS_SO` environment variable, e.g.:
```bash
export CODEREVIEWPROMPT_LANGS_SO=/path/to/your/langs.so
codereviewprompt list-langs
```

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

---

## 📝 License

MIT © 2025 Naoko Reeves & contributors
