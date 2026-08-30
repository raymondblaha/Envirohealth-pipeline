# SQL Layer

SQL files are organized under `sql/schema/`.

Planned order:

1. `001_create_schemas.sql`
2. `002_create_raw_tables.sql`
3. `003_create_core_tables.sql`
4. `004_add_indexes.sql`

Additional constraint and analytics-view files should be added after the ETL loads data into PostgreSQL and validates source-specific null semantics.

Raw-to-core transformations live under `sql/transformations/`.
