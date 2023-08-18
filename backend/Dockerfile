FROM python:3.11

COPY requirements/ /tmp/requirements/
COPY alembic.ini /alembic.ini
COPY alembic/ /alembic/
COPY src/ /src/

RUN pip install -r /tmp/requirements/base.txt

WORKDIR /src

ENV PYTHONPATH /src

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
