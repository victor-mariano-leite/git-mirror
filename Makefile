install:
	@pip install -r requirements/all.txt
	@pip install pre-commit
	@pre-commit install
	@mypy --install-types
	
prepare:
	@black . -v
	@isort .
	@mypy gitmirror
	@pylint gitmirror
	@flake8 gitmirror
	@echo Good to Go!

check:
	@black . -v --check
	@isort . --check
	@mypy gitmirror
	@flake8 gitmirror
	@pylint gitmirror
	@echo Good to Go!

docs:
	@mkdocs build --clean

docs-serve:
	@mkdocs serve

test:
	@pytest --cov gitmirror

test-cov:
	@pytest --cov gitmirror --cov-report xml:coverage.xml
.PHONY: docs
