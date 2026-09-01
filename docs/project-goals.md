# Project Goals Notes

## Main Goal

Build a compact but realistic AI support inbox agent that can be used to practice `LangChain`, `LangGraph`, and production-style agent design.

## Learning Goals

By the end of the project, the repository should help explain and demonstrate:

- when to use `LangChain` versus `LangGraph`;
- how to model workflow `State`, `Node`, and `Edge`;
- how to build a basic RAG pipeline;
- how to use structured outputs instead of free-form parsing;
- how to add tools for controlled side effects;
- how to implement human-in-the-loop review with pause and resume;
- how to reason about retries, checkpointing, and persistence;
- how to reduce hallucinations with grounded generation;
- how to test an agent workflow in layers.

## Product Goals

The project should be good enough to:

- run locally through a simple CLI flow;
- demonstrate low-risk and high-risk support scenarios;
- show grounded answers based on knowledge base retrieval;
- pause correctly for sensitive actions;
- resume cleanly after human approval;
- record visible outputs for debugging and demo purposes.

## Scope for the MVP

The first complete version should stay intentionally small.

Target MVP scope:

- one input channel such as CLI;
- a small markdown knowledge base;
- a simple embeddings plus vector-store pipeline;
- several fixed support categories;
- a draft-response step;
- a risk-assessment step;
- a human-review branch;
- a mock send-response tool;
- basic persistence and tests.

## Non-Goals for Early Iterations

The early versions do not need:

- a full web UI;
- multi-user auth;
- real email delivery;
- complex agent autonomy;
- a large-scale document ingestion pipeline;
- advanced infrastructure.

## What Success Looks Like

Success means the project is:

- easy to run locally;
- easy to explain in an interview;
- structured cleanly enough for incremental commits and PRs;
- realistic enough to discuss safety and production tradeoffs;
- small enough to finish without turning into a framework project.
