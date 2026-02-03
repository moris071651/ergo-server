import logging
import traceback
from typing import Optional, Dict
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException, Request, status
from psycopg2 import IntegrityError
from app.schemas.error import ErrorResponse
from starlette.responses import JSONResponse


logger = logging.getLogger(__name__)


class CustomBaseException(HTTPException):
    def __init__(self, status_code: int, message: str, detail: Optional[str] = None, headers: Optional[Dict[str, str]] = None):            
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.log_detail = detail or message


def setup_error_handling(app):
    @app.exception_handler(RequestValidationError)
    async def handle_validation_errors(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        if not errors:
            error_msg = "Invalid request"

        else:
            main_error = errors[0]
            loc = ".".join(str(x) for x in main_error["loc"] if x != "body")
            error_msg = f"{loc}: {main_error['msg']}"

        logger.warning(f"Validation Error at [{request.method}] {request.url.path}: {exc.errors()}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=ErrorResponse(error=error_msg).model_dump()
        )

    @app.exception_handler(HTTPException)
    async def handle_http_errors(request: Request, exception: HTTPException) -> ErrorResponse:
        log_func = logger.warning if exception.status_code >= 400 else logger.info
        log_func = logger.error if exception.status_code >= 500 else log_func

        log_detail = getattr(exception, "log_detail", exception.detail)
        log_func(f"HTTP {exception.status_code} at [{request.method}] {request.url.path}: {log_detail}")

        status_code = exception.status_code
        headers = getattr(exception, "headers", None)
        content = ErrorResponse(
            error=exception.detail
        ).model_dump()

        return JSONResponse(content, status_code, headers)
        
    @app.exception_handler(IntegrityError)
    def handle_integrity_errors(request: Request, exc: IntegrityError):
        logger.warning(f"Integrity Error at [{request.method}] {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(error="Database constraint violation").model_dump()
        )
    
    @app.exception_handler(NotImplementedError)
    async def handle_not_implemented_error(request: Request, exc: NotImplementedError):
        logger.info(f"NotImplemented Error at [{request.method}] {request.url.path}: {str(exc) or "Not implemented"}")

        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content=ErrorResponse(
                error="This feature is not implemented yet"
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def handle_generic_errors(request: Request, exception: Exception) -> ErrorResponse:
        error_traceback = traceback.format_exc()

        logger.critical(
            f"ERROR: {request.method} {request.url.path}\n"
            f"Exception: ({type(exception).__name__}) {str(exception)}\n"
            f"Traceback: {error_traceback}"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="An unexpected server error occurred"
            ).model_dump()
        )
    