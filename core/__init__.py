"""
Flask backend for a little tiny social network app
"""


# TODO: Add field "more_available" to post.get_public_info, in case post is content is cut
# TODO: Add field "more_available" to the feed object (change from array)

# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_cors import CORS


# Flask app
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
mig = Migrate(app, db)
CORS(app) # TODO: Update CORS before production


# Additional imports
from .exceptions import handler
from .endpoints import auth, users, posts, comments


# Registering error handler, blueprints
app.register_error_handler(Exception, handler)
app.register_blueprint(auth)
app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(comments)
