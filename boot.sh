#!/bin/bash
source venv/bin/activate
#. venv/bin/activate
export FLASK_APP=flasky.py
export FLASK_DEBUG=1
flask deploy
# flask run
# exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - flasky:app
exec gunicorn -b 0.0.0.0:5000  - flasky:app