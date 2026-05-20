from ai.inference import AISchedulerInterface
from .hardware import PCore, ECore

class HybridScheduler:
    def __init__(self):
        self.ai_engine = AISchedulerInterface()
        # EDP 계산을 위한 하드웨어 스펙 레퍼런스
        self.p_core_ref = PCore("ref")
        self.e_core_ref = ECore("ref")

    def choose_core_type(self, process):
        # AI에게 판단 요청 (실제 시뮬레이터 동작용 예측값)
        feat = list(process.features.values())
        decision = self.ai_engine.predict(feat)
        return "P" if decision == 1 else "E"

    def calculate_ideal_core(self, process):
        """
        EDP(Energy-Delay Product)를 계산하여 진정한 의미의 이상적인 정답 코어를 반환합니다.
        AI 모델의 학습용 라벨(Target)로 사용됩니다.
        """
        burst = process.burst_time
        cpu_load = process.features['cpu_load']
        mem_access = process.features['mem_access_freq']
        io_wait = process.features['io_wait_time']

        # I/O 및 메모리 대기 패널티 (코어 성능 무관)
        penalty_time = (io_wait + mem_access) * 0.1

        # --- P-Core 예상치 계산 ---
        # 실행 시간 = (연산 시간 / P코어 속도) + 패널티 지연 시간
        p_time = (burst / self.p_core_ref.multiplier) + penalty_time
        # 전력 소모 = (실행 시간 * P코어 기본 전력) + (CPU 부하에 따른 추가 전력)
        p_power = (p_time * self.p_core_ref.power_consumption) + (cpu_load * 0.05)
        p_edp = p_time * p_power

        # --- E-Core 예상치 계산 ---
        e_time = (burst / self.e_core_ref.multiplier) + penalty_time
        e_power = (e_time * self.e_core_ref.power_consumption) + (cpu_load * 0.01)
        e_edp = e_time * e_power

        # EDP가 더 작은 쪽이 고효율(정답)
        if p_edp < e_edp:
            return "P"
        else:
            return "E"
