.PHONY: setup etl validate analytics analysis model test lint check docker-build clean

PYTHON ?= .venv/bin/python
PYTEST ?= .venv/bin/pytest
RUFF ?= .venv/bin/ruff

setup:
	docker compose up -d postgres

etl:
	$(PYTHON) -m envirohealth.pipeline

validate:
	$(PYTHON) -m envirohealth.validation

analytics:
	$(PYTHON) -m envirohealth.analytics --rebuild-views

analysis:
	$(PYTHON) -m envirohealth.analysis

model:
	$(PYTHON) -m envirohealth.modeling

test:
	$(PYTEST)

lint:
	$(RUFF) check .

check:
	$(RUFF) check .
	$(PYTEST)

docker-build:
	docker compose build app

clean:
	docker compose down
