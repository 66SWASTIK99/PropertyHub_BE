class UserAlreadyExists(Exception):

    def __init__(self, message="User already exists."):
        self.message = message
        super().__init__(self.message)

class InvalidCredential(Exception):

    def __init__(self, message="Invalid Credential."):
        self.message = message
        super().__init__(self.message)

class EmailAlreadyExists(Exception):

    def __init__(self, message="Email Already Exists"):
        self.message = message
        super().__init__(self.message)