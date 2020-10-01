FROM binkhq/python:3.8

WORKDIR /app
ADD . .

RUN pip install --no-cache-dir pipenv==2020.8.13 && \
    pipenv install --system --deploy --ignore-pipfile

CMD ["python", "cyclops.py"]
