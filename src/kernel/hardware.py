class Core:
    def __init__(self, core_id, core_type, multiplier):
        self.core_id = core_id
        self.core_type = core_type  # "P" or "E"
        self.multiplier = multiplier
        self.current_process = None

    def is_busy(self):
        return self.current_process is not None

class PCore(Core):
    def __init__(self, core_id):
        super().__init__(core_id, "P", 2.0)

class ECore(Core):
    def __init__(self, core_id):
        super().__init__(core_id, "E", 1.0)