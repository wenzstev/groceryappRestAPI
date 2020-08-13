from grocerylistapp.models import Ingredient, RecipeLine, Recipe, GroceryList, LineIngredientAssociations
from grocerylistapp.errors.exceptions import InvalidUsage
from grocerylistapp.utils import get_resource_or_404


# method that checks if there are any arguments to filter, returns all ingredients if not
def get_ingredient_by_params(args):
    if args.get("recipe") and args.get("list"):
        raise InvalidUsage("Error: can't filter by recipe and line at the same time")

    if args.get("recipe"):
        set_to_return = set()
        for recipe_id in args.get("recipe"):
            set_to_return.update(
                Ingredient.query
                .join(LineIngredientAssociations, "recipe_lines")
                .join(RecipeLine)
                .join(Recipe)
                .filter(Recipe.id == recipe_id)
                .all())
        return set_to_return

    if args.get("list"):
        set_to_return = set()
        for line_id in args.get("list"):
            set_to_return.update(
                Ingredient.query
                .join(RecipeLine, "recipe_lines")
                .join(Recipe)
                .join(GroceryList, Recipe.grocery_lists)
                .filter(GroceryList.id == line_id)
            )
        return set_to_return

    # no queries, return all ingredients
    return Ingredient.query.all()


# method that can take either a name or an id and return an ingredient
def ingredient_by_name_or_id(identifier):
    if type(identifier) == str:
        return Ingredient.query.filter_by(name=identifier.replace("-", " ")).first()
    if type(identifier) == int:
        return Ingredient.query.get(identifier)
