from flask import g, jsonify

from grocerylistapp import db
from grocerylistapp.errors.exceptions import InvalidUsage
from grocerylistapp.models import recipe_list_associations, user_list_associations
from grocerylistapp.associations.schemas import ListRecipeAssociationSchema

list_recipes_associations_schema = ListRecipeAssociationSchema(many=True)
list_recipes_association_schema = ListRecipeAssociationSchema()

def get_associaton_by_params(param):
    if param.get("recipe") and param.get("list"):
        print(param.get("recipe"), param.get("list"))
        association = db.session.query(recipe_list_associations)\
            .filter(recipe_list_associations.c.recipe == param.get("recipe"))\
            .filter(recipe_list_associations.c.grocery_list == param.get("list")).first()
        print(association)
        if not association:
            raise InvalidUsage("No association exists between the specified list and recipe", 404)
        return list_recipes_association_schema.dump(association)
    if param.get("recipe"):
        associations = db.session.query(recipe_list_associations).filter(recipe_list_associations.c.recipe == param.get("recipe")).all()
    elif param.get("list"):
        associations = db.session.query(recipe_list_associations).filter(recipe_list_associations.c.grocery_list == param.get("list")).all()
    else:
        associations = db.session.query(recipe_list_associations).all()

    return list_recipes_associations_schema.dump(associations)


def load_list_and_check_permissions(association_to_modify, association_schema):
    list_to_modify, resource_to_change = association_schema.load(association_to_modify)
    if g.user not in list_to_modify.editors and g.user.id != list_to_modify.creator_id:
        raise InvalidUsage("You don't have permission to modify this list.", 401)

    return list_to_modify, resource_to_change


def get_association_or_404(id_, table):
    association = db.session.query(table).filter_by(id=id_).first()
    if not association:
        raise InvalidUsage("The association you're looking for can't be found.", 404)
    return association


def add_association(new_resource_for_list, list_to_add_to):
    if new_resource_for_list not in list_to_add_to:
        list_to_add_to.append(new_resource_for_list)
        db.session.commit()


