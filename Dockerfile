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

ENV NLTK_DATA=/usr/local/nltk_data
RUN [ "python", "-c", "import nltk; nltk.download('stopwords', download_dir='/usr/local/nltk_data')" ]


EXPOSE 8000

# add folder permission
RUN adduser flask
RUN chmod -R 775 /home/flasky
RUN chown -R flask /home/flasky
USER flask

# ENTRYPOINT ["./boot.sh"]
#  change the permission of the bash file by chmod +x run_flask.sh before calling ENTRYPOINT
RUN chmod +x run_flask.sh
ENTRYPOINT ["./run_flask.sh"]
