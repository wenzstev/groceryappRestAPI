from grocerylistapp import db

from grocerylistapp.models import Ingredient, RecipeLine, Recipe, GroceryList, LineIngredientAssociations
from grocerylistapp.errors.exceptions import InvalidUsage
from grocerylistapp.utils import get_resource_or_404

# TODO: refactor with better querying to remove the recipe ingredinet bug
# method that checks if there are any arguments to filter, returns all ingredients if not
def get_ingredient_by_params(args):
    recipes = args.get("recipe")
    grocerylists = args.get("list")
    ingredients = db.session.query(Ingredient)\
                    .join(LineIngredientAssociations, "recipe_lines") \
                    .join(RecipeLine) \
                    .join(Recipe)

    if recipes:
        ingredients = ingredients.filter(Recipe.id.in_(recipes.split(",")))  # this is OR, what about AND?

    if grocerylists:
        ingredients = ingredients.join(GroceryList, Recipe.grocery_lists)\
            .filter(GroceryList.id.in_(grocerylists.split(",")))

    return ingredients.all()

# method that can take either a name or an id and return an ingredient
def ingredient_by_name_or_id(identifier):
    if type(identifier) == str:
        return Ingredient.query.filter_by(name=identifier.replace("-", " ")).first()
    if type(identifier) == int:
        return Ingredient.query.get(identifier)
