from __future__ import annotations

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from clovars.app.config import DevConfig, ProdConfig

db = SQLAlchemy()


def init_app():
    """Initializes the CloVarS web app."""
    # SET APP CONFIGURATION
    app = Flask(__name__, instance_relative_config=False)
    if (env := _get_env(app=app)) == 'development':
        app.config.from_object(config.DevConfig)
    elif env == 'production':
        app.config.from_object(config.ProdConfig)

    # INIT PLUGINS
    Bootstrap(app)
    db.init_app(app)

    # REGISTER BLUEPRINTS
    with app.app_context():
        from clovars.app.home import routes as home_routes
        app.register_blueprint(home_routes.home_bp)
        from clovars.app.treatments import routes as treatment_routes
        app.register_blueprint(treatment_routes.treatment_bp)

    # INIT DATABASE
    with app.app_context():
        if env == 'development':
            db.drop_all()
            db.create_all()
            from clovars.app.models import place_initial_data
            place_initial_data(database=db)
        elif env == 'production':
            db.create_all()

    return app


def _get_env(app: Flask) -> str:
    """Returns the ENV string from the Flask's config dictionary."""
    env = app.config.get('ENV')
    if not env_is_valid(env=env):
        raise ValueError(f"Invalid value for ENV: {env}")
    return env


def env_is_valid(env: str) -> bool:
    """Returns whether the given ENV string represents a valid environment."""
    valid_envs = ['development', 'production']
    return env in valid_envs
