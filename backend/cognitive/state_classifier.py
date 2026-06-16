"""State Classifier — ML-backed classification of mental state vectors.

Uses a lightweight scikit-learn model for the MVP; designed to be
swapped for a fine-tuned transformer later.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder

from backend.sensing.mental_state import CognitiveState, MentalState
from backend.utils.logger import log


@dataclass
class ClassificationResult:
    predicted_state: CognitiveState
    confidence: float
    probabilities: dict[str, float]


class StateClassifier:
    """Trainable cognitive-state classifier wrapping scikit-learn."""

    def __init__(self) -> None:
        self._model: GradientBoostingClassifier | None = None
        self._label_encoder = LabelEncoder()
        self._is_trained = False

    def train(
        self,
        feature_vectors: list[list[float]],
        labels: list[str],
    ) -> dict[str, Any]:
        """Train on historical (fused-vector, label) pairs."""
        X = np.array(feature_vectors)
        y = self._label_encoder.fit_transform(labels)
        self._model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
        )
        self._model.fit(X, y)
        self._is_trained = True
        accuracy = float(self._model.score(X, y))
        log.info("classifier.trained", samples=len(labels), accuracy=accuracy)
        return {"accuracy": accuracy, "samples": len(labels)}

    def predict(self, mental_state: MentalState) -> ClassificationResult:
        """Predict a refined state given a fused ``MentalState``."""
        if not self._is_trained or self._model is None:
            return ClassificationResult(
                predicted_state=mental_state.state,
                confidence=mental_state.confidence,
                probabilities={mental_state.state.value: mental_state.confidence},
            )

        vec = np.array(mental_state.raw_vector).reshape(1, -1)
        proba = self._model.predict_proba(vec)[0]
        class_names = self._label_encoder.inverse_transform(
            range(len(proba))
        )
        prob_map = {str(c): float(p) for c, p in zip(class_names, proba)}
        best_idx = int(np.argmax(proba))
        best_label = str(class_names[best_idx])

        result = ClassificationResult(
            predicted_state=CognitiveState(best_label),
            confidence=float(proba[best_idx]),
            probabilities=prob_map,
        )
        log.debug("classifier.predict", state=best_label, conf=result.confidence)
        return result

    def save(self, path: str | Path) -> None:
        import joblib

        joblib.dump(
            {"model": self._model, "encoder": self._label_encoder},
            str(path),
        )

    def load(self, path: str | Path) -> None:
        import joblib

        data = joblib.load(str(path))
        self._model = data["model"]
        self._label_encoder = data["encoder"]
        self._is_trained = True
        log.info("classifier.loaded", path=str(path))
