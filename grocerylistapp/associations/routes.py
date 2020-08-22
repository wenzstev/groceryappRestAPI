from flask import Blueprint, jsonify, request, g

from grocerylistapp import db, auth
from grocerylistapp.models import recipe_list_associations, user_list_associations
from grocerylistapp.associations.utils import load_list_and_check_permissions, get_association_or_404, add_association, get_associaton_by_params
from grocerylistapp.associations.schemas import ListRecipeAssociationSchema, EditorAssociationSchema
from grocerylistapp.errors.exceptions import NotFoundException, InvalidUsage


associations = Blueprint("associations", __name__)

list_recipes_associations_schema = ListRecipeAssociationSchema(many=True)
list_recipes_association_schema = ListRecipeAssociationSchema()

list_user_associations_schema = EditorAssociationSchema(many=True)
list_user_association_schema = EditorAssociationSchema()


@associations.route("/list-recipe-associations", methods=["GET"])
def get_list_recipe_associations():
    return jsonify(list_recipes_associations_schema.dump(get_associaton_by_params(request.args)))


@associations.route("/list-recipe-associations/<int:id_>", methods=["GET"])
def get_specific_association(id_):
    current_association = get_association_or_404(id_, recipe_list_associations)
    return jsonify(list_recipes_association_schema.dump(current_association))


@associations.route("/list-recipe-associations", methods=["POST"])
@auth.login_required
def put_list_recipe_associations():
    list_to_modify, recipe_to_add = load_list_and_check_permissions(request.json, list_recipes_association_schema)
    add_association(recipe_to_add, list_to_modify.recipes)

    return jsonify(list_recipes_association_schema.dump(
        db.session.query(recipe_list_associations)
            .filter_by(recipe=recipe_to_add.id,
                       grocery_list=list_to_modify.id)
            .first())
    ), 201


@associations.route("/list-recipe-associations/<int:id_>", methods=["DELETE"])
@auth.login_required
def delete_list_recipe_assocation(id_):
    association_to_remove = get_association_or_404(id_, recipe_list_associations)
    list_to_modify, recipe_to_remove = load_list_and_check_permissions(association_to_remove, list_recipes_association_schema)
    list_to_modify.recipes.remove(recipe_to_remove)
    db.session.commit()
    return "", 204

# EDITOR ASSOCIATION ENDPOINTS
@associations.route("/list-user-associations", methods=["GET"])
def get_list_user_associations():
    return jsonify(list_user_associations_schema.dump(db.session.query(user_list_associations).all()))


@associations.route("/list-user-associations/<int:id_>", methods=["GET"])
def get_specific_list_user_association(id_):
    specific_association = get_association_or_404(id_, user_list_associations)
    return jsonify(list_user_association_schema.dump(specific_association))


@associations.route("/list-user-associations", methods=["POST"])
@auth.login_required
def post_list_user_association():
    list_to_modify, new_editor = load_list_and_check_permissions(request.json, list_user_association_schema)
    add_association(new_editor, list_to_modify.editors)

    return jsonify(list_user_association_schema.dump(
        db.session.query(user_list_associations).filter_by(
            grocery_list=list_to_modify.id,
            user=new_editor.id
        ).first()
    )), 201


@associations.route("/list-user-associations/<int:id_>", methods=["DELETE"])
@auth.login_required
def delete_list_user_association(id_):
    association_to_remove = get_association_or_404(id_, user_list_associations)
    list_to_modify, editor_to_remove = load_list_and_check_permissions(association_to_remove, list_user_association_schema)
    list_to_modify.editors.remove(editor_to_remove)
    db.session.commit()
    return "", 204

