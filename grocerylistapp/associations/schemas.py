from marshmallow import fields, post_dump, pre_dump, post_load, pre_load

from grocerylistapp import ma
from grocerylistapp.models import Recipe, GroceryList, User


def check_if_tuple(data, first_id_name, second_id_name):
    if isinstance(data, tuple):
        id_, first_id, second_id = data
        return {"id": id_, first_id_name: first_id, second_id_name: second_id}
    return data


class ListRecipeAssociationSchema(ma.Schema):
    id = fields.Int()
    recipe_id = fields.Int(required=True)
    grocerylist_id = fields.Int(required=True)

    @pre_dump
    def split_tuple_int_dict(self, data, **kwargs):
        return check_if_tuple(data, "recipe_id", "grocerylist_id")

    @post_load
    def get_associated_recipe_grocerylist(self, data, **kwargs):
        return (
            GroceryList.query.get(data["grocerylist_id"]),
            Recipe.query.get(data["recipe_id"])
        )

    @pre_load
    def check(self, data, **kwargs):
        return check_if_tuple(data, "recipe_id", "grocerylist_id")


class EditorAssociationSchema(ma.Schema):
    id = fields.Int()
    grocerylist_id = fields.Int(required=True)
    user_id = fields.Int(requred=True)

    @pre_load
    def load_data(self, data, **kwargs):
        print("in preload")
        print(data)
        return check_if_tuple(data, "grocerylist_id", "user_id")

    @post_load
    def get_associated_user_grocerylist(self, data, **kwargs):
        return (
            GroceryList.query.get(data["grocerylist_id"]),
            User.query.get(data["user_id"])
        )

    @pre_dump
    def dump_data(self, data, **kwargs):
        return check_if_tuple(data, "grocerylist_id", "user_id")

