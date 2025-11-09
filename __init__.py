"""Application factory for the SERM Monitoring API."""
from __future__ import annotations

import os
from flask import Flask, jsonify

from models.models import db

DEFAULT_DATABASE_URI = (
    "postgresql+psycopg2://pashkan:password@deleteme_db:5432/deleteme"
)


def create_app() -> Flask:
    """Create and configure a Flask application instance."""
    app = Flask(__name__)

    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URI),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
    )

    db.init_app(app)

    @app.route("/health", methods=["GET"])  # pragma: no cover - trivial endpoint
    def healthcheck():
        return jsonify({"status": "ok"})

    from api import register_resources

    register_resources(app)

    return app


__all__ = ["create_app", "db"]
