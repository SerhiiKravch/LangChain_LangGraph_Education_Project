# AI Support Inbox Agent Roadmap

## 1. Approximate Project File Structure

```text
LangChain_LangGraph_Educ_Project/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── docs/
│   ├── architecture.md
│   ├── workflow.md
│   └── interview-notes.md
├── data/
│   ├── kb/
│   │   ├── pricing.md
│   │   ├── refunds.md
│   │   ├── subscriptions.md
│   │   ├── account_deletion.md
│   │   └── rate_limits.md
│   └── fixtures/
│       ├── low_risk_ticket.json
│       ├── high_risk_ticket.json
│       └── low_confidence_ticket.json
├── notebooks/
│   ├── 01_kb_ingestion.ipynb
│   └── 02_rag_experiments.ipynb
├── src/
│   └── support_agent/
│       ├── __init__.py
│       ├── config.py
│       ├── schemas/
│       │   ├── state.py
│       │   ├── ticket.py
│       │   ├── classification.py
│       │   ├── retrieval.py
│       │   ├── draft.py
│       │   └── review.py
│       ├── llm/
│       │   ├── models.py
│       │   ├── prompts.py
│       │   └── structured_outputs.py
│       ├── retrieval/
│       │   ├── loader.py
│       │   ├── chunking.py
│       │   ├── embeddings.py
│       │   ├── vectorstore.py
│       │   └── retriever.py
│       ├── tools/
│       │   ├── send_response.py
│       │   ├── review_queue.py
│       │   └── audit_log.py
│       ├── graph/
│       │   ├── nodes/
│       │   │   ├── ingest_ticket.py
│       │   │   ├── classify_ticket.py
│       │   │   ├── retrieve_context.py
│       │   │   ├── draft_response.py
│       │   │   ├── assess_risk.py
│       │   │   ├── human_review.py
│       │   │   ├── send_response.py
│       │   │   └── close_ticket.py
│       │   ├── routing.py
│       │   ├── graph_builder.py
│       │   └── checkpoints.py
│       ├── services/
│       │   ├── ticket_service.py
│       │   ├── review_service.py
│       │   └── tracing.py
│       ├── storage/
│       │   ├── state_store.py
│       │   ├── outbox.py
│       │   └── kb_index.py
│       └── cli/
│           ├── main.py
│           ├── run_ticket.py
│           └── resume_review.py
├── tests/
│   ├── unit/
│   │   ├── test_classification.py
│   │   ├── test_retrieval.py
│   │   ├── test_risk_assessment.py
│   │   └── test_tools.py
│   ├── integration/
│   │   ├── test_low_risk_flow.py
│   │   ├── test_high_risk_review_flow.py
│   │   └── test_retry_and_resume.py
│   └── e2e/
│       └── test_cli_flow.py
└── outputs/
    ├── logs/
    ├── traces/
    └── outbox/
```

This structure is useful for learning because:

- `schemas/` keeps state and structured outputs explicit.
- `retrieval/` isolates the RAG layer.
- `graph/` isolates the `LangGraph` workflow and routing logic.
- `tools/` and `storage/` make side effects and idempotency easier to reason about.
- `tests/` supports production-style development and interview storytelling.

## 2. Roadmap of Commits and PR Branches

Build the project through a sequence of small PRs where each PR maps to a focused learning stage.

### PR 1: `chore/project-bootstrap`

Learning focus: project bootstrap, environment setup, DX, and quality baseline.

1. `chore: initialize project structure and pyproject with uv`
   Learning stage: organizing a Python codebase and setting up modern dependency management for an agent workflow project.
2. `chore: add env example makefile and gitignore`
   Learning stage: reproducible environment configuration and convenient local commands.
3. `chore: add docker and dockerignore setup`
   Learning stage: isolated and portable project execution.
4. `chore: add ruff and pytest configuration`
   Learning stage: establishing code quality checks and a basic automated test foundation from day one.
5. `docs: add architecture and project goals notes`
   Learning stage: explaining the system clearly at a high level and documenting local run paths.

### PR 2: `feat/kb-and-rag-foundation`

Learning focus: the RAG foundation in `LangChain`.

1. `feat: add markdown knowledge base documents`
   Learning stage: designing a compact support-focused knowledge base.
2. `feat: implement document loading and chunking`
   Learning stage: ingestion and preprocessing.
