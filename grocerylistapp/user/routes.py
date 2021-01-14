from flask import Blueprint, request, jsonify, g, make_response

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
@user.route("/api/users", methods=["GET"])
@auth.login_required
def get_users():
    all_users = User.query.all()
    return jsonify(users_schema.dump(all_users))


# post a new user
@user.route("/api/users", methods=["POST"])
def post_user():
    print(request.json)
    new_user = post_new_resource(User, request.json)
    return user_schema.dump(new_user)


# get a specific user
@user.route("/api/users/<int:id_>", methods=["GET"])
def get_user(id_):
    cur_user = get_resource_or_404(User, id_)
    return jsonify(user_schema.dump(cur_user))


# delete a user
@auth.login_required
@user.route("/api/users/<int:id_>", methods=["DELETE"])
def delete_user(id_):
    cur_user = get_resource_or_404(User, id_)
    if g.user != cur_user:
        raise InvalidUsage("You don't have permission to delete this user.", 401)
    db.session.delete(cur_user)
    db.session.commit()

    return ("", 204)


# change user information
@user.route("/api/users/<int:id_>", methods=["PUT"])
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
@user.route("/api/users/token")
def get_auth_token():
    refresh_token = request.cookies.get('refresh_token')
    print(refresh_token)
    if not refresh_token:
        raise InvalidUsage("No refresh token", 404)
    user = User.verify_auth_token(refresh_token)
    access_token = user.generate_auth_token(expiration=300)
    return jsonify({
        'token': access_token,
        'user': user_schema.dumps(user)
    })


# get a refresh token for a user
@user.route("/api/users/refresh-token")
@auth.login_required
def get_refresh_token():
    print(g.user)
    refresh_token = g.user.generate_auth_token(expiration=1209600)  # 14 days
    response = make_response('', 204)
    response.set_cookie('refresh_token', refresh_token, httponly=True)
    return response



# send a verification email
@user.route("/api/users/verification", methods=["GET"])
def send_verify_email():
    # not using decorator because email is not yet validated
    username = request.authorization["username"]
    password = request.authorization["password"]
    print(username, password)
    verify_password(username, password, needs_valid_email=False)

    url_to_send = request.args.get("url")
    if not url_to_send:
        raise InvalidUsage("You must provide a client-side url for the verification route")
    token = send_validate_email(g.user, url_to_send)
    return jsonify({"token": token})


# receive verification confirmation
@user.route("/api/users/verification", methods=["PUT"])
def verify_email():
    print("verifying email")
    token = request.args.get("token")
    print(token)
    print("args", request.args)
    if not token:
        raise InvalidUsage("No token received! Did you put it in the url?")
    user = User.verify_auth_token(token)
    if not user:
        raise InvalidUsage("Unable to get user from token.")
    user.email_validated = True
    db.session.commit()
    return jsonify(user_schema.dump(user))


# log out user by deleting httpOnly refresh cookie
@user.route('/api/users/logout')
def logout_user():
    response = make_response('', 204)
    response.set_cookie('refresh_token', '', expires=0)
    return response