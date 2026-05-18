import csv
import os
from common.config import DATA_PATH


class SystemLogger:
    def __init__(self):
        # 1. 파일이 이미 존재하는지 먼저 확인 (변수 정의)
        file_exists = os.path.exists(DATA_PATH)

        # 2. 추가 모드('a')로 파일 열기
        self.file = open(DATA_PATH, 'a', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)

        # 3. 파일이 새로 생성될 때만 헤더 작성
        if not file_exists:
            # 💡 [수정] 'power_consumption' 헤더를 정답(target_core) 바로 앞에 추가
            self.writer.writerow([
                'cpu_load', 'mem_access_freq', 'io_wait_time', 'fp_instruction_ratio',
                'power_consumption', 'target_core'
            ])

    # 💡 [수정] 파라미터에 power_consumption(전력 소모량)을 추가로 받도록 변경
    def log(self, features, power_consumption, decision):
        # 💡 [수정] features 리스트 뒤에 전력 소모량을 붙이고, 마지막에 정답(decision)을 합쳐서 저장
        self.writer.writerow(features + [power_consumption, decision])

    def close(self):
        self.file.close()