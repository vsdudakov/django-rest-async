.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1
	find . -type f -name "*.pyc" -exec rm -rf {} + > /dev/null 2>&1

.PHONY: lint
lint:
	flake8 --show-source src
	interrogate --config setup.cfg src

.PHONY: test
test:
	flake8 --show-source src
	isort --check-only src --diff
	python manage.py makemigrations --dry-run --check
	pytest --cov=src --cov-report=term --cov-report=html

.PHONY: all
all: clean lint

.PHONY: fix
fix:
	black src
	isort src

.PHONY: install
install:
	pipenv install --dev --ignore-pipfile
	pre-commit install
