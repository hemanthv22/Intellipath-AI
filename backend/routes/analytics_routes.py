from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.history_model import JobApplication

router = APIRouter()

# 1. ADD a new job application
@router.post("/add")
async def add_application(
    user_name: str = Form(...),
    company_name: str = Form(...),
    role_title: str = Form(...),
    status: str = Form(...),
    salary_range: str = Form(""),
    db: Session = Depends(get_db)
):
    new_app = JobApplication(
        user_name=user_name,
        company_name=company_name,
        role_title=role_title,
        status=status,
        salary_range=salary_range
    )
    db.add(new_app)
    db.commit()
    return {"status": "success", "message": "Application tracked successfully"}

# 2. GET all applications for a specific user
@router.get("/{user_name}")
def get_applications(user_name: str, db: Session = Depends(get_db)):
    apps = db.query(JobApplication).filter(JobApplication.user_name == user_name).order_by(JobApplication.created_at.desc()).all()
    
    # Format the data cleanly for the frontend
    return [
        {
            "id": app.id,
            "company_name": app.company_name,
            "role_title": app.role_title,
            "status": app.status,
            "salary_range": app.salary_range,
            "created_at": app.created_at.isoformat() if app.created_at else None
        }
        for app in apps
    ]

# 3. DELETE a specific application
@router.delete("/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id).first()
    if app:
        db.delete(app)
        db.commit()
        return {"status": "success"}
    return {"error": "Application not found"}