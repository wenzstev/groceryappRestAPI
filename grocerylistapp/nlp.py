from grocerylistapp import nlp


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

        current_recipe_line["text"] = [token.text for token in line_nlp]
        print(current_recipe_line["text"])

        #TODO: when ingredient found, append the location of the ingredient
        #TODO: WILL I NEED TO CHANGE THE INGREDIENT SCHEMA??

        for ent in line_nlp.ents:
            print("entity:", ent)
            if (ent.label_ == "INGREDIENT"):
                current_recipe_line["ingredients"].append({"name": ent.text})
        recipe_lines_with_ingredients.append(current_recipe_line)

    recipe_with_ingredients = recipe_dict
    recipe_with_ingredients["recipe_lines"] = recipe_lines_with_ingredients

    return recipe_with_ingredients