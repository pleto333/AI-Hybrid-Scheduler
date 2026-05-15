import os  # <--- 반드시 'os'여야 합니다.

# 코어 및 데이터 관련 상수
E_CORE = 0
P_CORE = 1
FEATURES = ['cpu_load', 'mem_access_freq', 'io_wait_time', 'fp_instruction_ratio']
LABEL = 'target_core'

# 경로 설정
# 파이썬 기본 모듈인 os를 사용하여 경로를 계산합니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "workload_log.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "scheduler_model.pkl")

# 디렉토리 자동 생성
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)