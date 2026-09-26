from datetime import datetime
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression

from app.config import Config
from app.ml.preprocessing import preprocess_text


def _model_dir() -> Path:
    return Path(Config.MODEL_DIR)


def _prepare_dataset(dataset):
    texts = []
    labels = []

    for record in dataset:

        if not record.email_content:
            continue

        if record.label not in ["SPAM", "NOT_SPAM"]:
            continue

        texts.append(
            preprocess_text(record.email_content)
        )

        labels.append(record.label)

    if len(texts) < 2:
        raise ValueError(
            "Dataset must contain at least 2 valid records."
        )

    if len(set(labels)) < 2:
        raise ValueError(
            "Dataset must contain both SPAM and NOT_SPAM labels."
        )

    return texts, labels


def _split_and_vectorize(texts, labels):
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            texts,
            labels,
            test_size=0.2,
            random_state=42,
            stratify=labels
        )
    except ValueError as exc:
        raise ValueError(
            "Dataset is too small for a stratified 80/20 split; add examples "
            "for both labels and retry."
        ) from exc

    vectorizer = TfidfVectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    return X_train_tfidf, X_test_tfidf, y_train, y_test, vectorizer


def _evaluate(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(
            y_test, y_pred, pos_label="SPAM", zero_division=0
        ),
        "recall": recall_score(
            y_test, y_pred, pos_label="SPAM", zero_division=0
        ),
        "f1_score": f1_score(
            y_test, y_pred, pos_label="SPAM", zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            y_test, y_pred, labels=["SPAM", "NOT_SPAM"]
        ).tolist(),
    }


def compare_models(dataset):
    """Evaluate the baseline and Logistic Regression on the same holdout."""
    texts, labels = _prepare_dataset(dataset)
    X_train, X_test, y_train, y_test, _ = _split_and_vectorize(texts, labels)

    results = []
    for name, model in (
        ("MultinomialNB", MultinomialNB()),
        ("LogisticRegression", LogisticRegression(max_iter=1000, random_state=42)),
    ):
        metrics = _evaluate(model, X_train, X_test, y_train, y_test)
        results.append({"model_name": name, **metrics})

    return {
        "evaluation_method": "Stratified 80/20 holdout (random_state=42)",
        "training_samples": len(y_train),
        "test_samples": len(y_test),
        "models": results,
    }


def train_model(dataset):
    """Train and persist the MultinomialNB model used for predictions."""
    texts, labels = _prepare_dataset(dataset)
    X_train, X_test, y_train, y_test, vectorizer = _split_and_vectorize(texts, labels)
    model = MultinomialNB()
    metrics = _evaluate(model, X_train, X_test, y_train, y_test)

    # ==========================================
    # TASK-017: Save Model
    # ==========================================

    model_dir = _model_dir()
    model_dir.mkdir(parents=True, exist_ok=True)

    model_version = generate_model_version()

    model_path = model_dir / f"spam_model_{model_version}.joblib"

    joblib.dump(
        {
            "model": model,
            "vectorizer": vectorizer,
            "version": model_version
        },
        model_path
    )

    return {
        "model_name": "MultinomialNB",
        "model_version": model_version,
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "confusion_matrix": metrics["confusion_matrix"],
        "trained_at": datetime.now(),
        "model_path": str(model_path)
    }


def generate_model_version():
    """
    Sinh version cho model.

    Ví dụ:
        20260818_191500
    """

    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
