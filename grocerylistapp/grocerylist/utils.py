
from grocerylistapp import db

from grocerylistapp.models import GroceryList, Recipe, RecipeLine, Ingredient
from grocerylistapp.schemas import IngredientSchema

ingredient_schema = IngredientSchema()


def add_additional_ingredients(grocerylist_id, ingredient):
    grocerylist = GroceryList.query.get(grocerylist_id)
    additional_ingredients = Recipe.query\
        .filter(Recipe.name == "Additional Ingredients",
                Recipe.grocery_lists.contains(grocerylist)).first()
    additional_ingredients.recipe_lines.append(RecipeLine(text=ingredient["name"], ingredients=[ingredient_schema.load(ingredient)]))
    db.session.commit()

