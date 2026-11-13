FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first so code edits don't bust the pip layer
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app

RUN useradd --create-home campusbite
USER campusbite

EXPOSE 8000

# Load demo data (no-op if the DB already has accounts), then serve
CMD ["sh", "-c", "python -m app.demo_data && uvicorn app.server:app --host 0.0.0.0 --port 8000"]
