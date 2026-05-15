class Dispatcher:
    @staticmethod
    def dispatch(process, core):
        process.state = "RUNNING"
        process.assigned_core = core.core_id
        core.current_process = process