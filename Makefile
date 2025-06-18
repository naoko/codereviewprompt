UV ?= uv

.PHONY: init test

init:
	@$(UV) venv .venv
	@$(UV) pip install .[dev]

test:
	@$(UV) run pytest
