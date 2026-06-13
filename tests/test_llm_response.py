from fastapi.testclient import TestClient
import src.agents.llm_response as llm_response

from src.main import app


client = TestClient(app)


def test_index() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


class FakeOpenAIResponse:
    content = "Hello from the real LLM test double."


class FakeChatOpenAI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def invoke(self, prompt: str) -> FakeOpenAIResponse:
        assert prompt == "Write a short greeting"
        return FakeOpenAIResponse()


class FakeRelationshipResponse:
    content = "Ananya Rao has the warmest recent context with Abhishek from the May 28 Teams review."


class FakeChatOpenAIForRelationship:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def invoke(self, prompt: str) -> FakeRelationshipResponse:
        assert "Abhishek" in prompt
        assert "BD Tracker" in prompt or "Microsoft Teams meeting" in prompt
        return FakeRelationshipResponse()


def test_llm_response_invoke(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-token")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr(llm_response, "ChatOpenAI", FakeChatOpenAI)

    response = client.post(
        "/llm-response/invoke",
        json={"input": {"input": "Write a short greeting"}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["output"]["input"] == "Write a short greeting"
    assert body["output"]["output"] == "Hello from the real LLM test double."


def test_llm_response_requires_input() -> None:
    response = client.post("/llm-response/invoke", json={"input": {}})

    assert response.status_code == 422


def test_relationship_intelligence_invoke(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-token")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr(llm_response, "ChatOpenAI", FakeChatOpenAIForRelationship)

    response = client.post(
        "/relationship-intelligence/invoke",
        json={
            "input": {
                "query": "Who has recently interacted with Abhishek?",
                "stakeholder_name": "Abhishek",
            }
        },
    )

    assert response.status_code == 200
    body = response.json()["output"]
    assert body["query"] == "Who has recently interacted with Abhishek?"
    assert "Abhishek" in body["stakeholders"][0]
    assert "Ananya Rao" in body["answer"]
    assert body["sources"][0]["stakeholder"] == "Abhishek"


def test_relationship_intelligence_requires_query() -> None:
    response = client.post("/relationship-intelligence/invoke", json={"input": {}})

    assert response.status_code == 422
