from fastapi import HTTPException, status

class BotNotFound(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = "bot not found"

class BotAlreadyExists(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = "bot already exists"
