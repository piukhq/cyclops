FROM python:3.8-alpine

WORKDIR /app
ADD . .

RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile

CMD ["/usr/local/bin/python", "cyclops.py"]
