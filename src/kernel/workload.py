import random

class TaskGenerator:
    SCENARIOS = {
        "cpu_bound": [
            ("Game_Engine", 150, 90, 30, 5, 0.9),
            ("Video_Render", 300, 95, 20, 2, 0.95),
            ("Physics_Simulation", 220, 88, 35, 4, 0.85),
            ("Data_Compression", 180, 82, 25, 6, 0.7),
        ],
        "io_bound": [
            ("Web_Browser", 40, 20, 70, 50, 0.1),
            ("File_Download", 80, 18, 45, 85, 0.05),
            ("Database_Query", 90, 35, 60, 70, 0.1),
            ("Log_Collector", 60, 15, 35, 90, 0.0),
        ],
        "memory_bound": [
            ("Image_Processing", 160, 55, 92, 10, 0.45),
            ("Large_Array_Scan", 140, 45, 95, 8, 0.2),
            ("Cache_Miss_Workload", 120, 50, 88, 15, 0.3),
            ("Graph_Traversal", 180, 60, 90, 12, 0.35),
        ],
        "background": [
            ("Background_Sync", 100, 10, 40, 80, 0.0),
            ("Notification_Service", 30, 8, 20, 60, 0.0),
            ("Telemetry_Upload", 50, 12, 25, 75, 0.0),
            ("Indexing_Idle", 90, 18, 55, 45, 0.05),
        ],
    }

    @staticmethod
    def available_scenarios():
        return list(TaskGenerator.SCENARIOS.keys()) + ["mixed"]

    @staticmethod
    def generate_random_task(scenario="mixed", rng=None):
        # (이름, 실행시간, CPU부하, 메모리접근, IO대기, FP비율)
        rng = rng or random
        if scenario == "mixed":
            tasks = [
                task
                for scenario_tasks in TaskGenerator.SCENARIOS.values()
                for task in scenario_tasks
            ]
        else:
            tasks = TaskGenerator.SCENARIOS.get(scenario)
            if tasks is None:
                valid = ", ".join(TaskGenerator.available_scenarios())
                raise ValueError(f"Unknown scenario: {scenario}. Available scenarios: {valid}")

        return rng.choice(tasks)
