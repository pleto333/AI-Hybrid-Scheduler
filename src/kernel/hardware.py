class Core:
    def __init__(self, core_id, core_type, multiplier, power_consumption):
        self.core_id = core_id
        self.core_type = core_type  # "P" or "E"
        self.multiplier = multiplier
        self.power_consumption = power_consumption # 틱당 전력 소모량
        self.current_process = None

    def is_busy(self):
        return self.current_process is not None

class PCore(Core):
    def __init__(self, core_id):
        # P코어: 속도 2배, 전력소모 3.0
        super().__init__(core_id, "P", 2.0, 3.0)

class ECore(Core):
    def __init__(self, core_id):
        # E코어: 속도 1배, 전력소모 1.0
        super().__init__(core_id, "E", 1.0, 1.0)