3. `feat: add embeddings and vector store setup`
   Learning stage: indexing and semantic retrieval basics.
4. `feat: implement retriever with basic search`
   Learning stage: retrieval as a reusable application layer.
5. `test: add retrieval unit tests and fixtures`
   Learning stage: testing RAG components.

### PR 3: `feat/classification-and-schemas`

Learning focus: structured outputs in `LangChain`.

1. `feat: add ticket and classification schemas`
   Learning stage: modeling typed state and outputs.
2. `feat: implement ticket classification chain`
   Learning stage: prompts plus structured model output.
3. `test: add classification tests with sample tickets`
   Learning stage: validating category behavior.
4. `docs: document category taxonomy and confidence handling`
   Learning stage: communicating design choices.

### PR 4: `feat/draft-response-chain`

Learning focus: grounded answer generation.

1. `feat: add response drafting prompt and output schema`
   Learning stage: response design for grounded generation.
2. `feat: implement draft generation from retrieved context`
   Learning stage: connecting retrieval to answer generation.
3. `feat: store citations and source snippets in state`
   Learning stage: explainability and hallucination control.
4. `test: add draft generation tests for grounded answers`
   Learning stage: testing groundedness.

### PR 5: `feat/risk-assessment-routing`

Learning focus: routing and decision policy.

1. `feat: add risk assessment schema and decision labels`
   Learning stage: explicit decision modeling.
2. `feat: implement low-risk high-risk insufficient-context logic`
   Learning stage: safe automation policy.
3. `test: add routing tests for risk scenarios`
   Learning stage: deterministic branching verification.

### PR 6: `feat/langgraph-core-workflow`

Learning focus: the core `LangGraph` workflow.

1. `feat: define ticket state model for graph execution`
   Learning stage: understanding `State` in `LangGraph`.
2. `feat: implement graph nodes for ingest classify retrieve and draft`
   Learning stage: decomposing the workflow into nodes.
3. `feat: add graph routing from risk assessment to next steps`
   Learning stage: conditional edges and workflow transitions.
4. `test: add integration test for low-risk happy path`
   Learning stage: validating the happy path end to end.

### PR 7: `feat/human-review-interrupts`

Learning focus: human-in-the-loop with pause and resume.

1. `feat: add review state and review action schemas`
   Learning stage: modeling human decisions in workflow state.
2. `feat: implement human review interrupt node`
   Learning stage: using `interrupt` in `LangGraph`.
3. `feat: add workflow resume handling after approval or edit`
   Learning stage: resume behavior after human input.
4. `test: add integration test for high-risk review flow`
   Learning stage: testing human review scenarios.

### PR 8: `feat/tools-and-side-effects`

Learning focus: tools, side effects, and idempotency.

1. `feat: implement mock send response tool`
   Learning stage: controlled tool execution.
2. `feat: add outbox and audit logging storage`
   Learning stage: observable side effects.
3. `feat: make send operation idempotent by ticket id`
   Learning stage: making external actions safe to retry.
4. `test: add tool tests for repeated sends and failures`
   Learning stage: testing side-effect behavior.

### PR 9: `feat/persistence-and-checkpointing`

Learning focus: recoverability and robustness.

1. `feat: add checkpoint store for graph state`
   Learning stage: checkpointing workflow execution.
2. `feat: persist ticket state and review status`
   Learning stage: resuming work across runs.
3. `feat: add retry policy for send failures`
   Learning stage: fault tolerance and retries.
4. `test: add retry and resume integration tests`
   Learning stage: verifying recovery paths.

### PR 10: `feat/cli-and-demo-flow`

Learning focus: demoability and user-facing workflow execution.

1. `feat: add cli command to run new support ticket`
   Learning stage: triggering the workflow manually.
2. `feat: add cli command to resume review decisions`
   Learning stage: demonstrating human review continuation.
3. `docs: add demo script and example walkthrough`
   Learning stage: presenting the project clearly in interviews.

### PR 11: `feat/observability-and-tracing`

Learning focus: production-style observability.

1. `feat: add structured logging across graph nodes`
   Learning stage: debugging and inspecting agent workflows.
2. `feat: add trace ids and execution metadata`
   Learning stage: end-to-end traceability.
3. `docs: add observability notes and debugging guide`
   Learning stage: explaining operational practices.

