FROM python:3.10
WORKDIR /fast
COPY ./requirements.txt /fast/requirements.txt
RUN pip3 install -r requirements.txt
COPY ./main.py /fast/
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host=0.0.0.0" , "--reload" , "--port", "8000"]