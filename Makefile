.PHONY: install compile-spec lint test dev migrate seed clean \
       frontend-install frontend-dev frontend-build frontend-lint frontend-test \
       docker-build docker-up docker-down docker-logs \
       e2e e2e-install setup

setup: install
	@echo "Setup complete"

install:
	uv sync
	cd spec && npm install
	cd frontend && npm install
	npm install

compile-spec:
	cd spec && npm run compile

lint:
	cd backend && ruff check .
	cd backend && ruff format --check .
	cd backend && mypy .

test:
	cd backend && pytest -v

dev:
	cd backend && uvicorn app.main:app --reload

seed:
	cd backend && uv run python -m app.seed

migrate:
	cd backend && alembic upgrade head

clean:
	rm -rf backend/scheduling.db
	rm -rf spec/node_modules
	rm -rf spec/tsp-output
	rm -rf backend/.mypy_cache
	rm -rf backend/.pytest_cache
	rm -rf backend/__pycache__
	find backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/.next
	rm -rf frontend/node_modules
	rm -rf node_modules
	rm -rf playwright-report
	rm -rf test-results

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

frontend-lint:
	cd frontend && npm run lint

frontend-test:
	cd frontend && npm test

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

e2e-install:
	npm ci
	npx playwright install --with-deps chromium

e2e:
	npx playwright test
