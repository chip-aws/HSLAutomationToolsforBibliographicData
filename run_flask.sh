#!/bin/sh
deactivate
. venv/bin/activate
# source venv/bin/activate
export FLASK_APP=flasky.py
export FLASK_DEBUG=1
# flask run
flask run -h 127.0.0.1 -p 5000
gunicorn -b 0.0.0.0:5000  - flasky:app
