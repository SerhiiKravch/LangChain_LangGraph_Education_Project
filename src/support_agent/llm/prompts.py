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

DRAFT_RESPONSE_SYSTEM_PROMPT = """You draft customer support replies.

Use only the provided knowledge-base context. Do not invent policy details,
account-specific decisions, refunds, cancellations, or completed actions.

If the context is insufficient, say what is missing and set needs_more_context to true.
Keep the reply clear, concise, and helpful.
"""

DRAFT_RESPONSE_USER_PROMPT = """Ticket:
{message}

Category:
{category}

Retrieved context:
{context}

Draft a grounded support response.
"""

DRAFT_RESPONSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", DRAFT_RESPONSE_SYSTEM_PROMPT),
        ("human", DRAFT_RESPONSE_USER_PROMPT),
    ]
)
