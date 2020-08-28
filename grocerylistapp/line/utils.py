# TODO: I need a way to retrieve a recipe line by searching an ingredient and
# TODO: the list the ingredient is on.

import json
from grocerylistapp.line.schemas import RecipeLineSchema


def get_new_ingredients_on_line(new_ingredient_json, line_to_change):
    cur_ingredient = ""
    cur_ingredient_id_ = None
    start = 0
    ingredient_list = []

    line_word_list = json.loads(line_to_change.text)

    for index, (ingredient_id_, word) in enumerate(zip(new_ingredient_json, line_word_list)):
        print(index, ingredient_id_, word)
        print(cur_ingredient_id_)
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
                    {"ingredient": {"name": cur_ingredient},
                     "relevant_tokens": (start, index)})
                cur_ingredient += word + " "
                start = index
                cur_ingredient_id_ = ingredient_id_
            else:
                cur_ingredient += word + " "
        elif cur_ingredient_id_ is not None:
            # we just ended an ingredient
            ingredient_list.append(
                {"ingredient": {"name": cur_ingredient},
                 "relevant_tokens": (start, index)})
            cur_ingredient = ""
            cur_ingredient_id_ = None

    if cur_ingredient:
        ingredient_list.append(
            {"ingredient": {"name": cur_ingredient},
                "relevant_tokens": (start, len(line_word_list))})

    print(json.dumps(ingredient_list))
    return json.dumps(ingredient_list)


