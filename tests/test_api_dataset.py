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

    update_response = client.put(
        f"/api/dataset/{dataset_id}",
        json={"label": "NOT_SPAM"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["label"] == "NOT_SPAM"

    delete_response = client.delete(f"/api/dataset/{dataset_id}")
    assert delete_response.status_code == 200


def test_dataset_validation(client):
    response = client.post("/api/dataset", json={"email": "", "label": "SPAM"})
    assert response.status_code == 400

    response = client.post("/api/dataset", json={"email": "hello", "label": "INVALID"})
    assert response.status_code == 400

    response = client.put("/api/dataset/999", json={"email": "hello"})
    assert response.status_code == 404
