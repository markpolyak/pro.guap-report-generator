import json
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)
class TestWrongParameters:
    def test_authorization_with_wrong_parameters(self):
        body = {
            "auth_form": {
                "login_pass": {
                    "login": 'invalidLogin',
                    "password": 'invalidPassword'
                }
            }
        }
        response = client.post("http://127.0.0.1/authorize",
                                 data=json.dumps(body),
                                 headers={"Content-Type": "application/json"},
                                 )
        assert response.status_code == 401
        print(response.json())
        body = {
            "auth_form": {
                "login_pass": {
                    "login": 'invalidLogin',
                    "password": 'invalidPassword'
                },
                "user_cookie": "definitelyInvalidCookie"
            }
        }
        response = client.post("http://127.0.0.1/authorize",
                                 data=json.dumps(body), headers={"Content-Type": "application/json"})
        assert response.status_code == 401

        print(response.json())

        body = {
            "login_pass": {
                "login": 'invalidLogin',
                "password": 'invalidPassword'
            }
        }
        response = client.post("http://127.0.0.1/authorize",
                                 data=json.dumps(body), headers={"Content-Type": "application/json"})
        assert response.status_code == 422
        print(response.json())
        body = {}
        response = client.post("http://127.0.0.1/authorize",
                                 data=json.dumps(body), headers={"Content-Type": "application/json"})
        assert response.status_code == 422
        print(response.json())

    def test_unauthorized_get_semesters(self):
        header = {'accept': 'application/json',
                  'user-id': 'no user id'}
        response = client.get("http://127.0.0.1/get-all-semesters/", headers=header)
        assert response.status_code == 401
        print(response.json())

    def test_unauthorized_get_subjects(self):
        header = {'accept': 'application/json',
                  'user-id': 'no user id'}
        params = {'semester_id': 19}
        response = client.get("http://127.0.0.1/get-all-semesters/", headers=header, params=params)
        assert response.status_code == 401
        print(response.json())
        params = {'semester_name': '2021/2022 весенний'}
        response = client.get("http://127.0.0.1/get-all-semesters/", headers=header, params=params)
        assert response.status_code == 401
        print(response.json())

    def test_unauthorized_get_tasks(self):
        header = {'accept': 'application/json',
                  'user-id': 'no user id'}
        params = {'subject_id': 2489856}
        response = client.get("http://127.0.0.1/get-tasks/", headers=header, params=params)
        assert response.status_code == 401
        print(response.json())
        params = {'subject_name': 'Операционные системы'}
        response = client.get("http://127.0.0.1/get-tasks/", headers=header, params=params)
        assert response.status_code == 401
        print(response.json())

    def test_unauthorized_get_report(self):
        header = {'accept': 'application/json',
                  'user-id': 'no user id'}
        params = {'task_id': 99880}
        response = client.get("http://127.0.0.1/get-task-report/", headers=header, params=params)
        assert response.status_code == 401
        print(response.json())
        params = {'task_name': 'ЛР1. Знакомство с системой контроля версий git и сервисом GitHub'}
        response = client.get("http://127.0.0.1/get-task-report/", headers=header, params=params)
        assert response.status_code == 401
        print(response.json())
