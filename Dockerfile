FROM python:3.12.1-slim as base

ENV PYTHONUNBUFFERED=1

# Build stage
FROM base as builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

WORKDIR /app

COPY pyproject.toml poetry.lock migrate.py alembic.ini seenspot.json /app/
COPY /alembic /app/alembic
COPY app /app/app

RUN . /venv/bin/activate && poetry install --no-dev

# Final stage
FROM base as final

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app

RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser
USER appuser

WORKDIR /app

ENV PORT=8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]