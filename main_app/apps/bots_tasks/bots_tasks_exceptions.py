from fastapi import HTTPException, status


class BotTaskNotFound(HTTPException):
	def __init__(self):
		self.status_code = 400
		self.detail = "Bot task not found"
