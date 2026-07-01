import json
from groq import Groq
from config import settings
from sqlalchemy.orm import Session
from models.history_model import SkillGapHistory

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_and_save_gap(user_name: str, role_title: str, missing_skills: str, suggestions: str, score: int, db: Session):
    prompt = f"""
    System: You are an Elite AI Tech Assessor.
    
    A candidate scored {score}/100 overall for the role: {role_title}.
    They are currently missing these skills: {missing_skills}
    
    Generate realistic individual proficiency scores (0 to 100) for this candidate across 6 core categories. 
    
    CRITICAL INSTRUCTION: Do NOT output static numbers. The scores MUST logically reflect their {score}% overall score. You MUST specifically lower the scores of the categories that relate to their missing skills.
    
    Return ONLY a valid JSON object in this exact format:
    {{
        "Frontend": <insert calculated number>,
        "Backend": <insert calculated number>,
        "Database": <insert calculated number>,
        "Cloud": <insert calculated number>,
        "SystemDesign": <insert calculated number>,
        "SoftSkills": <insert calculated number>
    }}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        radar_data = json.loads(chat_completion.choices[0].message.content)

        # Save to PostgreSQL
        new_gap = SkillGapHistory(
            user_name=user_name,
            role_title=role_title,
            overall_score=score,
            radar_scores=json.dumps(radar_data),
            missing_skills=missing_skills,
            ai_suggestions=suggestions
        )
        db.add(new_gap)
        db.commit()
        
        return {"status": "success", "radar_scores": radar_data}
        
    except Exception as e:
        print(f"Skill Gap AI Error: {e}")
        return {"error": str(e)}