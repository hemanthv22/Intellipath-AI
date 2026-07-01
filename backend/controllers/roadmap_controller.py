import json
from groq import Groq
from config import settings
from sqlalchemy.orm import Session
from models.history_model import RoadmapHistory

client = Groq(api_key=settings.GROQ_API_KEY)

def get_or_generate_roadmap(user_name: str, target_role: str, skill_gap_id: int, missing_skills: str, db: Session):
    
    # 1. CHECK POSTGRESQL FIRST
    # If a roadmap already exists for this exact analysis, return it instantly!
    existing_roadmap = db.query(RoadmapHistory).filter(RoadmapHistory.skill_gap_id == skill_gap_id).first()
    
    if existing_roadmap:
        return {
            "status": "success", 
            "cached": True, # Lets frontend know it was instant
            "roadmap": json.loads(existing_roadmap.roadmap_data)
        }

    # 2. IF NOT IN DB, CALL GROQ AI
    prompt = f"""
    System: You are an Elite Tech Career Coach.
    
    Target Role: {target_role}
    Missing Skills: {missing_skills}
    
    Create a highly structured, chronological learning roadmap to master these missing skills.
    
    Return ONLY a valid JSON object in this exact format:
    {{
        "phases": [
            {{
                "title": "Skill Name or Concept",
                "duration": "e.g., 2 Weeks",
                "difficulty": "Beginner, Intermediate, or Advanced",
                "description": "Specific, actionable advice on what to build or learn."
            }}
        ]
    }}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        roadmap_data = json.loads(chat_completion.choices[0].message.content)

        # 3. SAVE NEW ROADMAP TO POSTGRESQL
        new_roadmap = RoadmapHistory(
            user_name=user_name,
            target_role=target_role,
            skill_gap_id=skill_gap_id,
            roadmap_data=json.dumps(roadmap_data)
        )
        db.add(new_roadmap)
        db.commit()
        
        return {"status": "success", "cached": False, "roadmap": roadmap_data}
        
    except Exception as e:
        print(f"Roadmap AI Error: {e}")
        return {"error": str(e)}