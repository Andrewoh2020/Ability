.PHONY: run dev migrate revision test fmt lint

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

revision:
	alembic revision -m "$(m)" --autogenerate

test:
	pytest -q tests/

fmt:
	ruff check --fix .
	black .
	isort .

lint:
	mypy app
