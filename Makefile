UV ?= uv

.PHONY: init

init:
	@$(UV) venv .venv
	@$(UV) pip install .[dev]