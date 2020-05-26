from marshmallow import post_load, pre_load, fields

from grocerylistapp import db, ma
from grocerylistapp.models import Ingredient


# schema that returns/validates an ingredient
class IngredientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ingredient
        include_fk = True

    # links to the ingredient, via name and id
    _links = ma.Hyperlinks(
        {"by name": ma.URLFor("ingredient.get_ingredient", identifier="<name>"),
         "by id": ma.URLFor("ingredient.get_ingredient", identifier="<id>")}
    )

    # return an ingredient when schema is loaded, either the database ingredient or a new object
    @post_load
    def make_ingredient(self, data, **kwargs):
        print("in ingredient postload")
        existing_ingredient = Ingredient.query.filter_by(name=data["name"]).first()
        if existing_ingredient:
            return existing_ingredient

        print("creating new ingredient")
        new_ingredient = Ingredient(**data)
        db.session.add(new_ingredient)
        db.session.commit()
        return new_ingredient

    @pre_load
    def clean_ingredient(self, data, **kwargs):
        data["name"] = data["name"].lower()
        return data
