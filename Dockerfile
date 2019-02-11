FROM python:3.6-alpine

WORKDIR /app
ADD . .

RUN pip install -r requirements.txt

