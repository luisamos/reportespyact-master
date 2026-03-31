FROM python:3.12-slim-bookworm AS base

ENV APP_HOME=/usr/src/app \
    APP_DPLY=/usr/src/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR ${APP_HOME}

RUN useradd --create-home --shell /bin/bash appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS production
WORKDIR ${APP_HOME}
COPY --chown=appuser:appuser . .
USER appuser

# run server
WORKDIR ${APP_DPLY}

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:application"]