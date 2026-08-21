from app.ml.trainer import train_model


class DatasetRecord:
    def __init__(self, email_content, label):
        self.email_content = email_content
        self.label = label


def test_train_model_returns_metrics():
    dataset = [
        DatasetRecord("win free money now", "SPAM"),
        DatasetRecord("claim your prize today", "SPAM"),
        DatasetRecord("meeting tomorrow at 9", "NOT_SPAM"),
        DatasetRecord("project review on Friday", "NOT_SPAM"),
        DatasetRecord("limited offer cash reward", "SPAM"),
        DatasetRecord("submit assignment by Sunday", "NOT_SPAM"),
    ]

    result = train_model(dataset)

    assert result["model_name"] == "MultinomialNB"
    assert result["model_version"]
    assert 0 <= result["accuracy"] <= 1
    assert result["model_path"]
