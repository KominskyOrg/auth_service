class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

class AuthenticationError(Exception):
    def __init__(self, message="Authentication failed"):
        self.message = message

class AuthorizationError(Exception):
    def __init__(self, message="Authorization failed"):
        self.message = message

class DatabaseError(Exception):
    def __init__(self, message="Database operation failed"):
        self.message = message