### PR 12: `test/hardening-and-interview-polish`

Learning focus: final hardening and interview readiness.

1. `test: add end-to-end cli scenario coverage`
   Learning stage: system-level validation.
2. `refactor: clean graph builder and simplify node contracts`
   Learning stage: refactoring after MVP stabilization.
3. `docs: add interview notes tradeoffs and future improvements`
   Learning stage: speaking confidently about tradeoffs and next steps.

## Recommended Learning Order

1. Project bootstrap
2. RAG foundation
3. Structured outputs
4. Grounded response generation
5. Risk routing
6. `LangGraph` orchestration
7. Human-in-the-loop
8. Tools and side effects
9. Persistence and retries
10. CLI demo
11. Observability
12. Hardening and interview polish

## Learning Outcome by Stage

- After PRs 2 to 4, the project gives a solid practical base in `LangChain`.
- After PRs 6 to 9, the project becomes a strong example of `LangGraph` workflow design.
- After PRs 10 to 12, the repository is ready for demos, portfolio use, and interview discussion.

## Follow-Up Refactoring and Infrastructure Roadmap

Use this follow-up roadmap after the main MVP flow exists. These PRs focus on making the project easier to run, easier to explain, and closer to a production-style agent workflow.

### PR 13: `feat/compiled-langgraph-runner`

Learning focus: moving from manually chained node calls to a real compiled `LangGraph` workflow.

1. `feat: add graph builder with state graph nodes`
   Learning stage: assembling individual node functions into a `StateGraph`.
2. `feat: add conditional edges for risk and review routing`
   Learning stage: modeling branching behavior with conditional graph edges.
3. `feat: add send response node using retry policy`
   Learning stage: connecting graph execution to controlled side effects.
4. `test: add compiled graph integration tests`
   Learning stage: validating the real graph runner end to end.

### PR 14: `chore/test-fixtures-and-error-handling`

Learning focus: reducing test duplication and standardizing workflow failure behavior.

1. `test: move shared model fixtures into conftest`
   Learning stage: organizing reusable test data and reducing duplicated setup.
2. `test: add reusable support ticket and draft factories`
   Learning stage: building maintainable test helpers for workflow scenarios.
3. `feat: add centralized workflow error handling helper`
   Learning stage: consistently mapping exceptions to `WorkflowStatus.FAILED`.
4. `test: add error handling tests for graph nodes`
   Learning stage: validating failure paths as first-class workflow behavior.

### PR 15: `feat/audit-events-and-runtime-config`

Learning focus: making workflow execution observable and configurable.

1. `feat: add application config model`
   Learning stage: centralizing paths, retrieval settings, retry attempts, and model provider configuration.
2. `feat: record audit events for workflow transitions`
   Learning stage: tracing important state changes such as classification, review, send, and failure.
3. `feat: add audit logging to send and review flows`
   Learning stage: observing side effects and human decisions.
4. `test: add audit and config integration tests`
   Learning stage: testing configuration-driven execution and audit artifacts.

### PR 16: `feat/cli-demo-runner`

Learning focus: turning the internal workflow into a demo-friendly user-facing flow.

1. `feat: add cli command to run a support ticket through the graph`
   Learning stage: exposing workflow execution through a simple interface.
2. `feat: add cli command to inspect ticket status and review state`
   Learning stage: making persisted state visible during demos.
3. `feat: add cli command to resume a reviewed ticket`
   Learning stage: demonstrating pause and resume from the command line.
4. `test: add e2e cli tests for low-risk and high-risk flows`
   Learning stage: validating the system from the user entry point.

### PR 17: `chore/github-and-docs-polish`

Learning focus: repository readiness for GitHub, CI, and interview presentation.

1. `docs: update readme current status and run examples`
   Learning stage: keeping project documentation aligned with the implemented system.
2. `ci: add github actions for uv ruff and pytest`
   Learning stage: running automated quality checks on every PR.
3. `docs: add architecture diagrams for models and state flow`
   Learning stage: explaining the project visually and clearly.
4. `chore: clean generated pycache artifacts from workspace`
   Learning stage: keeping the repository and local project tree clean.

### Recommended Follow-Up Order

1. Compiled `LangGraph` runner
2. Send response graph node
3. Shared fixtures and error handling
4. Runtime config and audit events
5. CLI demo runner
6. README, diagrams, CI, and repository polish
