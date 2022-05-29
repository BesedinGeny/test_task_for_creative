import json
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app import crud
from app.config.db.session import engine
from main import app

client = TestClient(app)


class TestCompany:
    db: Session = Session(bind=engine, expire_on_commit=False)

    @pytest.fixture()
    def login_with_admin(self):
        client.post("/api/v1/login", data={"name": "User",
                                           "last_name": "0",
                                           "company": "test",
                                           "password": "12345"})
        yield
        client.post("/api/v1/logout")

    @pytest.fixture
    def company_name(self):
        return "test"

    @pytest.fixture
    def second_company_name(self):
        return "test2"

    @pytest.fixture
    def company(self, company_name):
        return self.db.query(models.Company).where(
            models.Company.name == company_name).first()

    @pytest.fixture
    def second_company(self, second_company_name):
        return self.db.query(models.Company).where(
            models.Company.name == second_company_name).first()

    @pytest.fixture
    def all_users_group(self, company):
        return self.db.query(models.Group).where(
            models.Group.group_sid is None,
            models.Group.company_sid == company.sid
        ).first()

    @pytest.fixture
    def second_all_users_group(self, second_company):
        return self.db.query(models.Group).where(
            models.Group.group_sid is None,
            models.Group.company_sid == second_company.sid
        ).first()

    @pytest.fixture
    def single_user_data(self, all_users_group):
        return {"name": "User",
                "last_name": "1",
                "group_sid": all_users_group.sid,
                "password": "12345"
                }

    @pytest.fixture
    def single_group_data(self, company, all_users_group):
        return {"name": "Group 1",
                "group_sid": all_users_group.sid,
                "company_sid": company.sid
                }

    @pytest.mark.parametrize(
        "user_data,expected_status,comment",
        [
            ({"name": "User",
              "last_name": "0",
              "company": "test",
              "password": "12345"
              },
             200, "Creation doesnt work"
             ),
            ({"name": "User",
              "last_name": "1",
              "company": "test",
              "password": "123456"
              },
             400, "Same company creation"
             ),
            ({"name": "New",
              "last_name": "Admin",
              "company": "test2",
              "password": "123456"
              },
             200, "Second company doesnt created"
             )
        ]
    )
    def test_register(self, user_data, expected_status, comment):
        response = client.post("/api/v1/company/register", data=user_data)
        assert response.status_code == expected_status, comment

    @pytest.mark.parametrize(
        "user_data,expected_status,comment",
        [
            ({"name": "User",
              "last_name": "1",
              "group_sid": all_users_group.sid,
              "password": "12345"
              },
             200, "Creation doesnt work"
             ),
            ({"name": "User",
              "last_name": "1",
              "group_sid": "NOT EVEN SID",
              "password": "123456"
              },
             420, "Wrong sid creation"
             ),
            ({"name": "New",
              "last_name": "User",
              "company": second_all_users_group,
              "password": "123456"
              },
             400, "Addition to external company"
             )
        ]
    )
    def test_add_new_user(self, user_data, expected_status, comment, login_with_admin):
        ex = None
        response = client.post("/api/v1/company/user", data=user_data)
        try:
            assert response.status_code == expected_status, comment
        except Exception as e:
            ex = e
        finally:
            data = json.loads(response.text)
            crud.user.remove(self.db, sid=data["sid"])
            if ex is not None: raise ex

    @pytest.mark.parametrize(
        "user_data,expected_status,comment",
        [
            ({"name": "Group 1",
              "group_sid": all_users_group.sid,
              "company_sid": company.sid
              },
             200, "Creation doesnt work"
             ),
            ({"name": "Group 1",
              "group_sid": None,
              "company_sid": company.sid
              },
             200, "Cant create same group as 'Все пользователи'"
             ),
            ({"name": "Group 1",
              "group_sid": None,
              "company_sid": second_company.sid
              },
             400, "Addition to external company"
             )
        ]
    )
    def test_add_new_group(self, user_data, expected_status, comment, login_with_admin):
        ex = None
        response = client.post("/api/v1/company/group", data=user_data)
        try:
            assert response.status_code == expected_status, comment
        except Exception as e:
            ex = e
        finally:
            data = json.loads(response.text)
            crud.group.remove(self.db, sid=data["sid"])
            if ex is not None: raise ex

    def test_get_user(self, single_user_data, login_with_admin):
        ex = None
        user_response = client.post("/api/v1/company/user", data=single_user_data)
        response = client.get("/api/v1/company/user",
                              params={"last_name": single_user_data["last_name"]})
        try:
            assert response.status_code == 200, "Get doesnt work"
        except Exception as e:
            ex = e
        finally:
            data = json.loads(user_response.text)
            crud.user.remove(self.db, sid=data["sid"])
            if ex is not None: raise ex

    def test_get_group(self, single_group_data, login_with_admin):
        ex = None
        group_response = client.post("/api/v1/company/group", data=single_group_data)
        response = client.get("/api/v1/company/group",
                              params={"name": single_group_data["name"]})
        try:
            assert response.status_code == 200, "Get doesnt work"
        except Exception as e:
            ex = e
        finally:
            data = json.loads(group_response.text)
            crud.group.remove(self.db, sid=data["sid"])
            if ex is not None: raise ex
