UV ?= uv

.PHONY: requirements init

requirements:
	@$(UV) venv .venv
	@$(UV) pip install pip-tools
	@$(UV) run pip-compile requirements.in

init: requirements
	@$(UV) pip install -r requirements.txt
	@$(UV) pip install -r requirements-dev.txt