"""
This constructor imports most of the Flask extensions currently in use,
but because there is no application instance to initialize them with,
it creates them uninitialized by passing no arguments into their constructors.

The create_app() function is the application factory, which takes as an argument the name of a configuration to use
for the application. The configuration settings stored in one of the classes defined in config.py can be imported
directly into the application using the from_object() method available in Flask’s app.config configuration object.

The configuration object is selected by name from the config dictionary. Once an application is created and
configured, the extensions can be initialized.
Calling init_app() on the extensions that were created earlier
completes their initialization.

The application initialization is now done in this factory function,
using the from_object() method from the Flask configuration object, which takes as an argu‐ ment one of the
configuration classes defined in config.py.

The init_app() method of the selected configuration is also invoked,
to allow more complex initialization proce‐ dures to take place. The factory function returns the created application
instance, but note that applica‐ tions created with the factory function in its current state are incomplete,
as they are missing routes and custom error page handlers. This is the topic of the next section.
"""

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    # attach routes and custom error pages here
    # import blueprint
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app