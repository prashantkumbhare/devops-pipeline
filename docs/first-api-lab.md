# First trading API exercise

Status: code prepared; container build and runtime checks must be performed by the learner.

This is a synthetic order intake service. ACCEPTED means validation passed, not that a trade was executed. No broker or exchange is connected. Orders live only in one process's memory and disappear on restart. Repeated submissions create separate orders; retry-safe submission and PostgreSQL follow in later increments.

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

## Demonstrate memory-only storage

```powershell
docker compose restart api
```

Wait for readiness, then GET /orders. Expect an empty list. Explain why before running this step. This is the reason for the PostgreSQL ticket.

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

Do not close D02 or D03 yet: these exercises need execution evidence, and D03 still requires PostgreSQL and persistence.
