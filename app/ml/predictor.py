from pathlib import Path

import joblib

from app.config import Config
from app.ml.preprocessing import preprocess_text
from app.models.model_information import ModelInformation


class ActiveModelNotFoundError(Exception):
    pass


def _model_dir() -> Path:
    return Path(Config.MODEL_DIR)


def load_active_model():
    model_info = ModelInformation.query.filter_by(is_active=True).first()
    if not model_info:
        raise ActiveModelNotFoundError("Active model not found.")

    model_path = _model_dir() / f"spam_model_{model_info.model_version}.joblib"
    if not model_path.exists():
        raise ActiveModelNotFoundError(
            f"Model file not found for version {model_info.model_version}."
        )

    payload = joblib.load(model_path)
    return model_info, payload["model"], payload["vectorizer"]


def predict_email(text: str):
    model_info, model, vectorizer = load_active_model()

    processed = preprocess_text(text)
    features = vectorizer.transform([processed])
    prediction = model.predict(features)[0]

    confidence = None
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        classes = list(model.classes_)
        prediction_index = classes.index(prediction)
        confidence = float(probabilities[prediction_index])

    return {
        "result": prediction,
        "confidence": confidence,
        "model_version": model_info.model_version,
    }
