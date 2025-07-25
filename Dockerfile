FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "report_generator.main:app", "--host", "0.0.0.0", "--port", "8000"]

#CMD ["sh", "-c", "echo '环境变量 RATE_LIMIT_ENABLED=$RATE_LIMIT_ENABLED'; uvicorn report_generator.main:app --host 0.0.0.0 --port 8000"]