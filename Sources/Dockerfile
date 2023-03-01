FROM python:3.11.1

WORKDIR /app

ENV PYTHONUNBUFFERED=1
RUN apt update && apt -y install gcc libpq-dev
COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

# RUN pip install .
EXPOSE 8000