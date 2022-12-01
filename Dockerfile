# FROM python:3.10-alpine
FROM python:3.8-slim

ENV FLASK_APP flasky.py
ENV FLASK_CONFIG docker

# RUN adduser -D flasky
# USER flasky

WORKDIR /home/flasky

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/requirements.txt

COPY app app
COPY migrations migrations
COPY results results
COPY tests tests
COPY uploads uploads

COPY flasky.py config.py boot.sh run_flask.sh ./
# runtime configuration
EXPOSE 5000

# ENTRYPOINT ["./boot.sh"]
ENTRYPOINT ["./run_flask.sh"]
