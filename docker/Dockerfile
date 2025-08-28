FROM python:3.12-slim

ARG PORT

WORKDIR /app

RUN apt-get update && apt-get install -y dos2unix && apt-get clean

COPY ../requirements.txt /app/
RUN pip install -r requirements.txt

COPY ../app /app/app
COPY ../alembic.ini /app/
COPY ../alembic /app/alembic

CMD alembic upgrade head && fastapi run app/main.py --port $PORT