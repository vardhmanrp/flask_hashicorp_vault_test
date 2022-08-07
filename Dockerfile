FROM python:3.6

LABEL maintainer "vardhman patil <vardhmanrp@gmail.com>"

RUN apt-get update

RUN mkdir /app

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV VAULT_ADD=http://localhost:8200
ENV VAULT_TOKEN=""
ENV FLASK_APP="app"
ENV FLASK_DEBUG=true

EXPOSE 5000
