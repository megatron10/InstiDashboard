import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure the app"""
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app = Flask(__name__, instance_relative_config=True)

    # Not actually mapping yet
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    @app.teardown_request
    def teardown_request(exception):
        if exception:
            app.logger.error(exception)
            db.rollback_db()

    from . import auth
    app.register_blueprint(auth.bp)

    from .gauth import gauth_bp
    app.register_blueprint(gauth_bp)

    from .orgs import orgs_bp
    app.register_blueprint(orgs_bp)

    # a simple index page that says hello
    @app.route('/')
    def index():
        return 'Hello, World!'

    return app
