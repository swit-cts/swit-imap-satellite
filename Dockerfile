FROM python:3.11-slim as requirement-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim

WORKDIR /satellite

COPY --from=requirement-stage /tmp/requirements.txt /satellite/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /satellite/requirements.txt

COPY ./ .

RUN ENV=prod

CMD ["gunicorn", "--bind", "0:80", "app.main:app", "--worker-class", "uvicorn.workers.UvicornWorker"]
