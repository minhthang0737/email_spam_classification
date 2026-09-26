def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"


def test_dataset_crud(client):
    create_response = client.post(
        "/api/dataset",
        json={"email": "Free prize waiting", "label": "SPAM"},
    )
    assert create_response.status_code == 201
    created = create_response.get_json()
    dataset_id = created["id"]

    list_response = client.get("/api/dataset")
    assert list_response.status_code == 200
    assert len(list_response.get_json()["data"]) == 1
    assert list_response.get_json()["pagination"]["total"] == 1

    update_response = client.put(
        f"/api/dataset/{dataset_id}",
        json={"label": "NOT_SPAM"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["label"] == "NOT_SPAM"

    delete_response = client.delete(f"/api/dataset/{dataset_id}")
    assert delete_response.status_code == 200


def test_dataset_seed_button_imports_gzip_idempotently(client, app, tmp_path):
    import csv
    import gzip

    seed = tmp_path / "small_seed.csv.gz"
    with gzip.open(seed, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["email", "label"])
        writer.writerow(["From: a@spam.test\nSubject: prize", "SPAM"])
        writer.writerow(["From: b@school.edu\nSubject: meeting", "NOT_SPAM"])

    app.config["DEMO_EMAIL_SEED_FILE"] = str(seed)
    first = client.post("/api/dataset/seed-large")
    assert first.status_code == 200
    assert first.get_json()["added"] == 2
    second = client.post("/api/dataset/seed-large")
    assert second.get_json()["added"] == 0
    assert second.get_json()["skipped"] == 2
    page = client.get("/api/dataset?per_page=1&page=1")
    assert len(page.get_json()["data"]) == 1
    assert page.get_json()["pagination"]["total"] == 2


def test_dataset_validation(client):
    response = client.post("/api/dataset", json={"email": "", "label": "SPAM"})
    assert response.status_code == 400

    response = client.post("/api/dataset", json={"email": "hello", "label": "INVALID"})
    assert response.status_code == 400

    response = client.put("/api/dataset/999", json={"email": "hello"})
    assert response.status_code == 404


def test_classification_feedback_adds_and_updates_dataset(client, app):
    from app import db
    from app.models.email_classification import EmailClassification
    from app.models.email_dataset import EmailDataset

    with app.app_context():
        record = EmailClassification(
            email_content="Khuyến mãi giả mạo", result="NOT_SPAM", confidence=0.6
        )
        db.session.add(record)
        db.session.commit()
        classification_id = record.id

    url = f"/api/classifications/{classification_id}/feedback"
    first = client.post(url, json={"label": " SPAM "})
    assert first.status_code == 200
    assert first.get_json()["action"] == "added"
    dataset_id = first.get_json()["dataset"]["id"]

    repeated = client.post(url, json={"label": "SPAM"})
    assert repeated.status_code == 200
    assert repeated.get_json()["action"] == "unchanged"

    corrected = client.post(url, json={"label": "NOT_SPAM"})
    assert corrected.status_code == 200
    assert corrected.get_json()["action"] == "updated"
    assert corrected.get_json()["dataset"]["id"] == dataset_id
    assert corrected.get_json()["dataset"]["label"] == "NOT_SPAM"

    with app.app_context():
        assert EmailDataset.query.count() == 1


def test_classification_feedback_validation_and_not_found(client):
    assert client.post(
        "/api/classifications/999/feedback", json={"label": "SPAM"}
    ).status_code == 404

    from app import db
    from app.models.email_classification import EmailClassification
    with client.application.app_context():
        record = EmailClassification(email_content="A message", result="SPAM")
        db.session.add(record)
        db.session.commit()
        classification_id = record.id

    assert client.post(
        f"/api/classifications/{classification_id}/feedback", json={"label": "unknown"}
    ).status_code == 400
