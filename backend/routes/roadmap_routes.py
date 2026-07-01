from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from controllers import roadmap_controller
from models.history_model import RoadmapHistory, UserProgress# Added import for history

router = APIRouter()

@router.post("/generate")
async def generate_roadmap(
    user_name: str = Form(...),
    target_role: str = Form(...),
    skill_gap_id: int = Form(...),
    missing_skills: str = Form(...),
    db: Session = Depends(get_db)
):
    return roadmap_controller.get_or_generate_roadmap(user_name, target_role, skill_gap_id, missing_skills, db)

# NEW: Route to fetch saved roadmaps for the table!
@router.get("/history/{user_name}")
def get_roadmap_history(user_name: str, db: Session = Depends(get_db)):
    return db.query(RoadmapHistory).filter(RoadmapHistory.user_name == user_name).order_by(RoadmapHistory.created_at.desc()).all()

@router.get("/progress/{user_name}")
def get_user_progress(user_name: str, db: Session = Depends(get_db)):
    # Try to find the user's progress
    progress = db.query(UserProgress).filter(UserProgress.user_name == user_name).first()
    
    # If it's a new user, create a default profile starting at 0
    if not progress:
        progress = UserProgress(
            user_name=user_name,
            current_level="Beginner",
            learning_streak=0,
            skills_mastered=0,
            total_xp=0
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)

    return {
        "level": progress.current_level,
        "streak": progress.learning_streak,
        "skills": progress.skills_mastered,
        "xp": progress.total_xp
    }