from app.models.email_dataset import EmailDataset


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


def test_train_and_get_model(client, app):
    with app.app_context():
        from app import db
        seed_dataset(db)

    train_response = client.post("/api/model/train")
    assert train_response.status_code == 200
    train_data = train_response.get_json()
    assert train_data["message"] == "Model trained successfully"
    assert train_data["accuracy"] is not None

    model_response = client.get("/api/model")
    assert model_response.status_code == 200
    model_data = model_response.get_json()
    assert model_data["model"] == "MultinomialNB"
    assert model_data["version"] == train_data["version"]


def test_train_with_insufficient_dataset(client, app):
    with app.app_context():
        from app import db
        db.session.add(EmailDataset(email_content="only one", label="SPAM"))
        db.session.commit()

    response = client.post("/api/model/train")
    assert response.status_code == 400
