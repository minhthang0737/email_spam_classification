from flask import Flask
from werkzeug.exceptions import HTTPException

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

from app.utils.errors import not_found_error, server_error
from app.utils.logger import get_logger

db = SQLAlchemy()
logger = get_logger(__name__)


def create_app(config_object="app.config.Config"):
    app = Flask(__name__)

    app.config.from_object(config_object)

    db.init_app(app)

    from app.models.user import User  # noqa: F401
    from app.models.ip_reputation import BlockedIP, BlockedDomain  # noqa: F401

    from app.api.dataset import dataset_bp
    from app.api.model import model_bp
    from app.api.health import health_bp
    from app.api.predict import predict_bp
    from app.api.classifications import classifications_bp
    from app.api.ip_reputation import ip_bp
    from app.api.users import users_bp
    from app.api.account import account_bp
    from app.api.demo import demo_bp
    from app.api.views import views_bp
    from app.auth import load_user

    app.register_blueprint(dataset_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(classifications_bp)
    app.register_blueprint(ip_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(demo_bp)
    app.register_blueprint(views_bp)
    app.before_request(load_user)

    @app.errorhandler(404)
    def handle_not_found(error):
        return not_found_error("Resource not found.")

    @app.errorhandler(500)
    def handle_server_error(error):
        logger.exception("Unhandled server error: %s", error)
        return server_error()

    @app.errorhandler(Exception)
    def handle_exception(error):
        if isinstance(error, HTTPException):
            return error
        if app.config.get("TESTING"):
            raise error
        logger.exception("Unhandled exception: %s", error)
        return server_error()

    with app.app_context():
        db.create_all()
        user_columns = {column["name"] for column in inspect(db.engine).get_columns("app_user")}
        with db.engine.begin() as connection:
            if "display_name" not in user_columns:
                connection.execute(text("ALTER TABLE app_user ADD COLUMN display_name VARCHAR(120)"))
            if "email" not in user_columns:
                connection.execute(text("ALTER TABLE app_user ADD COLUMN email VARCHAR(254)"))

    return app
