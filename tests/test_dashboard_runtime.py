from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.dashboard import aggregate_dashboard, load_recent_records, render_dashboard_html


def test_dashboard_aggregates_six_runtime_panels(tmp_path: Path) -> None:
    now = datetime(2026, 8, 11, 4, 0, tzinfo=timezone.utc)
    records = [
        {
            "ts": "2026-08-11T03:59:00Z",
            "event": "request_received",
        },
        {
            "ts": "2026-08-11T03:59:01Z",
            "event": "response_sent",
            "latency_ms": 1200,
            "cost_usd": 0.01,
            "tokens_in": 100,
            "tokens_out": 50,
            "quality_score": 0.8,
        },
    ]
    log_path = tmp_path / "logs.jsonl"
    log_path.write_text(
        "\n".join(json.dumps(record) for record in records), encoding="utf-8"
    )

    result = aggregate_dashboard(load_recent_records(log_path, now=now))

    assert result["latency"]["p95"] == 1200
    assert result["traffic"]["total"] == 1
    assert result["errors"]["rate"] == 0
    assert result["cost"]["total"] == 0.01
    assert result["tokens"]["values"] == [100, 50]
    assert result["quality"]["average"] == 0.8


def test_dashboard_html_shows_contract_and_thresholds() -> None:
    html = render_dashboard_html(aggregate_dashboard([]))

    for title in (
        "Latency percentiles",
        "Request traffic",
        "Error rate and breakdown",
        "Cost over time",
        "Input and output tokens",
        "Quality proxy",
    ):
        assert title in html
    assert "Last 60 minutes" in html
    assert "Auto refresh: 30 seconds" in html
