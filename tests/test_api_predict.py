from app.models.email_dataset import EmailDataset


def seed_and_train(client, app):
    with app.app_context():
        from app import db
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

    client.post("/api/model/train")


def test_predict_and_history(client, app):
    seed_and_train(client, app)

    predict_response = client.post(
        "/api/predict",
        json={"email": "Congratulations you won free money"},
    )
    assert predict_response.status_code == 200
    predict_data = predict_response.get_json()
    assert predict_data["result"] in ("SPAM", "NOT_SPAM")
    classification_id = predict_data["id"]

    list_response = client.get("/api/classifications")
    assert list_response.status_code == 200
    records = list_response.get_json()["data"]
    assert len(records) == 1
    assert records[0]["id"] == classification_id

    detail_response = client.get(f"/api/classifications/{classification_id}")
    assert detail_response.status_code == 200

    delete_response = client.delete(f"/api/classifications/{classification_id}")
    assert delete_response.status_code == 200


def test_predict_empty_email(client):
    response = client.post("/api/predict", json={"email": "   "})
    assert response.status_code == 400


def test_predict_without_model(client):
    response = client.post("/api/predict", json={"email": "hello world"})
    assert response.status_code == 404
