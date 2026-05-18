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

            # 2. 스케줄링 및 디스패칭 (Work Stealing & Out-of-Order Execution 적용)
            
            # 먼저 대기열(ready_queue) 복사본을 순회하면서 안전하게 할당
            # (순회 중 리스트 요소 삭제를 위해 [:] 사용)
            for proc in self.ready_queue[:]:
                # 놀고 있는 코어가 아예 없으면 더 이상 훑어볼 필요 없이 종료
                free_cores = [c for c in self.cores if not c.is_busy()]
                if not free_cores:
                    break
                    
                # AI의 실시간 예측(어떤 코어가 최적인가?)
                target_type = self.scheduler.choose_core_type(proc)
                
                assigned = False
                
                # 시도 1: AI가 추천한 타입의 코어 중 비어있는 곳이 있는지 확인
                for core in free_cores:
                    if core.core_type == target_type:
                        self.ready_queue.remove(proc)
                        Dispatcher.dispatch(proc, core)
                        assigned = True
                        break
                        
                # 시도 2 (Work Stealing): 추천 코어가 꽉 차있는데 다른 코어가 놀고 있다면? 
                # (기아 현상 방지 및 자원 활용 극대화)
                if not assigned:
                    # 그냥 비어있는 아무 코어(주로 다른 타입)에 할당
                    fallback_core = free_cores[0]
                    self.ready_queue.remove(proc)
                    Dispatcher.dispatch(proc, fallback_core)
                    
                # 로깅: 모델 학습을 위해 EDP 기반의 '이상적인 정답'을 기록
                ideal_target = self.scheduler.calculate_ideal_core(proc)
                self.logger.log(list(proc.features.values()), 1 if ideal_target == "P" else 0)


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
