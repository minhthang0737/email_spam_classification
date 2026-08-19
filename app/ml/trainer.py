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

from app.ml.preprocessing import preprocess_text


MODEL_DIR = Path("saved_models")


def train_model(dataset):
    """
    Train model từ dataset.

    dataset:
        List các object có:
        - email_content
        - label
    """

    # ==========================================
    # TASK-011: Chuẩn hóa dataset
    # ==========================================

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

    # ==========================================
    # TASK-015: Train/Test Split
    # ==========================================

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels
    )

    # ==========================================
    # TASK-013: TF-IDF
    # ==========================================

    vectorizer = TfidfVectorizer()

    X_train_tfidf = vectorizer.fit_transform(X_train)

    X_test_tfidf = vectorizer.transform(X_test)

    # ==========================================
    # TASK-014: Classification Algorithm
    # ==========================================

    model = MultinomialNB()

    model.fit(
        X_train_tfidf,
        y_train
    )

    # ==========================================
    # TASK-016: Evaluation
    # ==========================================

    y_pred = model.predict(
        X_test_tfidf
    )

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        pos_label="SPAM",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        pos_label="SPAM",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        pos_label="SPAM",
        zero_division=0
    )

    confusion = confusion_matrix(
        y_test,
        y_pred,
        labels=["SPAM", "NOT_SPAM"]
    )

    # ==========================================
    # TASK-017: Save Model
    # ==========================================

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    model_version = generate_model_version()

    model_path = (
        MODEL_DIR /
        f"spam_model_{model_version}.joblib"
    )

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
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": confusion.tolist(),
        "trained_at": datetime.now(),
        "model_path": str(model_path)
    }


def generate_model_version():
    """
    Sinh version cho model.

    Ví dụ:
        20260818_191500
    """

    return datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )