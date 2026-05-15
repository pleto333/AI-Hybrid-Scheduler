import joblib
import os
import pandas as pd  # <--- 추가
from common.config import MODEL_PATH, FEATURES  # <--- FEATURES 추가


class AISchedulerInterface:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print(">>> AI 모델 로드 완료.")
            except:
                print(">>> 모델 파일 로드 실패.")
        else:
            print(">>> AI 모델 없음. 규칙 기반 작동.")

    def predict(self, features):
        if self.model:
            # 경고 해결: 리스트를 이름이 있는 DataFrame으로 변환
            features_df = pd.DataFrame([features], columns=FEATURES)
            return int(self.model.predict(features_df)[0])

        # 모델 없을 때 기본 로직
        return 1 if features[0] > 70 or features[3] > 0.5 else 0