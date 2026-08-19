from app.models.email_dataset import EmailDataset
from app.models.model_information import ModelInformation


def seed_dataset(db):
    samples = [
        ("win free money now", "SPAM"),
        ("claim your prize today", "SPAM"),
        ("meeting tomorrow at 9", "NOT_SPAM"),
        ("project review on Friday", "NOT_SPAM"),
        ("limited offer cash reward", "SPAM"),
        ("submit assignment by Sunday", "NOT_SPAM"),
    ]
    for email_content, label in samples:
        db.session.add(EmailDataset(email_content=email_content, label=label))
    db.session.commit()


def test_full_flow_train_predict_history(client, app):
    with app.app_context():
        from app import db
        seed_dataset(db)

    first_train = client.post("/api/model/train")
    assert first_train.status_code == 200
    first_version = first_train.get_json()["version"]

    predict_response = client.post(
        "/api/predict",
        json={"email": "You won a free lottery prize"},
    )
    assert predict_response.status_code == 200
    first_predict = predict_response.get_json()
    assert first_predict["modelVersion"] == first_version

    second_train = client.post("/api/model/train")
    assert second_train.status_code == 200
    second_version = second_train.get_json()["version"]
    assert second_version != first_version

    with app.app_context():
        from app import db
        active_models = ModelInformation.query.filter_by(is_active=True).all()
        assert len(active_models) == 1
        assert active_models[0].model_version == second_version

    second_predict = client.post(
        "/api/predict",
        json={"email": "Team meeting tomorrow at 9 AM"},
    ).get_json()
    assert second_predict["modelVersion"] == second_version

    history = client.get("/api/classifications").get_json()["data"]
    assert len(history) == 2
    versions = {item["modelVersion"] for item in history}
    assert first_version in versions
    assert second_version in versions


def test_classification_detail_not_found(client):
    response = client.get("/api/classifications/999")
    assert response.status_code == 404
