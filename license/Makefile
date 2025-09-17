.PHONY: help install test lint format discover sync clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e .[dev]

test: ## Run tests
	pytest tests/ -v --cov=tap_sigma_computing

test-integration: ## Run integration tests (requires API credentials)
	pytest tests/test_tap_sigma_computing.py::TestIntegration -v

lint: ## Run linting checks
	flake8 tap_sigma_computing.py
	mypy tap_sigma_computing.py --ignore-missing-imports

format: ## Format code with black
	black tap_sigma_computing.py tests/

format-check: ## Check code formatting
	black --check --diff tap_sigma_computing.py tests/

discover: ## Run discovery mode (requires config.json)
	python tap_sigma_computing.py --config config.json --discover

sync: ## Run sync mode (requires config.json and catalog.json)
	python tap_sigma_computing.py --config config.json --catalog catalog.json

sync-state: ## Run sync mode with state (requires config.json, catalog.json, and state.json)
	python tap_sigma_computing.py --config config.json --catalog catalog.json --state state.json

meltano-run: ## Run with Meltano (for testing in Meltano project)
	meltano invoke tap-sigma-computing --discover
	meltano run tap-sigma-computing target-jsonl

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build: ## Build distribution packages
	python -m build

publish: ## Publish to PyPI (requires API token)
	python -m twine upload dist/*

docker-build: ## Build Docker image for testing
	docker build -t tap-sigma-computing .

docker-run: ## Run tap in Docker container
	docker run --rm -v $(PWD)/config.json:/config.json tap-sigma-computing --config /config.json --discover
