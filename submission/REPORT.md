# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: `100/100` trên 122 log records.
- Tổng số traces: 59 traces trên Langfuse tại thời điểm hoàn thiện CP2.
- Số PII leak còn lại: 0.
- Link/đường dẫn dashboard: `http://127.0.0.1:8000/dashboard` khi API đang chạy; evidence tại `evidence/dashboard-6-panels.png`.

## 3. Logging và tracing

- Evidence correlation ID: `evidence/redacted-correlation-log.png`.
- Evidence PII redaction: `evidence/redacted-correlation-log.png`; validator ghi nhận 0 potential PII leaks.
- Evidence trace waterfall: `evidence/langfuse-traces-waterfall.png` (trace chậm `630e7559556bb9e708b9c21c2c5d9c3a`).
- Giải thích một span đáng chú ý: trace `630e7559556bb9e708b9c21c2c5d9c3` thuộc session `s09` có generation latency 2.652 giây khi bật `rag_slow`; log cùng session/correlation ID `req-d3c95aee` ghi `latency_ms=2651`.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: version 1, labels `baseline` và `production` (trạng thái cuối sau rollback).
- Version/label candidate: version 2, labels `candidate` và `latest`.
- Trace ID của mỗi version: baseline v1 `4c23f2aba0af7bbf580de31e58cdd6d4`; candidate v2 `ded016c30daf75bb9f984c943308be7d`.
- Bằng chứng đổi label hoặc rollback: rollout production v2 `891cd6e0a7d91f1fa7fd28119e0446bc`; rollback production v1 `e53f2fc551dbd650bb323fab4225d286`. Evidence: `evidence/prompt-versioning-rollback.png`; chi tiết xác minh tại `evidence/cp2-langfuse-verification.md`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.` Evidence: `evidence/dashboard-validator.png`.
- Evidence dashboard: baseline `evidence/dashboard-6-panels.png`; sau incident `evidence/dashboard-rag-slow.png`.
- SLO đã chọn và lý do: error rate không quá 2%, P95 latency không quá 3000 ms, daily cost không quá USD 2.50 và quality trung bình ít nhất 0.75 trong cửa sổ 28 ngày. Các ngưỡng bám theo dashboard contract và phản ánh trực tiếp lỗi, độ chậm, chi phí và chất lượng người dùng nhận được.
- Alert rules và runbook: ba alert `HighRequestErrorRate`, `HighUserLatency`, `LowResponseQuality` trong `config/alert_rules.yaml`; quy trình triage và mitigation tại `docs/alerts.md`.

Runtime check: với cùng load test concurrency 5, P95 tăng từ 1370 ms lên 2651 ms khi bật `rag_slow`, sau đó incident được tắt. Chi tiết tại `evidence/cp2-runtime-verification.md`.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Thành viên C | Langfuse prompt versioning/traces, `error_rate_pct`, SLO, alert rules và runbook | Điền commit/PR sau khi commit | Liên kết SLI → SLO → alert; điều tra theo Metrics → Traces → Logs; rollout/rollback prompt bằng labels. |
