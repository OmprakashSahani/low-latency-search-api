from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_index_and_search_bm25():
    # index two simple docs
    batch = {
        "docs": [
            {
                "id": "d1",
                "text": "Neural retrieval with hybrid ranking approach",
                "meta": {"src": "t"},
            },
            {"id": "d2", "text": "Fast lexical BM25 baseline for search API", "meta": {"src": "t"}},
        ]
    }
    r = client.post("/v1/index", json=batch)
    assert r.status_code == 200
    assert r.json()["total"] >= 2

    # search for "lexical bm25"
    r = client.post("/v1/search", json={"query": "lexical bm25", "k": 2})
    assert r.status_code == 200
    body = r.json()
    assert len(body["hits"]) >= 1
    top_ids = [h["id"] for h in body["hits"]]
    assert "d2" in top_ids  # BM25 should match lexical/bm25 doc
