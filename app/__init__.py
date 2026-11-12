import os
from sqlalchemy import URL
from flask import Flask

from app.extensions import db, migrate
from app import models
from app.routes.home import home_bp
from app.routes.admin import admin_bp

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "TROQUE-ESTA-CHAVE-EM-DESENVOLVIMENTO"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
        drivername="postgresql+psycopg",
        username="anavrin",
        password=os.environ.get("POSTGRES_PASSWORD"),
        host="db",
        port=5432,
        database="anavrin"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp)

    return app
