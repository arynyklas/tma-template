set shell := ["bash", "-cu"]
set windows-shell := ["cmd.exe", "/c"]

set dotenv-load := true

# Local Docker shortcuts
up:
    docker compose up -d

down:
    docker compose down

restart:
    docker compose restart

# Production Docker
prod-up:
    docker compose -f docker-compose.prod.yml up -d

prod-down:
    docker compose -f docker-compose.prod.yml down

prod-restart:
    docker compose -f docker-compose.prod.yml restart

prod-logs:
    docker compose -f docker-compose.prod.yml logs -f

# Clean up
clean:
    docker compose down -v
    docker compose rm -f

# View logs
logs:
    docker compose logs -f

# Status
status:
    docker compose ps

# Presentations
api:
    uv run granian src.presentation.api.app:create_app --factory --port 8080 --interface asgi --reload

bot:
    uv run python -m src.presentation.bot.main

# Utils
test:
    docker compose -f docker-compose-test.yml up -d
    uv run pytest -n auto -ss -vv --maxfail=1
    docker compose -f docker-compose-test.yml down -v

test-db-up:
    docker compose -f docker-compose-test.yml up -d

test-db-down:
    docker compose -f docker-compose-test.yml down -v

# Other dev aliases
lint:
    uv run ruff format src tests
    uv run ruff check src tests --fix

ty:
    uv run ty check src/

generate-i18n:
    uv run python scripts/generate_i18n_stubs.py
    uv run ruff format src/infrastructure/i18n/types.py
