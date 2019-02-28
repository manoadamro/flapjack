from typing import Iterable, Optional, Type

import flask
import flask_sqlalchemy
import waitress

import flapi_jwt as jwt
import flapi_schema as schema


current_app = flask.current_app

schema = schema
jwt = jwt

Blueprint = flask.Blueprint

request = flask.request

render_template = flask.render_template
render_template_string = flask.render_template_string

db = flask_sqlalchemy.SQLAlchemy()


def response(body=None, code=200):
    return flask.make_response(flask.jsonify(body or {}), code)


class Config(flask.Config):
    API_HOST = "localhost"
    API_PORT = 9001

    JWT_HANDLER = None
    JWT_SECRET = None
    JWT_LIFESPAN = 900
    JWT_ISSUER = None
    JWT_AUDIENCE = None
    JWT_AUTO_UPDATE = False

    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TEST_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app(
    testing: bool = False,
    config_class: Type[Config] = None,
    use_jwt: bool = True,
    use_db: bool = True,
    blueprints: Optional[Iterable] = None,
):
    app = flask.Flask(__name__)

    if config_class is None:
        config_class = Config
    app.config.from_object(config_class)

    if testing:
        test_db_uri = app.config["SQLALCHEMY_TEST_DATABASE_URI"]
        app.config["SQLALCHEMY_DATABASE_URI"] = test_db_uri
        app.config["SEND_EMAILS"] = False
    app.testing = testing

    if use_jwt:
        app.config["JWT_HANDLER"] = jwt.FlaskJwt(
            app=app,
            secret=app.config["JWT_SECRET"],
            lifespan=app.config["JWT_LIFESPAN"],
            issuer=app.config["JWT_ISSUER"],
            audience=app.config["JWT_AUDIENCE"],
            auto_update=app.config["JWT_AUTO_UPDATE"],
            verify=(not app.testing),
        )

    if use_db is True:
        db.init_app(app)

    if blueprints is not None:
        for blueprint in blueprints:
            app.register_blueprint(blueprint)

    app.errorhandler(jwt.errors.JWTValidationError)(_handle_error(403))
    app.errorhandler(schema.errors.SchemaValidationError)(_handle_error(409))

    return app


def serve(app):
    config = app.confg
    waitress.serve(app, host=config["API_HOST"], port=config["API_PORT"])


def _handle_error(code):
    def wrapped(e):
        return flask.jsonify({"message": str(e)}), code
    return wrapped
