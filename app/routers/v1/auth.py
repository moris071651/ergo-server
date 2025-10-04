from fastapi import APIRouter, Body, Request
from app.exceptions.auth import UserAlreadyLoggedInException, UserNotLoggedInException
from app.schemas.users import UserLoginRequest, UserSignupRequest


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup')
def signup(req: Request, new_user: UserSignupRequest = Body()):
    if req.state.user is not None:
        raise UserAlreadyLoggedInException()


@router.post('/login')
def login(req: Request, new_user: UserLoginRequest = Body()):
    if req.state.user is not None:
        raise UserAlreadyLoggedInException()


@router.get('/login')
def get_session_info(req: Request):
    if req.state.user is not None:
        raise UserNotLoggedInException()


@router.delete('/logout')
def logout(req: Request):
    if req.state.user is not None:
        raise UserNotLoggedInException()
