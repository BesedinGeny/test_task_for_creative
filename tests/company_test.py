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
              "group_sid": "NOT EVEN SID",
              "password": "123456"
              },
             420, "Wrong sid creation"
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

    def test_add_new_group(self, single_group_data, login_with_admin):
        ex = None
        response = client.post("/api/v1/company/group", data=single_group_data)
        try:
            assert response.status_code == 200, "Creation doesnt work"
        except Exception as e:
            ex = e
        finally:
            data = json.loads(response.text)
            crud.group.remove(self.db, sid=data["sid"])
            if ex is not None: raise ex

    def test_add_new_user_single(self, single_user_data, login_with_admin):
        ex = None
        response = client.post("/api/v1/company/user", data=single_user_data)
        try:
            assert response.status_code == 200, "Creation doesnt work"
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

    def test_branch(self, single_user_data, single_group_data, login_with_admin):
        response = client.post("/api/v1/company/group", data=single_group_data)
        first_group_data = json.loads(response.text)
        first_group_sid = first_group_data["sid"]

        third_group_data = single_group_data.copy()
        third_group_data["name"] = "Group 3"
        response = client.post("/api/v1/company/group", data=single_group_data)
        third_group_data = json.loads(response.text)
        third_group_sid = third_group_data["sid"]

        single_user_data["group_sid"] = third_group_sid
        client.post("/api/v1/company/user", data=single_user_data)

        second_group_data = single_group_data.copy()
        second_group_data["name"] = "Group 2"
        second_group_data["group_sid"] = first_group_sid
        client.post("/api/v1/company/group", data=second_group_data)

        fourth_group_data = single_group_data.copy()
        fourth_group_data["name"] = "Group 4"
        fourth_group_data["group_sid"] = third_group_sid
        response = client.post("/api/v1/company/group", data=fourth_group_data)
        fourth_group_data = json.loads(response.text)
        fourth_group_sid = fourth_group_data["sid"]

        user_2_data = single_user_data.copy()
        user_2_data["last_name"] = "2"
        user_2_data["group_sid"] = fourth_group_sid
        client.post("/api/v1/company/group", data=user_2_data)
        user_3_data = user_2_data.copy()
        user_3_data["last_name"] = "3"
        client.post("/api/v1/company/group", data=user_3_data)

        # Создали структуру, теперь сделаем 2 теста на ней

        response = client.get("/api/v1/company/catalogue", params={"name": "Все пользователи"})
        data = json.loads(response.text)
        assert len(data) == 9, "неверное число отображаемых объектов"

        response = client.get("/api/v1/company/catalogue", params={"name": "Group 3"})
        data = json.loads(response.text)
        assert len(data) == 5, "неверное число отображаемых объектов"
