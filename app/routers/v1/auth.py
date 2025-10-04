from fastapi import APIRouter, Request
from app.exceptions.auth import UserAlreadyLoggedInException, UserNotLoggedInException


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup')
def signup(req: Request):
    if req.state.user is not None:
        raise UserAlreadyLoggedInException()


@router.post('/login')
def login(req: Request):
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
