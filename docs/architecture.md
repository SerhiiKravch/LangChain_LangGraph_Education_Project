# Architecture Notes

## Purpose

The project is a small production-style learning system for building an AI support inbox agent with `LangChain` and `LangGraph`.

The system should:

- accept an incoming support ticket;
- classify the request;
- retrieve relevant knowledge base context;
- draft a grounded reply;
- assess response risk;
- either send automatically or pause for human review.

## Architectural Layers

### 1. Application Layer

This layer owns the user-facing entry points and orchestration triggers.

Expected responsibilities:

- CLI commands for running and resuming workflows;
- loading environment configuration;
- wiring services together;
- exposing demo-friendly execution flows.

Main directories:

- `src/support_agent/cli/`
- `src/support_agent/config.py`
- `src/support_agent/services/`

### 2. LangChain Layer

This layer owns model-facing building blocks.

Expected responsibilities:

- chat model setup;
- prompt templates;
- structured output schemas;
- embeddings and retrieval primitives;
- reusable tool definitions.

Main directories:

- `src/support_agent/llm/`
- `src/support_agent/retrieval/`
- `src/support_agent/tools/`
- `src/support_agent/schemas/`

### 3. LangGraph Layer

This layer owns workflow orchestration.

Expected responsibilities:

- ticket state modeling;
- node definitions;
- routing and branching;
- interrupt and resume behavior;
- retries and checkpoint integration.

Main directories:

- `src/support_agent/graph/`
- `src/support_agent/graph/nodes/`

### 4. Persistence Layer

This layer owns durable and semi-durable state.

Expected responsibilities:

- workflow state persistence;
- outbox storage for sent responses;
- local indexes or checkpoint data;
- review queue state and audit artifacts.

Main directories:

- `src/support_agent/storage/`
- `outputs/`
- `data/`

## High-Level Workflow

The intended happy-path flow is:

1. `ingest_ticket`
2. `classify_ticket`
3. `retrieve_context`
4. `draft_response`
5. `assess_risk`
6. `send_response` or `human_review`
7. `close_ticket`

## Design Principles

- Prefer typed state over loosely structured dictionaries.
- Keep retrieval and orchestration separated.
- Make risky actions explicit and reviewable.
- Treat side effects as controlled tool calls.
- Build the project in small, testable increments.

## Why This Architecture Works Well for Learning

- It separates `LangChain` concerns from `LangGraph` concerns.
- It gives a realistic place for human-in-the-loop behavior.
- It supports interview-friendly explanations about safety, retries, and persistence.
- It keeps the project small enough to finish while still looking like a real system.
