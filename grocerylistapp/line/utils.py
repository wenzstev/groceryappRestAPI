# TODO: I need a way to retrieve a recipe line by searching an ingredient and
# TODO: the list the ingredient is on.

import json
from grocerylistapp.line.schemas import RecipeLineSchema


def get_new_ingredients_on_line(new_ingredient_json, line_to_change):
    print(line_to_change.text)
    print(new_ingredient_json)

    new_ingredients = []
    cur_ingredient_index = None
    cur_ingredient = ""
    start = 0

    line_text_list = json.loads(line_to_change.text)

    for i, (word, ingredient_index) in enumerate(zip(line_text_list, new_ingredient_json)):
        print(i, word, ingredient_index)
        if ingredient_index is not None:
            # check if we are in a new ingredient
            if cur_ingredient_index is None:
                cur_ingredient_index = ingredient_index
                print("cur ingredient index is now", cur_ingredient_index)
                start = i
            elif cur_ingredient_index != ingredient_index:
                end = i + 1 # add one because spaCy end is exclusive
                new_ingredients.append({"ingredient": cur_ingredient.strip(), "relevant_tokens": (start, end)})
                print("cur_index is", cur_ingredient_index)
                cur_ingredient_index = ingredient_index
                cur_ingredient = ""
                start = i
            cur_ingredient += word + " "
        elif cur_ingredient_index is not None:
            print("appending", cur_ingredient)
            new_ingredients.append({"ingredient": {"name":cur_ingredient.strip()}, "relevant_tokens":(start, i)})
            cur_ingredient_index = None
            cur_ingredient = ""

    print("left with", cur_ingredient)
    if cur_ingredient:
        print("appending last ingredient")
        new_ingredients.append({"ingredient":{"name": cur_ingredient}, "relevant_tokens": (start, len(line_text_list))})

    return json.dumps(new_ingredients)