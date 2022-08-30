class ApiVerifyError(Exception):
    def __init__(self, message, params={}):
        self.params = params
        self.message = message
        super().__init__(self.message)

class ApiCallerError(Exception):
    def __init__(self, message, params={}):
        self.params = params
        self.message = message
        super().__init__(self.message)