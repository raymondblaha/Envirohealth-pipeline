# Production Hardening

Milestone 8 focuses on making the project reproducible for another developer.

## Fresh Setup

1. Create a local environment file:

```bash
cp .env.example .env
```

2. Fill in local database credentials. The Docker PostgreSQL service reads `DB_PASSWORD` from `.env`.

```text
DB_PASSWORD=<local password>
```

3. Start PostgreSQL:

```bash
make setup
```

4. Run the pipeline and checks:

```bash
make etl
make validate
make analysis
make model
make check
```

## Docker

The repository includes:

- `Dockerfile` for the Python application
- `docker-compose.yml` for PostgreSQL and an optional app container
- PostgreSQL health check
- `.dockerignore` to keep secrets, raw data, outputs, caches, and virtual environments out of Docker build context

Build the application image:

```bash
make docker-build
```

Run the app container profile:

```bash
docker compose --profile app run --rm app
```

The app container expects raw data mounted at `data/raw/`.

## Integration Tests

Database integration tests are opt-in for local development:

```bash
RUN_DB_TESTS=1 make test
```

CI sets `RUN_DB_TESTS=1` and starts a PostgreSQL service automatically. The integration test applies schema SQL and loads one representative EPA county AQI file into the raw layer.

## Repository Hygiene

Raw data, generated outputs, virtual environments, local `.env`, Python caches, Ruff caches, and Docker build noise are excluded from Git.

Known local constraint: this external drive previously blocked `git init`. If that persists, move the project to a normal writable folder before publishing.
