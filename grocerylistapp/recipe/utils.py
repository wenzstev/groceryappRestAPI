
from grocerylistapp import nlp, db
from grocerylistapp.models import Ingredient, RecipeLine, Recipe, GroceryList, LineIngredientAssociations, User

from grocerylistapp.errors.exceptions import InvalidUsage, NotFoundException

def get_recipe_by_params(args):
    ingredient = args.get("ingredient")
    grocerylist = args.get("list")
    user = args.get("user")

    recipes = db.session.query(Recipe)

    if ingredient:
        recipes = recipes.join(RecipeLine)\
                    .join(LineIngredientAssociations, RecipeLine.ingredients)\
                    .join(Ingredient)\
                    .filter(Ingredient.name.in_(ingredient.split(',')))  # this is AND; what about ALL?

    if grocerylist:
        recipes = recipes.join(GroceryList, "grocery_lists").filter(GroceryList.id.in_(grocerylist.split(',')))

    if user:
        recipes = recipes.join(User).filter(User.id == user)    # no need for split because it's many-to-one

    return recipes.all()


