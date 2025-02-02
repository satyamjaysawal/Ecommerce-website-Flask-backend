from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from app.utils import hash_password
# Fetch all users (for admin)
def get_all_users(db: Session, skip: int = 0, limit: int = 10):
    """
    Retrieve all users with pagination.
    """
    return db.query(User).offset(skip).limit(limit).all()
def get_user_by_id(db: Session, user_id: int):
    """
    Retrieve a user by their ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """
    Retrieve a user by their username.
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user by their email.
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone_number(db: Session, phone_number: str):
    """
    Retrieve a user by their phone number.
    """
    return db.query(User).filter(User.phone_number == phone_number).first()

def create_user(db: Session, user: UserCreate):
    """
    Create a new user.
    """
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        phone_number=user.phone_number,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_profile(db: Session, user_id: int, update_data: dict):
    """
    Update a user's profile.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    """
    Delete a user by their ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return user
