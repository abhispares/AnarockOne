from langchain_core.runnables import RunnableLambda

from src.agents.llm_response import (
    LLMResponseInput,
    LLMResponseOutput,
    generate_llm_response,
)
from src.agents.relationship_intelligence import (
    RelationshipQueryInput,
    RelationshipQueryOutput,
    answer_relationship_query,
)

LLMResponseRunnableLambda = RunnableLambda(generate_llm_response).with_types(
    input_type=LLMResponseInput,
    output_type=LLMResponseOutput,
)

RelationshipIntelligenceRunnableLambda = RunnableLambda(answer_relationship_query).with_types(
    input_type=RelationshipQueryInput,
    output_type=RelationshipQueryOutput,
)

__all__ = [
    "LLMResponseInput",
    "LLMResponseOutput",
    "LLMResponseRunnableLambda",
    "RelationshipIntelligenceRunnableLambda",
    "RelationshipQueryInput",
    "RelationshipQueryOutput",
    "answer_relationship_query",
    "generate_llm_response",
]
