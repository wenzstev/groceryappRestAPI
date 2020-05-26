from flask import Blueprint, jsonify
from grocerylistapp.errors.exceptions import InvalidUsage, NotFoundException

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(InvalidUsage)
@errors.app_errorhandler(NotFoundException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

