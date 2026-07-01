from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from controllers import resume_controller
from models.history_model import ResumeHistory # 1. ADD THIS IMPORT

router = APIRouter()

@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...), 
    job_description: str = Form(...),
    user_name: str = Form("Guest"),
    db: Session = Depends(get_db)
):
    return resume_controller.analyze_resume_with_ai(file, job_description, user_name, db)

# 2. ADD THIS ENTIRE NEW ROUTE
@router.get("/history/{user_name}")
def get_resume_history(user_name: str, db: Session = Depends(get_db)):
    # Fetch the user's history, ordered by newest first, limited to 10 rows
    history = db.query(ResumeHistory).filter(ResumeHistory.user_name == user_name).order_by(ResumeHistory.created_at.desc()).limit(10).all()
    return history