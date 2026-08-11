# CP3 — Official K3 Challenge Investigation

Thời điểm chạy: 2026-08-11 04:56 UTC (11:56 ICT).

## Challenge contract

- Challenge ID: `day13-k3-observability-v1`.
- Incident do Coach phát hành: `rag_slow`.
- Feature bị ảnh hưởng: `refund`.
- Ngưỡng challenge: 2.000 ms.
- Input: 5 query chính thức, concurrency 5.
- `config/challenge.json` không bị chỉnh sửa trong quá trình điều tra.

## Metrics — phát hiện triệu chứng

Hai lượt chạy dùng cùng input và concurrency; chỉ trạng thái incident thay đổi.

Dashboard sau challenge: [`challenge-dashboard.png`](challenge-dashboard.png). Ảnh hiển thị đủ sáu panel, P95 3.590 ms vượt SLO line 3.000 ms, error rate 0% và quality 0,86.

| Metric | Baseline — incident off | Challenge — `rag_slow` on | Nhận định |
|---|---:|---:|---|
| Latency P50 | 1.071 ms | 3.549 ms | Tăng 2.478 ms |
| Latency P95 | 1.125 ms | 3.590 ms | Tăng 2.465 ms, tương đương 219,1% |
| Latency P99 | 1.125 ms | 3.590 ms | Vượt ngưỡng challenge và SLO |
| Error rate | 0% | 0% | Không phải error incident |
| Quality average | 0,86 | 0,86 | Không có quality regression |
| Tổng cost của batch | USD 0,008601 | USD 0,008976 | Chênh lệch nhỏ do token ngẫu nhiên, không phải cost spike |

Cả 5 request challenge có `latency_ms` từ 3.524 đến 3.590 ms, đều vượt ngưỡng challenge 2.000 ms và SLO P95 3.000 ms.

## Trace — khoanh vùng request chậm

So sánh cùng session `k3-challenge-s03`:

| Trạng thái | Trace ID | Observation | Start–end UTC | Duration |
|---|---|---|---|---:|
| Baseline | `19af02c12ea1b244d3704a338732b101` | `run` / `GENERATION` | 04:56:28.656–04:56:29.732 | 1,076 s |
| Incident | `42c56c458cbfad1564bf7bceb91b2b0f` | `run` / `GENERATION` | 04:56:32.851–04:56:36.449 | 3,598 s |

Trace incident dài hơn 2,522 giây. Chênh lệch này khớp với delay 2,5 giây được kích hoạt trong retrieval bởi scenario `rag_slow`. Trace dùng prompt `day13-chat`, feature `refund`, `doc_count=1`; trạng thái không lỗi.

## Logs — liên kết và chứng minh

Trace incident bắt đầu lúc `04:56:32.851 UTC`, trùng timestamp và session của log line 34:

```json
{"event":"request_received","correlation_id":"req-16c67803","session_id":"k3-challenge-s03","feature":"refund","ts":"2026-08-11T04:56:32.851525Z"}
```

Response tương ứng ở line 35:

```json
{"event":"response_sent","correlation_id":"req-16c67803","session_id":"k3-challenge-s03","feature":"refund","latency_ms":3590,"quality_score":0.8,"ts":"2026-08-11T04:56:36.450428Z"}
```

Ngay trước batch, control log ghi nhận `incident_enabled` với payload `name=rag_slow`. Sau điều tra, endpoint `/health` xác nhận cả ba incident đều đã tắt.

## Root cause và hành động

- Root cause: scenario chính thức bật `STATE["rag_slow"]`; bước retrieval trong `app/mock_rag.py` chờ thêm 2,5 giây trước khi tìm corpus. Delay xuất hiện trên mọi query `refund`, kéo P95 từ 1.125 lên 3.590 ms.
- Fix action: vô hiệu hóa `rag_slow`; trong production, đặt timeout cho retrieval, dùng fallback/cached result và chuyển traffic khỏi dependency chậm.
- Preventive measure: tạo child span riêng cho retrieval/generation, cảnh báo P95 > 3.000 ms, theo dõi dependency latency, áp dụng timeout/circuit breaker và chạy regression load test trước release.

## Verification

- `scripts/validate_logs.py`: 100/100 trên 44 records, 22 correlation IDs, 0 PII leak.
- Incident sau phép đo: `rag_slow=false`, `tool_fail=false`, `cost_spike=false`.
- Langfuse project: 24 traces tại thời điểm hoàn thiện báo cáo.
