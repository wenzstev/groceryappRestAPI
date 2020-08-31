# TODO: I need a way to retrieve a recipe line by searching an ingredient and
# TODO: the list the ingredient is on.

import json
from grocerylistapp import db
from grocerylistapp.line.schemas import RecipeLineSchema
from grocerylistapp.models import RecipeLine, Ingredient, LineIngredientAssociations, Recipe, GroceryList


def get_new_ingredients_on_line(new_ingredient_json, line_to_change):
    cur_ingredient = ""
    cur_ingredient_id_ = None
    start = 0
    ingredient_list = []

    line_word_list = json.loads(line_to_change.text)

    for index, (ingredient_id_, word) in enumerate(zip(new_ingredient_json, line_word_list)):
        if ingredient_id_ is not None:
            # we are in an ingredient
            if cur_ingredient_id_ is None:
                # starting new ingredient
                start = index
                cur_ingredient += word + " "
                cur_ingredient_id_ = ingredient_id_
            elif cur_ingredient_id_ != ingredient_id_:
                # we are changing from one ingredient to another
                ingredient_list.append(
                    {"ingredient": {"name": cur_ingredient.strip()},
                     "relevant_tokens": (start, index),
                     "color_index": cur_ingredient_id_})
                cur_ingredient += word + " "
                start = index
                cur_ingredient_id_ = ingredient_id_
            else:
                cur_ingredient += word + " "
        elif cur_ingredient_id_ is not None:
            # we just ended an ingredient
            ingredient_list.append(
                {"ingredient": {"name": cur_ingredient.strip()},
                 "relevant_tokens": (start, index),
                 "color_index": cur_ingredient_id_})
            cur_ingredient = ""
            cur_ingredient_id_ = None

    if cur_ingredient:
        ingredient_list.append(
            {"ingredient": {"name": cur_ingredient.strip()},
             "relevant_tokens": (start, len(line_word_list)),
             "color_index": cur_ingredient_id_})

    return json.dumps(ingredient_list)


# TODO: recreate this method of querying for all other queries
def get_line_by_params(params):
    ingredient = params.get("ingredient")
    grocery_list = params.get("list")
    lines = db.session.query(RecipeLine)

    if ingredient:
        lines = lines.join(LineIngredientAssociations, "ingredients")\
                .join(Ingredient)\
                .filter(Ingredient.name == ingredient)

    if grocery_list:
        lines = lines.join(Recipe)\
                .join(GroceryList, Recipe.grocery_lists)\
                .filter(GroceryList.id == grocery_list)

    return lines.all()


