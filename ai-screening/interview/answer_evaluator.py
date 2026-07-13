import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "gemma:2b"


def evaluate_candidate_answer(question, candidate_answer):
    if not candidate_answer or not candidate_answer.strip():
        return "No candidate answer provided for evaluation."

    prompt = f"""
You are an expert technical interviewer and hiring panel evaluator.

Evaluate the candidate's answer for the interview question below.

Interview Question:
{question}

Candidate Answer:
{candidate_answer}

Provide the evaluation in this exact format:

### AI Evaluation

**Score:** X/10

**Technical Accuracy:**
Explain whether the answer is technically correct.

**Depth of Knowledge:**
Explain whether the candidate shows beginner, intermediate, or advanced understanding.

**Communication Clarity:**
Explain whether the answer is clear, structured, and professional.

**Strengths:**
List the strong points in the candidate answer.

**Gaps / Missing Points:**
List what the candidate missed or could improve.

**Suggested Follow-up Question:**
Provide one follow-up question the interviewer should ask.

**Hiring Recommendation:**
Choose one:
- Strong Hire
- Hire
- Consider
- Reject

Then give a short reason.
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "No evaluation response received from Ollama.")

    except Exception as e:
        return f"AI evaluation error: {e}"
