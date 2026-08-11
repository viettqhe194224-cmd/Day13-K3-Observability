# Dashboard Spec — Day 13 AI Observability

Dashboard runtime có tại `http://127.0.0.1:8000/dashboard` khi API đang chạy. Nguồn chuẩn là `data/logs.jsonl`; endpoint `/metrics` được dùng để đối chiếu nhanh trạng thái tích lũy trong tiến trình hiện tại. Contract có thể kiểm tra bằng máy nằm tại `config/dashboard.yaml`.

## Phạm vi vận hành

- Time range mặc định: 60 phút gần nhất.
- Auto refresh: 30 giây.
- Bộ lọc điều tra khuyến nghị: `feature`, `session_id`, `model`, `error_type` và khoảng thời gian.
- Mỗi panel phải hiển thị tên, đơn vị, giá trị hiện tại và threshold/SLO line.
- Công cụ triển khai: dashboard HTML nội bộ tại `/dashboard`, được tổng hợp bởi `app/dashboard.py`.

## Thiết kế sáu panel

| ID | Tên panel | Event và field | Phép tổng hợp / hiển thị | Đơn vị | Threshold / SLO |
|---|---|---|---|---|---|
| `latency` | Latency percentiles | `response_sent.latency_ms` | Bar chart P50/P95/P99 | ms | P95 ≤ 3.000 ms |
| `traffic` | Request traffic | `request_received` | Line chart count theo phút và tổng request | requests/min | Kỳ vọng ≥ 1 request/phút khi có tải |
| `errors` | Error rate and breakdown | `request_received`, `request_failed.error_type` | Error rate = failed/received × 100 và breakdown theo loại | % và request | Error rate ≤ 2% |
| `cost` | Cost over time | `response_sent.cost_usd` | Line chart tổng cost theo phút và toàn cửa sổ | USD | Tổng cost ≤ USD 2,50 |
| `tokens` | Input and output tokens | `response_sent.tokens_in`, `tokens_out` | Hai cột tổng input/output | tokens | Tổng ≤ 50.000 tokens |
| `quality` | Quality proxy | `response_sent.quality_score` | Trung bình cộng trong cửa sổ | score 0–1 | Mean ≥ 0,75 |

## Mapping với `/metrics`

| Panel | Trường kiểm tra nhanh |
|---|---|
| Latency | `latency_p50`, `latency_p95`, `latency_p99` |
| Traffic | `traffic`, `total_requests` |
| Errors | `error_rate_pct`, `error_count`, `error_breakdown` |
| Cost | `total_cost_usd`, `avg_cost_usd` |
| Tokens | `tokens_in_total`, `tokens_out_total` |
| Quality | `quality_avg` |

`/metrics` nằm trong bộ nhớ và được reset khi API restart. Dashboard đọc JSONL nên phù hợp hơn cho evidence và phân tích theo time range.

## Quy trình điều tra từ dashboard

1. Xác định panel vượt threshold và khoảng thời gian bắt đầu bất thường.
2. Kiểm tra các panel còn lại để phân biệt latency, lỗi, cost hay quality regression.
3. Lọc trace Langfuse theo khoảng thời gian, feature/session và mở trace chậm hoặc lỗi.
4. Dùng session/timestamp hoặc correlation ID để tìm các dòng tương ứng trong `data/logs.jsonl`.
5. Chỉ kết luận root cause khi metric, trace và log cùng hỗ trợ một giả thuyết.

## Kết quả challenge K3

Với cùng năm query chính thức và concurrency 5, P95 ứng dụng tăng từ 1.125 ms khi incident tắt lên 3.590 ms khi `rag_slow` bật. Error rate vẫn 0% và quality trung bình vẫn 0,86. Dashboard vì vậy xác định đúng đây là latency regression, không phải lỗi, cost spike hay quality regression. Chi tiết tại `submission/evidence/cp3-challenge-investigation.md`.

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```
