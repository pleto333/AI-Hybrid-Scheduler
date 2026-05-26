import csv
import json
from collections import defaultdict
from pathlib import Path

from common.config import BASE_DIR, METRICS_PATH

REPORT_PATH = Path(BASE_DIR) / "data" / "metrics_report.html"

CHART_METRICS = [
    ("Completion Rate (%)", "completion_rate", "#2563eb"),
    ("Throughput (tasks/tick)", "throughput", "#059669"),
    ("Avg Turnaround Time", "avg_turnaround_time", "#dc2626"),
    ("Avg Waiting Time", "avg_waiting_time", "#ea580c"),
    ("Ready Queue Size", "remaining_queue_size", "#7c3aed"),
    ("Power per Completed Task", "power_per_completed_task", "#0891b2"),
    ("Ideal Core Match Rate (%)", "ideal_core_match_rate", "#16a34a"),
]

TABLE_HEADERS = [
    "scenario",
    "scheduler_policy",
    "completed_tasks",
    "completion_rate",
    "throughput",
    "avg_turnaround_time",
    "avg_waiting_time",
    "remaining_queue_size",
    "power_per_completed_task",
    "ideal_core_match_rate",
]

TABLE_LABELS = {
    "scenario": "시나리오",
    "scheduler_policy": "Policy",
    "completed_tasks": "Completed Tasks",
    "completion_rate": "Completion Rate",
    "throughput": "Throughput",
    "avg_turnaround_time": "Avg Turnaround Time",
    "avg_waiting_time": "Avg Waiting Time",
    "remaining_queue_size": "Ready Queue",
    "power_per_completed_task": "Power / Task",
    "ideal_core_match_rate": "Core Match Rate",
}

POLICY_LABELS = {
    "ai": "AI Hybrid",
    "rule_based": "Rule-based",
    "p_core_only": "P-Core 전용",
    "e_core_only": "E-Core 전용",
    "round_robin": "Round Robin",
}

SCENARIO_LABELS = {
    "cpu_bound": "CPU-bound",
    "io_bound": "I/O-bound",
    "memory_bound": "Memory-bound",
    "background": "Background",
    "trick_io_intensive": "High CPU + I/O",
    "trick_memory_intensive": "High CPU + Memory",
    "mixed": "Mixed Workload",
}


def as_float(row, key):
    try:
        return float(row.get(key, 0))
    except (TypeError, ValueError):
        return 0.0


def scenario_label(value):
    return SCENARIO_LABELS.get(value, value.replace("_", " ").title())


def policy_label(value):
    return POLICY_LABELS.get(value, value)


def display_value(row, header):
    value = row.get(header, "-")
    if header == "scenario":
        return scenario_label(value)
    if header == "scheduler_policy":
        return policy_label(value)
    return value


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

    grouped_data = defaultdict(list)
    for row in rows:
        grouped_data[row["scenario"]].append(row)

    return grouped_data, rows


def find_policy(rows, policy):
    return next((row for row in rows if row.get("scheduler_policy") == policy), None)


def pct_change(baseline, current, lower_is_better=False):
    if baseline == 0:
        return 0.0
    diff = baseline - current if lower_is_better else current - baseline
    return diff / baseline * 100


def build_summary_cards(grouped_data):
    rows = grouped_data.get("mixed") or next(iter(grouped_data.values()))
    ai = find_policy(rows, "ai")
    baseline = find_policy(rows, "rule_based")

    if not ai or not baseline:
        return ""

    turnaround_gain = pct_change(
        as_float(baseline, "avg_turnaround_time"),
        as_float(ai, "avg_turnaround_time"),
        lower_is_better=True,
    )
    waiting_gain = pct_change(
        as_float(baseline, "avg_waiting_time"),
        as_float(ai, "avg_waiting_time"),
        lower_is_better=True,
    )
    queue_gain = pct_change(
        as_float(baseline, "remaining_queue_size"),
        as_float(ai, "remaining_queue_size"),
        lower_is_better=True,
    )
    completed_diff = int(as_float(ai, "completed_tasks") - as_float(baseline, "completed_tasks"))

    cards = [
        ("대표 시나리오", scenario_label(ai.get("scenario", "-")), "text-slate-800"),
        ("Completed Tasks 증가", f"+{completed_diff}", "text-blue-700"),
        ("Turnaround Time 감소", f"{turnaround_gain:.1f}%", "text-red-700"),
        ("Waiting Time 감소", f"{waiting_gain:.1f}%", "text-orange-700"),
        ("Ready Queue 감소", f"{queue_gain:.1f}%", "text-purple-700"),
        ("AI Core Match Rate", f"{as_float(ai, 'ideal_core_match_rate'):.1f}%", "text-green-700"),
    ]

    return "\n".join(
        f"""
        <div class="bg-white rounded-lg border border-slate-200 p-4">
            <p class="text-xs font-semibold text-slate-500">{label}</p>
            <p class="mt-1 text-2xl font-bold {color}">{value}</p>
        </div>
        """
        for label, value, color in cards
    )


