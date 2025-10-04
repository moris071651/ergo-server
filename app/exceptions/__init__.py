from typing import Optional
from fastapi import Request, status
from schemas.error import ErrorResponse
from starlette.responses import JSONResponse

class CustomBaseException(Exception):
    def __init__(self, status: int, message: str, detail: Optional[str] = None):            
        super().__init__(message)
        self.status = status
        self.error = message
        self.detail = detail


def setup_error_handling(app):
    @app.exception_handler(CustomBaseException)
    def handle_server_errors(request: Request, exception: CustomBaseException) -> ErrorResponse:
        return JSONResponse(
            status_code=exception.status,
            content=ErrorResponse(
                error=exception.error,
                detail=exception.detail
            ).model_dump()
        )
    
    @app.exception_handler(Exception)
    def handle_generic_errors(request: Request, exception: Exception) -> ErrorResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal Server Error",
                detail=str(exception)
            ).model_dump()
        )
    