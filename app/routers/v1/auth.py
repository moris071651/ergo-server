from fastapi import APIRouter


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup')
def signup():
    pass


@router.post('/login')
def login():
    pass


@router.get('/login')
def get_session_info():
    pass


@router.delete('/logout')
def logout():
    pass
