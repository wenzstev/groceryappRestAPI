# groceryappRestAPI
RESTful API backend for new version of my Grocery List App. Rebuilt from ground up with more attention to design and stability. 

## Resources

The API exposes five main resources (Ingredients, Recipe Lines, Recipes, Grocery Lists, and Users), and two associations (Recipes-to-Grocery-Lists and Users-to-GroceryLists). Each of these resources supports GET, POST, PUT, and DELETE commands, with a few specific exceptions. 

### GroceryLists
**Accessed at:** /lists, /lists/<int:id>

**Ingredients can be accessed at:** /ingredients?list=<int:id>

Representation of a GroceryList. Essentially an empty container that holds recipes. Does not directly hold ingredients. Has one creator but an arbitrary number of editors. 

#### Attributes 
- id: The GroceryList's unique identifier in the database. Does not have real world meaning.
- name: The name of the GroceryList.
- creator_id: Identifier of the User who created the GroceryList. Cannot be changed. Many-to-one relationship.
- editors: List of Users who have editing permission for the GroceryList. Many-to-many relationship. Editors can add or remove recipes. Editors can add other users as Editors, but cannot remove the Creator. 
- recipes: List of recipes associated with the GroceryList. Many-to-many relationship. 

### Users
**Accessed at:** /users, /users/<int:id>

**Token at:** /users/token (requires authentication credentials)

Representation of a User. User can create an arbitrary number of GroceryLists and an arbitrary number of Recipes.

#### Attributes
- id: The User's unique identifier in the database. Does not have real world meaning.
- email: The User's email address. Must be verified (verification can currently be completed without email; requires frontend).
- password: The User's password. Hashed when stored in database. 
- access level: Determines whether or not user has admin powers. NOTE: Currently non-functional. 

### Recipes

**Accessed at:** /recipes, /recipes/<int:id>

Representation of a Recipe. Contains an arbitrary number of RecipeLines. Recipe can only be edited by it's creator; RecipeLines in the recipe can also only be edited by creator. Note that a Recipe can be added to a GroceryList by a user who is not the creator, but that user will be unable to edit the recipe's attributes. 

#### Attributes 
- id: The Recipe's unique identifier in the database. Does not have real world meaning.
- name: The name of the recipe
- recipe_lines: RecipeLines associated with the Recipe. Many-to-one relationship.
- creator_id: Identifier of the User who created the recipe. Cannot be changed. Only the user may edit the recipe's attributes and the associations of the RecipeLines. 
- url: If created from an online recipe, the URL of where the recipe was found. 

### RecipeLines

**Accessed at:** /lines, /lines/<int:id>

Representation of a line in a recipe (i.e., "one cup flour"). RecipeLines are not unique and their text may be duplicated. 

#### Attributes

- id: The RecipeLine's unique identifier in the database. Does not have real world meaning.
- text: String of the text in the RecipeLine. 
- recipe_id: Identifier of the Recipe the RecipeLine is associated with. Many-to-one relationship. 
- Ingredients: the Ingredients in the RecipeLine. Many-to-many relationship. Ingredients must be contained in the RecipeLine for the association to be accepted. 


### Ingredients

**Accessed at:** /ingredients, /ingredients/<int:id>, /ingredients/<string:name>

Representation of an ingredient. Ingredients are unique across the app; i.e., there is only one ingredient titled "white wine" and only one titled "flour." Each ingredient has a many-to-many association with a RecipeLine; Ingredients must be in the RecipeLine for an association to work; otherwise the program will reject it.

#### Attributes 

* id: The Ingredient's unqiue identifier in the database. Does not have real world meaning. 
* name: The text of the ingredient. Must be unique and lower-case (to prevent duplicates). 
