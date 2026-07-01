from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from controllers import assistant_controller

router = APIRouter()

@router.post("/chat")
async def chat_with_assistant(
    message: str = Form(...), 
    user_name: str = Form("Guest"),
    session_id: str = Form(None),
    db: Session = Depends(get_db)
):
    return assistant_controller.process_chat(message, user_name, session_id, db)

@router.get("/sessions/{user_name}")
def get_user_sessions(user_name: str, db: Session = Depends(get_db)):
    return assistant_controller.get_sessions(user_name, db)

@router.get("/messages/{session_id}")
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    return assistant_controller.get_messages(session_id, db)

@router.delete("/sessions/{session_id}")
def delete_chat_session(session_id: int, db: Session = Depends(get_db)):
    return assistant_controller.delete_session(session_id, db)