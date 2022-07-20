import re
import sys

import redis
import requests
import argparse

# User-Agent is used to get access to needed site
# Default value of User-Agent is "python-request/2.20.0", because of it server gives 404 as a response\
# In User-Agent below I show to the server that send request from browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/75.0.3770.142 Safari/537.36 '
}


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--docker', action='store_true', help='flag shows that prog will run on docker and '
                                                              'redis connection host will be "host.docker.internal"')
    parser.add_argument('-rl', '--ratelimit', action='store_true', help='flag applies rate limits to all requests '
                                                                        'as 5 per minute')
    parser.add_argument('-s', action='store_true', help='flag for tests')
    return parser.parse_args(args)


# args = parse_args(sys.argv[1:])
if re.search('pytest', sys.argv[0]):
    args = parse_args([])
else:
    args = parse_args(sys.argv[1:])


def connect_db():
    if args.docker:
        db = redis.Redis(host='host.docker.internal', port=6379, db=0)
    else:
        db = redis.Redis(host='localhost', port=6379, db=0)

    try:
        response = db.client_list()
    except redis.ConnectionError as err:
        print('Redis connection error:\n', err)
        exit(1)
    return db


def close_db():
    return db.flushall()


db = connect_db()

session = requests.Session()
session.get("https://pro.guap.ru/user/login", headers=headers)
