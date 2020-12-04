FROM python:3.8-slim

COPY . /app

WORKDIR /app
RUN python setup.py install

ENTRYPOINT [ "python", "dino/scp.py" ]
