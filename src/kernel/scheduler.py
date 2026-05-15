from ai.inference import AISchedulerInterface

class HybridScheduler:
    def __init__(self):
        self.ai_engine = AISchedulerInterface()

    def choose_core_type(self, process):
        # AI에게 판단 요청
        feat = list(process.features.values())
        decision = self.ai_engine.predict(feat)
        return "P" if decision == 1 else "E"