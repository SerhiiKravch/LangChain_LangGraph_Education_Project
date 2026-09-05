"""JSONL outbox storage for sent support responses."""

from __future__ import annotations

import json
from pathlib import Path

from support_agent.schemas import SendResponseResult

DEFAULT_OUTBOX_PATH = Path("outputs/outbox/messages.jsonl")


class OutboxStore:
    """File-backed storage for mocked outbound messages."""

    def __init__(self, path: str | Path = DEFAULT_OUTBOX_PATH) -> None:
        self.path = Path(path)

    def append(self, result: SendResponseResult) -> SendResponseResult:
        """Append a sent response result to the JSONL outbox."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"{result.model_dump_json()}\n")

        return result

    def list(self) -> list[SendResponseResult]:
        """Read all sent response results from the JSONL outbox."""
        if not self.path.exists():
            return []

        return [
            SendResponseResult.model_validate(json.loads(line))
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def find_by_ticket_id(self, ticket_id: str) -> SendResponseResult | None:
        """Return the first outbox result recorded for a ticket."""
        normalized_ticket_id = ticket_id.strip()
        if not normalized_ticket_id:
            raise ValueError("ticket_id cannot be blank")

        for result in self.list():
            if result.ticket_id == normalized_ticket_id:
                return result

        return None
