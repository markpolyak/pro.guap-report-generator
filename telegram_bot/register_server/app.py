import httpx

from flask import Flask, request, render_template
from configparser import ConfigParser

app = Flask(__name__)

config = ConfigParser()
config.read('config.ini')

backend_url = config['backend']['base_url']


@app.get('/register')
def register_get():
    return render_template('register.html')


@app.post('/register')
def register_post():
    username = request.form['username']
    password = request.form['password']

    response = httpx.post(backend_url + '/auth', data={'username': username, 'password': password})

    if response.status_code == 200:
        token = response.content.decode('utf8')
        return render_template('registered.html', token=token)
    else:
        return render_template('error.html')
