from fastapi import HTTPException, status


class BotTaskNotFound(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = "Bot task not found"

class UpdateFinishedTaskError(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = "Wtf? Task is finished. Let it have a rest or remove it"
