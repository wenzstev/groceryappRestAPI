from flask import g

from grocerylistapp.errors.exceptions import NotFoundException, InvalidUsage
from grocerylistapp.ingredient.schemas import IngredientSchema
from grocerylistapp.line.schemas import RecipeLineSchema
from grocerylistapp.recipe.schemas import RecipeSchema
from grocerylistapp.grocerylist.schemas import GroceryListSchema
from grocerylistapp.user.schemas import PostUserSchema
from grocerylistapp import db

from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

ingredient_schema = IngredientSchema()
recipeline_schema = RecipeLineSchema()
recipe_schema = RecipeSchema()
grocerylist_schema = GroceryListSchema()
user_schema = PostUserSchema()

base_schemas_to_models = {
    "ingredient": ingredient_schema,
    "recipe_line": recipeline_schema,
    "recipe": recipe_schema,
    "grocery_list": grocerylist_schema,
    "user": user_schema
}



def get_resource_or_404(resource_type, identifier):
    if type(identifier) == str:     # only used for ingredients
        resource = resource_type.query.filter_by(name=identifier).first()
    else:
        resource = resource_type.query.get(identifier)
        print(resource, identifier)
    if not resource:
        raise NotFoundException(resource_type, identifier)
    return resource


def load_resource_from_schema(resource_type, new_resource_json):
    if not new_resource_json:
        raise InvalidUsage(f"Data formatted incorrectly, no label of {resource_type.__tablename__} provided.")

    try:
        new_resource = base_schemas_to_models[resource_type.__tablename__].load(new_resource_json)
        return new_resource
    except ValidationError as e:
        raise InvalidUsage("Your data was not formatted correctly.", payload=e.messages)
    except IntegrityError as e:
        raise InvalidUsage("Your data was not formatted correctly; you are trying to insert something into the database "
                           "which already exists.", payload=e)
    except FlushError:
        raise InvalidUsage("Your data was not formatted correctly; are you using an id which already exists?")



def post_new_resource(resource_type, new_resource_json):
    print("new resource", new_resource_json)
    try:
        new_resource = load_resource_from_schema(resource_type, new_resource_json)
    except ValidationError as e:
        print("here")
        raise InvalidUsage("There was a problem with your formatting.", payload=(str(e)))

    try:
        db.session.add(new_resource)
        db.session.commit()
        return new_resource

    except IntegrityError as e:
        raise InvalidUsage("You're trying to load something that is already in the database.", payload=str(e))
    except ValueError as e:
        raise InvalidUsage("You are trying to load a resource that does not conform to database standards.",
                           payload={"details": {"resource": resource_type.__tablename__, "comments": str(e)}})



def put_resource(resource_type, old_version_of_resource, json_with_new_resource, id_):
    print("in put resource")

    if resource_type.__tablename__ == "recipe":
        json_with_new_resource["creator_id"] = g.user.id

    print("trying to load new resource...")
    new_version_of_resource = load_resource_from_schema(resource_type, json_with_new_resource)

    print("loaded new resource")

    db.session.delete(old_version_of_resource)


    print(old_version_of_resource)

    new_version_of_resource.id = id_
    db.session.add(new_version_of_resource)




    db.session.commit()
    return new_version_of_resource
