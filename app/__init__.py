from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    db.init_app(app)

    from app.api.dataset import dataset_bp
    app.register_blueprint(dataset_bp)

    from app.api.model import model_bp
    app.register_blueprint(model_bp)
    
    return app