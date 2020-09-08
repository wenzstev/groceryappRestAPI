

# custom exception for sending more detailed API information
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict({"payload": self.payload} or ())
        rv['message'] = self.message
        return rv


class NotFoundException(InvalidUsage):
    def __init__(self, resource, id, message=None):
        if message is None:
            message = "The resource you've requested does not exist."
        payload = {"details": {"resource": resource.__tablename__, "id": id}}
        super().__init__(message=message, payload=payload, status_code=404)


# TODO: add a bad schema exception
