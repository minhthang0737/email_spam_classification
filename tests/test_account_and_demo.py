import csv
import gzip

from app import db
from app.models.email_classification import EmailClassification
from app.models.email_dataset import EmailDataset
from app.models.ip_reputation import BlockedDomain, BlockedIP
from app.models.model_information import ModelInformation
from app.models.user import User


def test_profile_and_password_change(client, app):
    profile = client.put("/api/account/profile", json={
        "displayName": "Nguyễn Minh", "email": "MINH@example.com"
    })
    assert profile.status_code == 200
    assert profile.get_json()["user"]["displayName"] == "Nguyễn Minh"
    assert profile.get_json()["user"]["email"] == "minh@example.com"
    assert client.put("/api/account/profile", json={"email": "bad-address"}).status_code == 400

    assert client.put("/api/account/password", json={
        "currentPassword": "wrong-password", "newPassword": "new-password-123"
    }).status_code == 400
    changed = client.put("/api/account/password", json={
        "currentPassword": "test-password-123", "newPassword": "new-password-123"
    })
    assert changed.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username="test-admin").first()
        assert user.check_password("new-password-123")


def test_settings_page_available_to_signed_in_user(client):
    response = client.get("/settings")
    assert response.status_code == 200
    assert b"profile-form" in response.data
    assert b"password-form" in response.data
    assert b"seed-all-demo-btn" in response.data


def test_all_table_demo_seed_is_idempotent(client, app, tmp_path):
    seed = tmp_path / "demo.csv.gz"
    with gzip.open(seed, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["email", "label"])
        writer.writerow(["From: a@spam.test\nSubject: prize", "SPAM"])
        writer.writerow(["From: b@school.edu\nSubject: meeting", "NOT_SPAM"])
    app.config["DEMO_EMAIL_SEED_FILE"] = str(seed)

    first = client.post("/api/demo/seed")
    assert first.status_code == 200
    added = first.get_json()["added"]
    assert added == {"dataset": 2, "history": 100, "users": 1,
                     "ipBlocklist": 2, "domainBlocklist": 2, "modelInformation": 1}
    second = client.post("/api/demo/seed")
    assert second.status_code == 200
    assert all(value == 0 for value in second.get_json()["added"].values())

    with app.app_context():
        assert EmailDataset.query.count() == 2
        assert EmailClassification.query.count() == 100
        assert User.query.filter_by(username="demo.analyst").count() == 1
        assert BlockedIP.query.count() == 2
        assert BlockedDomain.query.count() == 2
        assert ModelInformation.query.filter_by(model_version="DEMO-SEED-NOT-TRAINED").count() == 1
