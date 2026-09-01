PYTHON := python3
UV := uv

.PHONY: install sync lock run lint format test check clean

install:
	$(UV) sync

sync:
	$(UV) sync

lock:
	$(UV) lock

run:
	$(UV) run $(PYTHON) -m support_agent.cli

lint:
	$(UV) run ruff check src tests

format:
	$(UV) run ruff format src tests

test:
	$(UV) run pytest

check:
	$(PYTHON) -m compileall src

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
