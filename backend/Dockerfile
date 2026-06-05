FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r ./backend/requirements.txt -r ./requirements.txt || true

COPY backend/ ./backend/
COPY src/ ./src/

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
