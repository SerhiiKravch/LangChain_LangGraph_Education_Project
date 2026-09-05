"""JSONL audit log storage for workflow events."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_AUDIT_LOG_PATH = Path("outputs/logs/audit.jsonl")


class AuditEvent(BaseModel):
    """A single workflow audit event."""

    model_config = ConfigDict(str_strip_whitespace=True)

    event_id: str = Field(
        default_factory=lambda: f"audit-{uuid4().hex}",
        min_length=1,
        description="Unique audit event identifier.",
    )
    event_type: str = Field(min_length=1, description="Workflow event type.")
    ticket_id: str = Field(min_length=1, description="Ticket identifier related to the event.")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event metadata.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the event was recorded.",
    )


class AuditLogStore:
    """File-backed append-only audit log."""

    def __init__(self, path: str | Path = DEFAULT_AUDIT_LOG_PATH) -> None:
        self.path = Path(path)

    def append(self, event: AuditEvent) -> AuditEvent:
        """Append an audit event to the JSONL log."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"{event.model_dump_json()}\n")

        return event

    def record(
        self,
        *,
        event_type: str,
        ticket_id: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Create and append an audit event."""
        event = AuditEvent(
            event_type=event_type,
            ticket_id=ticket_id,
            details=details or {},
        )
        return self.append(event)

    def list(self) -> list[AuditEvent]:
        """Read all audit events from the JSONL log."""
        if not self.path.exists():
            return []

        return [
            AuditEvent.model_validate(json.loads(line))
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
