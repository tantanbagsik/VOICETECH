FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.docker.txt ./requirements.docker.txt
RUN pip install --no-cache-dir -r requirements.docker.txt

COPY appointment_store.py ./appointment_store.py
COPY notification_service.py ./notification_service.py
COPY api_server.py ./api_server.py

EXPOSE 8000

CMD ["python", "api_server.py"]
