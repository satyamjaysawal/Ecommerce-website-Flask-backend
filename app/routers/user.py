from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.user import (
    get_user_by_id,
    get_all_users,
    update_user_profile,
    delete_user,
)
from app.utils import decode_access_token

router = APIRouter()

# Fetch logged-in user's profile
@router.get("/profile")
def get_logged_in_user_profile(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    print("DEBUG - Authorization Header:", authorization)  # Debugging header
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    print("DEBUG - Token Data:", token_data)  # Debugging token data

    user_id = token_data.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token does not contain user ID")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role,
    }

# Update logged-in user's profile
@router.put("/profile")
def update_logged_in_user_profile(
    update_data: dict,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    print("Authorization Header:", authorization)
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    print("Decoded Token Data:", token_data)

    user_id = token_data.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token does not contain user ID")

    # Fetch the user
    user = get_user_by_id(db, user_id)
    print("User Data Fetched:", user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Process the update
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    print("Updated User Data:", user)

    return {"message": "Profile updated successfully"}

# Fetch all users (Admin-only)
@router.get("/")
def get_all_users_for_admin(
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(10, description="Maximum number of records to fetch"),
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Admin-only: Fetch the list of all users with pagination.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    print("Token Data:", token_data)

    # Role check: Only admin users are allowed
    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    # Fetch users from the database
    users = get_all_users(db, skip=skip, limit=limit)
    return {
        "total_users": len(users),
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
            }
            for user in users
        ],
    }

# Fetch specific user profile (Admin-only)
@router.get("/{user_id}")
def get_any_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Admin-only: Fetch any user's profile by ID.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    print("Token Data:", token_data)

    # Role check: Only admin users are allowed
    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    # Fetch user from the database
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role,
    }

# Update user profile (Admin-only)
@router.put("/{user_id}")
def admin_update_user_profile(
    user_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Admin-only: Update any user's profile.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    print("Token Data:", token_data)

    # Role check: Only admin users are allowed
    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    # Fetch user to update
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return {
        "message": "User profile updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
        },
    }

# Delete user profile (Admin-only)
@router.delete("/{user_id}")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Admin-only: Delete any user's profile.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    print("Token Data:", token_data)

    # Role check: Only admin users are allowed
    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    # Fetch and delete user
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
