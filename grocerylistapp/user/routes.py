from flask import Blueprint, request, jsonify, g

from sqlalchemy.exc import IntegrityError

from marshmallow.exceptions import ValidationError


from grocerylistapp import db, auth
from grocerylistapp.models import User
from grocerylistapp.utils import get_resource_or_404, post_new_resource, load_resource_from_schema
from grocerylistapp.errors.exceptions import InvalidUsage, NotFoundException
from grocerylistapp.user.utils import send_validate_email, verify_password
from grocerylistapp.user.schemas import UserSchema, PostUserSchema


user = Blueprint("user", __name__)
user_schema = UserSchema(only=("email", "id", "access_level"))
users_schema = UserSchema(many=True, only=("email", "id", "access_level"))
create_user_schema = PostUserSchema()


# return all users, or a filtered list
@user.route("/users", methods=["GET"])
@auth.login_required
def get_users():
    all_users = User.query.all()
    return jsonify(users_schema.dump(all_users))


# post a new user
@user.route("/users", methods=["POST"])
def post_user():
    new_user = post_new_resource(User, request.json)
    return user_schema.dump(new_user)


# get a specific user
@user.route("/users/<int:id_>", methods=["GET"])
def get_user(id_):
    cur_user = get_resource_or_404(User, id_)
    return jsonify(user_schema.dump(cur_user))


# delete a user
@user.route("/users/<int:id_>", methods=["DELETE"])
def delete_user(id_):
    cur_user = get_resource_or_404(User, id_)
    db.session.delete(cur_user)
    db.session.commit()

    return ("", 204)


# change user information
@user.route("/users/<int:id_>", methods=["PUT"])
@auth.login_required
def change_user_info(id_):
    updated_user = get_resource_or_404(User, id_)
    if updated_user.id == g.user.id:
        try:
            updated_user_information = create_user_schema.load(request.json)
            updated_user.email = updated_user_information.email
            updated_user.hashed_password = updated_user_information.hashed_password
            db.session.commit()
            return jsonify(user_schema.dump(updated_user))
        except ValidationError as error:
            raise InvalidUsage("Your user data was not formatted correctly", payload=error.messages)
        except IntegrityError:
            raise InvalidUsage("That email is already in use.")

    raise InvalidUsage("You don't have permission to edit accounts that aren't yours.", 401)


# get a token for a user
@user.route("/users/token")
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


# send a verification email
@user.route("/users/verification", methods=["GET"])
def send_verify_email():
    # not using decorator because email is not yet validated
    username = request.authorization["username"]
    password = request.authorization["password"]
    verify_password(username, password, needs_valid_email=False)

    url_to_send = request.args.get("url")
    if not url_to_send:
        raise InvalidUsage("You must provide a client-side url for the verification route")
    token = send_validate_email(g.user, url_to_send)
    return jsonify({"token": token})


# receive verification confirmation
@user.route("/users/verification", methods=["PUT"])
def verify_email():
    print("verifying email")
    token = request.json.get("token")
    user = User.verify_auth_token(token)
    if not user:
        raise InvalidUsage("Unable to get user from token.")
    user.email_validated = True
    db.session.commit()
    return jsonify(user_schema.dump(user))