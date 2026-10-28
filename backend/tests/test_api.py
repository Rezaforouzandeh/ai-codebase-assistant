from fastapi.testclient import TestClient
from app import main


client = TestClient(main.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint(monkeypatch):

    async def fake_generate_response(prompt: str):
        return f"Mock response: {prompt}"

    monkeypatch.setattr(
        main,
        "generate_response",
        fake_generate_response
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "What is RAG?"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "answer": "Mock response: What is RAG?"
    }


def test_empty_message_rejected():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": ""
        }
    )

    assert response.status_code == 422


def test_missing_message_rejected():
    response = client.post(
        "/api/v1/chat",
        json={}
    )

    assert response.status_code == 422