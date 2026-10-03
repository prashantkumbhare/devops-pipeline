"""HTTP integration checks; standard library only, executed in a test container."""
import json
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = os.environ["BASE_URL"]


def request(path, expected, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    try:
        response = urlopen(req, timeout=8)
    except HTTPError as error:
        response = error
    with response:
        actual = response.status
        payload = json.load(response)
        assert actual == expected, (path, actual, expected, payload)
        assert response.headers.get("X-Request-ID"), "Missing request correlation ID"
        return payload


def wait_ready():
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            result = request("/health/ready", 200)
            assert result["storage"] == "postgresql" and result["persistent"] is True
            return
        except (URLError, AssertionError, TimeoutError):
            time.sleep(1)
    raise AssertionError("API did not become ready within 60 seconds")


mode = sys.argv[1]
if mode == "outage":
    assert request("/health/live", 200)["status"] == "ok"
    for path in ("/health/ready", "/orders"):
        assert request(path, 503)["detail"] == "Database unavailable"
else:
    wait_ready()
    if mode == "create":
        body = {"symbol": "DEMO", "side": "BUY", "quantity": 10, "limit_price": "125.50"}
        order = request("/orders", 201, body)
        assert order["status"] == "ACCEPTED" and order["limit_price"] == "125.50"
        assert request("/orders/" + order["id"], 200) == order
        assert order in request("/orders", 200)
        body["quantity"] = 0
        invalid = request("/orders", 422, body)
        assert any(item["loc"] == ["body", "quantity"] for item in invalid["detail"])
        assert len(request("/orders", 200)) == 1, "Invalid request inserted an order"
        request("/orders/00000000-0000-0000-0000-000000000000", 404)
    elif mode == "persist":
        orders = request("/orders", 200)
        assert len(orders) == 1, "Original order did not survive"
        order = orders[0]
        assert order["symbol"] == "DEMO" and order["quantity"] == 10
        assert order["limit_price"] == "125.50"
        assert request("/orders/" + order["id"], 200) == order
    else:
        raise ValueError("Unknown test mode: " + mode)
print("PASS: " + mode)
