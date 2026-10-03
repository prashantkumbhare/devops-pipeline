# PostgreSQL persistence lab

This replaces the earlier in-memory storage. Old memory-only orders cannot be recovered.

## Quick reference (Git Bash)

1. `cp .env.example .env` and edit `.env` in VS Code to choose a unique local password.
2. `docker compose up -d --build`
3. `docker compose ps` - wait for both services to be healthy.
4. `curl -i http://localhost:8000/health/ready` - PostgreSQL, persistent true.
5. Create an order using the previous POST example and record its returned ID.
6. `docker compose restart api`; wait for healthy, then GET `/orders/{recorded-id}`.
7. `docker compose down` followed by `docker compose up -d`; GET the same ID again.

Both checks must return the same order. `down` preserves named volumes by default.
Do not add `-v`: that removes the database volume and its data.

Inspect records directly:

```bash
docker compose exec db psql -U trading -d trading -c "SELECT id, symbol, quantity FROM orders;"
```

## Detailed explanation

The API connects to `db:5432` on the Compose network. `localhost` in the API
container would refer to that API container itself, not PostgreSQL. The database
publishes `127.0.0.1:5432:5432` for clients on this Windows laptop. A host client
uses host `127.0.0.1`, port `5432`, database and user `trading`, and the password
from `.env`. A Windows installation of `psql` is needed for direct host CLI access;
`docker compose exec db psql -U trading -d trading` uses the bundled client instead.
The loopback binding does not expose the database to the second laptop.
Apply a port configuration change with `docker compose up -d db`, not `restart`.
Container recreation retains the named volume and its database records.

PostgreSQL writes database files into a named volume mounted at its data directory.
That volume exists independently of the container. It is local storage, not a backup
or replicated database, and does not automatically travel to the second laptop.

The API uses parameterized SQL and commits each successful insert before responding
201. Blocking database operations run in synchronous FastAPI endpoints, in its worker
thread pool. This first version opens a connection per request; pooling comes later.
Startup creates the initial schema; future schema changes require migrations.

Liveness checks the API process; readiness queries the database's orders table.
If the database is unavailable after startup, readiness and order operations return
503, while liveness remains 200. Compose waits for database health on startup; it
does not automatically restart a running API just because its dependency becomes unhealthy.

`.env` is ignored by Git and excluded from the image. Do not paste it or expanded
Compose configuration into chat. Changing the password in `.env` does not change
the password of an already initialized database. This lab uses one database owner
account; separate least-privilege runtime and migration accounts are future work.

## Interview Q&A

- Dockerfile vs Compose? The first packages the image, the second configures services.
- Why CMD in Dockerfile? The image has a usable default even without Compose.
- Why did memory orders disappear? Restart erased process memory.
- Why do these orders survive recreation? PostgreSQL writes to a retained named volume.
- Is a volume a backup? No; backup and restore need their own procedure.
- Why readiness plus liveness? A process can be alive while its database is unavailable.

## Learning journal

Verified before this change: valid POST returned 201, invalid quantity zero returned
422, response request ID matched the JSON log, and restart cleared memory orders.
PostgreSQL build and runtime checks are pending the learner's commands.

Related: [first API exercise](first-api-lab.md), [local setup](local-setup.md).
Sources: [PostgreSQL image](https://hub.docker.com/_/postgres),
[Psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/usage.html).
