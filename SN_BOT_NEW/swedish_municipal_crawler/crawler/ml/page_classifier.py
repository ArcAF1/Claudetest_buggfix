from __future__ import annotations
import os
from pathlib import Path
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib


class PageClassifier:
    """Lightweight text classifier to detect pages relevant to Phase 1 data."""

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or str(Path(__file__).with_suffix('.joblib'))
        if Path(self.model_path).exists():
            self.pipeline: Pipeline = joblib.load(self.model_path)
        else:
            # Initialize empty pipeline; caller must train() before using
            self.pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(stop_words="swedish", max_features=5000)),
                ("logreg", LogisticRegression(max_iter=1000)),
            ])

    def train(self, texts: List[str], labels: List[int]) -> None:
        """Train model from scratch and save to disk."""
        self.pipeline.fit(texts, labels)
        joblib.dump(self.pipeline, self.model_path)

    def predict_proba(self, texts: List[str]) -> List[float]:
        """Return probability that each text is relevant."""
        if not hasattr(self.pipeline, "predict_proba"):
            raise RuntimeError("Model is not trained")
        return self.pipeline.predict_proba(texts)[:, 1].tolist()

    def is_relevant(self, text: str, threshold: float = 0.5) -> bool:
        """Return True if text likely contains municipal fee information."""
        prob = self.predict_proba([text])[0]
        return prob >= threshold
