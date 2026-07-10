.PHONY: install test lint fmt clean run

install:
	pip install -r requirements.txt
	pip install pytest pytest-cov

test:
	python -m pytest tests/ -v --tb=short

test-cov:
	python -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing --cov-report=html

lint:
	ruff check src/ tests/ app.py
	mypy src/ --strict --ignore-missing-imports

fmt:
	ruff format src/ tests/ app.py
	ruff check --fix src/ tests/ app.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf .mypy_cache .pytest_cache .ruff_cache htmlcov

run:
	streamlit run app.py --server.port 8501