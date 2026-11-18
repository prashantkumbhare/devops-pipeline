"""Run on the EC2 host after provisioning. Inserts one synthetic order."""

import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8000"


def request(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=5) as response:
        return response.status, json.load(response)


deadline = time.monotonic() + 480
while True:
    try:
        status, ready = request("/health/ready")
        if status != 200 or ready != {"status": "ready", "storage": "postgresql", "persistent": True}:
            raise RuntimeError(f"Unexpected readiness: {status} {ready}")
        break
    except (URLError, OSError):
        if time.monotonic() >= deadline:
            raise
        time.sleep(5)

status, live = request("/health/live")
if status != 200 or live != {"status": "ok"}:
    raise RuntimeError(f"Unexpected liveness: {status} {live}")

status, created = request("/orders", {
    "symbol": "DEMO", "side": "BUY", "quantity": 1, "limit_price": "10.00"
})
if status != 201 or created.get("status") != "ACCEPTED":
    raise RuntimeError(f"Order not accepted: {status} {created}")

status, fetched = request("/orders/" + created["id"])
if status != 200 or fetched != created:
    raise RuntimeError(f"Order read-back mismatch: {status} {fetched}")

print(json.dumps({"liveness": live, "readiness": ready, "verified_order_id": created["id"]}))
