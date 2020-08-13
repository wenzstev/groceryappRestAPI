from marshmallow import pre_load, post_load, pre_dump, post_dump, fields, EXCLUDE
from flask import g

import json

from grocerylistapp import ma, db
from grocerylistapp.models import RecipeLine, LineIngredientAssociations

from grocerylistapp.ingredient.schemas import IngredientSchema


class RecipelineIngredientAssociationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LineIngredientAssociations
        include_fk = True

    ingredient = fields.Nested(IngredientSchema)

    @post_load
    def make_association(self, data, **kwargs):
        new_association = LineIngredientAssociations(**data)
        return new_association

    @post_dump
    def convert_token_string_to_list(self, data, **kwargs):
        data["relevant_tokens"] = json.loads(data["relevant_tokens"])
        return data

    @pre_load
    def check_json(self, data, **kwargs):
        print("preloaded data:", data)
        # turn list into string
        if isinstance(data["relevant_tokens"], list):
            data["relevant_tokens"] = json.dumps(data["relevant_tokens"])
        return data


class RecipeLineSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RecipeLine
        include_fk = True

    # nested schema for the ingredients on the line
    ingredients = fields.Nested(RecipelineIngredientAssociationSchema, many=True)

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
        print("adding ingredients:", data["ingredients"])
        new_recipeline.ingredients = data["ingredients"]  # add the ingredients separately so the validator works
        return new_recipeline

    @post_dump
    def convert_string_to_list(self, data, **kwargs):
        print("postdump data:", data)
        data["text"] = json.loads(data["text"])

        return data

