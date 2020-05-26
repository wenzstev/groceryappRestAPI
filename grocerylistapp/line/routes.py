from flask import Blueprint, request, jsonify, g

from sqlalchemy.exc import IntegrityError

from grocerylistapp import db, auth
from grocerylistapp.models import RecipeLine, Recipe
from grocerylistapp.utils import get_resource_or_404, put_resource, post_new_resource
from grocerylistapp.errors.exceptions import InvalidUsage

from grocerylistapp.line.schemas import RecipeLineSchema
from grocerylistapp.ingredient.schemas import IngredientSchema

line = Blueprint("line", __name__)
recipeline_schema = RecipeLineSchema()
recipelines_schema = RecipeLineSchema(many=True)
ingredients_schema = IngredientSchema(many=True)


@line.route("/lines/<int:id_>", methods=['GET'])
def get_line(id_):
    current_line = get_resource_or_404(RecipeLine, id_)
    return jsonify(recipeline_schema.dump(current_line))


@line.route("/lines", methods=['POST'])
@auth.login_required
def post_line():
    recipe_to_add_line = get_resource_or_404(Recipe, request.json.get("recipe_id"))
    if recipe_to_add_line.creator_id == g.user.id:
        new_line = post_new_resource(RecipeLine, request.json)
        return jsonify(recipeline_schema.dump(new_line))
    else:
        raise InvalidUsage("You don't have permission to modify that recipe.")


@line.route("/lines/<int:id_>", methods=['PUT'])
@auth.login_required
def put_line(id_):
    line_to_change = get_resource_or_404(RecipeLine, id_)
    if g.user.id == line_to_change.recipe.creator_id:
        line_to_change.text = request.json.get("text", "")
        line_to_change.ingredients = ingredients_schema.load(request.json.get("ingredients", ""))
        db.session.commit()
        return jsonify(recipeline_schema.dump(line_to_change))
    else:
        raise InvalidUsage("You don't have permission to modify that line.", 401)


@line.route("/lines/<int:id_>", methods=["DELETE"])
@auth.login_required
def delete_line(id_):
    line_to_delete = get_resource_or_404(RecipeLine, id_)

    db.session.delete(line_to_delete)
    db.session.commit()

    return ('', 204)