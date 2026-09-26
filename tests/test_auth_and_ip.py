def test_login_protects_admin_pages_and_api(app):
    anonymous = app.test_client()
    page = anonymous.get("/admin/dataset")
    assert page.status_code == 302
    assert "/login" in page.headers["Location"]
    response = anonymous.post("/api/dataset", json={"email": "x", "label": "SPAM"})
    assert response.status_code == 401
    assert anonymous.get("/api/classifications").status_code == 401


def test_login_rejects_bad_password(client):
    client.post("/logout")
    response = client.post("/login", data={"username": "test-admin", "password": "wrong"})
    assert response.status_code == 200
    assert "Sai tên đăng nhập hoặc mật khẩu.".encode("utf-8") in response.data
    assert client.get("/admin/dataset").status_code == 302


def test_analyst_can_use_history_but_not_admin_apis(client):
    created = client.post("/api/users", json={
        "username": "analyst-role", "password": "analyst-password", "role": "analyst"
    })
    assert created.status_code == 201
    client.post("/logout")
    assert client.post("/login", data={
        "username": "analyst-role", "password": "analyst-password"
    }).status_code == 302
    assert client.get("/api/classifications").status_code == 200
    assert client.get("/api/dataset").status_code == 403
    assert client.post("/api/model/train").status_code == 403
    assert client.get("/admin/users").status_code == 302


def test_ip_check_and_blocklist_crud(client):
    added = client.post("/api/ip/blocklist", json={"ip": "203.0.113.9", "reason": "Demo test"})
    assert added.status_code == 201
    row = added.get_json()
    checked = client.post("/api/ip/check", json={
        "text": "Received from https://203.0.113.9:443/path, plus 192.168.1.2 and [2001:4860:4860::8888]"
    })
    data = {item["ip"]: item for item in checked.get_json()["data"]}
    assert data["203.0.113.9"]["blocked"] is True
    assert data["192.168.1.2"]["scope"] == "private/reserved"
    assert data["2001:4860:4860::8888"]["version"] == 6
    updated = client.put(f"/api/ip/blocklist/{row['id']}", json={"reason": "Updated"})
    assert updated.get_json()["reason"] == "Updated"
    assert client.delete(f"/api/ip/blocklist/{row['id']}").status_code == 200
    assert client.post("/api/ip/blocklist", json={"ip": "not-an-ip"}).status_code == 400


def test_domain_blocklist_crud_and_email_inspection(client):
    added = client.post("/api/ip/domain-blocklist", json={
        "domain": " Phish.Example.COM. ", "reason": "Reported sender"
    })
    assert added.status_code == 201
    row = added.get_json()
    assert row["domain"] == "phish.example.com"

    checked = client.post("/api/ip/check", json={
        "text": "From: support@PHISH.example.com\nVisit https://safe.example.org/path"
    })
    domains = {item["domain"]: item for item in checked.get_json()["domains"]}
    assert domains["phish.example.com"]["blocked"] is True
    assert domains["safe.example.org"]["blocked"] is False

    updated = client.put(f"/api/ip/domain-blocklist/{row['id']}", json={"reason": "Confirmed"})
    assert updated.get_json()["reason"] == "Confirmed"
    assert client.post("/api/ip/domain-blocklist", json={"domain": "bad..example"}).status_code == 400
    assert client.delete(f"/api/ip/domain-blocklist/{row['id']}").status_code == 200


def test_admin_user_lifecycle_and_last_admin_guard(client):
    created = client.post("/api/users", json={"username":"analyst1","password":"long-password","role":"analyst"})
    assert created.status_code == 201
    user_id = created.get_json()["id"]
    assert client.put(f"/api/users/{user_id}", json={"role":"admin","isActive":True}).status_code == 200
    assert client.delete(f"/api/users/{user_id}").status_code == 200
    admin_id = client.get("/api/users").get_json()["data"][0]["id"]
    assert client.put(f"/api/users/{admin_id}", json={"role":"analyst","isActive":True}).status_code == 409
