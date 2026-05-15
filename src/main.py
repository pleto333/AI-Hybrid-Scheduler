from kernel.simulator import OSSimulator

if __name__ == "__main__":
    # 시뮬레이터 실행 (2000틱 동안 데이터 수집 및 시뮬레이션)
    sim = OSSimulator()
    sim.run(max_ticks=50000)