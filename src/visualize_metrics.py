import csv
import html
from pathlib import Path

from common.config import BASE_DIR, METRICS_PATH


REPORT_PATH = Path(BASE_DIR) / "data" / "metrics_report.html"
CHARTS = [
    ("total_power_consumed", "Total Power Consumption", "W"),
    ("avg_turnaround_time", "Average Turnaround Time", "Ticks"),
    ("completion_rate", "Completion Rate", "%"),
]
COLORS = ["#2563eb", "#059669", "#dc2626", "#7c3aed", "#ea580c", "#0891b2"]


def load_metrics():
    path = Path(METRICS_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Metrics CSV not found: {path}")

    with path.open("r", newline="", encoding="utf-8") as file:
        rows = [
            row for row in csv.DictReader(file)
            if row.get("scenario") and row.get("scenario") != "scenario"
        ]

    if not rows:
        raise ValueError(f"No metrics rows found in: {path}")

    return rows


def metric_value(row, key):
    try:
        return float(row.get(key) or 0)
    except ValueError:
        return 0


def row_label(row):
    scenario = row.get("scenario") or "unknown"
    policy = row.get("scheduler_policy") or "legacy"
    seed = row.get("random_seed")
    return f"{scenario} / {policy}" + (f" / seed {seed}" if seed else "")


def bar_chart(rows, key, title, unit):
    width = 980
    left = 230
    right = 90
    row_height = 34
    top = 52
    height = top + len(rows) * row_height + 24
    max_value = max(metric_value(row, key) for row in rows) or 1
    bar_max = width - left - right

    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f'<text x="0" y="24" class="chart-title">{html.escape(title)}</text>',
    ]

    for index, row in enumerate(rows):
        value = metric_value(row, key)
        bar_width = (value / max_value) * bar_max
        y = top + index * row_height
        color = COLORS[index % len(COLORS)]
        label = html.escape(row_label(row))
        value_text = f"{value:,.2f}".rstrip("0").rstrip(".")

        parts.extend([
            f'<text x="0" y="{y + 19}" class="axis-label">{label}</text>',
            f'<rect x="{left}" y="{y}" width="{bar_max}" height="22" rx="4" class="bar-track" />',
            f'<rect x="{left}" y="{y}" width="{bar_width:.2f}" height="22" rx="4" fill="{color}" />',
            f'<text x="{left + bar_width + 8:.2f}" y="{y + 16}" class="value-label">'
            f'{html.escape(value_text)} {html.escape(unit)}</text>',
        ])

    parts.append("</svg>")
    return "\n".join(parts)


def summary_cards(rows):
    latest = rows[-1]
    cards = [
        ("Scenario", latest.get("scenario", "-")),
        ("Policy", latest.get("scheduler_policy") or "legacy"),
        ("Power", f"{metric_value(latest, 'total_power_consumed'):,.1f} W"),
        ("Completion", f"{metric_value(latest, 'completion_rate'):.1f}%"),
    ]

    return "\n".join(
        f"""
        <section class="metric-card">
          <span>{html.escape(title)}</span>
          <strong>{html.escape(str(value))}</strong>
        </section>
        """
        for title, value in cards
    )


def metrics_table(rows):
    columns = [
        "scenario",
        "scheduler_policy",
        "random_seed",
        "total_ticks",
        "total_power_consumed",
        "generated_tasks",
        "completed_tasks",
        "completion_rate",
        "avg_turnaround_time",
        "p_core_ratio",
        "e_core_ratio",
    ]
    header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body = []

    for row in rows:
        cells = "".join(f"<td>{html.escape(row.get(column, ''))}</td>" for column in columns)
        body.append(f"<tr>{cells}</tr>")

    return f"""
    <table>
      <thead><tr>{header}</tr></thead>
      <tbody>{''.join(body)}</tbody>
    </table>
    """


def build_report(rows):
    charts = "\n".join(bar_chart(rows, *chart) for chart in CHARTS)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Hybrid Scheduler Metrics</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --text: #172033;
      --muted: #667085;
      --line: #d7dce5;
      --track: #edf1f7;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 24px 48px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      letter-spacing: 0;
    }}
    p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.55;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .metric-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .metric-card span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .metric-card strong {{
      display: block;
      font-size: 22px;
      letter-spacing: 0;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px;
      margin-top: 16px;
      overflow-x: auto;
    }}
    svg {{
      width: 100%;
      min-width: 820px;
      display: block;
      margin: 0 0 22px;
    }}
    .chart-title {{
      font-size: 18px;
      font-weight: 700;
      fill: var(--text);
    }}
    .axis-label {{
      font-size: 12px;
      fill: var(--muted);
    }}
    .value-label {{
      font-size: 12px;
      fill: var(--text);
    }}
    .bar-track {{
      fill: var(--track);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 10px 8px;
      text-align: left;
      white-space: nowrap;
    }}
    th {{
      color: var(--muted);
      font-weight: 700;
    }}
    @media (max-width: 800px) {{
      .cards {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      main {{ padding: 24px 14px 36px; }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>AI Hybrid Scheduler Metrics</h1>
    <p>Generated from <code>{html.escape(str(METRICS_PATH))}</code>. Use identical seeds when comparing policies.</p>
    <div class="cards">
      {summary_cards(rows)}
    </div>
    <section class="panel">
      {charts}
    </section>
    <section class="panel">
      {metrics_table(rows)}
    </section>
  </main>
</body>
</html>
"""


def main():
    rows = load_metrics()
    REPORT_PATH.write_text(build_report(rows), encoding="utf-8")
    print(f">>> Metrics report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
