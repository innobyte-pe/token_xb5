# services/users/project/__init__.py


import os

from flask import Flask  # nuevo
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS  # nuevo

# instanciando la db
db = SQLAlchemy()
toolbar = DebugToolbarExtension()
cors = CORS()  # nuevo
# new
def create_app(script_info=None):

    # instanciando la app
    app = Flask(__name__)

    # estableciendo la configuración
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # preparando la extensión
    db.init_app(app)
    toolbar.init_app(app) # nuevo
    cors.init_app(app,resources={r"/*":{"origins":"*"}})
    # registrar blueprints
    from project.api.index import users_blueprint

    app.register_blueprint(users_blueprint)

    # contexto shell para flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    return app
