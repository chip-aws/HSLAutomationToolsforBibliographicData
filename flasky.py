# main script
# The script begins by creating an application.
# The configuration is taken from the environment variable FLASK_CONFIG if it’s defined,
# or else the default configuration is used. Flask-Migrate 
# and the custom context for the Python shell are then initialized.


import os
from app import create_app, db
# from app.models import User, Role
# problem occused by docker container
from app.models import User
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

# The unit tests can be executed as follows:
# (venv) $ flask test
@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
