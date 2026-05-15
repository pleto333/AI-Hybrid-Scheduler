import random

from .hardware import PCore, ECore
from .scheduler import HybridScheduler
from .dispatcher import Dispatcher
from .workload import TaskGenerator
from .pcb import Process
from .logger import SystemLogger

from common.config import DATA_PATH

class OSSimulator:
    def __init__(self):
        self.cores = [PCore("P0"), PCore("P1"), ECore("E0"), ECore("E1")]
        self.ready_queue = []
        self.scheduler = HybridScheduler()
        self.logger = SystemLogger()
        self.tick = 0

    def run(self, max_ticks=500):
        print(">>> Simulator Running...")
        while self.tick < max_ticks:
            # 1. 태스크 생성
            if random.random() < 0.15:
                new_proc = Process(*TaskGenerator.generate_random_task())
                self.ready_queue.append(new_proc)

            # 2. 스케줄링 및 디스패칭
            for core in self.cores:
                if not core.is_busy() and self.ready_queue:
                    proc = self.ready_queue[0]
                    target_type = self.scheduler.choose_core_type(proc)

                    if core.core_type == target_type:
                        self.ready_queue.pop(0)
                        Dispatcher.dispatch(proc, core)
                        self.logger.log(list(proc.features.values()), 1 if target_type == "P" else 0)

            # 3. 실행 (Tick)
            for core in self.cores:
                if core.is_busy():
                    p = core.current_process
                    p.remaining_time -= (1 * core.multiplier)
                    if p.remaining_time <= 0:
                        core.current_process = None
            self.tick += 1
        self.logger.close()
        print(f">>> Simulation Finished. Data saved to {DATA_PATH}")