import json
from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

# Added 'difficulty' to the function arguments
def generate_interview_question(resume_text: str, job_desc: str, difficulty: str):
    prompt = f"""
    System: You are an elite Technical Hiring Manager. 
    
    Look at this Job Description: {job_desc}
    Look at this Resume Context: {resume_text}
    
    Task: Based on the candidate's skills and the job description, generate a set of 5 Multiple Choice Questions (MCQs).
    
    CRITICAL REQUIREMENT: The difficulty level of these questions MUST BE strictly tailored to a {difficulty.upper()} level candidate.
    - If Beginner: Focus on core concepts and basic syntax.
    - If Intermediate: Focus on implementation details, edge cases, and standard architecture.
    - If Advanced: Focus on system design at scale, deep optimization, trade-offs, and complex debugging.
    
    Return ONLY a JSON object in this exact format:
    {{
        "questions": [
            {{
                "question": "The technical question?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "The exact string of the correct option",
                "explanation": "Briefly explain WHY this is correct."
            }}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", # Updated to a valid Groq model!
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

def evaluate_answer(question: str, user_answer: str):
    prompt = f"""
    You are a Technical Interviewer grading a candidate's MCQ answer.
    Question Asked: {question}
    Candidate Selected: {user_answer}
    
    Determine if this is the correct answer.
    Return ONLY a JSON object in this exact format:
    {{
        "score": 100, 
        "feedback": "Briefly explain WHY this is correct or incorrect."
    }}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", # Updated to a valid Groq model!
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}