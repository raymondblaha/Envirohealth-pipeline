# ETL Design

Milestone 4 introduces a reproducible raw-to-core pipeline.

## Entry Point

```bash
python -m envirohealth.pipeline
```

The pipeline:

1. Applies schema SQL.
2. Discovers source CSVs under `data/raw/`.
3. Loads each source file into its matching `raw.*` table.
4. Records an ingestion run in `raw.ingestion_runs`.
5. Deletes and reloads rows for the same `source_file` so reruns are idempotent.
6. Validates `rows_read == rows_loaded`.
7. Transforms `raw.*` tables into normalized `core.*` tables.
8. Writes an ETL run summary to `outputs/pipeline/etl_run_summary.csv`.

## Source-Row Lineage

Raw tables include pipeline metadata:

- `ingestion_run_id`
- `source_file`
- `source_row_number`
- `loaded_at`

These fields let a suspicious core record be traced back to a raw database row and then to the original CSV line.

## Configuration

Database credentials are read from environment variables or a local `.env` file:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

`.env` is ignored by Git. `.env.example` contains safe placeholders.

## Transaction Strategy

The Python pipeline owns transaction boundaries. Schema application, each source-file load, and raw-to-core transformation are committed only after their validation checks pass. If a critical step fails, the active transaction is rolled back.

