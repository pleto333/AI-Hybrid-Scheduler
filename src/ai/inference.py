import os
import pandas as pd
from common.config import MODEL_PATH, FEATURES

class AISchedulerInterface:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            try:
                import joblib
                self.model = joblib.load(MODEL_PATH)
                print(">>> AI 모델 파일 로드 성공.")
            except Exception as e:
                print(f">>> [오류] AI 모델 파일 로드 실패: {e}")
                self.model = None
        else:
            print(">>> [경고] 학습된 AI 모델 파일이 없습니다. 규칙 기반으로 작동합니다.")

    def predict(self, features):
        if self.model:
            # 경고 해결: 리스트를 이름이 있는 DataFrame으로 변환
            features_df = pd.DataFrame([features], columns=FEATURES)
            return int(self.model.predict(features_df)[0])

        # 모델 없을 때 기본 로직
        return 1 if features[0] > 70 or features[3] > 0.5 else 0
