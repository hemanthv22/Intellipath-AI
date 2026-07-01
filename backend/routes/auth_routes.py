from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.db import get_db
from controllers import auth_controller

router = APIRouter()

# --- 1. PYDANTIC MODELS (This fixes the 422 Error!) ---
# These tell FastAPI exactly what data the frontend is sending
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    college: str = ""
    branch: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

# --- 2. ROUTES ---
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    # .dict() converts the Pydantic model back into a standard dictionary 
    # so your existing auth_controller doesn't have to change at all!
    return auth_controller.handle_signup(user_data.dict(), db)

@router.post("/login")
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    return auth_controller.handle_login(user_data.dict(), db)

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return auth_controller.handle_forgot_password(payload.email, db)

@router.post("/verify-otp")
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    return auth_controller.handle_verify_otp(payload.email, payload.otp, db)

@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_controller.handle_reset_password(payload.email, payload.otp, payload.new_password, db)