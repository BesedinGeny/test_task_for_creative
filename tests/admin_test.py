import json

import pytest
from fastapi.testclient import TestClient

from app.config.db.session import engine
from main import app

client = TestClient(app)


class TestAdmin:

    @staticmethod
    def hard_user_delete_by_email(user_sid):
        con = engine.connect()
        con.execute(f"DELETE FROM security.user_x_role WHERE user_sid = '{user_sid}'")
        con.execute(f"DELETE FROM users.user WHERE sid = '{user_sid}'")

    @pytest.fixture(autouse=True)
    def login_with_root(self):
        client.post("/api/v1/login", data={"username": "root@estesis.tech",
                                           "password": "123123"})
        yield
        client.post("/api/v1/logout")

    def test_users_list(self):
        response = client.get("/api/v1/admin/users_list")
        assert response.status_code == 200
    
    def test_get_roles(self):
        response = client.get("/api/v1/admin/get_roles")
        assert response.status_code == 200

    def test_unauthorized_get_roles(self):
        client.post("/api/v1/logout")
        response = client.get("/api/v1/admin/get_roles")
        assert response.status_code == 401

    def test_get_roles2(self):
        response = client.get("/api/v1/admin/get_roles")
        assert response.status_code == 200

    @pytest.fixture
    def new_user_dict(self):
        return {
            "email": "test@test.creation",
            "password": "testtest",
            "role": "ADMIN",
            "username": "test_user"
        }

    def test_user_create_from_admin(self, new_user_dict):
        response = client.post('/api/v1/admin/create_user', json=new_user_dict)
        assert response.status_code == 200
        sid = json.loads(response.text).get("sid")
        self.hard_user_delete_by_email(sid)

    def test_change_another_user(self, new_user_dict):
        response = client.post('/api/v1/admin/create_user', json=new_user_dict)
        sid = json.loads(response.text).get("sid")

        response = client.put(f'/api/v1/admin/{sid}', json={
            "name": "new test name"
        })
        assert response.status_code == 200
        new_name = json.loads(response.text).get("name")
        assert new_name == "new test name"
        self.hard_user_delete_by_email(sid)

    def test_lock_another_user(self, new_user_dict):
        response = client.post('/api/v1/admin/create_user', json=new_user_dict)
        sid = json.loads(response.text).get("sid")
        sid = json.loads(response.text).get("sid")

        response = client.post(f'/api/v1/admin/{sid}')
        assert response.status_code == 200
        new_name = json.loads(response.text).get("name")
        assert new_name == "new test name"
        self.hard_user_delete_by_email(sid)
