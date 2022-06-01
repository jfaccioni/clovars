from __future__ import annotations

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from clovars.app.config import DevConfig

db = SQLAlchemy()


def init_app():
    """Initializes the CloVarS web app."""
    # APP CONFIGURATION
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config.DevConfig)
    Bootstrap(app)  # Flask-Bootstrap4 requires this line

    db.init_app(app)
    with app.app_context():
        from clovars.app.home import routes
        app.register_blueprint(routes.main_blueprint)
        if app.config.get('FLASK_ENV') == 'development':  # Refreshes database during development
            db.drop_all()
        db.create_all()

    return app
