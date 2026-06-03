from app.exceptions import CustomBaseException
from fastapi import status


class EmailUsedExistsException(CustomBaseException):
    def __init__(self):
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            'Email already used'
        )
