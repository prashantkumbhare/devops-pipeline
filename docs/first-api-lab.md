# First trading API exercise

Status: initial API exercise completed locally. The current code now uses PostgreSQL;
see [the PostgreSQL lab](postgres-lab.md) for current storage behaviour.

This is a synthetic order intake service. ACCEPTED means validation passed, not that a trade was executed. No broker or exchange is connected. The initial version stored orders only in process memory; the current version commits them to PostgreSQL. Repeated submissions create separate orders; retry-safe submission remains future work.

## Run from the repository terminal

```powershell
docker compose up --build -d
docker compose ps
Invoke-RestMethod http://localhost:8000/health/ready
```

Open http://localhost:8000/docs for interactive API documentation.

## Submit and retrieve an order

```powershell
$orderBody = @{symbol='DEMO'; side='BUY'; quantity=10; limit_price='125.50'} | ConvertTo-Json
$order = Invoke-RestMethod -Method Post -Uri http://localhost:8000/orders -ContentType 'application/json' -Body $orderBody
$order
Invoke-RestMethod "http://localhost:8000/orders/$($order.id)"
```

Expect HTTP 201 on creation, with an ID and timestamp. Decimal prices serialize as strings to preserve decimal precision.

## Reject invalid input

In /docs submit an order with quantity 0. Expect HTTP 422 and field details. Look at X-Request-ID in the response headers and find the matching request in:

```powershell
docker compose logs --tail 30 api
```

## Historical memory-only storage experiment

This experiment was completed before PostgreSQL was added. With the current code,
the restart below preserves committed orders rather than clearing them.

```powershell
docker compose restart api
```

In the initial version, GET /orders returned an empty list after restart because
the process dictionary was lost. This motivated adding persistent database storage.

## Stop

```powershell
docker compose down
```

## Read the files

- app/main.py: models validate the body; endpoints implement behaviour; middleware logs requests.
- Dockerfile: packages Python dependencies and code; starts a single non-root application process.
- compose.yaml: builds/runs the service, publishes a localhost port and checks readiness.
- .gitattributes: defines cross-platform line endings.

The process listens on 0.0.0.0 inside its container, while Compose publishes port 8000 only on the laptop's loopback interface. Python is installed inside the image; you do not need a local Python installation.

Dependencies use bounded ranges for this first exercise. A tested lock file and fixed base-image digest are required before claiming reproducible release builds.

Local execution evidence: valid creation returned 201, invalid quantity returned
422 with a matching request ID in logs, PostgreSQL orders survived API restart and
container recreation, and database outage/recovery produced the expected 503/200
responses. Automated CI checks have not yet been added.
