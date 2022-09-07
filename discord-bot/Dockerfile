FROM python:3.9
WORKDIR /app

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

RUN apt-get update

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .