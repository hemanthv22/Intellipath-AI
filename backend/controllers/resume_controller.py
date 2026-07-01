import io
import PyPDF2
import json
from groq import Groq
from fastapi import UploadFile
from sqlalchemy.orm import Session
from config import settings
from models.history_model import ResumeHistory # Import your new model

client = Groq(api_key=settings.GROQ_API_KEY)

# Notice we added user_name and db to the parameters
def analyze_resume_with_ai(resume_file: UploadFile, job_description: str, user_name: str, db: Session):
    # 1. Extract Text
    try:
        content = resume_file.file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        resume_text = "".join([page.extract_text() for page in pdf_reader.pages])
    except Exception as e:
        return {"error": f"PDF Parsing failed: {str(e)}"}

    # 2. Create the Prompt
    prompt = f"""
    System: You are an elite Technical Recruiter.
    Task: Compare the Resume below against the Job Description. 
    Output: A valid JSON object only.
    
    Job Description: {job_description}
    Resume: {resume_text}
    
    Required JSON structure:
    {{
        "score": 85,
        "keyword_match": "82%",
        "readability": "8/10",
        "missing": ["list", "of", "missing", "skills"],
        "suggestions": ["specific", "actionable", "advice"]
    }}
    """

    # 3. Call Groq
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", # Feel free to use your preferred model
            temperature=0.2, 
            response_format={"type": "json_object"} 
        )
        
        result = json.loads(chat_completion.choices[0].message.content)
        
        # ---------------------------------------------------------
        # 4. SAVE TO POSTGRESQL DATABASE
        # ---------------------------------------------------------
        try:
            new_history = ResumeHistory(
                user_name=user_name,
                job_target=job_description,
                score=result.get("score", 0),
                keyword_match=result.get("keyword_match", "N/A"),
                readability=result.get("readability", "N/A"),
                # NEW: Convert the Python arrays into JSON strings so Postgres can store them safely
                missing_skills=json.dumps(result.get("missing", [])),
                ai_suggestions=json.dumps(result.get("suggestions", []))
            )
            db.add(new_history)
            db.commit()
        except Exception as db_error:
            print(f"Database Save Error: {db_error}")

        return result

    except Exception as e:
        print(f"Groq API Error: {e}")
        return {"error": str(e)}