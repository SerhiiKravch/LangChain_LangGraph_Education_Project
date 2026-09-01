"""Smoke tests for the bootstrap CLI."""

from support_agent.cli.__main__ import main


def test_cli_bootstrap_message(capsys) -> None:
    """CLI bootstrap prints the expected placeholder message."""
    main()

    captured = capsys.readouterr()

    assert captured.out.strip() == "AI Support Inbox Agent bootstrap is ready."
