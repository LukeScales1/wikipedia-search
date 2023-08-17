FROM python:3.9

COPY requirements/ /tmp/requirements/
COPY alembic.ini /alembic.ini
COPY alembic/ /alembic/
COPY src/ /src/

RUN pip install -r /tmp/requirements/base.txt

WORKDIR /src

ENV PYTHONPATH /src

EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
