from fastapi import Body, status, HTTPException, Header, APIRouter
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.responses import FileResponse
from bs4 import BeautifulSoup
from utils import session, db
from forms import AuthForm
import requests
import re
import os

limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
router = APIRouter()


def create_report(task_data: dict):
    report = open('report', 'wb')
    report.seek(4095)
    report.write(b"\0")
    report.close()
    return report


def check_auth(user_id: str):
    user_cookie = db.get(user_id)
    if user_cookie is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={'Error': 'User unauthorized'})

    cookie = requests.cookies.create_cookie(
        domain='pro.guap.ru',
        name='PHPSESSID',
        value=user_cookie.decode('utf8')
    )
    session.cookies.set_cookie(cookie)

    res = session.post('https://pro.guap.ru/get-student-tasks/', {
        'type': '0',
        'status': '0',
        'semester': '0',
        'subject': '0',
        'iduser': user_id,
        'offset': '0',
        'limit': '10'
    })

    if res.status_code == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={'Error': 'Cookie is invalid'})

    elif res.status_code != 200:
        raise HTTPException(status_code=res.status_code,
                            detail={'Error': 'Connection error'})

    return res


login_check_url = "https://pro.guap.ru/user/login_check"
right_url = "https://pro.guap.ru/inside_s"
wrong_url = "https://pro.guap.ru/forbidden"


@router.post('/authorize', name='user: authorize')
def authorization(auth_form: AuthForm = Body(..., embed=True)):
    if auth_form.user_cookie:
        cookie = requests.cookies.create_cookie(
            domain='pro.guap.ru',
            name='PHPSESSID',
            value=auth_form.user_cookie
        )
        session.cookies.set_cookie(cookie)
    else:
        session.post(login_check_url, {
            '_username': auth_form.login_pass.login,
            '_password': auth_form.login_pass.password
        })

    res = session.get(right_url)
    if res.status_code != 200:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'Error': 'Connection Error'})

    if res.url == wrong_url:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={'Error': 'Wrong login/password or dead cookie'})
    # elif res.url == right_url:

    auth_form.user_cookie = session.cookies.get_dict().get('PHPSESSID')

    soup = BeautifulSoup(res.text, 'lxml')

    script = soup.find('script')

    # https://ru.stackoverflow.com/questions/705737/
    user_ids = re.findall(r'[\'\"]user_id[\'\"]\s*\:\s*[\"]([^\"]*)[\"]',
                          script.text, flags=re.I)

    user_id = user_ids[0]
    db.set(user_id, auth_form.user_cookie)
    return {'Authorize': user_id}


@router.get('/get-task-report/', name='Task: get-report')
def get_report(task_name: str = '', task_id: str = '', user_id: str = Header('')):
    res = check_auth(user_id)
    dictionary = res.json()

    report = ''

    if task_name:
        tasks = dictionary.get('tasks')
        for task in tasks:
            if task['name'] == task_name:
                report = create_report(task)
                break
    else:
        tasks = dictionary.get('tasks')
        for task in tasks:
            if task['id'] == task_id:
                report = create_report(task)
                break

    if report:
        path = os.getcwd() + '/' + report.name
        return FileResponse(path=path, media_type='application/octet-stream',
                            filename=report.name)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'Error': 'Task not found'})


@router.get('/get-all-semesters/', name='Task: get-semesters')
def get_semesters(request: Request, user_id: str = Header('')):
    res = check_auth(user_id)
    dictionary = res.json()

    semesters = dictionary.get('dictionaries').get('semester')

    result = {
        item['id']: item['name'] for item in semesters
    }
    return result


@router.get('/get-subjects/', name='Task: get-subjects')
def get_subjects(semester_id: str = '0', semester_name: str = '', user_id: str = Header(None)):
    res = check_auth(user_id)
    dictionary = res.json()

    if semester_name:
        semesters = dictionary.get('dictionaries').get('semester')
        for sem in semesters:
            if sem['name'] == semester_name:
                semester_id = sem['id']
                break

    subjects = dictionary.get('dictionaries').get('subjects')

    result = {}
    for item in subjects:
        if item['semester'] == semester_id:
            result[item['id']] = item['text']

    return result


@router.get('/get-tasks/', name='Task: get-tasks')
def get_tasks(subject_id: str = '0', subject_name: str = '', user_id: str = Header('')):
    res = check_auth(user_id)
    dictionary = res.json()

    subject_ids = [subject_id]
    if subject_name:
        subjects = dictionary.get('dictionaries').get('subjects')
        for sub in subjects:
            if sub['text'] == subject_name:
                subject_ids.append(sub['id'])

    tasks = dictionary.get('tasks')
    result = {}
    for s_id in subject_ids:
        for item in tasks:
            if item['subject'] == s_id:
                result[item['id']] = item['name']

    return result
