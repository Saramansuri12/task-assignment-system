from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd


class AssignmentPredictor:

    _model_cache = {}

    def __init__(self):

        self.model = None

        backend_model_path = (
            Path(__file__).resolve().parent
            / "model"
            / "assignment_model.pkl"
        )

        root_model_path = (
            Path(__file__).resolve().parents[3]
            / "ml"
            / "models"
            / "xgboost_assignment_model.pkl"
        )

        self.model_path = (
            backend_model_path
            if backend_model_path.exists()
            else root_model_path
        )

        self.load_model()

    # =========================================================
    # LOAD MODEL
    # =========================================================

    def load_model(self):

        cached_model = self._model_cache.get(
            str(self.model_path)
        )

        if cached_model is not None:
            self.model = cached_model
            return

        if not self.model_path.exists():

            print(
                f"[ML] Model not found: "
                f"{self.model_path}"
            )

            print(
                "[ML] Running in fallback scoring mode."
            )

            return

        try:

            self.model = joblib.load(
                self.model_path
            )

            self._model_cache[
                str(self.model_path)
            ] = self.model

            print(
                "[ML] Assignment model loaded."
            )

        except Exception as exc:

            print(
                f"[ML] Could not load model: {exc}"
            )

            self.model = None

    # =========================================================
    # PREDICT
    # =========================================================

    def predict(
        self,
        skill_match: float,
        experience_match: float,
        availability: float,
        reliability: float,
        features: Optional[dict] = None,
    ) -> Optional[float]:

        if self.model is None:
            return None

        try:

            if features is not None:
                input_data = pd.DataFrame([features])

                if hasattr(self.model, "predict_proba"):
                    probability = self.model.predict_proba(input_data)[0]
                    return round(float(probability[-1]) * 100, 2)

                prediction = float(self.model.predict(input_data)[0])
                if 0 <= prediction <= 1:
                    prediction *= 100

                return round(max(0, min(prediction, 100)), 2)

            numeric_features = np.array([
                [
                    skill_match,
                    experience_match,
                    availability,
                    reliability,
                ]
            ])

            # Classification model
            if hasattr(
                self.model,
                "predict_proba",
            ):

                probability = (
                    self.model
                    .predict_proba(numeric_features)[0]
                )

                # Positive class probability
                if len(probability) >= 2:

                    return round(
                        float(
                            probability[1]
                        ) * 100,
                        2,
                    )

                return round(
                    float(probability[0])
                    * 100,
                    2,
                )

            # Regression model
            prediction = self.model.predict(
                numeric_features
            )[0]

            prediction = float(prediction)

            # Normalize if model returns 0-1
            if 0 <= prediction <= 1:
                prediction *= 100

            return round(
                max(
                    0,
                    min(prediction, 100),
                ),
                2,
            )

        except Exception as exc:

            print(
                f"[ML] Prediction failed: {exc}"
            )

            return None