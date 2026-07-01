from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from config import settings

# Setup the password hashing context using bcrypt
# Note: Ensure bcrypt==4.0.1 is installed to avoid the 72-byte bug
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the hashed version. 
    Handles potential passlib/bcrypt library conflicts."""
    try:
        # Cast to string to ensure passlib processes it correctly
        return pwd_context.verify(str(plain_password), str(hashed_password))
    except Exception as e:
        print(f"❌ Password verification failed: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hashes a plain text password for secure database storage."""
    return pwd_context.hash(str(password))

def create_access_token(data: dict) -> str:
    """Generates a JWT token for user sessions using modern UTC methods."""
    to_encode = data.copy()
    
    # NEW: Use timezone-aware UTC (required in Python 3.12+)
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode the JWT using settings from your .env
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt