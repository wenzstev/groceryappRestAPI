from marshmallow import fields, pre_load, post_load, ValidationError
from flask import g


from grocerylistapp import db, ma
from grocerylistapp.models import Recipe
from grocerylistapp.scraper import get_recipe_from_url
from grocerylistapp.nlp import determine_ingredients_in_line


# schema that returns/validates a recipe
class RecipeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Recipe
        include_fk = True

    # nested Schema for recipe lines
    recipe_lines = fields.Nested("RecipeLineSchema", many=True, exclude=("recipe_id",))

    # nested schema for the creator
    creator = fields.Nested("UserSchema", exclude=("hashed_password",))

    # provide links to the resource
    _links = ma.Hyperlinks(
        {"individual": ma.URLFor("recipe.get_recipe_info", id_="<id>"),
         "collection": ma.URLFor("recipe.get_recipes")}
    )

    @pre_load
    def build_from_url(self, data, **kwargs):
        print("in recipe preload")
        if data.get("create_from_url", ""):
            try:
                print("creating recipe")
                recipe_from_url = get_recipe_from_url(data["create_from_url"])
                recipe_from_url_with_ingredients = determine_ingredients_in_line(recipe_from_url)
                recipe_from_url_with_ingredients["creator_id"] = g.user.id
                print("final structure:", recipe_from_url_with_ingredients)
                return recipe_from_url_with_ingredients
            except KeyError as e:
                raise ValidationError(f"Missing data: {repr(e)}")

        if not data.get('creator'):
            data['creator_id'] = g.user.id
        print(data)
        return data

    # create the Recipe object, or return the existing recipe object if it already exists
    @post_load
    def make_recipe(self, data, **kwargs):
        print("In recipe postload")

        return Recipe(**data)