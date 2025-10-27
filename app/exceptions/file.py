from fastapi import status

from app.exceptions import CustomBaseException


class NotImageFormatException(CustomBaseException):
    def __init__(self, user_id, file_ext):
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f'The provided "{file_ext}" is not a image',
            f'Wrong file format ({file_ext}) provided by user[{user_id}]'
        )


class FileCreationFailedException(CustomBaseException):
    def __init__(self, error_msg):
        super().__init__(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f'Upload failed. Please try again.',
            f'File upload encountered an error: {error_msg}'
        )


class FileDeletionFailedException(CustomBaseException):
    def __init__(self, error_msg):
        super().__init__(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f'Deletion failed. Please try again.',
            f'File deletion encountered an error: {error_msg}'
        )


class FileFetchingFailedException(CustomBaseException):
    def __init__(self, error_msg):
        super().__init__(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f'Fetching failed. Please try again.',
            f'File fetching encountered an error: {error_msg}'
        )