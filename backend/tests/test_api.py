from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_chat_latency_and_shape():
    payload = {"session_id": "test", "query": "介绍系统架构"}
    r = client.post("/api/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data and isinstance(data["answer"], str)
    assert "latency_ms" in data and data["latency_ms"] < 2000


def test_upload_md():
    files = {"files": ("a.md", "# 标题\n内容".encode("utf-8"), "text/markdown")}
    r = client.post("/api/upload", files=files)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
