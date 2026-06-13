import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator

load_dotenv()


class LLMResponseInput(BaseModel):
    input: str = Field(..., min_length=1, description="User input for the LLM")

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("input must not be empty")
        return value


class LLMResponseOutput(BaseModel):
    input: str
    output: str


def _get_openai_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    kwargs: dict[str, Any] = {
        "openai_api_key": api_key,
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0")),
    }

    organization = (
        os.getenv("OPENAI_ORGANISATION_ID", "").strip()
        or os.getenv("OPENAI_ORGANIZATION_ID", "").strip()
    )
    if organization:
        kwargs["openai_organization"] = organization

    return ChatOpenAI(**kwargs)


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                text_parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                text_parts.append(str(item))
        return "".join(text_parts).strip()

    return str(content)


def generate_llm_response(body: LLMResponseInput | dict[str, Any]) -> LLMResponseOutput:
    request = body if isinstance(body, LLMResponseInput) else LLMResponseInput(**body)
    user_input = request.input.strip()
    response = _get_openai_llm().invoke(user_input)
    output = _content_to_text(getattr(response, "content", response)).strip()

    return LLMResponseOutput(
        input=user_input,
        output=output,
    )
