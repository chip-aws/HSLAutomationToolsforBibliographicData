# FROM python:3.10-alpine
FROM python:3.8-slim
USER root

ENV FLASK_APP flasky.py
ENV FLASK_CONFIG docker

RUN useradd -m flasky 
RUN chown -R flasky:flasky /home/flasky

RUN mkdir -p /home/flasky/
COPY requirements /home/flasky
RUN python -m venv /home/flasky/venv
RUN /home/flasky/venv/bin/pip install -r requirements/requirements.txt

COPY app /home/flasky/app
COPY migrations /home/flasky/migrations
COPY results /home/flasky/results
COPY tests /home/flasky/tests
COPY uploads /home/flasky/uploads
COPY flasky.py config.py boot.sh run_flask.sh /home/flasky
RUN chown -R flasky:flasky /home/flasky
USER flasky

# runtime configuration
EXPOSE 5000

# ENTRYPOINT ["./boot.sh"]
#  change the permission of the bash file by chmod +x run_flask.sh before calling ENTRYPOINT
RUN chmod +x run_flask.sh
ENTRYPOINT ["./run_flask.sh"]
