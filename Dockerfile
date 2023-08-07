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

EXPOSE 8000

RUN useradd flasky
RUN usermod -u 1001380000 flasky
RUN chown -R flasky:flasky /home/flasky

# ENTRYPOINT ["./boot.sh"]
#  change the permission of the bash file by chmod +x run_flask.sh before calling ENTRYPOINT
RUN chmod +x run_flask.sh

USER flasky

CMD ["/bin/bash", "-c", "sleep infinity"]
