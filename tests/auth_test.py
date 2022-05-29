import json
import pytest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestAuth:
    @pytest.fixture
    def logout(self):
        """Log out after test"""
        yield
        client.post("/api/v1/logout")

    @pytest.mark.parametrize(
        "user_dict,expected_status,assertion_comment",
        [({"username": "root@estesis.tech", "password": "123123"},
          200, "Authorization doesn't work"),
         ({"username": "boop@wrong.email", "password": "test"},
          400, "Authorization goes anyway"),
         ({}, 422, "Empty entry")]
    )
    def test_login(self, user_dict, expected_status, assertion_comment, logout):
        response = client.post("/api/v1/login", data=user_dict)
        assert response.status_code == expected_status, assertion_comment

    @pytest.mark.parametrize(
        "email,password,expected_status,assertion_comment",
        [
            ("root@estesis.tech", "123123", 200, "Tokens weren't saved"),
            ("boop@wrong.email", "test", 401, "Found unauthorized user")
         ]
    )
    def test_me(self, email, password, expected_status, assertion_comment, logout):
        client.post("/api/v1/login", data={"username": email, "password": password})

        response = client.get("/api/v1/users/me")
        assert response.status_code == expected_status, assertion_comment
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data["email"] == email
