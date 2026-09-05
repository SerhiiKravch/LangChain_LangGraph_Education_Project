"""Application-facing storage for ticket workflow state."""

from __future__ import annotations

from pathlib import Path

from support_agent.schemas import HumanReviewState, HumanReviewStatus, TicketState, WorkflowStatus
from support_agent.storage.checkpoints import CheckpointStore, StateCheckpoint


class TicketStateStore:
    """Persist and restore ticket workflow state using checkpoints."""

    def __init__(self, checkpoint_store: CheckpointStore | None = None) -> None:
        self.checkpoint_store = checkpoint_store or CheckpointStore()

    @classmethod
    def from_path(cls, path: str | Path) -> "TicketStateStore":
        """Create a ticket state store backed by a checkpoint file path."""
        return cls(checkpoint_store=CheckpointStore(path))

    def save(self, state: TicketState) -> StateCheckpoint:
        """Persist the latest workflow state for a ticket."""
        return self.checkpoint_store.save(state)

    def load(self, ticket_id: str) -> TicketState | None:
        """Load the latest workflow state for a ticket."""
        return self.checkpoint_store.load_latest(ticket_id)

    def status_for(self, ticket_id: str) -> WorkflowStatus | None:
        """Return the latest workflow status for a ticket."""
        state = self.load(ticket_id)
        if state is None:
            return None

        return state.status

    def review_for(self, ticket_id: str) -> HumanReviewState | None:
        """Return the latest human review state for a ticket."""
        state = self.load(ticket_id)
        if state is None:
            return None

        return state.review

    def review_status_for(self, ticket_id: str) -> HumanReviewStatus | None:
        """Return the latest human review status for a ticket."""
        review = self.review_for(ticket_id)
        if review is None:
            return None

        return review.status
