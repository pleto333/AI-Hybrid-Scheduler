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

        # [추가] 시뮬레이션 전체에서 소모한 총 전력량 (0 W로 시작)
        self.total_power_consumed = 0

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

                        # 💡 [체크 및 수정] logger.py에 맞게 core.power_consumption을 중간에 추가함!
                        self.logger.log(
                            list(proc.features.values()),
                            core.power_consumption,
                            1 if target_type == "P" else 0
                        )

            # 3. 실행 (Tick) 및 실시간 전력 소모량 연산
            for core in self.cores:
                if core.is_busy():
                    # [추가] 코어가 일하고 있으면 해당 코어의 전력(P:10W / E:2W)을 누적
                    self.total_power_consumed += core.power_consumption

                    p = core.current_process
                    p.remaining_time -= (1 * core.multiplier)
                    if p.remaining_time <= 0:
                        core.current_process = None
                else:
                    # [추가] 코어가 놀고(Idle) 있을 때도 기본 대기 전력 0.5W 누적
                    self.total_power_consumed += 0.5

            self.tick += 1
        self.logger.close()
        print(f">>> Simulation Finished. Data saved to {DATA_PATH}")
        # [임시 추가] 전력이 잘 누적되는지 눈으로 확인하기 위한 프린트문
        print(f">>> [⚡전력 리포트] 총 전력 소모량: {self.total_power_consumed} W")