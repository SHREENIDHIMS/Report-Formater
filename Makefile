.PHONY: infra-up infra-down api-dev api-test api-lint web-dev
infra-up:
	docker compose up -d postgres redis
infra-down:
	docker compose down
api-dev:
	cd apps/api && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
api-test:
	cd apps/api && uv run pytest
api-lint:
	cd apps/api && uv run ruff check . && uv run mypy app
web-dev:
	pnpm --filter @vtu-report-studio/web dev
