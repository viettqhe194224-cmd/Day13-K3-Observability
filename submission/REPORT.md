# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nhóm K3 Observability.
- Repository URL: `https://github.com/viettqhe194224-cmd/Day13-K3-Observability.git`.
- Commit SHA tại thời điểm bắt đầu phần Thành viên D: `1318d2a2af2f0e0fe4a14411ebbeeb89c3ae4f4f` (cập nhật SHA nộp bài sau commit cuối).
- Thành viên và vai trò:
  - Trần Quốc Việt (Thành viên A) — Logging & Middleware.
  - Dương Đức Trung (Thành viên B) — Security & Compliance.
  - Phạm Phúc Minh (Thành viên C) — Metrics & Alerting.
  - Nguyễn Xuân Huy (Thành viên D) — QA & Incident Analyst.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: `100/100` trên 44 log records sau challenge.
- Tổng số traces: 24 traces trên Langfuse tại thời điểm hoàn thiện báo cáo, lớn hơn yêu cầu tối thiểu 10.
- Số PII leak còn lại: 0.
- Dashboard: `http://127.0.0.1:8000/dashboard` khi API đang chạy.
- Dashboard spec: [`../docs/dashboard-spec.md`](../docs/dashboard-spec.md).
- Evidence dashboard: [`evidence/dashboard-6-panels.png`](evidence/dashboard-6-panels.png), [`evidence/dashboard-rag-slow.png`](evidence/dashboard-rag-slow.png) và challenge chính thức [`evidence/challenge-dashboard.png`](evidence/challenge-dashboard.png).

## 3. Logging và tracing

- Evidence correlation ID: [`evidence/redacted-correlation-log.png`](evidence/redacted-correlation-log.png).
- Evidence PII redaction: cùng evidence trên; validator ghi nhận 0 potential PII leaks.
- Evidence trace waterfall: [`evidence/langfuse-traces-waterfall.png`](evidence/langfuse-traces-waterfall.png).
- Trace challenge đáng chú ý: `42c56c458cbfad1564bf7bceb91b2b0f`, session `k3-challenge-s03`, observation `run` kéo dài 3,598 giây. Log cùng session/timestamp có correlation ID `req-16c67803` và `latency_ms=3590`.
- Chi tiết đối chiếu machine-readable: [`evidence/cp3-challenge-investigation.md`](evidence/cp3-challenge-investigation.md).

## 4. Prompt versioning

- Prompt name: `day13-chat`.
- Version/label baseline: version 1, labels `baseline` và `production` sau rollback.
- Version/label candidate: version 2, labels `candidate` và `latest`.
- Trace baseline v1: `4c23f2aba0af7bbf580de31e58cdd6d4`.
- Trace candidate v2: `ded016c30daf75bb9f984c943308be7d`.
- Rollout production v2: `891cd6e0a7d91f1fa7fd28119e0446bc`; rollback production v1: `e53f2fc551dbd650bb323fab4225d286`.
- Evidence: [`evidence/prompt-versioning-rollback.png`](evidence/prompt-versioning-rollback.png) và [`evidence/cp2-langfuse-verification.md`](evidence/cp2-langfuse-verification.md).

## 5. Dashboard, SLO và alerts

- `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence validator: [`evidence/dashboard-validator.png`](evidence/dashboard-validator.png).
- Sáu panel: latency P50/P95/P99, traffic, error rate/breakdown, cost, tokens input/output và quality proxy; time range 60 phút, refresh 30 giây.
- SLO: error rate ≤ 2%, P95 latency ≤ 3.000 ms, daily cost ≤ USD 2,50 và quality trung bình ≥ 0,75 trong cửa sổ 28 ngày. Các ngưỡng phản ánh trực tiếp độ tin cậy, trải nghiệm, ngân sách và chất lượng người dùng.
- Alert rules: `HighRequestErrorRate`, `HighUserLatency`, `LowResponseQuality` trong [`../config/alert_rules.yaml`](../config/alert_rules.yaml); runbook tại [`../docs/alerts.md`](../docs/alerts.md).
- Runtime CP2: P95 tăng từ 1.370 lên 2.651 ms khi bật practice `rag_slow`; xem [`evidence/cp2-runtime-verification.md`](evidence/cp2-runtime-verification.md).

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`; incident chính thức `rag_slow`; feature `refund`.
- Triệu chứng từ metrics: với cùng 5 query và concurrency 5, P95 tăng từ 1.125 lên 3.590 ms (+219,1%), vượt ngưỡng challenge 2.000 ms và SLO 3.000 ms. Error rate vẫn 0%, quality vẫn 0,86.
- Evidence metrics challenge: [`evidence/challenge-dashboard.png`](evidence/challenge-dashboard.png).
- Trace ID: incident `42c56c458cbfad1564bf7bceb91b2b0f` dài 3,598 s; baseline cùng session `19af02c12ea1b244d3704a338732b101` dài 1,076 s.
- Log/correlation ID: `req-16c67803`, session `k3-challenge-s03`; `request_received` tại `04:56:32.851525Z`, `response_sent` tại `04:56:36.450428Z` với `latency_ms=3590`.
- Root cause: `rag_slow` làm retrieval chờ thêm 2,5 giây trong `app/mock_rag.py`, phù hợp với chênh lệch trace 2,522 giây và mức tăng latency ở toàn bộ batch.
- Fix action: tắt incident; trong production đặt retrieval timeout, fallback/cache và chuyển traffic khỏi dependency chậm.
- Preventive measure: child span cho retrieval/generation, alert P95, dependency latency metrics, timeout/circuit breaker và regression load test.
- Evidence đầy đủ: [`evidence/cp3-challenge-investigation.md`](evidence/cp3-challenge-investigation.md).

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Trần Quốc Việt (A) | Correlation ID middleware, response headers và log context | `4425def` cùng các commit CP1 liên quan | Cô lập context giữa request và truy vết log bằng correlation ID. |
| Dương Đức Trung (B) | PII processor, redaction toàn cục và regex PII | Các commit CP1 liên quan | Scrub dữ liệu trước khi render/ghi JSON và kiểm tra độc lập bằng validator. |
| Phạm Phúc Minh (C) | Langfuse prompt/traces, metrics, SLO, alert rules, runbook và dashboard runtime | `aa18f14`, `1318d2a` | Liên kết SLI → SLO → alert và quản lý rollout/rollback prompt bằng labels. |
| Nguyễn Xuân Huy (D) | Chạy load test chính thức, hoàn thiện Dashboard Spec, điều tra CP3 và tổng hợp báo cáo/evidence | Commit phần D cần điền sau khi commit | Điều tra theo Metrics → Traces → Logs và phân biệt latency incident với error/cost/quality regression. |
