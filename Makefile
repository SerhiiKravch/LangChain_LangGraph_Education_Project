PYTHON := python3
UV := uv

.PHONY: install sync lock run check clean

install:
	$(UV) sync

sync:
	$(UV) sync

lock:
	$(UV) lock

run:
	$(UV) run $(PYTHON) -m support_agent.cli

check:
	$(PYTHON) -m compileall src

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
