from flask import Blueprint, jsonify, request, g

from grocerylistapp import db
from grocerylistapp.models import GroceryList, Recipe, recipe_list_associations
from grocerylistapp.utils import get_resource_or_404, post_new_resource, put_resource

from grocerylistapp.grocerylist.schemas import GroceryListSchema
from grocerylistapp.grocerylist.utils import get_list_by_params
from grocerylistapp.user.schemas import UserSchema
from grocerylistapp.recipe.schemas import RecipeSchema

from grocerylistapp.errors.exceptions import InvalidUsage, NotFoundException

grocerylist = Blueprint("grocerylist", __name__)

grocerylist_schema = GroceryListSchema()
grocerylists_schema = GroceryListSchema(many=True)

user_schema = UserSchema(exclude=("hashed_password",))
users_schema = UserSchema(many=True, exclude=("hashed_password",))


# return list of GroceryLists, with optional filters
@grocerylist.route("/api/lists", methods=["GET"])
def get_lists():
    lists = get_list_by_params(request.args)
    return jsonify(grocerylists_schema.dump(lists))


# post a new GroceryList
@grocerylist.route("/api/lists", methods=["POST"])
def post_list():
    new_list_json = request.json
    new_list_json["creator_id"] = None 
    new_grocerylist = post_new_resource(GroceryList, new_list_json)
    new_grocerylist.create_additional_ingredients_recipe()
    print("list", grocerylist_schema.dump(new_grocerylist))
    return jsonify(grocerylist_schema.dump(new_grocerylist)), 201


# get a specific GroceryList
@grocerylist.route("/api/lists/<int:id_>", methods=["GET"])
def get_list(id_):
    current_list = get_resource_or_404(GroceryList, id_)
    return jsonify(grocerylist_schema.dump(current_list))


# set GroceryList recipe and ingredients
@grocerylist.route("/api/lists/<int:id_>", methods=["PUT"])
def modify_list(id_):
    list_to_modify = get_resource_or_404(GroceryList, id_)
    if list_to_modify.creator_id == g.user.id or g.user.id in list_to_modify.editors:
        list_to_modify.name = request.json.get("name", list_to_modify.name)
        db.session.commit()
        return jsonify(grocerylist_schema.dump(list_to_modify))
    else:
        raise InvalidUsage("You don't have permission to modify this list.", 401)


# special route for accessing the "Additional Ingredients" recipe for a specific list
@grocerylist.route("/api/lists/<int:id_>/additionalingredients", methods=['GET'])
def get_additional_ingredients(id_):
    list_to_get = get_resource_or_404(GroceryList, id_)
    recipe_schema = RecipeSchema()
    return jsonify(recipe_schema.dump(list_to_get.additional_ingredients))



# set editors to a GroceryList
@grocerylist.route("/api/lists/<int:id_>/editors", methods=["PUT"])
def add_editors(id_):
    current_list = get_resource_or_404(GroceryList, id_)
    if current_list.creator is not g.user:
        raise InvalidUsage("You are not the creator of this Grocery List", 401)
    new_editors = users_schema.load(request.json.get("users"))
    current_list.editors = new_editors
    db.session.commit()

    return jsonify(users_schema.dump(new_editors)), 201


# delete a GroceryList
@grocerylist.route("/api/lists/<int:id_>", methods=["DELETE"])
def delete_list(id_):
    list_to_delete = get_resource_or_404(GroceryList, id_)
    db.session.delete(list_to_delete)
    db.session.commit()

    return ("", 204)