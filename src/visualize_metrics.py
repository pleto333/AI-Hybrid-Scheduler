import csv
import json
from pathlib import Path
from collections import defaultdict

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

    # 시나리오별로 데이터 그룹화
    grouped_data = defaultdict(list)
    for row in rows:
        grouped_data[row['scenario']].append(row)
        
    return grouped_data, rows


def build_report(grouped_data, all_rows):
    # 최신 데이터 요약용
    latest = all_rows[-1] if all_rows else {}
    latest_power = f"{float(latest.get('total_power_consumed', 0)):,.1f} W"
    latest_time = f"{float(latest.get('avg_turnaround_time', 0)):,.1f} Ticks"
    latest_comp = f"{float(latest.get('completion_rate', 0)):.1f}%"

    # 시나리오별 차트 섹션 HTML 생성
    scenario_sections_html = ""
    chart_scripts = []
    
    for i, (scenario, rows) in enumerate(grouped_data.items()):
        chart_id_prefix = f"scenario{i}"
        
        # Chart.js 데이터 준비
        labels = [row['scheduler_policy'] for row in rows]
        power_data = [float(row.get("total_power_consumed", 0)) for row in rows]
        time_data = [float(row.get("avg_turnaround_time", 0)) for row in rows]
        
        scenario_sections_html += f"""
        <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6 tracking-tight">{scenario.replace("_", " ").title()} Scenario</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <h3 class="text-lg font-semibold text-gray-700 mb-4">Total Power Consumption (W)</h3>
                    <div class="relative h-72"><canvas id="{chart_id_prefix}PowerChart"></canvas></div>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-gray-700 mb-4">Average Turnaround Time (Ticks)</h3>
                    <div class="relative h-72"><canvas id="{chart_id_prefix}TimeChart"></canvas></div>
                </div>
            </div>
        </div>
        """
        
        chart_scripts.append(f"""
            createChart('{chart_id_prefix}PowerChart', {json.dumps(labels)}, {json.dumps(power_data)}, '#10b981');
            createChart('{chart_id_prefix}TimeChart', {json.dumps(labels)}, {json.dumps(time_data)}, '#3b82f6');
        """)

    # 상세 테이블 헤더 동적 생성
    table_headers = list(all_rows[0].keys()) if all_rows else []

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
            <p class="text-gray-500 mt-2">Scenario-based comparison of scheduling policies</p>
        </header>

        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100"><p class="text-sm font-medium text-gray-500 mb-1">Latest Scenario</p><p class="text-2xl font-bold text-gray-800">{latest.get('scenario', '-')}</p></div>
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100"><p class="text-sm font-medium text-gray-500 mb-1">Total Power</p><p class="text-2xl font-bold text-emerald-600">{latest_power}</p></div>
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100"><p class="text-sm font-medium text-gray-500 mb-1">Avg Time</p><p class="text-2xl font-bold text-blue-600">{latest_time}</p></div>
            <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100"><p class="text-sm font-medium text-gray-500 mb-1">Completion Rate</p><p class="text-2xl font-bold text-purple-600">{latest_comp}</p></div>
        </div>

        <!-- Scenario-specific Charts -->
        {scenario_sections_html}

        <!-- Detailed Log Table -->
        <div class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
            <div class="px-6 py-4 border-b border-gray-100"><h3 class="text-lg font-semibold text-gray-700">Detailed Metrics Log</h3></div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 text-sm">
                    <thead class="bg-gray-50">
                        <tr>{"".join(f'<th class="px-4 py-3 text-left font-medium text-gray-500 uppercase tracking-wider">{h.replace("_", " ").title()}</th>' for h in table_headers)}</tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {"".join('<tr>' + "".join(f'<td class="px-4 py-4 whitespace-nowrap text-gray-700">{r.get(k, "-")}</td>' for k in table_headers) + '</tr>' for r in all_rows)}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function createChart(canvasId, labels, data, color) {{
            new Chart(document.getElementById(canvasId), {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: data,
                        backgroundColor: color,
                        borderRadius: 6,
                        barPercentage: 0.6,
                        categoryPercentage: 0.7
                    }}]
                }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }}, tooltip: {{ backgroundColor: 'rgba(17, 24, 39, 0.9)', padding: 12, titleFont: {{ size: 13, family: 'Inter' }}, bodyFont: {{ size: 14, family: 'Inter', weight: 'bold' }}, cornerRadius: 8, displayColors: false }} }},
                    scales: {{
                        y: {{ beginAtZero: true, grid: {{ color: '#e5e7eb' }}, border: {{ display: false }}, ticks: {{ font: {{ family: 'Inter' }}, color: '#6b7280' }} }},
                        x: {{ grid: {{ display: false }}, border: {{ display: false }}, ticks: {{ font: {{ family: 'Inter' }}, color: '#6b7280' }} }}
                    }}
                }}
            }});
        }}
        
        {''.join(chart_scripts)}
    </script>
</body>
</html>"""
    return html_content


def main():
    grouped_data, all_rows = load_metrics()
    REPORT_PATH.write_text(build_report(grouped_data, all_rows), encoding="utf-8")
    print(f">>> Metrics report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
