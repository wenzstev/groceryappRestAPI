
from grocerylistapp.models import User, GroceryList
from grocerylistapp.errors.exceptions import InvalidUsage

def get_list_by_params(args):
    if args.get("user"):
        user_id = args.get("user")
        if not User.query.get(user_id):
            raise InvalidUsage("This user does not exist.")
        user_lists = GroceryList.query\
            .join(User)\
            .filter(User.id==user_id)\
            .all()
        return user_lists

    return GroceryList.query.all()

