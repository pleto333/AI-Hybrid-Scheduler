import argparse

from kernel.simulator import OSSimulator
from kernel.workload import TaskGenerator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Hybrid Scheduler Simulator")
    parser.add_argument(
        "--scenario",
        choices=TaskGenerator.available_scenarios() + ["all"],
        default="mixed",
        help="실행할 워크로드 시나리오",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=50000,
        help="시뮬레이션 실행 tick 수",
    )
    parser.add_argument(
        "--spawn-rate",
        type=float,
        default=0.15,
        help="각 tick마다 새 태스크가 생성될 확률",
    )
    args = parser.parse_args()

    scenarios = TaskGenerator.available_scenarios() if args.scenario == "all" else [args.scenario]

    for scenario in scenarios:
        sim = OSSimulator(scenario=scenario, task_spawn_rate=args.spawn_rate)
        sim.run(max_ticks=args.ticks)
