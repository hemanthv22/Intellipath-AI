from groq import Groq
from config import settings
from sqlalchemy.orm import Session
from models.history_model import ChatSession, ChatMessage

client = Groq(api_key=settings.GROQ_API_KEY)

def process_chat(message: str, user_name: str, session_id: str, db: Session):
    # 1. Create a new session if one doesn't exist
    if not session_id or session_id == "null":
        new_session = ChatSession(user_name=user_name, title=message[:30] + "...")
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session_id = str(new_session.id)
    
    # 2. Save User Message
    user_msg = ChatMessage(session_id=int(session_id), sender="user", text=message)
    db.add(user_msg)
    db.commit()

    # 3. Call Groq AI
    prompt = f"System: You are IntelliPath Mentor, an elite tech career advisor. You are talking to {user_name}. Format your responses cleanly using markdown (e.g., ### for headers, backticks for code).\nUser: {message}"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.5
        )
        reply_text = response.choices[0].message.content
        
        # 4. Save AI Response
        ai_msg = ChatMessage(session_id=int(session_id), sender="ai", text=reply_text)
        db.add(ai_msg)
        db.commit()

        return {"reply": reply_text, "session_id": session_id}
    except Exception as e:
        return {"error": str(e)}

def get_sessions(user_name: str, db: Session):
    sessions = db.query(ChatSession).filter(ChatSession.user_name == user_name).order_by(ChatSession.created_at.desc()).all()
    return [{"id": s.id, "title": s.title} for s in sessions]

def get_messages(session_id: int, db: Session):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return [{"sender": m.sender, "text": m.text} for m in messages]

def delete_session(session_id: int, db: Session):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        # Delete messages inside the session first
        db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
        # Delete the session itself
        db.delete(session)
        db.commit()
        return {"status": "success"}
    return {"error": "Session not found"}