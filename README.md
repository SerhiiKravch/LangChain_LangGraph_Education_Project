# AI Support Inbox Agent

Educational pet project for practicing `LangChain` and `LangGraph` on a realistic support inbox workflow.

The idea is to build a compact AI agent that:

- accepts a support ticket;
- classifies the request;
- retrieves relevant context from a knowledge base;
- drafts a grounded response;
- assesses risk;
- either sends the reply automatically or pauses for human review.

This repository is meant to be small enough to finish, but structured enough to discuss real engineering topics like orchestration, retries, persistence, observability, and testing.

## Why This Project

This is not "just another LLM chat app". It is a workflow-oriented system designed to help practice:

- `LangChain` for models, prompts, tools, structured outputs, and RAG
- `LangGraph` for stateful orchestration, branching, interrupts, retries, and resume
- human-in-the-loop safety patterns
- production-minded project structure and developer experience

It is especially useful for interview prep because it gives concrete examples for:

- `LangChain` vs `LangGraph`
- agents vs deterministic workflows
- state modeling
- RAG architecture
- tool calling
- checkpointing and persistence
- testing agent workflows

## Current Status

As of September 1, 2026, the project is in the bootstrap phase.

Already added:

- Python package structure under `src/`
- `uv`-based project setup
- `Makefile` commands for common tasks
- Docker bootstrap files
- `ruff` and `pytest` configuration
- architecture and project-goals documentation

Next steps:

- add markdown knowledge base documents
- implement retrieval and RAG components
- add ticket classification
- build the `LangGraph` workflow
- introduce human review and persistence

## Project Structure

```text
.
├── README.md
├── AGENTS.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── docs/
├── data/
├── notebooks/
├── outputs/
├── src/
│   └── support_agent/
└── tests/
```

Key areas:

- `src/support_agent/` contains the application code
- `docs/` contains architecture and learning notes
- `data/` will hold the knowledge base and fixtures
- `tests/` contains unit, integration, and e2e tests
- `outputs/` is reserved for logs, traces, and mock outbox artifacts

## Quick Start

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd LangChain_LangGraph_Educ_Project
```

### 2. Create environment file

```bash
cp .env.example .env
```

Fill in at least:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_EMBEDDING_MODEL`

Optional tracing-related variables are also available in `.env.example`.

### 3. Install dependencies with `uv`

```bash
uv sync
```

### 4. Run the bootstrap CLI

```bash
make run
```

### 5. Run checks

```bash
make lint
make test
make check
```

## Run With Docker

Build and run:

```bash
docker compose up --build
```

Note:

- `docker-compose.yml` expects a local `.env`
- `data/` and `outputs/` are mounted into the container

## Tooling

- Python `3.11+`
- `uv` for dependency management
- `LangChain`
- `LangGraph`
- `pytest`
- `ruff`
- Docker

## Documentation

More detailed notes live here:

- [Architecture Notes](./docs/architecture.md)
- [Project Goals Notes](./docs/project-goals.md)
- [Classification Taxonomy](./docs/classification-taxonomy.md)
- [Extended Product Notes](./Docs.md)

## Roadmap

The project is being built through small PR-style milestones:

1. `chore/project-bootstrap`
2. `feat/kb-and-rag-foundation`
3. `feat/classification-and-schemas`
4. `feat/draft-response-chain`
5. `feat/risk-assessment-routing`
6. `feat/langgraph-core-workflow`
7. `feat/human-review-interrupts`
8. `feat/tools-and-side-effects`
9. `feat/persistence-and-checkpointing`
10. `feat/cli-and-demo-flow`
11. `feat/observability-and-tracing`
12. `test/hardening-and-interview-polish`

The detailed learning roadmap is documented in [AGENTS.md](./AGENTS.md).

## Development Principles

- keep state explicit and typed
- separate `LangChain` components from `LangGraph` orchestration
- avoid uncontrolled side effects
- prefer grounded answers over confident hallucinations
- build incrementally with tests and clear commits

## License

MIT
