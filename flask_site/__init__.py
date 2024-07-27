import os


from flask import Flask, Response, flash

from . import db
from . import base, auth, argue
from .htmx import htmx
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import CSRFError

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY= os.environ.get('SECRET_KEY', default='dev'),
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
            )
    if app.config['SECRET_KEY'] == 'dev':
        print('WARNING: SECRET_KEY is set to default value. This is not secure.')


    db.init_app(app)
    htmx.init_app(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    # this should probably live in a separate file
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        resp = Response("CSRF Error")
        resp.status_code = 400
        flash('CSRF Error, Try again.')
        resp.headers['HX-Refresh'] = 'true'
        return resp

    # app.register_blueprint(base.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(argue.bp)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
