from grocerylistapp import nlp

import json


def determine_ingredients_in_line(recipe_dict):
    print("determining ingredients")

    recipe_lines_with_ingredients = []

    for line in recipe_dict["recipe_lines"]:
        current_recipe_line = {
            "text": [],
            "ingredients": []
        }
        print(line)
        line_nlp = nlp(line)

        current_recipe_line["text"] = json.dumps([token.text for token in line_nlp])
        print(current_recipe_line["text"])

        for ent in line_nlp.ents:
            print("entity:", ent)
            if (ent.label_ == "INGREDIENT"):
                current_recipe_line["ingredients"].append({
                    "ingredient": {"name": ent.text},
                    "relevant_tokens": json.dumps((ent.start, ent.end))
                })
        recipe_lines_with_ingredients.append(current_recipe_line)

    recipe_with_ingredients = recipe_dict
    recipe_with_ingredients["recipe_lines"] = recipe_lines_with_ingredients

    return recipe_with_ingredients