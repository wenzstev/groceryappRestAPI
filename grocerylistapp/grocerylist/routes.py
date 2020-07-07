from flask import Blueprint, jsonify, request, g

from grocerylistapp import db, auth
from grocerylistapp.models import GroceryList, Recipe, recipe_list_associations
from grocerylistapp.utils import get_resource_or_404, post_new_resource, put_resource

from grocerylistapp.grocerylist.schemas import GroceryListSchema
from grocerylistapp.grocerylist.utils import get_list_by_params
from grocerylistapp.user.schemas import UserSchema
from grocerylistapp.recipe.schemas import RecipeSchema

from grocerylistapp.errors.exceptions import InvalidUsage

grocerylist = Blueprint("grocerylist", __name__)

grocerylist_schema = GroceryListSchema()
grocerylists_schema = GroceryListSchema(many=True)

user_schema = UserSchema(exclude=("hashed_password",))
users_schema = UserSchema(many=True, exclude=("hashed_password",))


# return list of GroceryLists, with optional filters
@grocerylist.route("/lists", methods=["GET"])
def get_lists():
    lists = get_list_by_params(request.args)
    return jsonify(grocerylists_schema.dump(lists))


# post a new GroceryList
@grocerylist.route("/lists", methods=["POST"])
@auth.login_required
def post_list():
    new_list_json = request.json
    new_list_json["creator_id"] = g.user.id
    new_grocerylist = post_new_resource(GroceryList, new_list_json)
    return jsonify(grocerylist_schema.dump(new_grocerylist)), 201


# get a specific GroceryList
@grocerylist.route("/lists/<int:id_>", methods=["GET"])
def get_list(id_):
    current_list = get_resource_or_404(GroceryList, id_)
    return jsonify(grocerylist_schema.dump(current_list))


# set GroceryList recipe and ingredients
@grocerylist.route("/lists/<int:id_>", methods=["PUT"])
@auth.login_required
def modify_list(id_):
    list_to_modify = get_resource_or_404(GroceryList, id_)
    if list_to_modify.creator_id == g.user.id or g.user.id in list_to_modify.editors:
        list_to_modify.name = request.json.get("name", list_to_modify.name)
        db.session.commit()
        return jsonify(grocerylist_schema.dump(list_to_modify))
    else:
        raise InvalidUsage("You don't have permission to modify this list.", 401)



# set editors to a GroceryList
@grocerylist.route("/lists/<int:id_>/editors", methods=["PUT"])
@auth.login_required
def add_editors(id_):
    current_list = get_resource_or_404(GroceryList, id_)
    if current_list.creator is not g.user:
        raise InvalidUsage("You are not the creator of this Grocery List", 401)
    new_editors = users_schema.load(request.json.get("users"))
    current_list.editors = new_editors
    db.session.commit()

    return jsonify(users_schema.dump(new_editors)), 201


# delete a GroceryList
@grocerylist.route("/lists/<int:id_>", methods=["DELETE"])
def delete_list(id_):
    list_to_delete = get_resource_or_404(GroceryList, id_)

    # we need to specifically delete the GroceryList's "Additional Ingredients" recipe
    additional_ingredients = Recipe.query.filter(Recipe.name == "Additional Ingredients",
                                                 Recipe.grocery_lists.contains(list_to_delete)).first()
    db.session.delete(list_to_delete)
    db.session.delete(additional_ingredients)
    db.session.commit()

    return ("", 204)