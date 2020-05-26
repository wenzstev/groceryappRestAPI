from flask import g
from flask_mail import Message

from grocerylistapp import mail, auth
from grocerylistapp.models import User
from grocerylistapp.errors.exceptions import InvalidUsage


# email a user with the validation route, provided by the client
def send_validate_email(user, route):
    token = user.generate_auth_token(expiration=2000)
    print("token:", token)
    msg = Message('Verify Your Email', sender='groceryapp@gmail.com', recipients=[user.email])
    msg.body = f'''To verify your email, please visit this link: {route}/{token}.'''
    mail.send(msg)

    return token


# verifying password and email
@auth.verify_password
def verify_password(username_or_token, password, needs_valid_email=True):
    print(username_or_token, password)
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username, password
        user = User.query.filter_by(email=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
        if needs_valid_email and not user.email_validated:
            raise InvalidUsage("Email not validated.", 401)
    g.user = user
    return True

