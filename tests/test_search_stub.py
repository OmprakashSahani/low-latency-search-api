from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_stub_basic():
    r = client.post("/v1/search", json={"query": "neural retrieval", "k": 3})
    assert r.status_code == 200
    body = r.json()
    assert "hits" in body and len(body["hits"]) == 3
    assert body["hits"][0]["id"].startswith("doc-")
    assert body["latency_ms"] >= 0.0
    assert isinstance(body["trace_id"], str) and len(body["trace_id"]) > 0
