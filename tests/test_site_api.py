import pytest


def test_tasks_requires_auth(client):
    response = client.get("/tasks")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authorized"}


def test_tasks_returns_tasks_for_authorized_user(monkeypatch, client):
    async def fake_get_tasks_with_steps(user_id):
        return [
            {
                "id": 1,
                "title": "Test task",
                "is_done": False,
                "total_minutes": 15,
                "steps": [
                    {"title": "Step 1", "description": "Desc", "minutes": 15, "is_done": False}
                ]
            }
        ]

    monkeypatch.setattr("site_F.main.get_tasks_with_steps", fake_get_tasks_with_steps)

    client.cookies.set("user_id", "1")
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "Test task",
            "is_done": False,
            "total_minutes": 15,
            "steps": [
                {"title": "Step 1", "description": "Desc", "minutes": 15, "is_done": False}
            ]
        }
    ]


def test_done_endpoint_requires_auth(client):
    response = client.post("/done/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authorized"}


def test_done_endpoint_forbidden(monkeypatch, client):
    async def fake_get_task_owner(task_id):
        return 99

    monkeypatch.setattr("site_F.main.get_task_owner", fake_get_task_owner)

    client.cookies.set("user_id", "1")
    response = client.post("/done/1")

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden: Task does not belong to this user"}


def test_done_endpoint_success(monkeypatch, client):
    called = []

    async def fake_get_task_owner(task_id):
        return 1

    async def fake_mark_done(task_id):
        called.append(task_id)

    monkeypatch.setattr("site_F.main.get_task_owner", fake_get_task_owner)
    monkeypatch.setattr("site_F.main.mark_done", fake_mark_done)

    client.cookies.set("user_id", "1")
    response = client.post("/done/1")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert called == [1]


def test_delete_endpoint_requires_auth(client):
    response = client.delete("/delete/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authorized"}


def test_delete_endpoint_forbidden(monkeypatch, client):
    async def fake_get_task_owner(task_id):
        return 99

    monkeypatch.setattr("site_F.main.get_task_owner", fake_get_task_owner)

    client.cookies.set("user_id", "1")
    response = client.delete("/delete/1")

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden: Task does not belong to this user"}


def test_delete_endpoint_success(monkeypatch, client):
    called = []

    async def fake_get_task_owner(task_id):
        return 1

    async def fake_delete_task(task_id):
        called.append(task_id)

    monkeypatch.setattr("site_F.main.get_task_owner", fake_get_task_owner)
    monkeypatch.setattr("site_F.main.delete_task", fake_delete_task)

    client.cookies.set("user_id", "1")
    response = client.delete("/delete/1")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert called == [1]


def test_auth_endpoint_sets_cookie(monkeypatch, client):
    async def fake_get_user_by_token(token):
        return 7

    monkeypatch.setattr("site_F.main.get_user_by_token", fake_get_user_by_token)

    response = client.get("/auth/testtoken", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/dashboard"
    assert response.cookies.get("user_id") == "7"


def test_auth_endpoint_invalid_token(monkeypatch, client):
    async def fake_get_user_by_token(token):
        return None

    monkeypatch.setattr("site_F.main.get_user_by_token", fake_get_user_by_token)

    response = client.get("/auth/badtoken")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_dashboard_redirects_when_not_logged_in(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/login"


def test_settings_redirects_when_not_logged_in(client):
    response = client.get("/settings", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/login"
