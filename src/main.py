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
    parser.add_argument(
        "--policy",
        choices=OSSimulator.POLICIES + ["all"],
        default="ai",
        help="비교할 스케줄링 정책",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="동일 워크로드 재현을 위한 랜덤 시드",
    )
    args = parser.parse_args()

    scenarios = TaskGenerator.available_scenarios() if args.scenario == "all" else [args.scenario]
    policies = OSSimulator.POLICIES if args.policy == "all" else [args.policy]

    for scenario in scenarios:
        for policy in policies:
            sim = OSSimulator(
                scenario=scenario,
                task_spawn_rate=args.spawn_rate,
                scheduler_policy=policy,
                random_seed=args.seed,
            )
            sim.run(max_ticks=args.ticks)
