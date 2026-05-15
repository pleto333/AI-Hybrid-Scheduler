import sys
import os  # <--- 이게 빠져서 NameError가 난 거야!
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

# 1. 경로 문제 해결을 위해 src 폴더를 시스템 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 이제 common을 안전하게 불러올 수 있어
from common.config import DATA_PATH, MODEL_PATH


def train_model():
    # 데이터 파일이 있는지 확인
    if not os.path.exists(DATA_PATH):
        print(f"데이터 파일이 없습니다: {DATA_PATH}")
        print("먼저 src/main.py를 실행해서 데이터를 수집하세요.")
        return

    print(">>> 데이터를 읽어오는 중...")
    df = pd.read_csv(DATA_PATH)

    # 특징 벡터(X)와 정답(y) 분리
    X = df.drop('target_core', axis=1)
    y = df['target_core']

    print(">>> AI 모델 학습 시작 (Random Forest)...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # 모델 저장
    joblib.dump(model, MODEL_PATH)
    print(f">>> 모델 학습 완료 및 저장 성공!")
    print(f">>> 경로: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()