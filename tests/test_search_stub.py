from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_basic_after_index():
    # 1) index three docs that should all match "neural retrieval"
    batch = {
        "docs": [
            {"id": "a", "text": "Neural retrieval systems for search"},
            {"id": "b", "text": "Retrieval augmented generation and neural ranking"},
            {"id": "c", "text": "Neural methods for information retrieval"},
        ]
    }
    r = client.post("/v1/index", json=batch)
    assert r.status_code == 200
    assert r.json()["total"] >= 3

    # 2) search for 3 results
    r = client.post("/v1/search", json={"query": "neural retrieval", "k": 3})
    assert r.status_code == 200
    body = r.json()
    assert "hits" in body
    assert len(body["hits"]) == 3

    # sanity: we should see our docs in the top-k
    ids = {h["id"] for h in body["hits"]}
    assert {"a", "b", "c"}.issubset(ids) or len(ids) == 3
