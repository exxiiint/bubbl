.PHONY: up down logs migrate seed seed-heavy test load-smoke load-planned load-stress load-x10

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -m app.scripts.seed

seed-heavy:
	docker compose exec backend python -m app.scripts.heavy_seed

test:
	docker compose exec backend pytest -q

load-smoke:
	k6 run load-tests/k6/smoke.js

load-planned:
	k6 run load-tests/k6/planned-load.js

load-stress:
	k6 run load-tests/k6/stress.js

load-x10:
	k6 run load-tests/k6/x10-load.js
