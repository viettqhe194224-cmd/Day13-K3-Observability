# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: version 1, labels `baseline` và `production` (trạng thái cuối sau rollback).
- Version/label candidate: version 2, labels `candidate` và `latest`.
- Trace ID của mỗi version: baseline v1 `4c23f2aba0af7bbf580de31e58cdd6d4`; candidate v2 `ded016c30daf75bb9f984c943308be7d`.
- Bằng chứng đổi label hoặc rollback: rollout production v2 `891cd6e0a7d91f1fa7fd28119e0446bc`; rollback production v1 `e53f2fc551dbd650bb323fab4225d286`. Chi tiết xác minh tại `evidence/cp2-langfuse-verification.md`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard:
- SLO đã chọn và lý do: error rate không quá 2%, P95 latency không quá 3000 ms, daily cost không quá USD 2.50 và quality trung bình ít nhất 0.75 trong cửa sổ 28 ngày. Các ngưỡng bám theo dashboard contract và phản ánh trực tiếp lỗi, độ chậm, chi phí và chất lượng người dùng nhận được.
- Alert rules và runbook: ba alert `HighRequestErrorRate`, `HighUserLatency`, `LowResponseQuality` trong `config/alert_rules.yaml`; quy trình triage và mitigation tại `docs/alerts.md`.

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
