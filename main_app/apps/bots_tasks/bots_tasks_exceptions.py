from fastapi import HTTPException, status

class TaskTypeExist(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = "Task type exist"

class ErrorCreateTask(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = "Error while creating task"

class BotTaskNotFound(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = "Bot task not found"

class UpdateFinishedTaskError(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = "Wtf? Task is finished. Let it have a rest or remove it"
