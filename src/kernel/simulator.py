import csv
import os
import random

from .hardware import PCore, ECore
from .scheduler import HybridScheduler
from .dispatcher import Dispatcher
from .workload import TaskGenerator
from .pcb import Process
from .logger import SystemLogger

from common.config import DATA_PATH, METRICS_PATH


class OSSimulator:
    POLICIES = ["ai", "rule_based", "p_core_only", "e_core_only", "round_robin"]

    def __init__(
        self,
        scenario="mixed",
        task_spawn_rate=0.15,
        scheduler_policy="ai",
        random_seed=42,
    ):
        self.cores = [PCore("P0"), PCore("P1"), ECore("E0"), ECore("E1")]
        self.ready_queue = []
        self.scheduler = HybridScheduler()
        self.logger = SystemLogger()
        self.tick = 0
        self.scenario = scenario
        self.task_spawn_rate = task_spawn_rate
        self.scheduler_policy = scheduler_policy
        self.random_seed = random_seed
        self.rng = random.Random(random_seed)
        self.assignment_counts = {"P": 0, "E": 0}
        self.generated_tasks = 0
        self.round_robin_index = 0

        self.total_power_consumed = 0
        self.completed_tasks = []

    def run(self, max_ticks=500):
        print(
            f">>> Simulator Running... scenario={self.scenario}, "
            f"policy={self.scheduler_policy}, seed={self.random_seed}, ticks={max_ticks}"
        )
        while self.tick < max_ticks:
            # 1. 태스크 생성
            if self.rng.random() < self.task_spawn_rate:
                new_proc = Process(*TaskGenerator.generate_random_task(self.scenario, self.rng))
                new_proc.recorded_arrival_time = self.tick

                self.ready_queue.append(new_proc)
                self.generated_tasks += 1

            # 2. 스케줄링 및 디스패칭
            for proc in self.ready_queue[:]:
                free_cores = [c for c in self.cores if not c.is_busy()]
                if not free_cores:
                    break

                assigned_core = self.select_core(proc, free_cores)
                if assigned_core is None:
                    continue

                self.ready_queue.remove(proc)
                Dispatcher.dispatch(proc, assigned_core)
                self.assignment_counts[assigned_core.core_type] += 1

                # 로깅: '작업의 순수 특징'과 'EDP 기반의 이상적인 정답'만 기록 (전력소모 제외)
                ideal_target = self.scheduler.calculate_ideal_core(proc)
                self.logger.log(
                    list(proc.features.values()),
                    1 if ideal_target == "P" else 0
                )

            # 3. 실행 (Tick) 및 실시간 전력 소모량 연산
            for core in self.cores:
                if core.is_busy():
                    self.total_power_consumed += core.power_consumption

                    p = core.current_process
                    p.remaining_time -= (1 * core.multiplier)

                    if p.remaining_time <= 0:
                        p.end_time = self.tick
                        self.completed_tasks.append(p)
                        core.current_process = None
                else:
                    # 코어가 놀고(Idle) 있을 때 대기 전력 누적
                    self.total_power_consumed += 0.5

            self.tick += 1

        self.logger.close()
        print(f">>> Simulation Finished. Data saved to {DATA_PATH}")

        # 메트릭 계산 및 저장 로직
        turnaround_times = []
        for task in self.completed_tasks:
            duration = task.end_time - task.recorded_arrival_time
            turnaround_times.append(duration)

        avg_turnaround = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0
        total_assignments = sum(self.assignment_counts.values())
        p_ratio = (self.assignment_counts["P"] / total_assignments * 100) if total_assignments else 0
        e_ratio = (self.assignment_counts["E"] / total_assignments * 100) if total_assignments else 0
        completed_count = len(self.completed_tasks)
        running_tasks = sum(1 for core in self.cores if core.is_busy())
        remaining_queue_size = len(self.ready_queue)
        completion_rate = (completed_count / self.generated_tasks * 100) if self.generated_tasks else 0
        
        metrics = {
            "scenario": self.scenario,
            "scheduler_policy": self.scheduler_policy,
            "random_seed": self.random_seed,
            "total_ticks": self.tick,
            "total_power_consumed": round(self.total_power_consumed, 2),
            "generated_tasks": self.generated_tasks,
            "completed_tasks": completed_count,
            "completion_rate": round(completion_rate, 2),
            "remaining_queue_size": remaining_queue_size,
            "running_tasks": running_tasks,
            "avg_turnaround_time": round(avg_turnaround, 2),
            "p_core_assignments": self.assignment_counts["P"],
            "e_core_assignments": self.assignment_counts["E"],
            "p_core_ratio": round(p_ratio, 2),
            "e_core_ratio": round(e_ratio, 2),
        }
        self.save_metrics(metrics)

    def select_core(self, process, free_cores):
        if self.scheduler_policy == "ai":
            target_type = self.scheduler.choose_core_type(process)
            return self.preferred_or_fallback_core(target_type, free_cores)

        if self.scheduler_policy == "rule_based":
            features = process.features
            target_type = (
                "P"
                if features["cpu_load"] > 70 or features["fp_instruction_ratio"] > 0.5
                else "E"
            )
            return self.preferred_or_fallback_core(target_type, free_cores)

        if self.scheduler_policy == "p_core_only":
            return next((core for core in free_cores if core.core_type == "P"), None)

        if self.scheduler_policy == "e_core_only":
            return next((core for core in free_cores if core.core_type == "E"), None)

        if self.scheduler_policy == "round_robin":
            return self.round_robin_core(free_cores)

        raise ValueError(f"Unknown scheduler policy: {self.scheduler_policy}")

    @staticmethod
    def preferred_or_fallback_core(target_type, free_cores):
        for core in free_cores:
            if core.core_type == target_type:
                return core
        return free_cores[0] if free_cores else None

    def round_robin_core(self, free_cores):
        for offset in range(len(self.cores)):
            core = self.cores[(self.round_robin_index + offset) % len(self.cores)]
            if core in free_cores:
                self.round_robin_index = (self.cores.index(core) + 1) % len(self.cores)
                return core
        return None

    def save_metrics(self, metrics):
        fieldnames = list(metrics.keys())
        file_exists = os.path.exists(METRICS_PATH)
        existing_rows = []

        if file_exists:
            with open(METRICS_PATH, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                duplicate_header_exists = any(row.get("scenario") == "scenario" for row in rows)
                existing_rows = [
                    row for row in rows
                    if row.get("scenario") and row.get("scenario") != "scenario"
                ]
                if reader.fieldnames != fieldnames or duplicate_header_exists:
                    file_exists = False

        if existing_rows and not file_exists:
            with open(METRICS_PATH, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for row in existing_rows:
                    writer.writerow({field: row.get(field, "") for field in fieldnames})
            file_exists = True

        with open(METRICS_PATH, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(metrics)
