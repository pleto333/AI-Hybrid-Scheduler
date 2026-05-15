import random

class TaskGenerator:
    @staticmethod
    def generate_random_task():
        # (이름, 실행시간, CPU부하, 메모리접근, IO대기, FP비율)
        scenarios = [
            ("Game_Engine", 150, 90, 30, 5, 0.9),
            ("Web_Browser", 40, 20, 70, 50, 0.1),
            ("Video_Render", 300, 95, 20, 2, 0.95),
            ("Background_Sync", 100, 10, 40, 80, 0.0)
        ]
        return random.choice(scenarios)