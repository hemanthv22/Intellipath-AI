from fastapi import APIRouter, Form
from controllers import interview_controller

router = APIRouter()

@router.post("/generate")
async def generate_question(
    resume_text: str = Form(...), 
    job_desc: str = Form(...),
    difficulty: str = Form("Intermediate") # Added difficulty parameter!
):
    # Pass the difficulty to the controller
    return interview_controller.generate_interview_question(resume_text, job_desc, difficulty)

@router.post("/evaluate")
async def evaluate_answer(
    question: str = Form(...), 
    user_answer: str = Form(...)
):
    return interview_controller.evaluate_answer(question, user_answer)