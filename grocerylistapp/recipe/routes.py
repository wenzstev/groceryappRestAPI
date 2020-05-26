from flask import Blueprint, request, jsonify, g

from marshmallow import ValidationError

from grocerylistapp import db, auth
from grocerylistapp.models import Recipe
from grocerylistapp.utils import get_resource_or_404, post_new_resource, put_resource
from grocerylistapp.errors.exceptions import InvalidUsage
from grocerylistapp.recipe.utils import get_recipe_by_params
from grocerylistapp.recipe.schemas import RecipeSchema
from grocerylistapp.line.schemas import RecipeLineSchema
from grocerylistapp.ingredient.schemas import IngredientSchema
from grocerylistapp.user.schemas import UserSchema


recipe = Blueprint('recipe', __name__)
ingredient_schema = IngredientSchema()
ingredients_schema = IngredientSchema(many=True)
recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)
recipeline_schema = RecipeLineSchema()
recipelines_schema = RecipeLineSchema(many=True)
user_schema = UserSchema()


@recipe.route("/recipes", methods=["GET"])
def get_recipes():
    recipes = get_recipe_by_params(request.args)
    return jsonify(recipes_schema.dump(recipes))


@recipe.route("/recipes", methods=["POST"])
@auth.login_required
def post_recipe():
    new_recipe = post_new_resource(Recipe, request.json)
    return jsonify(recipe_schema.dump(new_recipe)), 201


@recipe.route("/recipes/<int:id_>", methods=["GET"])
def get_recipe_info(id_):
    current_recipe = get_resource_or_404(Recipe, id_)
    return jsonify(recipe_schema.dump(current_recipe))


@recipe.route("/recipes/<int:id_>", methods=["PUT"])
@auth.login_required
def put_recipe(id_):
    recipe_to_change = get_resource_or_404(Recipe, id_)
    if recipe_to_change.creator_id == g.user.id:
        recipe_to_change.name = request.json.get("name", recipe_to_change.name)
        recipe_to_change.url = request.json.get("url", recipe_to_change.url)

        return jsonify(recipe_schema.dump(recipe_to_change))
    else:
        raise InvalidUsage("You don't have permission to modify this recipe.")



@recipe.route("/recipes/<int:id_>", methods=["DELETE"])
@auth.login_required
def delete_recipe(id_):
    recipe_to_delete = get_resource_or_404(Recipe, id_)

    if recipe_to_delete.creator is not g.user:
        raise InvalidUsage("You are not the creator of this recipe.", 401)

    db.session.delete(recipe_to_delete)
    db.session.commit()

    return ('', 204)






