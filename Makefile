.PHONY: fmt lint typecheck test qa run

fmt:
	black .

lint:
	ruff check .
	ruff format --check .

typecheck:
	mypy app

test:
	PYTHONPATH=. pytest

qa: fmt lint typecheck test

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
