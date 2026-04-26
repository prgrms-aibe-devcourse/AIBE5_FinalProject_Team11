# yoga-api

Java Spring Boot backend for the yoga matching system.

## Goals

- Serve pose metadata and matching results through `/api/v1`.
- Provide Schema.org JSON-LD output for AI-friendly discovery.
- Support JPA persistence for enriched pose data and migration-driven schema.

## Quick start

```bash
cd yoga-api
mvn spring-boot:run
```

If a Maven wrapper is added later, use:

```bash
./mvnw spring-boot:run
```

## Configuration

Update environment variables or `application.yml` for:
- `DB_USER`
- `DB_PASS`
- `SPRING_DATASOURCE_URL` (optional override)

By default, the service connects to:
- `jdbc:postgresql://localhost:5432/yogadb`

## Database migration

The project includes a Flyway migration at:
- `src/main/resources/db/migration/V1__create_pose_tables.sql`

The migration runs automatically on startup if Flyway is enabled.

## Data ingestion

The initial pose metadata source is generated in `aeogeo` by `scripts/enrich_poses.py`.
A SQL import file can be created from the enriched pose JSON using:

```bash
cd ../aeogeo
python3 scripts/generate_pose_insert_sql.py
```

The generated SQL file is written to `data/poses/pose_enriched_ingest.sql`.
Import that file into the Java backend database using an ingestion step or a separate loader component.

If using Docker Compose, the SQL load command looks like this:

```bash
cd /home/aiegoo/repos/aiegoo/aeogeo
docker compose up -d postgres
docker exec -i $(docker compose ps -q postgres) \
  psql -U ${DB_USER:-postgres} -d yogadb < data/poses/pose_enriched_ingest.sql
```

If connecting to a local Postgres instance, use:

```bash
psql -h localhost -p 5432 -U postgres -d yogadb \
  -f data/poses/pose_enriched_ingest.sql
```

## API Endpoints

- `GET /api/v1/poses` — list all poses
- `GET /api/v1/poses/{id}` — retrieve a single pose
- `GET /api/v1/poses/{id}.jsonld` — retrieve Schema.org `HowTo` JSON-LD for the pose
- `POST /api/v1/match` — submit a match request and receive recommendations
- `GET /api/v1/match/status` — health/status check for the matching service

## Browser API docs

- Swagger UI should be available in the browser at `/swagger-ui.html` or `/swagger-ui/index.html`
- The raw OpenAPI JSON is available at `/api/v1/openapi.json`

## OpenAPI

OpenAPI docs are available at:
- `/api/v1/openapi.json`

## Notes

- The `yoga` repository is consumed as a read-only data source.
- The Java API does not edit files in `yoga` directly.

