FROM node:18-bullseye-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY frontend/ ./
RUN yarn build

FROM python:3.12-slim-bullseye AS app

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_PROGRESS_BAR=off

COPY pyproject.toml README.md ./
COPY src ./src
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

RUN pip install --no-cache-dir --progress-bar off -e .

EXPOSE 8000
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
