"""LLM integration layer."""

from support_agent.llm.classification import (
    CATEGORY_KEYWORDS,
    TicketLike,
    build_ticket_classification_chain,
    classify_ticket,
)
from support_agent.llm.prompts import (
    CLASSIFICATION_SYSTEM_PROMPT,
    CLASSIFICATION_USER_PROMPT,
    DRAFT_RESPONSE_PROMPT,
    DRAFT_RESPONSE_SYSTEM_PROMPT,
    DRAFT_RESPONSE_USER_PROMPT,
    TICKET_CLASSIFICATION_PROMPT,
)

__all__ = [
    "CATEGORY_KEYWORDS",
    "CLASSIFICATION_SYSTEM_PROMPT",
    "CLASSIFICATION_USER_PROMPT",
    "DRAFT_RESPONSE_PROMPT",
    "DRAFT_RESPONSE_SYSTEM_PROMPT",
    "DRAFT_RESPONSE_USER_PROMPT",
    "TICKET_CLASSIFICATION_PROMPT",
    "TicketLike",
    "build_ticket_classification_chain",
    "classify_ticket",
]
