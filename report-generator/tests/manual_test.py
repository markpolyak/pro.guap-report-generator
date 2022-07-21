from unittest import TestCase
import getpass
import json
from fastapi.testclient import TestClient

from app.main import app

user_id = ''
client = TestClient(app)


class TestAuthorization(TestCase):

    def test_authorization(self):
        login = input("login: ")
        password = getpass.getpass(prompt="password: ")
        body = {
            "auth_form": {
                "login_pass": {
                    "login": login,
                    "password": password
                }
            }
        }
        response = client.post("http://127.0.0.1:8080/authorize",
                                 data=json.dumps(body), headers={"Content-Type": "application/json"})
        print('status_code: ', response.status_code)
        assert response.status_code == 200
        print(response.json())

    def test_cookie_authorization(self):
        global user_id
        cookie = input('cookie: ')
        body = {"auth_form": {
            "user_cookie": cookie
        }
        }
        response = client.post("http://127.0.0.1:8080/authorize",
                                 data=json.dumps(body), headers={"Content-Type": "application/json"})
        assert response.status_code == 200
        print(response.json())
        user_id = response.json().get('Authorize')

    def test_get_semesters(self):
        header = {'accept': 'application/json',
                  'user-id': user_id}
        response = client.get("http://127.0.0.1:8080/get-all-semesters/", headers=header)
        assert response.status_code == 200

    def test_get_subjects(self):
        print('Test get-subjects')
        header = {'accept': 'application/json',
                  'user-id': user_id}
        params = {'semester_id': 19}
        response = client.get("http://127.0.0.1:8080/get-all-semesters/", headers=header, params=params)
        assert response.status_code == 200
        params = {'semester_name': '2021/2022 весенний'}
        response = client.get("http://127.0.0.1:8080/get-all-semesters/", headers=header, params=params)
        assert response.status_code == 200

    def test_get_tasks(self):
        print('Test get-tasks')
        header = {'accept': 'application/json',
                  'user-id': user_id}
        params = {'subject_id': 2489856}
        response = client.get("http://127.0.0.1:8080/get-tasks/", headers=header, params=params)
        assert response.status_code == 200
        params = {'subject_name': 'Операционные системы'}
        response = client.get("http://127.0.0.1:8080/get-tasks/", headers=header, params=params)
        assert response.status_code == 200

    def test_get_report(self):
        print('Test get-report')
        header = {'accept': 'application/json',
                  'user-id': user_id}
        params = {'task_id': 99880}
        response = client.get("http://127.0.0.1:8080/get-task-report/", headers=header, params=params, stream=True)
        assert response.status_code == 200
        if response.status_code == 200:
            assert response.headers['content-length'] == '4096'
        params = {'task_name': 'ЛР1. Знакомство с системой контроля версий git и сервисом GitHub'}
        response = client.get("http://127.0.0.1:8080/get-task-report/", headers=header, params=params)
        assert response.status_code == 200
        if response.status_code == 200:
            assert response.headers['content-length'] == '4096'
