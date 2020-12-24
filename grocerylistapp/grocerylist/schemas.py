from marshmallow import pre_load, post_load, fields, ValidationError

from grocerylistapp import db, ma
from grocerylistapp.models import Recipe, GroceryList, RecipeLine
from grocerylistapp.ingredient.schemas import IngredientSchema
from grocerylistapp.recipe.schemas import RecipeSchema


# schema that returns/validates a list
class GroceryListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GroceryList
        include_fk = True

    # nested recipes in the list, but we're going to exclude the recipe lines
    recipes = fields.Nested("RecipeSchema", many=True, exclude=("recipe_lines",))

    # takes the provided id of a recipe and returns the whole recipe
    @staticmethod
    def add_loaded_recipes(data, recipe_schema):
        print("in add loaded recipes")
        try:
            for index, recipe in enumerate(data["recipes"]):
                try:
                    full_recipe_schema = recipe_schema.dump(Recipe.query.get(recipe["id_"]))
                    data["recipes"][index] = full_recipe_schema
                except KeyError:
                    raise ValidationError(f"Unable to find recipe: ID not provided. Value: {recipe}")
            print("finished", data)
        except TypeError as e:
            raise ValidationError("Recipe data must be in the form {'id': <int>}. recipe data is: " + str(data["recipes"]))

    # create the "Additional Ingredients" recipe
    @staticmethod
    def create_additional_ingredients(data, recipe_schema):
        print(data)
        additional_ingredient_recipe = Recipe(name="Additional Ingredients", creator_id=data["creator_id"])
        try:
            additional_ingredients = data.pop("ingredients")
            ingredient_schema = IngredientSchema()

            for ingredient in additional_ingredients:
                ingredient = ingredient_schema.load(ingredient)  # load to class

                additional_ingredient_recipe.recipe_lines.append(RecipeLine(text=ingredient.name, ingredients=[ingredient]))
        except KeyError:
            # no single ingredients in the recipe, we can pass
            pass

        db.session.add(additional_ingredient_recipe)
        db.session.commit()
        data["recipes"].append(recipe_schema.dump(additional_ingredient_recipe))

    # function to supply the loaded recipes, rather than creating new ones
    #@pre_load
    def preload_functions(self, data, **kwargs):
        recipe_schema = RecipeSchema(exclude=("recipe_lines", "_links"))

        if data.get("recipes"):
            self.add_loaded_recipes(data, recipe_schema)
        else:
            data["recipes"] = []
        self.create_additional_ingredients(data, recipe_schema)

        return data

    @post_load
    def make_list(self, data, **kwargs):
        print("making list", data)
        return GroceryList(**data)


