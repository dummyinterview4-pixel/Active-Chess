from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, User as UserSchema, Token
from app.config import settings
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
router = APIRouter()
@router.post('/register', response_model=UserSchema, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user.username) | (User.email == user.email)).first():
        raise HTTPException(400, 'Username or email already registered')
    obj = User(username=user.username, email=user.email, full_name=user.full_name, hashed_password=hash_password(user.password), role=user.role)
    db.add(obj); db.commit(); db.refresh(obj); return obj
@router.post('/login', response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password): raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Incorrect username or password')
    return {'access_token': create_access_token(user.username), 'token_type':'bearer'}
@router.get('/me', response_model=UserSchema)
def me(user=Depends(get_current_user)): return user
