from app.ml.trainer import compare_models, train_model


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


def test_compare_models_uses_same_holdout_and_reports_metrics():
    dataset = [
        DatasetRecord("win prize now", "SPAM"),
        DatasetRecord("claim cash reward", "SPAM"),
        DatasetRecord("free money offer", "SPAM"),
        DatasetRecord("urgent lottery winner", "SPAM"),
        DatasetRecord("meeting tomorrow", "NOT_SPAM"),
        DatasetRecord("review project document", "NOT_SPAM"),
        DatasetRecord("lunch at noon", "NOT_SPAM"),
        DatasetRecord("submit assignment Friday", "NOT_SPAM"),
    ]
    result = compare_models(dataset)
    assert result["training_samples"] + result["test_samples"] == len(dataset)
    assert [model["model_name"] for model in result["models"]] == [
        "MultinomialNB", "LogisticRegression"
    ]
    for model in result["models"]:
        assert all(0 <= model[key] <= 1 for key in (
            "accuracy", "precision", "recall", "f1_score"
        ))
        assert len(model["confusion_matrix"]) == 2


def test_compare_models_rejects_dataset_too_small_for_stratified_split():
    dataset = [
        DatasetRecord("spam one", "SPAM"),
        DatasetRecord("ham one", "NOT_SPAM"),
    ]
    try:
        compare_models(dataset)
    except ValueError as exc:
        assert "too small" in str(exc)
    else:
        raise AssertionError("Expected validation error for an impossible split")
