import pandas as pd
import joblib
import os
import sys

# 경로 문제 해결
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import DATA_PATH, MODEL_PATH, FEATURES, LABEL
from sklearn.ensemble import RandomForestClassifier


def train_model():
    if not os.path.exists(DATA_PATH):
        print(f"데이터 파일이 없습니다: {DATA_PATH}")
        print("먼저 src/main.py를 실행해서 데이터를 수집하세요.")
        return

    print(">>> 데이터를 읽어오는 중...")
    df = pd.read_csv(DATA_PATH)

    # --- 데이터 클리닝 로직 추가 ---
    # 1. 학습에 필요한 컬럼에 빈칸(NaN)이 있는지 확인
    initial_rows = len(df)
    df.dropna(subset=FEATURES + [LABEL], inplace=True)
    cleaned_rows = len(df)

    if initial_rows > cleaned_rows:
        print(f">>> 경고: 데이터에서 {initial_rows - cleaned_rows}개의 부적합한 행(NaN 포함)을 제거했습니다.")

    if df.empty:
        print(">>> 오류: 데이터를 정제한 후 학습할 데이터가 남아있지 않습니다.")
        return
    # --------------------------------

    # AI가 학습할 특징(X)과 정답(y)을 명확히 분리
    X = df[FEATURES]
    y = df[LABEL]

    print(">>> AI 모델 학습 시작 (Random Forest)...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print(f">>> 모델 학습 완료 및 저장 성공!")
    print(f">>> 경로: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
