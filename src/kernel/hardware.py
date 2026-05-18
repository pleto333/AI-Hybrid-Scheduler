class Core:
    def __init__(self, core_id, core_type, multiplier, power_consumption):
        self.core_id = core_id
        self.core_type = core_type  # "P" or "E"
        self.multiplier = multiplier
        self.current_process = None
        # 💡 [추가] 이 코어가 틱당 소모하는 전력량 (W)
        self.power_consumption = power_consumption

    def is_busy(self):
        return self.current_process is not None

class PCore(Core):
    def __init__(self, core_id):
        # 💡 [수정] super()에 P코어 전력 소모량(10)을 추가로 넘겨줌
        super().__init__(core_id, "P", 2.0, power_consumption=10)

class ECore(Core):
    def __init__(self, core_id):
        # 💡 [수정] super()에 E코어 전력 소모량(2)을 추가로 넘겨줌
        super().__init__(core_id, "E", 1.0, power_consumption=2)