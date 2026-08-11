# Alert và Runbook

Các alert dưới đây dựa trên triệu chứng người dùng hoặc SLO. Dashboard và alert dùng cửa sổ trượt; nguồn chuẩn của metrics là `data/logs.jsonl`.

## Alert 1: High Request Error Rate

- Tên: `HighRequestErrorRate`
- Severity: `critical`
- SLI/SLO liên quan: `error_rate_pct <= 2%` trong cửa sổ SLO 28 ngày.
- Điều kiện và thời gian duy trì: `error_rate_pct > 2` liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: nhiều request trả lỗi, người dùng không nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Mở panel Error rate, xác nhận mức tăng và `error_type` chiếm ưu thế.
  2. Lấy một trace trong khoảng lỗi để tìm generation hoặc span thất bại.
  3. Dùng trace ID/correlation ID tra `data/logs.jsonl`, xác nhận dependency hoặc bước xử lý gây lỗi.
- Mitigation tạm thời: tắt incident/feature lỗi, rollback thay đổi gần nhất hoặc chuyển sang đường fallback đã kiểm thử.
- Owner: `metrics-alerting`; phối hợp `incident-analysis` khi alert kéo dài quá 10 phút.

## Alert 2: High User Latency

- Tên: `HighUserLatency`
- Severity: `warning`
- SLI/SLO liên quan: `latency_p95_ms <= 3000 ms` trong cửa sổ SLO 28 ngày.
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000` liên tục trong 10 phút.
- Ảnh hưởng tới người dùng: ít nhất 5% request phản hồi chậm hơn mục tiêu trải nghiệm.
- Ba bước kiểm tra đầu tiên:
  1. So sánh P50/P95/P99 và traffic để phân biệt chậm diện rộng với outlier.
  2. Mở các trace chậm nhất, so sánh thời gian retrieval và generation.
  3. Tra log theo correlation ID, kiểm tra incident, timeout và dependency latency.
- Mitigation tạm thời: tắt đường xử lý chậm, giảm concurrency/tải, giới hạn context hoặc dùng fallback nhanh hơn.
- Owner: `metrics-alerting`; phối hợp owner của span gây chậm.

## Alert 3: Low Response Quality

- Tên: `LowResponseQuality`
- Severity: `warning`
- SLI/SLO liên quan: `quality_score_avg >= 0.75` trong cửa sổ SLO 28 ngày.
- Điều kiện và thời gian duy trì: `quality_score_avg < 0.75` liên tục trong 15 phút.
- Ảnh hưởng tới người dùng: câu trả lời có thể thiếu ngữ cảnh, không đầy đủ hoặc không đúng nhu cầu.
- Ba bước kiểm tra đầu tiên:
  1. Phân tách quality theo feature, model và prompt version.
  2. Mở trace có score thấp, kiểm tra prompt version, số tài liệu retrieval và token usage.
  3. Đối chiếu log theo correlation ID để xác nhận input đã được xử lý và không có fallback bất thường.
- Mitigation tạm thời: rollback label `production` về prompt version ổn định và vô hiệu hóa candidate gây suy giảm.
- Owner: `metrics-alerting`; phối hợp owner prompt/retrieval.

## Quy tắc đóng alert

- Chỉ đóng khi metric trở lại ngưỡng tốt trong ít nhất một khoảng thời gian bằng thời gian duy trì của alert.
- Ghi lại trace ID, correlation ID, root cause, mitigation và người xác nhận.
- Nếu cùng triệu chứng tái diễn, tạo preventive action thay vì chỉ lặp lại mitigation.
