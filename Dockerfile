FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.3.2

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root

COPY start.sh ./start.sh
COPY . .

EXPOSE 8000

CMD ["sh", "/app/start.sh"]
