
from grocerylistapp import nlp
from grocerylistapp.models import Ingredient, RecipeLine, Recipe, GroceryList

from grocerylistapp.errors.exceptions import InvalidUsage, NotFoundException


def get_recipe_by_params(args):
    if args.get("ingredient") and args.get("list"):
        raise InvalidUsage("Too many parameters. You cannot query for ingredients and lists at the same time.")

    if args.get("ingredient"):
        recipes_by_ingredient = []
        for ingredient in args.get("ingredient").split(","):
            recipes_by_ingredient.append(set(
                Recipe.query
                .join(RecipeLine)
                .join(Ingredient, RecipeLine.ingredients)
                .filter(Ingredient.name == ingredient)
                .all()))
        # find the intersection of all the sets and return
        intersection_set = set(recipes_by_ingredient[0]).intersection(*(recipes_by_ingredient[1:]))
        return intersection_set

    if args.get("list"):
        if not GroceryList.query.get(args.get("list")):
            raise NotFoundException("GroceryList", args.get("list"),
                                    "List must be returned by id; only one list can be queried at a time.")
        recipes_by_list = Recipe.query\
            .join(GroceryList, "grocery_lists")\
            .filter(GroceryList.id == args.get("list"))\
            .all()

        return recipes_by_list

    return Recipe.query.all()