def build_report(grouped_data, all_rows):
    scenario_sections = []
    chart_scripts = []

    for index, (scenario, rows) in enumerate(grouped_data.items()):
        labels = [policy_label(row["scheduler_policy"]) for row in rows]
        chart_cards = []

        for metric_index, (title, key, color) in enumerate(CHART_METRICS):
            canvas_id = f"scenario{index}metric{metric_index}"
            data = [as_float(row, key) for row in rows]
            chart_cards.append(
                f"""
                <div class="bg-white rounded-lg border border-slate-200 p-4">
                    <h3 class="mb-3 text-sm font-semibold text-slate-700">{title}</h3>
                    <div class="h-56"><canvas id="{canvas_id}"></canvas></div>
                </div>
                """
            )
            chart_scripts.append(
                f"createChart('{canvas_id}', {json.dumps(labels)}, {json.dumps(data)}, '{color}');"
            )

        scenario_sections.append(
            f"""
            <section class="mb-10">
                <h2 class="mb-4 text-xl font-bold text-slate-800">{scenario_label(scenario)}</h2>
                <div class="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
                    {''.join(chart_cards)}
                </div>
            </section>
            """
        )

    table_html = "\n".join(
        "<tr>"
        + "".join(
            f'<td class="whitespace-nowrap px-3 py-3 text-slate-700">{display_value(row, header)}</td>'
            for header in TABLE_HEADERS
        )
        + "</tr>"
        for row in all_rows
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Hybrid Scheduler 성능 대시보드</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-slate-100 p-6">
    <main class="mx-auto max-w-7xl">
        <header class="mb-6">
            <h1 class="text-3xl font-bold text-slate-900">AI Hybrid Scheduler 성능 분석</h1>
            <p class="mt-2 text-slate-600">Completion, latency, queue pressure, AI decision quality를 중심으로 스케줄링 정책을 비교합니다.</p>
        </header>

        <section class="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3 xl:grid-cols-6">
            {build_summary_cards(grouped_data)}
        </section>

        {''.join(scenario_sections)}

        <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
            <div class="border-b border-slate-200 px-4 py-3">
                <h2 class="text-lg font-bold text-slate-800">Detailed Metrics</h2>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-slate-200 text-sm">
                    <thead class="bg-slate-50">
                        <tr>
                            {''.join(f'<th class="whitespace-nowrap px-3 py-3 text-left text-xs font-bold text-slate-500">{TABLE_LABELS.get(header, header)}</th>' for header in TABLE_HEADERS)}
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                        {table_html}
                    </tbody>
                </table>
            </div>
        </section>
    </main>

    <script>
        function createChart(canvasId, labels, data, color) {{
            new Chart(document.getElementById(canvasId), {{
                type: 'bar',
                data: {{
                    labels,
                    datasets: [{{
                        data,
                        backgroundColor: color,
                        borderRadius: 5,
                        barPercentage: 0.65,
                        categoryPercentage: 0.75
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{ displayColors: false }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true, grid: {{ color: '#e2e8f0' }} }},
                        x: {{ grid: {{ display: false }} }}
                    }}
                }}
            }});
        }}

        {''.join(chart_scripts)}
    </script>
</body>
</html>"""


def main():
    grouped_data, all_rows = load_metrics()
    REPORT_PATH.write_text(build_report(grouped_data, all_rows), encoding="utf-8")
    print(f">>> Metrics report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
