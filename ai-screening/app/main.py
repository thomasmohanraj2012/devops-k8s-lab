from fastapi import FastAPI
from pydantic import BaseModel
import requests
from prompts import SYSTEM_PROMPT, SCREENING_TEMPLATE

app = FastAPI(title="Comcast Talent Screening POC")

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL_NAME = "gemma:2b"

class ScreeningRequest(BaseModel):
    resume_text: str
    job_description: str
    role_activities: str

@app.get("/")
def home():
    return {
        "message": "Talent Screening POC API is running",
        "note": "Human-in-the-loop assistant only. No automated hiring decisions."
    }

@app.post("/screen")
def screen_candidate(request: ScreeningRequest):
    prompt = SYSTEM_PROMPT + "\n\n" + SCREENING_TEMPLATE.format(
        job_description=request.job_description,
        role_activities=request.role_activities,
        resume_text=request.resume_text
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    response.raise_for_status()

    result = response.json()

    return {
        "model": MODEL_NAME,
        "screening_summary": result.get("response", ""),
        "decision_note": "This output is for recruiter/hiring-manager review only. It must not be used as an automated hiring decision."
    }
