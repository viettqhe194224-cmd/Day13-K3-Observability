# CP2 runtime verification

## Dashboard contract

- Source: `data/logs.jsonl`.
- Time range: 60 minutes.
- Refresh: 30 seconds.
- Panels: latency, traffic, errors, cost, tokens and quality.
- Validator result: `HỢP LỆ: 6/6 panel có trong dashboard contract.`

## Baseline

- Command: `python scripts/load_test.py --concurrency 5`.
- Dashboard P95: 1370 ms.
- Evidence: `dashboard-6-panels.png`.

## Practice incident: rag_slow

- Enabled with `python scripts/inject_incident.py --scenario rag_slow`.
- Repeated the same load test at concurrency 5.
- Dashboard P95 increased to 2651 ms (about 93.5% above baseline).
- Evidence: `dashboard-rag-slow.png`.
- Slow trace ID: `630e7559556bb9e708b9c21c2c5d9c3`.
- Session ID: `s09`.
- Correlation ID: `req-d3c95aee`.
- Matching response log: `latency_ms=2651`, `event=response_sent`.
- Disabled with `python scripts/inject_incident.py --scenario rag_slow --disable`.

This establishes the required investigation path: Metrics → Trace → Log.
