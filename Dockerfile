FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY alembic ./alembic
COPY alembic.ini ./
COPY app ./app
COPY frontend ./frontend

RUN addgroup --system taskflow \
    && adduser --system --ingroup taskflow taskflow \
    && chown -R taskflow:taskflow /app

USER taskflow

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
