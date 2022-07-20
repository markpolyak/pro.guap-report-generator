FROM python:3.10

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

ENV PATH /home/${USERNAME}/.local/bin:${PATH}

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY ./app /code/app

CMD ["python", "./app/main.py", "--docker"]