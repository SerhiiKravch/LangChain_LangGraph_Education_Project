"""JSONL checkpoint storage for graph state snapshots."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from support_agent.schemas import TicketState, WorkflowStatus

DEFAULT_CHECKPOINT_PATH = Path("outputs/traces/checkpoints.jsonl")


class StateCheckpoint(BaseModel):
    """A persisted snapshot of graph workflow state."""

    model_config = ConfigDict(str_strip_whitespace=True)

    checkpoint_id: str = Field(
        default_factory=lambda: f"checkpoint-{uuid4().hex}",
        min_length=1,
        description="Unique checkpoint identifier.",
    )
    ticket_id: str = Field(min_length=1, description="Ticket identifier for this checkpoint.")
    status: WorkflowStatus = Field(description="Workflow status at checkpoint time.")
    state: TicketState = Field(description="Full graph state snapshot.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the checkpoint was saved.",
    )


class CheckpointStore:
    """File-backed append-only checkpoint store."""

    def __init__(self, path: str | Path = DEFAULT_CHECKPOINT_PATH) -> None:
        self.path = Path(path)

    def save(self, state: TicketState) -> StateCheckpoint:
        """Persist a graph state snapshot as a new checkpoint."""
        checkpoint = StateCheckpoint(
            ticket_id=state.ticket.ticket_id,
            status=state.status,
            state=state,
        )
        return self.append(checkpoint)

    def append(self, checkpoint: StateCheckpoint) -> StateCheckpoint:
        """Append a checkpoint to the JSONL store."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"{checkpoint.model_dump_json()}\n")

        return checkpoint

    def list(self, ticket_id: str | None = None) -> list[StateCheckpoint]:
        """Read checkpoints, optionally filtered by ticket id."""
        normalized_ticket_id = ticket_id.strip() if ticket_id is not None else None
        if normalized_ticket_id == "":
            raise ValueError("ticket_id cannot be blank")

        if not self.path.exists():
            return []

        checkpoints = [
            StateCheckpoint.model_validate(json.loads(line))
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if ticket_id is None:
            return checkpoints

        return [
            checkpoint
            for checkpoint in checkpoints
            if checkpoint.ticket_id == normalized_ticket_id
        ]

    def latest(self, ticket_id: str) -> StateCheckpoint | None:
        """Return the latest checkpoint for a ticket."""
        checkpoints = self.list(ticket_id=ticket_id)
        if not checkpoints:
            return None

        return checkpoints[-1]

    def load_latest(self, ticket_id: str) -> TicketState | None:
        """Return the latest graph state snapshot for a ticket."""
        checkpoint = self.latest(ticket_id)
        if checkpoint is None:
            return None

        return checkpoint.state
