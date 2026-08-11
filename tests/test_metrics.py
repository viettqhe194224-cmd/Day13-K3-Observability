from app import metrics
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_reports_error_rate_as_percentage(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 8)
    monkeypatch.setattr(metrics, "ERRORS", metrics.Counter({"TimeoutError": 2}))

    result = metrics.snapshot()

    assert result["total_requests"] == 10
    assert result["error_count"] == 2
    assert result["error_rate_pct"] == 20.0


def test_snapshot_error_rate_is_zero_without_requests(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 0)
    monkeypatch.setattr(metrics, "ERRORS", metrics.Counter())

    assert metrics.snapshot()["error_rate_pct"] == 0.0
