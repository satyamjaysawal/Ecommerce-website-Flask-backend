from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserResponse, LoginRequest 
from app.crud.user import create_user, get_user_by_username, get_user_by_email, get_user_by_phone_number
from app.utils import (
    verify_password,
    create_access_token,
    decode_access_token,
    blacklist_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Use synchronous function calls (remove await)
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_phone_number(db, user.phone_number):
        raise HTTPException(status_code=400, detail="Phone number already registered")
    return create_user(db, user)

@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token_data = {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }
    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(authorization: str = Header(None)):
    """
    Logout a user by blacklisting their JWT token.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.split("Bearer ")[-1]
    decoded_data = decode_access_token(token)  # Validate token before blacklisting

    blacklist_token(token)  # Add token to blacklist

    return {"message": "Successfully logged out"}
