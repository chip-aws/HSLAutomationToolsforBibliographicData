
# A blueprint is similar to an application in that it can also define routes and error handlers.

from flask import Blueprint

main = Blueprint('main', __name__)
from . import views, errors