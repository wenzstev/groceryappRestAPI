from marshmallow import fields, post_load, validates, ValidationError

from grocerylistapp import ma
from grocerylistapp.models import User


# schema that returns/validates a user
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True

    # return a user
    @post_load
    def return_user(self, data, **kwargs):
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user:
            return existing_user
        else:
            return User(**data)


# schema for creating a new user
class PostUserSchema(ma.Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    access_level = fields.Int(default=0)

    @post_load
    def return_new_user(self, data, **kwargs):
        data["hashed_password"] = data.pop("password")  # prevent typeerror when creating User
        new_user = User(**data)
        new_user.hash_password(new_user.hashed_password)
        return new_user

    @validates('password')
    def validate_password(self, password):
        if len(password) < 6:
            raise ValidationError("Password is too short!")
        if len(password) > 20:
            raise ValidationError("Password is too long!")
        if password.isalpha():
            raise ValidationError("Password must contain at least one number and one symbol!")
        if password.isdigit():
            raise ValidationError("Password must contain at least one letter!")
        required_characters = ['!', '@', "#", "$", "%", "^", "&", "*", "+", "=", "?"]
        if not any(char in password for char in required_characters):
            raise ValidationError(f"Password must contain one of the following characters: {required_characters}")

        return True

