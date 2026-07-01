from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.user_model import User, PasswordResetOTP
from utils.security import get_password_hash, verify_password, create_access_token
from utils.email_utils import generate_otp, send_otp_email
from config import settings


def _is_expired(expires_at) -> bool:
    """Safely compares expires_at (which may come back tz-naive from some
    DB backends) against the current UTC time."""
    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        now = now.replace(tzinfo=None)
    return expires_at < now

def handle_signup(user_data: dict, db: Session):
    email = user_data.get("email")
    password = user_data.get("password")
    name = user_data.get("name", "Guest") # Default to Guest if not provided
    
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # 2. Hash the password
    hashed_password = get_password_hash(password)

    # 3. Create the new user object
    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
        college=user_data.get("college", ""),
        branch=user_data.get("branch", "")
    )

    # 4. Save to PostgreSQL
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully!", "user_id": new_user.id}

def handle_login(user_data: dict, db: Session):
    email = user_data.get("email")
    password = user_data.get("password")

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.name,
        "email": user.email
    }


# ==========================================
# FORGOT PASSWORD (OTP) FLOW
# ==========================================

def handle_forgot_password(email: str, db: Session):
    """Step 1: Generate an OTP, store it, and email it to the user."""
    user = db.query(User).filter(User.email == email).first()

    # Always clear out any older OTPs for this email first.
    db.query(PasswordResetOTP).filter(PasswordResetOTP.email == email).delete()

    if user:
        otp_code = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

        otp_entry = PasswordResetOTP(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.add(otp_entry)
        db.commit()

        send_otp_email(email, otp_code)

    # Same response whether or not the account exists, so we don't reveal
    # which emails are registered.
    return {"message": "If an account exists with this email, an OTP has been sent."}


def handle_verify_otp(email: str, otp: str, db: Session):
    """Step 2: Verify the OTP the user entered."""
    record = (
        db.query(PasswordResetOTP)
        .filter(PasswordResetOTP.email == email)
        .order_by(PasswordResetOTP.id.desc())
        .first()
    )

    if not record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No OTP request found for this email")

    if _is_expired(record.expires_at):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired. Please request a new one")

    if record.attempts >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Too many incorrect attempts. Please request a new OTP")

    if record.otp_code != otp:
        record.attempts += 1
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    record.is_verified = True
    db.commit()

    return {"message": "OTP verified successfully"}


def handle_reset_password(email: str, otp: str, new_password: str, db: Session):
    """Step 3: Confirm the OTP was verified, then update the password."""
    record = (
        db.query(PasswordResetOTP)
        .filter(PasswordResetOTP.email == email, PasswordResetOTP.otp_code == otp)
        .order_by(PasswordResetOTP.id.desc())
        .first()
    )

    if not record or not record.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP not verified. Please verify your OTP first")

    if _is_expired(record.expires_at):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired. Please request a new one")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password_hash = get_password_hash(new_password)
    db.delete(record)
    db.commit()

    return {"message": "Password updated successfully"}