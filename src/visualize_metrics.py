import csv
import json
from pathlib import Path

from common.config import BASE_DIR, METRICS_PATH

REPORT_PATH = Path(BASE_DIR) / "data" / "metrics_report.html"


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


def build_report(rows):
    # Chart.js에 전달할 데이터 준비
    labels = []
    power_data = []
    time_data = []
    completion_data = []

    for row in rows:
        scenario = row.get("scenario", "Unknown")
        policy = row.get("scheduler_policy", "Legacy")
        labels.append(f"{scenario} ({policy})")
        power_data.append(float(row.get("total_power_consumed", 0)))
        time_data.append(float(row.get("avg_turnaround_time", 0)))
        completion_data.append(float(row.get("completion_rate", 0)))

    # 최신 데이터 요약용
    latest = rows[-1] if rows else {}
    latest_power = f"{float(latest.get('total_power_consumed', 0)):,.1f} W"
    latest_time = f"{float(latest.get('avg_turnaround_time', 0)):,.1f} Ticks"
    latest_comp = f"{float(latest.get('completion_rate', 0)):.1f}%"

    # 상세 테이블 헤더 동적 생성 (CSV 파일의 모든 컬럼을 사용)
    table_headers = list(rows[0].keys()) if rows else []
    
    def format_value(key, value):
        try:
            val = float(value)
            if '_ratio' in key or 'rate' in key:
                return f"{val:.1f}%"
            if 'power' in key:
                return f"{val:,.1f}"
            if 'time' in key or 'ticks' in key:
                return f"{val:,.2f}"
            return f"{int(val):,}"
        except (ValueError, TypeError):
            return value

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Hybrid Scheduler Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f3f4f6; }}
    </style>
</head>
<body class="p-8">

    <div class="max-w-7xl mx-auto">
        <header class="mb-8">
            <h1 class="text-3xl font-bold text-gray-800 tracking-tight">AI Hybrid Scheduler Performance</h1>
            <p class="text-gray-500 mt-2">Comparison of Baseline (Legacy) vs Proposed (AI) Scheduling Policies</p>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <p class="text-sm font-medium text-gray-500 mb-1">Latest Scenario</p>
                <p class="text-2xl font-bold text-gray-800">{latest.get('scenario', '-')}</p>
            </div>
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <p class="text-sm font-medium text-gray-500 mb-1">Total Power Consumption</p>
                <p class="text-2xl font-bold text-emerald-600">{latest_power}</p>
            </div>
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <p class="text-sm font-medium text-gray-500 mb-1">Avg Turnaround Time</p>
                <p class="text-2xl font-bold text-blue-600">{latest_time}</p>
            </div>
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <p class="text-sm font-medium text-gray-500 mb-1">Completion Rate</p>
                <p class="text-2xl font-bold text-purple-600">{latest_comp}</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <h3 class="text-lg font-semibold text-gray-700 mb-4">Total Power Consumption (W)</h3>
                <div class="relative h-64"><canvas id="powerChart"></canvas></div>
            </div>
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <h3 class="text-lg font-semibold text-gray-700 mb-4">Average Turnaround Time (Ticks)</h3>
                <div class="relative h-64"><canvas id="timeChart"></canvas></div>
            </div>
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <h3 class="text-lg font-semibold text-gray-700 mb-4">Task Completion Rate (%)</h3>
                <div class="relative h-64"><canvas id="completionChart"></canvas></div>
            </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
            <div class="px-6 py-4 border-b border-gray-100">
                <h3 class="text-lg font-semibold text-gray-700">Detailed Metrics Log</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 text-sm">
                    <thead class="bg-gray-50">
                        <tr>
                            {"".join(f'<th class="px-4 py-3 text-left font-medium text-gray-500 uppercase tracking-wider">{h.replace("_", " ").title()}</th>' for h in table_headers)}
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {"".join(
                            '<tr>' + "".join(f'<td class="px-4 py-4 whitespace-nowrap text-gray-700">{format_value(k, r.get(k, "-"))}</td>' for k in table_headers) + '</tr>'
                            for r in rows
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const labels = {json.dumps(labels)};
        const powerData = {json.dumps(power_data)};
        const timeData = {json.dumps(time_data)};
        const completionData = {json.dumps(completion_data)};

        const commonOptions = {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }}, tooltip: {{ backgroundColor: 'rgba(17, 24, 39, 0.9)', padding: 12, titleFont: {{ size: 13, family: 'Inter' }}, bodyFont: {{ size: 14, family: 'Inter', weight: 'bold' }}, cornerRadius: 8, displayColors: false }} }},
            scales: {{
                y: {{ beginAtZero: true, grid: {{ color: '#f3f4f6', drawBorder: false }}, border: {{ display: false }}, ticks: {{ font: {{ family: 'Inter' }}, color: '#6b7280' }} }},
                x: {{ grid: {{ display: false, drawBorder: false }}, border: {{ display: false }}, ticks: {{ font: {{ family: 'Inter' }}, color: '#6b7280' }} }}
            }}
        }};

        new Chart(document.getElementById('powerChart'), {{ type: 'bar', data: {{ labels: labels, datasets: [{{ data: powerData, backgroundColor: '#10b981', borderRadius: 6 }}] }}, options: commonOptions }});
        new Chart(document.getElementById('timeChart'), {{ type: 'bar', data: {{ labels: labels, datasets: [{{ data: timeData, backgroundColor: '#3b82f6', borderRadius: 6 }}] }}, options: commonOptions }});
        new Chart(document.getElementById('completionChart'), {{ type: 'bar', data: {{ labels: labels, datasets: [{{ data: completionData, backgroundColor: '#8b5cf6', borderRadius: 6 }}] }}, options: commonOptions }});
    </script>
</body>
</html>"""
    return html_content


def main():
    rows = load_metrics()
    REPORT_PATH.write_text(build_report(rows), encoding="utf-8")
    print(f">>> Metrics report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
