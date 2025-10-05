from app.exceptions import CustomBaseException
from fastapi import status


class UserAlreadyLoggedInException(CustomBaseException):
    def __init__(self):
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            'User Already Logged In'
        )



class UserNotLoggedInException(CustomBaseException):
    def __init__(self):
        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            'User Not Logged In'
        )


class UserAlreadyExistsException(CustomBaseException):
    def __init__(self):
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            'Username or email already exists'
        )


class InvalidCredentialsException(CustomBaseException):
    def __init__(self):
        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            'Invalid username or password'
        )