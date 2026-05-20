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

        # 💡 [추가] 시뮬레이션 중 완료된 프로세스들을 모아둘 보관함 리스트
        self.completed_tasks = []

    def run(self, max_ticks=500):
        print(">>> Simulator Running...")
        while self.tick < max_ticks:
            # 1. 태스크 생성
            if random.random() < 0.15:
                new_proc = Process(*TaskGenerator.generate_random_task())

                # 💡 [추가] 성우가 Process 클래스에 만든 생성시간 변수명이 뭔지 몰라도
                # 여기서 안전하게 현재 틱(self.tick)을 대피용 속성으로 무조건 저장해둠!
                new_proc.recorded_arrival_time = self.tick

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
                        assigned_core = core
                        break

                # 시도 2 (Work Stealing): 추천 코어가 꽉 차있는데 다른 코어가 놀고 있다면?
                # (기아 현상 방지 및 자원 활용 극대화)
                if not assigned:
                    # 그냥 비어있는 아무 코어(주로 다른 타입)에 할당
                    fallback_core = free_cores[0]
                    self.ready_queue.remove(proc)
                    Dispatcher.dispatch(proc, fallback_core)
                    assigned_core = fallback_core

                # 로깅: 모델 학습을 위해 EDP 기반의 '이상적인 정답'을 기록
                ideal_target = self.scheduler.calculate_ideal_core(proc)
                self.logger.log(
                    list(proc.features.values()),
                    assigned_core.power_consumption,
                    1 if ideal_target == "P" else 0
                )

            # 3. 실행 (Tick) 및 실시간 전력 소모량 연산
            for core in self.cores:
                if core.is_busy():
                    # [추가] 코어가 일하고 있으면 해당 코어의 전력(P:10W / E:2W)을 누적
                    self.total_power_consumed += core.power_consumption

                    p = core.current_process
                    p.remaining_time -= (1 * core.multiplier)

                    # 💡 프로세스가 실행을 끝마친 순간!
                    if p.remaining_time <= 0:
                        # 💡 [추가] 프로세스가 끝난 시점의 현재 틱을 기록
                        p.end_time = self.tick

                        # 💡 [추가] 완료 보관함에 이 프로세스 객체를 쏙 집어넣음
                        self.completed_tasks.append(p)

                        core.current_process = None
                else:
                    # [추가] 코어가 놀고(Idle) 있을 때도 기본 대기 전력 0.5W 누적
                    self.total_power_consumed += 0.5

            self.tick += 1

        self.logger.close()
        print(f">>> Simulation Finished. Data saved to {DATA_PATH}")

        # 💡 [추가] 시뮬레이션 종료 후 평균 턴어라운드 타임(Turnaround Time) 계산
        # 턴어라운드 타임 = 프로세스 종료 시간 - 프로세스 생성 시간
        turnaround_times = []
        for task in self.completed_tasks:
            # 우리가 태스크 생성 시점에 강제로 심어둔 recorded_arrival_time을 활용해 연산
            duration = task.end_time - task.recorded_arrival_time
            turnaround_times.append(duration)

        avg_turnaround = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0

        # 💡 [추가] 교수님 피티에 바로 캡처해서 넣을 수 있는 웅장한 종합 성능 리포트 출력
        print("\n" + "=" * 50)
        print("📊 AM:PM AI 하이브리드 스케줄러 최종 성능 리포트")
        print("=" * 50)
        print(f"⏱️  총 시뮬레이션 시간 : {self.tick} Ticks")
        print(f"⚡  총 전력 소모량      : {self.total_power_consumed:,.1f} W")
        print(f"✅  처리 완료된 태스크  : {len(self.completed_tasks)} 개")
        print(f"📈  평균 턴어라운드 타임 : {avg_turnaround:.2f} Ticks")
        print("=" * 50)
