FROM python:3.8-slim

COPY . /app

WORKDIR /app
RUN python setup.py develop

ENTRYPOINT [ "python", "dino/scp.py" ]
