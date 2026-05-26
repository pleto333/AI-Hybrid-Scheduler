import uuid

class Process:
    def __init__(self, name, burst_time, cpu_load, mem_access, io_wait, fp_ratio):
        self.pid = str(uuid.uuid4())[:8]
        self.name = name
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.features = {
            'cpu_load': cpu_load,
            'mem_access_freq': mem_access,
            'io_wait_time': io_wait,
            'fp_instruction_ratio': fp_ratio
        }
        self.state = "READY"
        self.assigned_core = None
        self.recorded_arrival_time = None
        self.start_time = None
        self.end_time = None
