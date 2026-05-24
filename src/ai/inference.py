import os
import pickle

from common.config import MODEL_PATH


class AISchedulerInterface:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as file:
                    self.model = pickle.load(file)
                print(">>> AI model loaded.")
            except Exception as e:
                print(f">>> [error] Failed to load AI model: {e}")
                self.model = None
        else:
            print(">>> [warning] AI model file not found. Falling back to rule-based scheduling.")

    def predict(self, features):
        if self.model:
            return int(self.model.predict([features])[0])

        return 1 if features[0] > 70 or features[3] > 0.5 else 0
