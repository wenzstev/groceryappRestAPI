from marshmallow import pre_load, post_load, fields, EXCLUDE
from flask import g

from grocerylistapp import ma
from grocerylistapp.models import RecipeLine

from grocerylistapp.ingredient.schemas import IngredientSchema


class RecipeLineSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RecipeLine
        include_fk = True

    # nested schema for the ingredients on the line
    ingredients = fields.Nested(IngredientSchema, many=True)

    # link to individual line
    _links = ma.Hyperlinks({
        "line": ma.URLFor("line.get_line", id_="<id>")
    })

    # return a recipeline when schema is loaded
    @post_load
    def make_recipe(self, data, **kwargs):
        new_recipeline = RecipeLine(text=data["text"])
        if data.get("recipe_id"):
            new_recipeline.recipe_id = data.get("recipe_id")
        new_recipeline.ingredients = data["ingredients"]  # add the ingredients separately so the validator works
        return new_recipeline

