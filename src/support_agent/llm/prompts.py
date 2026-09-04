"""Prompt templates used by LLM-powered components."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

CLASSIFICATION_SYSTEM_PROMPT = """You classify customer support tickets.

Return one of these categories:
- billing
- refund
- account
- technical
- pricing
- other

Prefer sensitive categories such as refund, billing, and account when the user asks for
money movement, subscription changes, account deletion, or identity-sensitive actions.
"""

CLASSIFICATION_USER_PROMPT = """Classify this support ticket:

{message}
"""

TICKET_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", CLASSIFICATION_SYSTEM_PROMPT),
        ("human", CLASSIFICATION_USER_PROMPT),
    ]
)
