VENV := venv
PYTHON := $(VENV)/bin/python3.12

.PHONY: all install run clean test

all: install run

install:
	python3.12 -m venv $(VENV)
	@echo "Venv created. No external dependencies required."

run:
	$(PYTHON) -m src.main

generate-5:
	$(PYTHON) -m src.main -n 5

generate-10:
	$(PYTHON) -m src.main -n 10

generate-100:
	$(PYTHON) -m src.main -n 100 --format json

test:
	$(PYTHON) -m src.test_solver

clean:
	rm -rf $(VENV) __pycache__ src/__pycache__
