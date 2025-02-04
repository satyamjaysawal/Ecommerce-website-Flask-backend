from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from typing import Optional
import random
import string

# Secure Secret Key (Store in ENV Variables)
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Token Blacklist Storage (In-memory, for demo purposes)
BLACKLISTED_TOKENS = set()

def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT access token with user data."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """Decodes a JWT token and verifies its validity."""
    try:
        if token in BLACKLISTED_TOKENS:
            raise HTTPException(status_code=401, detail="Token has been revoked. Please login again.")
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def blacklist_token(token: str):
    """Add token to the blacklist to prevent further use."""
    BLACKLISTED_TOKENS.add(token)

def check_user_role(token: str, required_roles: list):
    """Validates the user's role from the JWT token against the required roles."""
    payload = decode_access_token(token.split("Bearer ")[-1])
    if payload.get("role") not in required_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return payload.get("role")

def generate_transaction_id():
    """Generate a random transaction ID (12 characters)."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def generate_tracking_id():
    """Generate a random tracking ID (10 characters)."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def get_user_role_from_token(authorization: str) -> str:
    """
    Decode token and return the user's role.
    """
    user_role = "guest"  # Default role
    if authorization:
        parts = authorization.split("Bearer ")
        if len(parts) == 2:
            token = parts[1]
            try:
                token_data = decode_access_token(token)
                user_role = token_data.get("role", "guest")
            except Exception as e:
                raise HTTPException(status_code=401, detail="Invalid authentication token.")
    return user_role