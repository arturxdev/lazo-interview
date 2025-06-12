FROM python:3.11-buster

RUN pip install poetry==2.1.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PYTHONUNBUFFERED=1 

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY interview ./interview
RUN chmod -R 777 /app/interview/data

RUN touch README.md

RUN poetry install

EXPOSE 3000

CMD ["poetry", "run", "gunicorn","--reload", "--bind", "0.0.0.0:3000", "interview.app:app"]