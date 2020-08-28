from flask import current_app

from grocerylistapp import db

from passlib.apps import custom_app_context as pwd_context

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

# association table between RecipeLine and Ingredient models (many-to-many relationship)
# CURRENTLY UNUSED
line_ingredient_associations = db.Table('line_ingredient_associations_UNUSED',
                                        db.Column('ingredient', db.Integer, db.ForeignKey('ingredient.id')),
                                        db.Column('recipe_line', db.Integer, db.ForeignKey('recipe_line.id')),
                                        db.Column('relevant_tokens', db.String)
                                        )

# association table between Recipe and GroceryList models (many-to-many relationship)
recipe_list_associations = db.Table('recipe_list_associations',
                                    db.Column('id', db.Integer, primary_key=True),
                                    db.Column('recipe', db.Integer, db.ForeignKey('recipe.id')),
                                    db.Column('grocery_list', db.Integer, db.ForeignKey('grocery_list.id'))
                                    )

# association table between GroceryList and User models (many-to-many relationship)
user_list_associations = db.Table('user_list_associations',
                                  db.Column('id', db.Integer, primary_key=True),
                                  db.Column('grocery_list', db.Integer, db.ForeignKey('grocery_list.id')),
                                  db.Column('user', db.Integer, db.ForeignKey('user.id'))
                                  )


# Represents an association between an ingredient and a recipe line
class LineIngredientAssociations(db.Model):
    __tablename__='line_ingredient_associations'
    id_ = db.Column(db.Integer, primary_key=True)  # separate because ingredient could appear more than once in a line
    ingredient_id = db.Column(db.ForeignKey('ingredient.id'))
    recipeline_id = db.Column(db.ForeignKey('recipe_line.id'))
    relevant_tokens = db.Column(db.String(), nullable=False)
    ingredient = db.relationship("Ingredient", back_populates='recipe_lines')
    recipe_line = db.relationship("RecipeLine", back_populates='ingredients')
    #TODO: color attribute to maintain persistent colors for frontend

    # TODO: Create a validator to confirm that the ingredient is on the recipe line

    def __repr__(self):
        return f"<Association of {self.ingredient} with {self.recipe_line} at {self.relevant_tokens}>"

# Represents an ingredient.
class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)    # the actual name of the ingredient
    recipe_lines = db.relationship("LineIngredientAssociations",    # lines where this ingredient appears.
                                   back_populates='ingredient')


    # validator to ensure that an ingredient is in the proper form (all lower case, no dashes or other symbols)
    @db.validates('name')
    def validate_name(self, key, address):
        if not address.islower():
            raise ValueError("Ingredient must be in all lower case!")
        return address

    # equal function for comparing different instances of the same Ingredient
    def __eq__(self, other):
        return self.id == other.id and self.name == other.name

    # hash function to enable sets to eliminate duplicates
    def __hash__(self):
        return hash((self.id, self.name))

    def __repr__(self):
        return f"<Ingredient '{self.name}'>"


# Represents a line in a recipe. Can hold an arbitrary number of ingredients
class RecipeLine(db.Model):
    __tablename__ = 'recipe_line'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)  # the text of the line
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    recipe = db.relationship("Recipe", back_populates="recipe_lines")
    ingredients = db.relationship("LineIngredientAssociations",
                                  back_populates="recipe_line")


    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        print(self.recipe)
        print(self.text)
        return f"<RecipeLine in '{self.recipe}' -- '{self.text[0:20]}...' >"


# Represents a recipe. Can relate to an arbitrary number of RecipeLines, many-to-one
class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200))     # url of where the recipe was gotten (if applicable)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # the creator of the recipe (used for editing permissions)
    creator = db.relationship("User", back_populates="recipes")
    recipe_lines = db.relationship("RecipeLine",
                                   back_populates='recipe',
                                   cascade="all, delete-orphan")
    grocery_lists = db.relationship("GroceryList",
                                    secondary=recipe_list_associations,
                                    back_populates="recipes")
    ai_list = db.relationship("GroceryList", back_populates="additional_ingredients")

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"<Recipe '{self.name}' id: {self.id}>"


# Represents a grocery list. Can relate to an arbitrary number of Recipes and Users (to allow collaboration)
class GroceryList(db.Model):
    __tablename__ = 'grocery_list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    recipes = db.relationship("Recipe",
                              secondary=recipe_list_associations,
                              back_populates="grocery_lists")
    additional_ingredients_id = db.Column(db.Integer, db.ForeignKey("recipe.id"))
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))   # the creator of the grocerylist. can add others to edit
    creator = db.relationship("User", back_populates="created_lists")
    editors = db.relationship("User",                           # other users with permission to edit the grocery list
                            secondary=user_list_associations,
                            back_populates="editable_lists")
    additional_ingredients = db.relationship("Recipe", back_populates="ai_list", cascade="all, delete-orphan", single_parent=True)



    # clears the grocerylist (for PUT requests) without removing the "Additional Ingredients" recipe
    # CURRENTLY UNUSED
    def clear_grocerylist(self):
        print(self)
        additional_ingredients = Recipe.query \
            .filter(Recipe.name == "Additional Ingredients",
                    Recipe.grocery_lists.contains(self)).first()
        print(additional_ingredients)
        additional_ingredients.recipe_lines.clear()
        self.recipes.clear()
        self.recipes.append(additional_ingredients)
        db.session.commit()


    def create_additional_ingredients_recipe(self):
        additional_ingredients_recipe = Recipe(name="Additional Ingredients", creator_id=self.creator_id)
        self.additional_ingredients = additional_ingredients_recipe
        self.recipes.append(additional_ingredients_recipe)
        db.session.add(additional_ingredients_recipe)
        db.session.commit()

    def __repr__(self):
        return f"<GroceryList '{self.name}'>"


# Represents a user. Can relate to an arbitrary number of GroceryLists
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    email_validated = db.Column(db.Boolean, nullable=False, default=False)
    hashed_password = db.Column(db.String(16), nullable=False)
    access_level = db.Column(db.Integer, nullable=False, default=0)
    recipes = db.relationship("Recipe", back_populates="creator")  # the recipes created by this user
    created_lists = db.relationship("GroceryList", back_populates="creator", cascade="all, delete-orphan")  # lists created by this user
    editable_lists = db.relationship("GroceryList",
                                    secondary=user_list_associations,
                                    back_populates="editors")

    # function to hash password
    def hash_password(self, password):
        self.hashed_password = pwd_context.encrypt(password)

    # function to verify password
    def verify_password(self, password):
        print(self.hashed_password)
        return pwd_context.verify(password, self.hashed_password)

    # generate a secure token for authentication
    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode("utf-8")


    # verify a token
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            print("signature expired")
            return None  # valid token, expired
        except BadSignature:
            print("invalid token")
            return None  # invalid token

        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return f"<User {id} -- email:'{self.email}' access_level: {self.access_level}>"
