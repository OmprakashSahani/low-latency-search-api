from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_latency_headers_present():
    # ensure at least one doc indexed so lexical path runs
    client.post(
        "/v1/index",
        json={"docs": [{"id": "xx", "text": "bm25 latency header smoke test"}]},
    )
    r = client.post("/v1/search", json={"query": "latency", "k": 1})
    assert r.status_code == 200
    # headers
    assert "X-Latency-Total-ms" in r.headers
    # X-Compute may be empty when no stages run, but here lexical should exist
    assert "X-Compute" in r.headers
    assert "Trace-Id" in r.headers
