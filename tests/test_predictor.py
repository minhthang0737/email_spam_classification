import pytest

from app import db
from app.ml.predictor import ActiveModelNotFoundError, predict_email
from app.ml.trainer import train_model
from app.models.email_dataset import EmailDataset
from app.services.model_service import save_model_information


class DatasetRecord:
    def __init__(self, email_content, label):
        self.email_content = email_content
        self.label = label


@pytest.fixture
def trained_model(app):
    dataset = [
        DatasetRecord("win free money now", "SPAM"),
        DatasetRecord("claim your prize today", "SPAM"),
        DatasetRecord("meeting tomorrow at 9", "NOT_SPAM"),
        DatasetRecord("project review on Friday", "NOT_SPAM"),
        DatasetRecord("limited offer cash reward", "SPAM"),
        DatasetRecord("submit assignment by Sunday", "NOT_SPAM"),
    ]
    result = train_model(dataset)
    save_model_information(
        model_name=result["model_name"],
        model_version=result["model_version"],
        accuracy=result["accuracy"],
        precision_score=result["precision"],
        recall_score=result["recall"],
        f1_score=result["f1_score"],
    )
    return result


def test_predict_email_after_training(app, trained_model):
    prediction = predict_email("You won free money click now")
    assert prediction["result"] in ("SPAM", "NOT_SPAM")
    assert prediction["model_version"] == trained_model["model_version"]
    assert prediction["confidence"] is not None


def test_predict_without_active_model_raises(app):
    with pytest.raises(ActiveModelNotFoundError):
        predict_email("hello")
