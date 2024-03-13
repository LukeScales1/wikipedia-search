FROM python:3.12

# Install PostgreSQL
RUN apt-get update && apt-get install -y postgresql

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements/ /tmp/requirements/
COPY alembic.ini /alembic.ini
COPY alembic/ /alembic/
COPY src/ /src/
COPY pyproject.toml /pyproject.toml
COPY setup.cfg /setup.cfg

RUN pip install -r /tmp/requirements/test.txt
RUN pip install -e .

WORKDIR /src

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
