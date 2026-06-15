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
    content = """{
        "answer": "Lodha Group is Amber because INR 1.8 crore is pending and a collections escalation is open.",
        "follow_up_questions": [
            "Which Lodha Group collection item needs leadership attention?",
            "Who owns the Lodha Group reconciliation pack?",
            "What should I ask Lodha Group next?"
        ]
    }"""


class FakeChatOpenAIForRelationship:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def invoke(self, prompt: str) -> FakeRelationshipResponse:
        assert "Lodha Group" in prompt
        assert "pending collections" in prompt.lower()
        assert "open escalations" in prompt.lower()
        assert "Booking count is decreasing" in prompt
        assert "repeated Call Center and AI follow-up calls" in prompt
        assert "BD Tracker" in prompt or "Microsoft Teams meeting" in prompt
        return FakeRelationshipResponse()


class FakeGreetingResponse:
    content = """{
        "answer": "Hi Anuj, what account, escalation, collection, or conversation would you like to review?",
        "follow_up_questions": [
            "Show accounts with open escalations",
            "Summarize accounts with pending collections",
            "Show me ongoing conversations with key accounts."
        ]
    }"""


class FakeContactReferenceResponse:
    content = """{
        "answer": "Recent Anarock references for DLF: Kabir Arora met Radhika Singh, and Pooja Menon met Abhishek Bansal.",
        "follow_up_questions": [
            "Show recent Anarock references for this account",
            "List internal teams engaged with this developer",
            "Show developer-side contacts for this account"
        ]
    }"""


class FakeActiveEngagementResponse:
    content = """{
        "answer": "Active Engagements\\nResidential Sales\\nInventory review discussions\\n4 meetings in last 2 weeks\\nCommercial\\nOffice leasing mandate review\\nMost Engaged Stakeholders\\n1. Rahul Verma - Residential Sales\\n2. Neha Gupta - Consulting\\nTotal Active Teams\\n5 Departments",
        "follow_up_questions": [
            "Show recent Anarock references for Godrej Properties",
            "List developer-side contacts for Godrej Properties",
            "Show internal teams engaged with Godrej Properties"
        ]
    }"""


class FakeChatOpenAIForGreeting:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def invoke(self, prompt: str) -> FakeGreetingResponse:
        assert "No matching dummy relationship records were found." in prompt
        assert "Lodha Group" not in prompt
        assert "clickable suggested queries" in prompt
        return FakeGreetingResponse()


class FakeChatOpenAIForContactReference:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def invoke(self, prompt: str) -> FakeContactReferenceResponse:
        assert "Current answer mode: contact_reference" in prompt
        assert "Developer-side contacts" in prompt
        assert "Recent Anarock reference meetings" in prompt
        assert "Kabir Arora" in prompt
        assert "Radhika Singh" in prompt
        return FakeContactReferenceResponse()


class FakeChatOpenAIForActiveEngagement:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def invoke(self, prompt: str) -> FakeActiveEngagementResponse:
        assert "Current answer mode: contact_reference" in prompt
        assert "Active department engagements" in prompt
        assert "Residential Sales | Rahul Verma" in prompt
        assert "4 meetings in last 2 weeks" in prompt
        assert "Total Active Teams" in prompt
        assert "Pending collections" not in prompt
        return FakeActiveEngagementResponse()


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
                "query": "Give health check for Lodha Group",
                "stakeholder_name": "Lodha Group",
            }
        },
    )

    assert response.status_code == 200
    body = response.json()["output"]
    assert body["query"] == "Give health check for Lodha Group"
    assert "Lodha Group" in body["stakeholders"][0]
    assert "INR 1.8 crore" in body["answer"]
    assert body["sources"][0]["stakeholder"] == "Lodha Group"
    assert len(body["follow_up_questions"]) == 3
    assert body["follow_up_questions"][0] == "Which Lodha Group collection item needs leadership attention?"


def test_relationship_intelligence_contact_reference_mode(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-token")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr(llm_response, "ChatOpenAI", FakeChatOpenAIForContactReference)

    response = client.post(
        "/relationship-intelligence/invoke",
        json={
            "input": {
                "query": "Who can reference us at DLF?",
                "stakeholder_name": "DLF",
            }
        },
    )

    assert response.status_code == 200
    body = response.json()["output"]
    assert body["query"] == "Who can reference us at DLF?"
    assert "DLF" in body["stakeholders"][0]
    assert "Kabir Arora" in body["answer"]
    assert len(body["follow_up_questions"]) == 3


def test_relationship_intelligence_active_engagement_mode(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-token")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr(llm_response, "ChatOpenAI", FakeChatOpenAIForActiveEngagement)

    response = client.post(
        "/relationship-intelligence/invoke",
        json={"input": {"query": "Who is currently engaging with Godrej?"}},
    )

    assert response.status_code == 200
    body = response.json()["output"]
    assert body["query"] == "Who is currently engaging with Godrej?"
    assert "Godrej Properties" in body["stakeholders"][0]
    assert "Active Engagements" in body["answer"]
    assert "5 Departments" in body["answer"]


def test_relationship_intelligence_greeting_does_not_default_to_lodha(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-token")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr(llm_response, "ChatOpenAI", FakeChatOpenAIForGreeting)

    response = client.post(
        "/relationship-intelligence/invoke",
        json={"input": {"query": "Hi"}},
    )

    assert response.status_code == 200
    body = response.json()["output"]
    assert body["stakeholders"] == []
    assert body["sources"] == []
    assert "Hi Anuj" in body["answer"]
    assert len(body["follow_up_questions"]) == 3


def test_relationship_intelligence_requires_query() -> None:
    response = client.post("/relationship-intelligence/invoke", json={"input": {}})

    assert response.status_code == 422
