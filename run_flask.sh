#!/bin/sh
deactivate
. venv/bin/activate
export FLASK_APP=flasky.py
export FLASK_DEBUG=1
flask run --host=0.0.0.0
