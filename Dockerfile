FROM python:3.12 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Debug step to check what is in .venv/bin/
RUN ls -la /app/.venv/bin/

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .
# this by fly.io generated line had to be changed to account for the different start command:
# CMD ["/app/.venv/bin/fastapi", "run"]
# to use when online:
CMD ["/app/.venv/bin/uvicorn", "scanlyticsbe.app.main:app", "--host", "0.0.0.0", "--port", "8000"]