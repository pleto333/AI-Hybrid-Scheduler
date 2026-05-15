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
            self.writer.writerow(['cpu_load', 'mem_access_freq', 'io_wait_time', 'fp_instruction_ratio', 'target_core'])

    def log(self, features, decision):
        self.writer.writerow(features + [decision])

    def close(self):
        self.file.close()