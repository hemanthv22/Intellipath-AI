from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from controllers import assessment_controller
from models.history_model import SkillGapHistory

router = APIRouter()

@router.post("/generate")
async def generate_gap(
    user_name: str = Form(...),
    role_title: str = Form(...),
    missing_skills: str = Form(...),
    suggestions: str = Form(...),
    score: int = Form(...),
    db: Session = Depends(get_db)
):
    return assessment_controller.generate_and_save_gap(user_name, role_title, missing_skills, suggestions, score, db)

@router.get("/history/{user_name}")
def get_gap_history(user_name: str, db: Session = Depends(get_db)):
    # Fetch past gap analyses ordered by newest first
    return db.query(SkillGapHistory).filter(SkillGapHistory.user_name == user_name).order_by(SkillGapHistory.created_at.desc()).all()