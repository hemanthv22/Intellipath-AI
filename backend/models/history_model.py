from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.sql import func
from database.db import Base

class ResumeHistory(Base):
    __tablename__ = "resume_history_v2" # Automatically creates a fresh table with the new columns!

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True) 
    job_target = Column(Text)            
    score = Column(Integer)
    keyword_match = Column(String)
    readability = Column(String)
    missing_skills = Column(Text, default="[]") 
    ai_suggestions = Column(Text, default="[]") 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Add this to the BOTTOM of your existing models/history_model.py file

class SkillGapHistory(Base):
    __tablename__ = "skill_gap_history"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    role_title = Column(String)
    overall_score = Column(Integer)
    
    # Store the 6 AI-generated category scores as a JSON string
    radar_scores = Column(Text) 
    missing_skills = Column(Text) 
    ai_suggestions = Column(Text) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Add this to the BOTTOM of your existing models/history_model.py file

class RoadmapHistory(Base):
    __tablename__ = "roadmap_history"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    target_role = Column(String)
    skill_gap_id = Column(Integer, index=True) # Links roadmap to the exact Skill Gap Analysis
    
    # Store the complete AI-generated timeline as a JSON string
    roadmap_data = Column(Text) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Add this to the BOTTOM of your existing models/history_model.py file

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    title = Column(String) # Auto-generated from the first message
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)
    sender = Column(String) # 'user' or 'ai'
    text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    company_name = Column(String)
    role_title = Column(String)
    status = Column(String) # Examples: 'Applied', 'Interviewing', 'Offered', 'Rejected'
    salary_range = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    
    # Roadmap Stats
    current_level = Column(String, default="Beginner")
    learning_streak = Column(Integer, default=0)
    skills_mastered = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())