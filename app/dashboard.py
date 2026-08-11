from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from .metrics import percentile


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_recent_records(
    path: Path,
    *,
    now: datetime | None = None,
    minutes: int = 60,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    cutoff = current - timedelta(minutes=minutes)
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        timestamp = _parse_timestamp(record.get("ts"))
        if timestamp is not None and cutoff <= timestamp <= current:
            record["_timestamp"] = timestamp
            records.append(record)
    return records


def aggregate_dashboard(records: list[dict[str, Any]]) -> dict[str, Any]:
    received = [record for record in records if record.get("event") == "request_received"]
    failed = [record for record in records if record.get("event") == "request_failed"]
    responses = [record for record in records if record.get("event") == "response_sent"]

    latencies = [
        int(record["latency_ms"])
        for record in responses
        if isinstance(record.get("latency_ms"), (int, float))
    ]
    costs = [
        float(record["cost_usd"])
        for record in responses
        if isinstance(record.get("cost_usd"), (int, float))
    ]
    quality = [
        float(record["quality_score"])
        for record in responses
        if isinstance(record.get("quality_score"), (int, float))
    ]

    traffic_by_minute: dict[str, int] = defaultdict(int)
    cost_by_minute: dict[str, float] = defaultdict(float)
    for record in received:
        timestamp = record.get("_timestamp")
        if isinstance(timestamp, datetime):
            traffic_by_minute[timestamp.strftime("%H:%M")] += 1
    for record in responses:
        timestamp = record.get("_timestamp")
        cost = record.get("cost_usd")
        if isinstance(timestamp, datetime) and isinstance(cost, (int, float)):
            cost_by_minute[timestamp.strftime("%H:%M")] += float(cost)

    error_breakdown = Counter(
        str(record.get("error_type") or "UnknownError") for record in failed
    )
    error_rate_pct = round((len(failed) / len(received)) * 100, 2) if received else 0.0

    return {
        "latency": {
            "labels": ["P50", "P95", "P99"],
            "values": [
                percentile(latencies, 50),
                percentile(latencies, 95),
                percentile(latencies, 99),
            ],
            "p95": percentile(latencies, 95),
            "threshold": 3000,
            "unit": "ms",
        },
        "traffic": {
            "labels": list(traffic_by_minute),
            "values": list(traffic_by_minute.values()),
            "total": len(received),
            "threshold": 1,
            "unit": "requests/min",
        },
        "errors": {
            "labels": list(error_breakdown) or ["No errors"],
            "values": list(error_breakdown.values()) or [0],
            "rate": error_rate_pct,
            "failed": len(failed),
            "threshold": 2,
            "unit": "%",
        },
        "cost": {
            "labels": list(cost_by_minute),
            "values": [round(value, 6) for value in cost_by_minute.values()],
            "total": round(sum(costs), 6),
            "threshold": 2.5,
            "unit": "USD",
        },
        "tokens": {
            "labels": ["Input", "Output"],
            "values": [
                sum(int(record.get("tokens_in") or 0) for record in responses),
                sum(int(record.get("tokens_out") or 0) for record in responses),
            ],
            "threshold": 50000,
            "unit": "tokens",
        },
        "quality": {
            "labels": ["Average quality"],
            "values": [round(mean(quality), 4) if quality else 0.0],
            "average": round(mean(quality), 4) if quality else 0.0,
            "threshold": 0.75,
            "unit": "score (0–1)",
        },
        "record_count": len(records),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def render_dashboard_html(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="30">
  <title>Day 13 AI Observability</title>
  <style>
    :root {{ color-scheme: light; --ink:#102a43; --muted:#627d98; --line:#d9e2ec; --surface:#fff; --page:#f0f4f8; --blue:#2563eb; --green:#059669; --red:#dc2626; --amber:#d97706; --purple:#7c3aed; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--page); color:var(--ink); font:14px/1.45 Inter,Segoe UI,Arial,sans-serif; }}
    main {{ max-width:1440px; margin:auto; padding:24px; }}
    header {{ display:flex; align-items:flex-end; justify-content:space-between; gap:20px; margin-bottom:18px; }}
    h1 {{ margin:0; font-size:26px; }}
    .subtitle {{ color:var(--muted); margin-top:4px; }}
    .status {{ display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; }}
    .badge {{ background:var(--surface); border:1px solid var(--line); border-radius:999px; padding:7px 11px; color:var(--muted); }}
    .grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; }}
    .panel {{ min-width:0; background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:16px; box-shadow:0 1px 2px rgb(16 42 67 / 5%); }}
    .panel-head {{ display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }}
    h2 {{ margin:0; font-size:16px; }}
    .metric {{ margin-top:7px; font-size:28px; font-weight:700; letter-spacing:-.02em; }}
    .unit {{ color:var(--muted); font-size:13px; font-weight:400; }}
    .threshold {{ color:var(--muted); font-size:12px; text-align:right; }}
    canvas {{ width:100%; height:190px; display:block; margin-top:12px; }}
    .legend {{ display:flex; flex-wrap:wrap; gap:12px; color:var(--muted); font-size:12px; margin-top:8px; }}
    .dot {{ width:9px; height:9px; border-radius:50%; display:inline-block; margin-right:5px; }}
    footer {{ color:var(--muted); margin-top:16px; font-size:12px; }}
    @media (max-width:1050px) {{ .grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
    @media (max-width:700px) {{ main {{ padding:14px; }} header {{ align-items:flex-start; flex-direction:column; }} .status {{ justify-content:flex-start; }} .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <header>
    <div><h1>Day 13 AI Observability</h1><div class="subtitle">Source: data/logs.jsonl · Runtime dashboard contract v1</div></div>
    <div class="status"><span class="badge">Time range: Last 60 minutes</span><span class="badge">Auto refresh: 30 seconds</span><span class="badge">Records: {data['record_count']}</span></div>
  </header>
  <section class="grid">
    <article class="panel"><div class="panel-head"><div><h2>Latency percentiles</h2><div class="metric">{data['latency']['p95']:.0f} <span class="unit">ms P95</span></div></div><div class="threshold">SLO ≤ 3000 ms</div></div><canvas id="latency"></canvas><div class="legend"><span><i class="dot" style="background:var(--blue)"></i>P50 / P95 / P99</span><span><i class="dot" style="background:var(--red)"></i>Threshold</span></div></article>
    <article class="panel"><div class="panel-head"><div><h2>Request traffic</h2><div class="metric">{data['traffic']['total']} <span class="unit">requests</span></div></div><div class="threshold">Expected ≥ 1 request/min</div></div><canvas id="traffic"></canvas><div class="legend"><span><i class="dot" style="background:var(--green)"></i>Requests per minute</span></div></article>
    <article class="panel"><div class="panel-head"><div><h2>Error rate and breakdown</h2><div class="metric">{data['errors']['rate']:.2f}<span class="unit">%</span></div></div><div class="threshold">SLO ≤ 2%</div></div><canvas id="errors"></canvas><div class="legend"><span><i class="dot" style="background:var(--red)"></i>Failures by error type</span></div></article>
    <article class="panel"><div class="panel-head"><div><h2>Cost over time</h2><div class="metric">${data['cost']['total']:.4f} <span class="unit">total</span></div></div><div class="threshold">Budget ≤ $2.50</div></div><canvas id="cost"></canvas><div class="legend"><span><i class="dot" style="background:var(--amber)"></i>USD per minute</span></div></article>
    <article class="panel"><div class="panel-head"><div><h2>Input and output tokens</h2><div class="metric">{sum(data['tokens']['values']):,} <span class="unit">tokens</span></div></div><div class="threshold">Threshold ≤ 50,000</div></div><canvas id="tokens"></canvas><div class="legend"><span><i class="dot" style="background:var(--purple)"></i>Tokens by direction</span></div></article>
    <article class="panel"><div class="panel-head"><div><h2>Quality proxy</h2><div class="metric">{data['quality']['average']:.2f} <span class="unit">score</span></div></div><div class="threshold">SLO ≥ 0.75</div></div><canvas id="quality"></canvas><div class="legend"><span><i class="dot" style="background:var(--green)"></i>Average score</span><span><i class="dot" style="background:var(--red)"></i>Threshold</span></div></article>
  </section>
  <footer>Generated {data['generated_at']} · Thresholds from config/dashboard.yaml and config/slo.yaml</footer>
</main>
<script>
const DATA={payload};
const colors={{blue:'#2563eb',green:'#059669',red:'#dc2626',amber:'#d97706',purple:'#7c3aed',grid:'#d9e2ec',text:'#627d98'}};
function context(id){{const c=document.getElementById(id),d=window.devicePixelRatio||1,w=c.clientWidth,h=c.clientHeight;c.width=w*d;c.height=h*d;const x=c.getContext('2d');x.scale(d,d);x.font='12px Segoe UI';return{{x,w,h}}}}
function frame(x,w,h,max){{const p={{l:48,r:14,t:14,b:34}};x.strokeStyle=colors.grid;x.lineWidth=1;x.beginPath();x.moveTo(p.l,p.t);x.lineTo(p.l,h-p.b);x.lineTo(w-p.r,h-p.b);x.stroke();x.fillStyle=colors.text;x.textAlign='right';x.fillText(max.toLocaleString(undefined,{{maximumFractionDigits:2}}),p.l-7,p.t+4);x.fillText('0',p.l-7,h-p.b+4);return p}}
function bars(id,labels,values,color,threshold=null,forcedMax=null){{const{{x,w,h}}=context(id);const max=Math.max(forcedMax||0,threshold||0,...values,1)*1.12,p=frame(x,w,h,max),cw=w-p.l-p.r,bw=Math.max(12,Math.min(58,cw/Math.max(labels.length,1)*.58));values.forEach((v,i)=>{{const cx=p.l+cw*(i+.5)/values.length,y=h-p.b-(v/max)*(h-p.t-p.b);x.fillStyle=color;x.fillRect(cx-bw/2,y,bw,h-p.b-y);x.fillStyle=colors.text;x.textAlign='center';x.fillText(Number(v).toLocaleString(undefined,{{maximumFractionDigits:2}}),cx,Math.max(p.t+11,y-6));x.fillText(labels[i].slice(0,14),cx,h-12)}});if(threshold!==null){{const y=h-p.b-(threshold/max)*(h-p.t-p.b);x.strokeStyle=colors.red;x.setLineDash([5,4]);x.beginPath();x.moveTo(p.l,y);x.lineTo(w-p.r,y);x.stroke();x.setLineDash([])}}}}
function line(id,labels,values,color,threshold=null){{const{{x,w,h}}=context(id);const vals=values.length?values:[0],labs=labels.length?labels:['No data'],max=Math.max(threshold||0,...vals,1)*1.12,p=frame(x,w,h,max),cw=w-p.l-p.r,ch=h-p.t-p.b;x.strokeStyle=color;x.lineWidth=2;x.beginPath();vals.forEach((v,i)=>{{const px=p.l+(vals.length===1?cw/2:cw*i/(vals.length-1)),py=h-p.b-v/max*ch;i?x.lineTo(px,py):x.moveTo(px,py)}});x.stroke();x.fillStyle=color;vals.forEach((v,i)=>{{const px=p.l+(vals.length===1?cw/2:cw*i/(vals.length-1)),py=h-p.b-v/max*ch;x.beginPath();x.arc(px,py,3,0,Math.PI*2);x.fill()}});x.fillStyle=colors.text;x.textAlign='center';x.fillText(labs[0],p.l,h-12);if(labs.length>1)x.fillText(labs[labs.length-1],w-p.r,h-12);if(threshold!==null){{const y=h-p.b-threshold/max*ch;x.strokeStyle=colors.red;x.setLineDash([5,4]);x.beginPath();x.moveTo(p.l,y);x.lineTo(w-p.r,y);x.stroke();x.setLineDash([])}}}}
function draw(){{bars('latency',DATA.latency.labels,DATA.latency.values,colors.blue,DATA.latency.threshold);line('traffic',DATA.traffic.labels,DATA.traffic.values,colors.green,DATA.traffic.threshold);bars('errors',DATA.errors.labels,DATA.errors.values,colors.red);line('cost',DATA.cost.labels,DATA.cost.values,colors.amber,DATA.cost.threshold);bars('tokens',DATA.tokens.labels,DATA.tokens.values,colors.purple,DATA.tokens.threshold);bars('quality',DATA.quality.labels,DATA.quality.values,colors.green,DATA.quality.threshold,1)}}
draw();window.addEventListener('resize',()=>{{clearTimeout(window.__dashResize);window.__dashResize=setTimeout(draw,120)}});
</script>
</body>
</html>"""
