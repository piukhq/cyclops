FROM ghcr.io/binkhq/python:3.10 as build

WORKDIR /src

RUN apt update && apt -y install git
RUN pip install poetry==1.2.0b3
RUN pip install dynamic-versioning-plugin
RUN poetry config virtualenvs.create flase

ADD . .

RUN poetry build

FROM ghcr.io/binkhq/python:3.10

ARG wheel=cyclops-*-py3-none-any.whl

WORKDIR /app
COPY --from=build /src/dist/$wheel .
COPY --from=build /src/asgi.py .
COPY --from=build /src/fe2/ ./fe2/
RUN pip install $wheel && rm $wheel


ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "uvicorn", "asgi:app", "--host", "0.0.0.0", "--port", "6502" ]
