"""Persistence and storage adapters."""

from support_agent.storage.audit_log import DEFAULT_AUDIT_LOG_PATH, AuditEvent, AuditLogStore
from support_agent.storage.checkpoints import (
    DEFAULT_CHECKPOINT_PATH,
    CheckpointStore,
    StateCheckpoint,
)
from support_agent.storage.outbox import DEFAULT_OUTBOX_PATH, OutboxStore
from support_agent.storage.state_store import TicketStateStore

__all__ = [
    "AuditEvent",
    "AuditLogStore",
    "CheckpointStore",
    "DEFAULT_AUDIT_LOG_PATH",
    "DEFAULT_CHECKPOINT_PATH",
    "DEFAULT_OUTBOX_PATH",
    "OutboxStore",
    "StateCheckpoint",
    "TicketStateStore",
]
