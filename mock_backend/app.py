# Этот файл содержит тестовый бэкенд, который
# впоследствии будет необходимо заменить на реализованный
# другим студентом в задании №3

import http
import flask

from flask import Flask, jsonify, request
from io import BytesIO

app = Flask(__name__)

# Тестовые данные для регистрации
accounts = {
    'user1': {
        'password': '1234',
        'token': 'user1token'
    },
    'user2': {
        'password': '0000',
        'token': 'user2token'
    }
}

users_data = {
    'user1token': {  # Токен
        1: [ # Семестр
            1, 3 # Предметы в семестре
        ],
        2: [2]
    },
    'user2token': {
        2: [2, 3],
        3: [1, 2, 3]
    }
}

semesters = {
    1: 'Семестр 1',
    2: 'Семестр 2',
    3: 'Семестр 3',
}

subjects = {
    1: 'Предмет 1',
    2: 'Предмет 2',
    3: 'Предмет 3'
}


@app.post('/api/v0/auth')
def post_auth():
    username = request.form['username']
    password = request.form['password']

    account = accounts.get(username)

    if account is not None and account['password'] == password:
        return account['token']
    else:
        return flask.Response(status=http.HTTPStatus.UNAUTHORIZED)


@app.get('/api/v0/semesters')
def get_semesters():
    token = request.headers.get('Authorization')

    if token is None or token not in users_data:
        return flask.Response(status=http.HTTPStatus.UNAUTHORIZED)

    sems = {sem_id: semesters[sem_id] for sem_id in users_data[token]}

    return jsonify(sems)


@app.get('/api/v0/subjects/<int:semester_id>')
def get_subjects(semester_id):
    token = request.headers.get('Authorization')

    if token is None or token not in users_data:
        return flask.Response(status=http.HTTPStatus.UNAUTHORIZED)

    subjects_in_semester = users_data[token].get(semester_id)
    if subjects_in_semester is None:
        return flask.Response(status=http.HTTPStatus.NOT_FOUND)

    return jsonify({
        subj_id: subjects[subj_id] for subj_id in subjects_in_semester
    })


@app.get('/api/v0/reports/<int:semester_id>/<int:subject_id>')
def get_reports(semester_id, subject_id):
    token = request.headers.get('Authorization')

    if token is None or token not in users_data:
        return flask.Response(status=http.HTTPStatus.UNAUTHORIZED)

    reports = dict()

    for i in range(0, 10):
        report_id = 100 * semester_id + 10 * subject_id + i
        reports[report_id] = f'Отчёт {report_id}'

    return jsonify(reports)


@app.get('/api/v0/report/<int:semester_id>/<int:subject_id>/<int:report_id>')
def get_report(semester_id, subject_id, report_id):
    token = request.headers.get('Authorization')

    if token is None \
            or token not in users_data \
            or semester_id not in users_data[token] \
            or subject_id not in users_data[token][semester_id] \
            or report_id - (report_id % 10) != 100 * semester_id + 10 * subject_id:
        return flask.Response(status=http.HTTPStatus.UNAUTHORIZED)

    file = BytesIO(bytes(f'Отчёт {report_id} по {subjects[subject_id]} в {semesters[semester_id]}', 'utf8'))
    file.name = f'report {report_id}.txt'

    return flask.send_file(file, download_name=file.name)
