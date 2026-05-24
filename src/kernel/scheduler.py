from ai.inference import AISchedulerInterface
from .hardware import PCore, ECore


class HybridScheduler:
    def __init__(self):
        self.ai_engine = AISchedulerInterface()
        self.p_core_ref = PCore("ref")
        self.e_core_ref = ECore("ref")

    def choose_core_type(self, process):
        cached_target = getattr(process, "_ai_target_core", None)
        if cached_target is not None:
            return cached_target

        feat = list(process.features.values())
        decision = self.ai_engine.predict(feat)
        target = "P" if decision == 1 else "E"
        process._ai_target_core = target
        return target

    def score_process_for_core(self, process, core_type, current_tick, core_multiplier):
        target_type = self.choose_core_type(process)
        mismatch_penalty = 1000 if target_type != core_type else 0
        estimated_runtime = process.remaining_time / core_multiplier
        age = max(0, current_tick - getattr(process, "recorded_arrival_time", current_tick))

        features = process.features
        cpu_load = features["cpu_load"]
        mem_access = features["mem_access_freq"]
        io_wait = features["io_wait_time"]
        fp_ratio = features["fp_instruction_ratio"]

        if core_type == "P":
            affinity = cpu_load * 0.4 + fp_ratio * 100 * 0.4 + min(process.burst_time / 3, 100) * 0.2
        else:
            affinity = io_wait * 0.5 + mem_access * 0.35 + (100 - cpu_load) * 0.15

        aging_bonus = min(age, 2000) * 0.02
        return mismatch_penalty + estimated_runtime - affinity * 0.05 - aging_bonus

    def calculate_ideal_core(self, process):
        """
        Return the target core used as the AI training label.

        P-Core is treated as the better target for compute-heavy work that gains
        enough speed from the faster core. E-Core is treated as the better target
        for I/O or memory-stall-heavy work because a faster core cannot remove
        most of that waiting time.
        """
        burst = process.burst_time
        cpu_load = process.features["cpu_load"]
        mem_access = process.features["mem_access_freq"]
        io_wait = process.features["io_wait_time"]
        fp_ratio = process.features["fp_instruction_ratio"]

        non_compute_penalty = (io_wait + mem_access) * 0.8
        p_time = (burst / self.p_core_ref.multiplier) + non_compute_penalty
        e_time = (burst / self.e_core_ref.multiplier) + non_compute_penalty
        speedup_ratio = (e_time - p_time) / e_time if e_time else 0

        compute_score = (
            cpu_load * 0.45
            + fp_ratio * 100 * 0.35
            + min(burst / 3, 100) * 0.20
        )
        stall_score = io_wait * 0.55 + mem_access * 0.45

        if speedup_ratio >= 0.25 and compute_score >= stall_score * 0.95:
            return "P"
        return "E"
