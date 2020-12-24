from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS

import spacy

from grocerylistapp.config import Config

db = SQLAlchemy()
ma = Marshmallow()
mail = Mail()
auth = HTTPBasicAuth()
nlp = spacy.load("ingredient_test")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    CORS(app)

    from grocerylistapp.ingredient.routes import ingredient
    app.register_blueprint(ingredient)

    from grocerylistapp.line.routes import line
    app.register_blueprint(line)

    from grocerylistapp.recipe.routes import recipe
    app.register_blueprint(recipe)

    from grocerylistapp.grocerylist.routes import grocerylist
    app.register_blueprint(grocerylist)

#    from grocerylistapp.user.routes import user
#    app.register_blueprint(user)

    from grocerylistapp.associations.routes import associations
    app.register_blueprint(associations)

    from grocerylistapp.errors.handlers import errors
    app.register_blueprint(errors)

    return app
