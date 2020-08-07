from grocerylistapp import nlp


def determine_ingredients_in_line(recipe_dict):
    print("determining ingredients")

    recipe_lines_with_ingredients = []

    for line in recipe_dict["recipe_lines"]:
        current_recipe_line = {
            "text": line,
            "ingredients": []
        }
        print(line)
        line_nlp = nlp(line)

        for ent in line_nlp.ents:
            print("entity:", ent)
            if (ent.label_ == "INGREDIENT"):
                current_recipe_line["ingredients"].append({"name": ent.text})
        recipe_lines_with_ingredients.append(current_recipe_line)

    recipe_with_ingredients = recipe_dict
    recipe_with_ingredients["recipe_lines"] = recipe_lines_with_ingredients

    return recipe_with_ingredients