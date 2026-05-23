import csv
import os
from common.config import DATA_PATH, FEATURES, LABEL

class SystemLogger:
    def __init__(self):
        file_exists = os.path.exists(DATA_PATH)
        self.file = open(DATA_PATH, 'a', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)

        if not file_exists:
            # AI 학습에 필요한 특징(4개)과 정답(1개) 헤더만 기록
            self.writer.writerow(FEATURES + [LABEL])

    def log(self, features, decision):
        # 작업의 특징(4개)과 EDP 기반의 이상적인 정답(1개)만 기록
        self.writer.writerow(features + [decision])

    def close(self):
        self.file.close()
