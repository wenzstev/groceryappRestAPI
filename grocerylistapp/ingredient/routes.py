from flask import Blueprint, jsonify, request

from sqlalchemy.exc import IntegrityError

from grocerylistapp import db
from grocerylistapp.models import Ingredient, Recipe, RecipeLine
from grocerylistapp.utils import get_resource_or_404, post_new_resource

from grocerylistapp.ingredient.schemas import IngredientSchema
from grocerylistapp.ingredient.utils import ingredient_by_name_or_id, get_ingredient_by_params

from grocerylistapp.errors.exceptions import InvalidUsage, NotFoundException

ingredient = Blueprint('ingredient', __name__)

ingredient_schema = IngredientSchema()
ingredients_schema = IngredientSchema(many=True)


@ingredient.route("/ingredients", methods=['GET'])
def get_ingredients():
    ingredients_to_return = get_ingredient_by_params(request.args)
    return jsonify(ingredients_schema.dump(ingredients_to_return))


@ingredient.route("/ingredients", methods=['POST'])
def add_ingredients():
    new_ingredient = post_new_resource(Ingredient, request.json)
    return jsonify(ingredient_schema.dump(new_ingredient)), 201



@ingredient.route("/ingredients/<int:identifier>", methods=["GET"])
@ingredient.route("/ingredients/<string:identifier>", methods=["GET"])
def get_ingredient(identifier):
    cur_ingredient = get_resource_or_404(Ingredient, identifier)
    return jsonify(ingredient_schema.dump(cur_ingredient))


@ingredient.route("/ingredients/<string:identifier>", methods=["DELETE"])
@ingredient.route("/ingredients/<int:identifier>", methods=["DELETE"])
def delete_ingredients(identifier):
    ingredient_to_delete = get_resource_or_404(Ingredient, identifier)

    db.session.delete(ingredient_to_delete)
    db.session.commit()

    return ('', 204)

